"""Evidence, bounded balance warnings, native builds and closed distribution staging."""
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from .contracts import BuilderError, contained, digest, encoded, input_hash, load_audio, load_dialogue, load_events, load_items, load_presentation, load_sprites, read_json, validate
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


def native_evidence(toolkit, root):
    marker = contained(root, '.builder/native-evidence.json')
    if not marker.exists():
        return None
    index = read_json(marker)
    evidence_path = contained(root, index['path'])
    if not evidence_path.is_file() or digest(evidence_path.read_bytes()) != index['sha256']:
        raise BuilderError('Native evidence changed or disappeared')
    receipt = read_json(evidence_path)
    config, cards, _, lock = validate(toolkit, root)
    build_receipt = read_json(contained(root, '.builder/build.json'))
    if (receipt.get('kind') != 'native' or receipt.get('ok') is not True or receipt.get('process_exit') != 0
            or receipt.get('input_sha256') != input_hash(root) or receipt.get('source_sha256') != source_hash(root)
            or receipt.get('toolkit_commit') != lock['toolkit_commit']
            or receipt.get('release_dll_sha256') != build_receipt['dll_sha256']
            or receipt.get('release_dll_sha256') != digest(contained(root, f'build/native/{config["id"]}.dll').read_bytes())):
        raise BuilderError('Native evidence is stale or did not pass; run a fresh lab')
    labels = {check.get('check') for check in receipt.get('checks', [])}
    required = {'registration', 'starting-kit', 'starter-trigger', 'resource-turn', 'rewards-shop', 'native-save-resume', 'item-pools', 'event-pools', 'dialogue-controls', 'sprite-integration', 'audio-controls', 'presentation-controls'}
    played = [(check.get('card'), check.get('upgraded')) for check in receipt.get('checks', []) if check.get('check') == 'paid-card']
    expected = {(card['id'], upgraded) for card in cards for upgraded in (False, True)}
    if receipt.get('failures') or not required <= labels or set(played) != expected or len(played) != len(expected):
        raise BuilderError('Native evidence does not cover the required suite and every generated upgrade')
    portraits = [(check.get('card'), check.get('upgraded'), check.get('asset')) for check in receipt.get('checks', [])
                 if check.get('check') == 'card-portrait']
    expected_portraits = {(card['id'], upgraded, card.get('portrait', 'assets/card.svg'))
                         for card in cards for upgraded in (False, True)}
    if set(portraits) != expected_portraits or len(portraits) != len(expected_portraits):
        raise BuilderError('Native evidence does not cover every generated portrait and upgrade')
    items = load_items(toolkit, root, config)
    for group, label in (('relics', 'authored-relic'), ('potions', 'authored-potion')):
        actual = [check.get('id') for check in receipt.get('checks', []) if check.get('check') == label]
        expected_items = {row['id'] for row in items[group]}
        if set(actual) != expected_items or len(actual) != len(expected_items):
            raise BuilderError(f'Native evidence does not cover every authored {group}')
    events = load_events(toolkit, root, config)
    for label in ('authored-event', 'event-leave', 'event-resume'):
        actual = [(check.get('id'), check.get('choice') if label == 'authored-event' else None)
                  for check in receipt.get('checks', []) if check.get('check') == label]
        expected_events = {(event['id'], choice['id'] if label == 'authored-event' else None) for event in events
                           for choice in (event['choices'] if label == 'authored-event' else [None])}
        if set(actual) != expected_events or len(actual) != len(expected_events):
            raise BuilderError(f'Native evidence does not cover every {label} case')
    dialogue = load_dialogue(toolkit, root, config)
    for label in ('authored-dialogue', 'dialogue-resume'):
        actual = [(c.get('ancient'), c.get('visit')) for c in receipt.get('checks', []) if c.get('check') == label]
        expected_dialogue = {(r['ancient'], r['visit']) for r in dialogue}
        if set(actual) != expected_dialogue or len(actual) != len(expected_dialogue):
            raise BuilderError(f'Native evidence does not cover every {label} case')
    sprites = load_sprites(toolkit, root, config)
    actual = [c.get('state') for c in receipt.get('checks', []) if c.get('check') == 'sprite-state']
    expected_states = set(sprites['states']) if sprites else set()
    if set(actual) != expected_states or len(actual) != len(expected_states):
        raise BuilderError('Native evidence does not cover every sprite state')
    if sprites and not {'sprite-victory', 'sprite-reset', 'sprite-resume'} <= labels:
        raise BuilderError('Native evidence does not cover sprite victory/reset/resume')
    fairy = [c.get('case') for c in receipt.get('checks', []) if c.get('check') == 'sprite-fairy-revive']
    expected_fairy = {'lethal-hit', 'held-death-pose', 'repeated-lethal-hit'} if sprites else set()
    if set(fairy) != expected_fairy or len(fairy) != len(expected_fairy):
        raise BuilderError('Native evidence does not cover every Fairy sprite revive case')
    audio = load_audio(toolkit, root, config)
    actual = [c.get('cue') for c in receipt.get('checks', []) if c.get('check') == 'audio-cue']
    expected_audio = set(audio['cues']) if audio else set()
    if set(actual) != expected_audio or len(actual) != len(expected_audio):
        raise BuilderError('Native evidence does not cover every audio cue')
    presentation = load_presentation(toolkit, root, config)
    rooms = set(presentation['rooms']) if presentation else set()
    actual = [c.get('room') for c in receipt.get('checks', []) if c.get('check') == 'room-presentation']
    if set(actual) != rooms or len(actual) != len(rooms):
        raise BuilderError('Native evidence does not cover every room presentation')
    if 'rest' in rooms and 'presentation-resume' not in labels:
        raise BuilderError('Native evidence does not cover presentation resume')
    return receipt


def balance(toolkit, root, comparator=None):
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
    report = dict(kind='heuristic', input_sha256=input_hash(root), findings=findings, reward_cards=len(reward),
                distribution=distribution, gaps=['Native comparator counts/type/rarity mix not supplied',
                'No campaign, synergy or human playtest evidence; thresholds are warnings, not balance verdicts'])
    merchant_counts = {kind: sum(c['type'] == kind for c in reward) for kind in ('Attack', 'Skill', 'Power')}
    report['merchant_coverage'] = dict(actual=merchant_counts, minimum=dict(Attack=2, Skill=2, Power=1),
                                     adequate=all(merchant_counts[kind] >= minimum for kind, minimum in [('Attack', 2), ('Skill', 2), ('Power', 1)]))
    if comparator:
        evidence = native_evidence(toolkit, root)
        if evidence is None:
            raise BuilderError('Native comparator parity requires a passing current test-native lab')
        matches = [c for c in evidence['native_comparators'] if c['character'] == comparator]
        if len(matches) != 1:
            raise BuilderError('Choose an exact native comparator ID: ' + ', '.join(c['character'] for c in evidence['native_comparators']))
        native = matches[0]['cards']
        def cells(rows):
            from collections import Counter
            return dict(Counter(c['rarity'] + '/' + c['type'] for c in rows))
        actual, target = cells(reward), cells(native)
        report['native_parity'] = dict(character=comparator, game=evidence['game'], expected=len(native), actual=len(reward),
            matches=target == actual,
            target_cells=target, actual_cells=actual,
            deficits={key: target.get(key, 0) - actual.get(key, 0) for key in sorted(target.keys() | actual.keys()) if target.get(key, 0) > actual.get(key, 0)},
            excess={key: actual.get(key, 0) - target.get(key, 0) for key in sorted(target.keys() | actual.keys()) if actual.get(key, 0) > target.get(key, 0)})
        report['gaps'].pop(0)
    return report


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
                             '-o', str(out), f'-p:Sts2DataDir={game_data}', '-p:BuilderNativeTests=false'], cwd=root,
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
    root = Path(root).resolve()
    paths = [contained(root, 'Character.csproj'), *sorted((root / 'src').rglob('*.cs'))]
    return digest(encoded({p.relative_to(root).as_posix(): digest(contained(root, p.relative_to(root).as_posix()).read_bytes()) for p in paths}))


def verify(toolkit, root):
    config, _, _, lock = validate(toolkit, root)
    pin_check(toolkit, root, lock)
    generate(toolkit, root, check=True)
    gaps = ['Native card lifecycle, targeting, power/resource, save/resume and room presentation unverified',
            'Full-pool native comparator and human balance playtests unperformed',
            'Physical Deck/controller and co-op unverified', 'Workshop upload/download verification unperformed']
    if config['features']['audio']:
        gaps.append('audio: audible/hardware review, hurt/victory cues and compressed/looped audio remain separate')
        if not load_audio(toolkit, root, config):
            gaps.append('audio: enabled without authored data; project-owned extensions require separate native evidence')
    if config['features']['events'] and not load_events(toolkit, root, config):
        gaps.append('events: enabled without authored data; project-owned extensions require separate native evidence')
    if config['features']['dialogue'] and not load_dialogue(toolkit, root, config):
        gaps.append('dialogue: enabled without authored data; project-owned extensions require separate native evidence')
    if config['features']['presentation']:
        gaps.append('presentation: selection/ending/energy/VFX and human room/layout/device review remain separate')
        presentation = load_presentation(toolkit, root, config)
        omitted = {'rest', 'shop'} - (set(presentation['rooms']) if presentation else set())
        if omitted:
            gaps.append('presentation: native imagery retained for ' + ', '.join(sorted(omitted)))
    if config['features']['sprites']:
        gaps.append('sprites: human crop/style review and selection/ending presentation remain separate')
        if not load_sprites(toolkit, root, config):
            gaps.append('sprites: enabled without authored data; project-owned extensions require separate native evidence')
    result = dict(kind='structural', toolkit_commit=lock['toolkit_commit'], input_sha256=input_hash(root),
                  source_sha256=source_hash(root), structural='pass', gaps=gaps, release_ready=False)
    try:
        evidence = native_evidence(toolkit, root)
        result['native'] = dict(status='pass', checks=len(evidence['checks']), game=evidence['game']) if evidence else dict(status='unperformed')
        if evidence:
            result['gaps'][0] = 'Native numeric fixtures passed; visual selection/room presentation still unreviewed'
            result['gaps'][1] = 'Native comparator catalog collected; original full-pool parity and human balance playtests still pending'
    except BuilderError as error:
        result['native'] = dict(status='stale', reason=str(error))
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
    try:
        evidence = native_evidence(toolkit, root)
        report['native_validation'] = dict(status='pass', game=evidence['game'], checks=len(evidence['checks']),
            test_dll_sha256=evidence.get('test_dll_sha256'), probe_source_sha256=evidence.get('probe_source_sha256'),
            gaps=evidence.get('gaps', [])) if evidence else dict(status='unperformed')
    except BuilderError as error:
        report['native_validation'] = dict(status='stale', reason=str(error))
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
