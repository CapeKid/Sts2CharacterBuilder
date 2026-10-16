"""Disposable owned-game labs; exact payloads, independent copies and one-shot probes."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import time
import uuid

from .contracts import BuilderError, contained, digest, encoded, input_hash, read_json, validate
from .project import atomic, generate
from .verification import build, pin_check, source_hash

APP_ID = '2868840'
PROFILE_PREFIX = 'Sts2CharacterBuilderLab-'
EXCLUDED = {'mods', 'mods_steamtest', 'steam_appid.txt', 'override.cfg'}


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def plain_tree(root):
    """Never follow links/junctions while preparing a supposedly independent game copy."""
    for directory, folders, files in os.walk(root, followlinks=False):
        for name in [*folders, *files]:
            path = Path(directory) / name
            attributes = getattr(path.lstat(), 'st_file_attributes', 0)
            if path.is_symlink() or attributes & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400):
                raise BuilderError(f'Lab sources cannot contain links: {path}')
        yield Path(directory), folders, files


def workshop_catalog(root):
    if not root.is_dir():
        raise BuilderError('Provide the actual existing Workshop content directory')
    rows = []
    for directory, _, files in plain_tree(root):
        for name in files:
            if not name.endswith('.json'):
                continue
            path = directory / name
            try:
                value = read_json(path)
            except BuilderError:
                continue
            if isinstance(value, dict) and isinstance(value.get('id'), str) and 'has_dll' in value:
                rows.append(dict(id=value['id'], path=path.relative_to(root).as_posix(), sha256=file_hash(path)))
    return sorted(rows, key=lambda row: row['path'])


def accounts(userdata):
    if not userdata.is_dir():
        raise BuilderError('Provide the existing Steam userdata directory for account discovery')
    # Steam directory names are account IDs; no personal identity is embedded in the toolkit.
    return ['default/1', *sorted('steam/' + str(76561197960265728 + int(p.name))
                                for p in userdata.iterdir() if p.is_dir() and p.name.isdecimal())]


def profile_parent():
    if os.name == 'nt' and os.environ.get('APPDATA'):
        return Path(os.environ['APPDATA']).resolve()
    if __import__('sys').platform.startswith('linux'):
        return Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))).resolve()
    raise BuilderError('Native lab profile setup currently supports Windows and Linux')


def check_target(toolkit, target, game):
    pins = read_json(toolkit / 'builder/compatibility.json')
    actual = str(game.get('version', '')).removeprefix('v')
    if target not in pins or actual != pins[target]['version']:
        raise BuilderError(f'Native lab target {target} does not match enabled game version {actual!r}; review compatibility pins before testing a new build')


def copy_lab(lab, game, baselib, profile, account_paths, catalog, mod_id, dll, payloads, token):
    """Prepare only new destinations. Kept separate so isolation can be tested without game files."""
    lab, game, profile = Path(lab).resolve(), Path(game).resolve(), Path(profile).resolve()
    if lab.exists() or profile.exists():
        raise BuilderError('Use fresh lab and profile directories; existing data is never reset')
    if game == lab or game.is_relative_to(lab) or lab.is_relative_to(game):
        raise BuilderError('Lab and owned source game must not overlap')
    if not profile.name.startswith(PROFILE_PREFIX) or not re.fullmatch(r'Sts2CharacterBuilderLab-[0-9a-f]{32}', profile.name):
        raise BuilderError('Profile must use a fresh generated lab identity')
    if lab == profile or lab.is_relative_to(profile) or profile.is_relative_to(lab):
        raise BuilderError('Godot profile and game lab must be distinct')
    # Complete source/link/path preflight before making any destination.
    sources = []
    for directory, folders, files in plain_tree(game):
        if directory == game:
            folders[:] = [name for name in folders if name.lower() not in EXCLUDED]
        for name in files:
            source = directory / name
            if directory == game and name.lower() in EXCLUDED:
                continue
            sources.append((source, source.relative_to(game).as_posix()))
    for relative in payloads:
        contained(lab, 'game/mods/' + mod_id + '/' + relative)
    for account in account_paths:
        contained(profile, account + '/settings.save')
    required_base = {'BaseLib.dll': baselib / 'lib/net9.0/BaseLib.dll',
                     'BaseLib.json': baselib / 'Content/BaseLib.json', 'BaseLib.pck': baselib / 'Content/BaseLib.pck'}
    if not all(path.is_file() for path in required_base.values()):
        raise BuilderError('BaseLib package must contain its DLL, manifest and PCK')
    inventory = {}
    for source, relative in sources:
        target = contained(lab, 'game/' + relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)  # Never hardlink or mutate the installed game.
        inventory['game/' + relative] = file_hash(target)
    atomic(contained(lab, 'game/steam_appid.txt'), APP_ID.encode())
    atomic(contained(lab, 'game/override.cfg'), (
        '[application]\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="' + profile.name +
        '"\n[display]\nwindow/size/mode=0\n').encode())
    for name, path in required_base.items():
        atomic(contained(lab, 'game/mods/BaseLib/' + name), path.read_bytes())
    for relative, data in payloads.items():
        atomic(contained(lab, 'game/mods/' + mod_id + '/' + relative), data)
    atomic(contained(lab, 'game/mods/' + mod_id + '/' + mod_id + '.dll'), dll)
    settings = dict(schema_version=5, fullscreen=False, window_size=dict(x=1280, y=800), language='eng',
                    seen_ea_disclaimer=True, mod_settings=dict(mods_enabled=True,
                    mod_list=[dict(id=row['id'], source=2, is_enabled=False) for row in catalog] +
                    [dict(id='BaseLib', source=1, is_enabled=True), dict(id=mod_id, source=1, is_enabled=True)]))
    for account in account_paths:
        atomic(contained(profile, account + '/settings.save'), encoded(settings))
    atomic(profile / 'builder-lab.json', encoded(dict(token=token, lab=str(lab))))
    # Include every copied/generated game byte in the launch verification contract.
    for path in (lab / 'game').rglob('*'):
        if path.is_file():
            inventory[path.relative_to(lab).as_posix()] = file_hash(path)
    return inventory


def prepare(toolkit, root, game, baselib, workshop, steam_userdata, lab_id):
    root = Path(root).resolve()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', lab_id):
        raise BuilderError('Lab ID must be a plain name of at most 64 characters')
    config, cards, assets, lock = validate(toolkit, root)
    pin_check(toolkit, root, lock)
    lab = contained(root, 'private/labs/' + lab_id)
    if lab.exists():
        raise BuilderError('Lab already exists; use a new ID')
    game, baselib, workshop, steam_userdata = map(lambda p: Path(p).resolve(), (game, baselib, workshop, steam_userdata))
    if not (game / 'release_info.json').is_file():
        raise BuilderError('Game root must contain release_info.json')
    check_target(toolkit, config['target'], read_json(game / 'release_info.json'))
    data_candidates = [p for p in game.glob('data_sts2_*') if (p / 'sts2.dll').is_file()]
    if len(data_candidates) != 1:
        raise BuilderError('Expected one owned data_sts2_* directory')
    catalog = workshop_catalog(workshop)
    account_paths = accounts(steam_userdata)
    base_manifest = read_json(baselib / 'Content/BaseLib.json')
    if base_manifest.get('id') != 'BaseLib' or base_manifest.get('version', '').removeprefix('v') != lock['baselib']:
        raise BuilderError('Lab BaseLib manifest must match the pinned dependency version')
    release = build(toolkit, root, data_candidates[0])
    probe = (toolkit / 'builder/templates/NativeProbe.cs.txt').read_text(encoding='utf-8').replace('@NAMESPACE@', config['namespace'])
    probe_path = contained(root, '.builder/NativeProbe.cs')
    atomic(probe_path, probe.encode())
    test_output = contained(root, 'build/native-tests')
    result = subprocess.run(['dotnet', 'build', str(root / 'Character.csproj'), '-c', 'Release', '-o', str(test_output),
                             f'-p:Sts2DataDir={data_candidates[0]}', '-p:BuilderNativeTests=true',
                             f'-p:BuilderProbeSource={probe_path}'], cwd=root, capture_output=True, text=True)
    atomic(contained(root, 'private/native-build.log'), (result.stdout + result.stderr).encode())
    if result.returncode:
        raise BuilderError('Native probe compile failed; see private/native-build.log')
    dll = contained(root, f'build/native-tests/{config["id"]}.dll').read_bytes()
    token = uuid.uuid4().hex
    profile = profile_parent() / (PROFILE_PREFIX + token)
    payloads = {config['id'] + '.json': contained(root, config['id'] + '.json').read_bytes()}
    payloads.update({asset['path']: contained(root, asset['path']).read_bytes() for asset in assets})
    inventory = copy_lab(lab, game, baselib, profile, account_paths, catalog, config['id'], dll, payloads, token)
    for name, expected in release['references'].items():
        relative = 'game/' + data_candidates[0].name + '/' + name
        if inventory.get(relative) != expected:
            raise BuilderError('Owned game changed during preparation; create a new lab')
    request = dict(token=token, profile_path=str(profile), test_dll_sha256=digest(dll),
                   game_dll_sha256=release['references']['sts2.dll'], baselib_sha256=file_hash(baselib / 'lib/net9.0/BaseLib.dll'),
                   input_sha256=input_hash(root), cards=cards,
                   focus_starter=config['features']['items'] and config['features']['mechanic'])
    atomic(lab / 'request.json', encoded(request))
    manifest = dict(schema_version=1, id=lab_id, mod_id=config['id'], token=token, profile_path=str(profile),
                    game_source=str(game), workshop=str(workshop), workshop_catalog=catalog,
                    toolkit_commit=lock['toolkit_commit'], input_sha256=input_hash(root), source_sha256=source_hash(root),
                    probe_source_sha256=digest(probe.encode()), request_sha256=file_hash(lab / 'request.json'),
                    game=release['game'], target=config['target'], release_dll_sha256=release['dll_sha256'],
                    inventory=inventory, independent_copies=True,
                    profile_inventory={p.relative_to(profile).as_posix(): file_hash(p) for p in profile.rglob('*') if p.is_file()})
    atomic(lab / 'lab.json', encoded(manifest))
    return dict(lab=str(lab), profile=str(profile), game=release['game'], status='prepared', test_dll_sha256=digest(dll))


def check_lab(toolkit, root, lab_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', lab_id):
        raise BuilderError('Invalid lab ID')
    config, _, _, lock = validate(toolkit, root)
    pin_check(toolkit, root, lock)
    generate(toolkit, root, check=True)
    lab = contained(root, 'private/labs/' + lab_id)
    manifest = read_json(lab / 'lab.json')
    if manifest['input_sha256'] != input_hash(root) or manifest['source_sha256'] != source_hash(root) or manifest['toolkit_commit'] != lock['toolkit_commit']:
        raise BuilderError('Lab is stale; prepare a new lab from the current project/toolkit')
    if manifest['request_sha256'] != file_hash(lab / 'request.json'):
        raise BuilderError('Lab request changed')
    if manifest['workshop_catalog'] != workshop_catalog(Path(manifest['workshop'])):
        raise BuilderError('Workshop catalog changed; prepare a new isolated lab')
    for relative, expected in manifest['inventory'].items():
        path = contained(lab, relative)
        if not path.is_file() or file_hash(path) != expected:
            raise BuilderError(f'Lab byte changed: {relative}')
    actual = {p.relative_to(lab).as_posix() for directory, _, files in plain_tree(lab / 'game') for p in (directory / name for name in files)}
    if actual != manifest['inventory'].keys():
        raise BuilderError('Lab game has extra or missing files')
    profile = Path(manifest['profile_path']).resolve()
    expected_profile = (profile_parent() / (PROFILE_PREFIX + manifest['token'])).resolve()
    if profile != expected_profile:
        raise BuilderError('Lab profile identity/path differs')
    for relative, expected in manifest['profile_inventory'].items():
        path = contained(profile, relative)
        if not path.is_file() or file_hash(path) != expected:
            raise BuilderError(f'Lab profile byte changed: {relative}')
    return lab, manifest


def run_native(toolkit, root, lab_id, timeout=240):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', lab_id):
        raise BuilderError('Invalid lab ID')
    if not 30 <= timeout <= 600:
        raise BuilderError('Native timeout must be between 30 and 600 seconds')
    lab = contained(root, 'private/labs/' + lab_id)
    if (lab / 'run.json').exists() or (lab / 'result.json').exists():
        raise BuilderError('This one-shot lab was already started; never replay a timed-out mutation')
    lab, manifest = check_lab(toolkit, root, lab_id)
    candidates = [p for p in (lab / 'game').iterdir() if p.name in ('SlayTheSpire2.exe', 'SlayTheSpire2', 'SlayTheSpire2.x86_64')]
    if len(candidates) != 1:
        raise BuilderError('Could not identify the copied game executable')
    request = read_json(lab / 'request.json')
    env = dict(os.environ, STSCB_TEST_ROOT=str(lab), STSCB_TEST_TOKEN=manifest['token'])
    atomic(lab / 'run.json', encoded(dict(status='started', token=manifest['token'])))
    kwargs = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
    log = lab / 'process.log'
    with log.open('wb') as stream:
        process = subprocess.Popen([str(candidates[0]), '--headless', '--path', str(lab / 'game'), '--log-file', str(lab / 'godot.log')],
                                   cwd=lab / 'game', env=env, stdout=stream, stderr=subprocess.STDOUT, **kwargs)
        deadline = time.monotonic() + timeout
        progress = None
        try:
            while process.poll() is None and time.monotonic() < deadline:
                if (lab / 'progress.json').exists():
                    try:
                        current = read_json(lab / 'progress.json')
                        if current != progress:
                            print(__import__('json').dumps(current), flush=True)
                            progress = current
                    except BuilderError:
                        pass
                time.sleep(.25)
            if process.poll() is None:
                process.kill(); process.wait(timeout=10)
                atomic(lab / 'run.json', encoded(dict(status='timeout', token=manifest['token'])))
                raise BuilderError(f'Native probe timed out; inspect {log}; prepare a new lab rather than replaying it')
        finally:
            if process.poll() is None:
                process.kill(); process.wait(timeout=10)
    if not (lab / 'result.json').is_file():
        raise BuilderError(f'Game exited {process.returncode} without native evidence; inspect {log}')
    result = read_json(lab / 'result.json')
    for key in ('token', 'input_sha256', 'test_dll_sha256', 'game_dll_sha256', 'baselib_sha256'):
        if result.get(key) != request[key]:
            raise BuilderError(f'Native evidence correlation/hash mismatch: {key}')
    if result.get('kind') != 'native' or not isinstance(result.get('checks'), list):
        raise BuilderError('Invalid native evidence envelope')
    receipt = dict(**result, game=manifest['game'], target=manifest['target'], toolkit_commit=manifest['toolkit_commit'],
                   source_sha256=manifest['source_sha256'], release_dll_sha256=manifest['release_dll_sha256'],
                   probe_source_sha256=manifest['probe_source_sha256'], process_exit=process.returncode,
                   independent_copies=True, profile_path=manifest['profile_path'])
    atomic(lab / 'evidence.json', encoded(receipt))
    atomic(lab / 'run.json', encoded(dict(status='complete' if result.get('ok') and process.returncode == 0 else 'failed', token=manifest['token'])))
    if not result.get('ok') or process.returncode != 0:
        raise BuilderError(f'Native checks failed; inspect {lab / "evidence.json"}')
    if manifest['input_sha256'] != input_hash(root) or manifest['source_sha256'] != source_hash(root):
        raise BuilderError('Project changed while the native lab ran; historical evidence was preserved, but a fresh lab is required')
    atomic(contained(root, '.builder/native-evidence.json'), encoded(dict(path=(lab / 'evidence.json').relative_to(root).as_posix(),
           sha256=file_hash(lab / 'evidence.json'))))
    return dict(evidence=str(lab / 'evidence.json'), checks=len(result['checks']), status='pass', gaps=result['gaps'])
