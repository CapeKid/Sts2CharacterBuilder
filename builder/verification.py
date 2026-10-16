"""Evidence, bounded balance warnings, native builds and closed distribution staging."""
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from .contracts import BuilderError, contained, digest, encoded, input_hash, read_json, validate
from .project import OPTIONAL, STEPS, atomic, generate, run


def pin_check(toolkit, root, lock):
    pinned = contained(root, 'tools/character-builder')
    if not pinned.is_dir():
        raise BuilderError('Missing toolkit submodule; run git submodule update --init --recursive')
    if not (pinned / '.git').is_file():
        raise BuilderError('Toolkit must be a real Git submodule, not a copied directory')
    index = run(['git', 'ls-files', '--stage', 'tools/character-builder'], root)
    if not index.startswith('160000 ' + lock['toolkit_commit'] + ' '):
        raise BuilderError('Stage the toolkit gitlink matching builder.lock.json')
    actual = run(['git', 'rev-parse', 'HEAD'], pinned)
    if actual != lock['toolkit_commit'] or toolkit.resolve() != pinned.resolve():
        raise BuilderError('Run the pinned submodule CLI; toolkit commit differs from builder.lock.json')
    if run(['git', 'status', '--porcelain', '--untracked-files=normal'], pinned):
        raise BuilderError('Toolkit submodule is modified; commit and review an explicit upgrade first')


def doctor(toolkit, root, game_data=None):
    result = dict(python=sys.version.split()[0], git=shutil.which('git'), dotnet=shutil.which('dotnet'),
                  game_data=None, gaps=[])
    if game_data:
        directory = Path(game_data).resolve()
        required = ['sts2.dll', 'GodotSharp.dll', '0Harmony.dll']
        result['game_data'] = {x: (directory / x).is_file() for x in required}
        if not all(result['game_data'].values()):
            result['gaps'].append('Owned game references are incomplete')
    else:
        result['gaps'].append('Pass --game-data to test owned local references')
    if not result['dotnet']:
        result['gaps'].append('.NET SDK is missing')
    if not result['git']:
        result['gaps'].append('Git is missing')
    if (root / 'character.json').is_file():
        *_, lock = validate(toolkit, root)
        pin_check(toolkit, root, lock)
        result['project'] = 'valid'
    result['native_gameplay'] = 'unperformed; compilation does not establish gameplay correctness'
    return result


def resume(toolkit, root):
    config, _, _, lock = validate(toolkit, root)
    pin_check(toolkit, root, lock)
    current = input_hash(root)
    state_file = contained(root, '.builder/state.json')
    state = read_json(state_file) if state_file.exists() else {}
    rows = {}
    for step in STEPS:
        record = state.get(step)
        if step in OPTIONAL and not config['features'][OPTIONAL[step]]:
            rows[step] = dict(status='skipped', reason='Custom feature disabled; documented fallback applies')
        elif record and record['input_sha256'] == current and all(
                contained(root, p).is_file() and digest(contained(root, p).read_bytes()) == h
                for p, h in record['outputs'].items()):
            rows[step] = record
        else:
            rows[step] = dict(status='pending', reason='Inputs/evidence changed' if record else 'No completion evidence')
    return dict(input_sha256=current, steps=rows, next=next((s for s in STEPS if rows[s]['status'] not in {'complete', 'skipped'}), None))


def record(toolkit, root, step, status, evidence, note):
    validate(toolkit, root)
    if status == 'complete' and not evidence:
        raise BuilderError('Completion requires project-relative evidence files')
    paths = {p: digest(contained(root, p).read_bytes()) for p in evidence}
    state_file = contained(root, '.builder/state.json')
    state = read_json(state_file) if state_file.exists() else {}
    state[step] = dict(status=status, input_sha256=input_hash(root), outputs=paths, note=note)
    atomic(state_file, encoded(state))
    return state[step]


def balance(toolkit, root):
    config, cards, _, _ = validate(toolkit, root)
    findings = []
    for card in cards:
        for version in ('base', 'upgrade'):
            v = card[version]
            cost = v['cost']
            codes = []
            repeatable = card['type'] != 'Power' and not card['exhaust']
            if v['draw'] and v['energy'] >= cost and repeatable:
                codes.append('repeatable_draw_energy_loop_risk')
            if cost == 0 and (v['draw'] or v['focus']) and repeatable:
                codes.append('repeatable_free_scaling_risk')
            if v['energy'] > cost:
                codes.append('energy_positive')
            if v['damage'] + v['block'] > 14 * max(1, cost) or v['focus'] > 3:
                codes.append('high_combined_payoff_review')
            if not sum(v[k] for k in ('damage', 'block', 'draw', 'energy', 'focus')):
                codes.append('no_payoff')
            if cost >= 2 and v['damage'] + v['block'] < 5 and not (v['draw'] or v['energy'] or v['focus']):
                codes.append('low_payoff_review')
            for code in codes:
                findings.append(dict(card=card['id'], version=version, code=code, severity='review'))
    reward = [c for c in cards if c['rarity'] != 'Basic']
    distribution = {key: {value: sum(c[key] == value for c in reward) for value in sorted({c[key] for c in reward})}
                    for key in ('rarity', 'type')}
    return dict(kind='heuristic', input_sha256=input_hash(root), findings=findings, reward_cards=len(reward),
                distribution=distribution, gaps=['Native comparator counts/type/rarity mix not supplied',
                'No campaign, synergy or human playtest evidence; thresholds are warnings, not balance verdicts'])


def build(toolkit, root, game_data):
    config, _, _, lock = validate(toolkit, root)
    pin_check(toolkit, root, lock)
    generate(toolkit, root, check=True)
    game_data = Path(game_data).resolve()
    reference_hashes = {}
    for name in ('sts2.dll', 'GodotSharp.dll', '0Harmony.dll'):
        path = game_data / name
        if not path.is_file():
            raise BuilderError(f'Missing owned game reference: {name}')
        reference_hashes[name] = digest(path.read_bytes())
    out = contained(root, 'build/native')
    # Native outputs are never released by globbing this directory.
    result = subprocess.run(['dotnet', 'build', str(root / 'Character.csproj'), '-c', 'Release',
                             '-o', str(out), f'-p:Sts2DataDir={game_data}'], cwd=root,
                            capture_output=True, text=True)
    atomic(contained(root, 'private/build.log'), (result.stdout + result.stderr).encode())
    if result.returncode:
        raise BuilderError('Native compile failed; see private/build.log')
    # The first successful build may enter native saves. Persist identity protection in Git,
    # rather than relying on ignored receipts that disappear in a recursive clone.
    generate(toolkit, root, freeze=True)
    dll = contained(root, f'build/native/{config["id"]}.dll')
    release_info = game_data.parent / 'release_info.json'
    commit = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], cwd=root, capture_output=True, text=True)
    receipt = dict(kind='compile', toolkit_commit=lock['toolkit_commit'], project_commit=commit.stdout.strip() if commit.returncode == 0 else 'uncommitted',
                   project_dirty=bool(run(['git', 'status', '--porcelain'], root)),
                   input_sha256=input_hash(root), dll_sha256=digest(dll.read_bytes()),
                   references=reference_hashes, baselib=lock['baselib'], target=config['target'],
                   game=read_json(release_info) if release_info.exists() else {'version': 'unidentified'},
                   source_sha256=source_hash(root), native_gameplay='unperformed')
    atomic(contained(root, '.builder/build.json'), encoded(receipt))
    return receipt


def source_hash(root):
    paths = [contained(root, 'Character.csproj'), *sorted((root / 'src').rglob('*.cs'))]
    return digest(encoded({p.relative_to(root).as_posix(): digest(contained(root, p.relative_to(root).as_posix()).read_bytes()) for p in paths}))


def verify(toolkit, root):
    config, _, _, lock = validate(toolkit, root)
    pin_check(toolkit, root, lock)
    generate(toolkit, root, check=True)
    gaps = ['Native card lifecycle, targeting, power/resource, save/resume and room presentation unverified',
            'Full-pool native comparator and human balance playtests unperformed',
            'Physical Deck/controller and co-op unverified', 'Workshop upload/download verification unperformed']
    for feature in ('events', 'dialogue', 'sprites', 'audio'):
        if config['features'][feature]:
            gaps.append(f'{feature}: requires project-owned implementation and native evidence; generator does not implement it')
    result = dict(kind='structural', toolkit_commit=lock['toolkit_commit'], input_sha256=input_hash(root),
                  source_sha256=source_hash(root), structural='pass', gaps=gaps, release_ready=False)
    atomic(contained(root, 'private/verification.json'), encoded(result))
    return result


def stage(toolkit, root):
    config, _, assets, lock = validate(toolkit, root)
    pin_check(toolkit, root, lock)
    generate(toolkit, root, check=True)
    receipt = read_json(contained(root, '.builder/build.json'))
    dll = contained(root, f'build/native/{config["id"]}.dll').read_bytes()
    if receipt['input_sha256'] != input_hash(root) or receipt['source_sha256'] != source_hash(root) or receipt['dll_sha256'] != digest(dll):
        raise BuilderError('Build receipt is stale; rebuild before staging')
    # Exact allowlist: no toolkit, game assemblies, saves, logs or development bridge.
    prefix = config['id'] + '/'
    files = {prefix + config['id'] + '.dll': dll,
             prefix + config['id'] + '.json': contained(root, config['id'] + '.json').read_bytes(),
             prefix + 'LICENSE': contained(root, 'LICENSE').read_bytes()}
    for asset in assets:
        files[prefix + asset['path']] = contained(root, asset['path']).read_bytes()
    files[prefix + 'assets/manifest.json'] = contained(root, 'assets/manifest.json').read_bytes()
    report = dict(kind='private-test-package', id=config['id'], version=config['version'],
                  input_sha256=input_hash(root), build=receipt, release_ready=False,
                  files={p: digest(data) for p, data in sorted(files.items())},
                  dependency='Install BaseLib 3.4.7 separately; it is not bundled')
    files[prefix + 'package-inspection.json'] = encoded(report)
    dist = contained(root, 'dist')
    dist.mkdir(exist_ok=True)
    target = dist / f'{config["id"]}-{config["version"]}.zip'
    with tempfile.TemporaryFile() as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path, data in sorted(files.items()):
                info = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
        stream.seek(0)
        atomic(target, stream.read())
    atomic(contained(root, 'dist/package-inspection.json'), encoded(report))
    return dict(archive=str(target), sha256=digest(target.read_bytes()), **report)


def compare_delivery(root, directory):
    report = read_json(contained(root, 'dist/package-inspection.json'))
    directory = Path(directory).resolve()
    for name, expected in report['files'].items():
        path = contained(directory, name)
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise BuilderError(f'Downloaded delivery differs: {name}')
    expected_paths = set(report['files']) | {report['id'] + '/package-inspection.json'}
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    if actual != expected_paths:
        raise BuilderError('Downloaded delivery has unexpected or missing files')
    return dict(kind='delivery-bytes', status='match', visibility='requires authenticated Workshop verification')
