"""Strict authoring contracts, adapted from scripts/design_schema.py without game tables."""
import hashlib
import json
import re
from pathlib import Path


class BuilderError(ValueError):
    pass


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise BuilderError(f'{path}: duplicate property {key}')
            result[key] = value
        return result

    def invalid(value):
        raise BuilderError(f'{path}: invalid number {value}')

    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                          object_pairs_hook=unique, parse_constant=invalid)
    except (OSError, UnicodeError, ValueError) as error:
        raise BuilderError(str(error)) from error


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def contained(root, relative):
    if not isinstance(relative, str) or '\\' in relative or ':' in relative:
        raise BuilderError(f'Unsafe project path: {relative!r}')
    if not relative or relative.startswith('/') or any(x in ('', '.', '..') for x in relative.split('/')):
        raise BuilderError(f'Unsafe project path: {relative!r}')
    root = Path(root).resolve()
    path = root / relative
    # Refuse symlinks/junctions even when they happen to point back into the project.
    for parent in [path, *path.parents]:
        if parent == root:
            break
        if parent.is_symlink() or (hasattr(parent, 'is_junction') and parent.is_junction()):
            raise BuilderError(f'Linked project path: {relative}')
    if not path.resolve().is_relative_to(root):
        raise BuilderError(f'Path escapes project: {relative}')
    return path


def check_schema(value, spec, label='$'):
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
    expected = types[spec['type']]
    if type(value) is not expected:
        raise BuilderError(f'{label}: expected {spec["type"]}')
    if 'enum' in spec and value not in spec['enum']:
        raise BuilderError(f'{label}: expected one of {spec["enum"]}')
    if expected is dict:
        missing = set(spec.get('required', [])) - value.keys()
        unknown = value.keys() - spec.get('properties', {}).keys()
        if missing or (unknown and not spec.get('additionalProperties', False)):
            raise BuilderError(f'{label}: missing {sorted(missing)}, unknown {sorted(unknown)}')
        for key, child in value.items():
            if key in spec.get('properties', {}):
                check_schema(child, spec['properties'][key], f'{label}.{key}')
    elif expected is list:
        if len(value) < spec.get('minItems', 0) or len(value) > spec.get('maxItems', 10000):
            raise BuilderError(f'{label}: array size outside bounds')
        for index, child in enumerate(value):
            check_schema(child, spec['items'], f'{label}[{index}]')
    elif expected is str:
        if len(value.strip()) < spec.get('minLength', 0) or len(value) > spec.get('maxLength', 10000):
            raise BuilderError(f'{label}: text length outside bounds')
        if 'pattern' in spec and not re.fullmatch(spec['pattern'], value):
            raise BuilderError(f'{label}: invalid format')
    elif expected is int:
        if not spec.get('minimum', -10000) <= value <= spec.get('maximum', 10000):
            raise BuilderError(f'{label}: number outside bounds')


def load_playtests(toolkit, root, config=None, cards=None):
    path = contained(root, 'design/playtests.json')
    if not path.exists():
        return []
    plan = read_json(path)
    check_schema(plan, read_json(toolkit / 'builder/playtests.schema.json'), '$playtests')
    if config is None:
        config = read_json(contained(root, 'character.json'))
    if cards is None:
        cards = read_json(contained(root, 'design/cards.json'))
    rows = plan['scenarios']
    if rows and not config['features']['cards']:
        raise BuilderError('Archetype playtests require generated custom cards')
    ids = [r['id'].casefold() for r in rows]
    if len(ids) != len(set(ids)):
        raise BuilderError('Duplicate playtest scenario IDs')
    if sum(r['max_turns'] for r in rows) > 24 or sum(r['max_plays'] for r in rows) > 180:
        raise BuilderError('Playtests exceed the total 24-turn/180-play budget')
    known = {c['id'] for c in cards}
    for row in rows:
        deck = {c['card'] for c in row['deck']}
        if not deck <= known:
            raise BuilderError(f'{row["id"]}: unknown playtest deck card')
        if len(row['priority']) != len(set(row['priority'])) or set(row['priority']) != deck:
            raise BuilderError(f'{row["id"]}: priority must list every distinct deck card exactly once')
    return rows


def load_items(toolkit, root, config=None):
    path = contained(root, 'design/items.json')
    items = read_json(path) if path.exists() else dict(schema_version=1, relics=[], potions=[])
    check_schema(items, read_json(toolkit / 'builder/items.schema.json'), '$items')
    if config is None:
        config = read_json(contained(root, 'character.json'))
    if not config['features']['items'] and (items['relics'] or items['potions'] or 'starting_relic' in items):
        raise BuilderError('Custom items disabled: clear relics, potions and starting_relic')
    declared = {a['path'] for a in read_json(contained(root, 'assets/manifest.json'))}
    for group in ('relics', 'potions'):
        # Native class-name conversion inserts word separators. Reserve ambiguous
        # underscore/case variants rather than discovering a collision at startup.
        ids = [r['id'].replace('_', '').casefold() for r in items[group]]
        if len(ids) != len(set(ids)):
            raise BuilderError(f'Duplicate {group} IDs (including case/underscore variants)')
        for row in items[group]:
            art = row.get('art', {})
            if 'art' in row and not art:
                raise BuilderError(f'{row["id"]}: item art needs at least one role, or omit art for native fallbacks')
            if art and not config['features']['art']:
                raise BuilderError(f'{row["id"]}: item art requires the art feature')
            for asset in art.values():
                contained(root, asset)
                if asset not in declared or Path(asset).suffix.lower() not in {'.svg', '.png'}:
                    raise BuilderError(f'{row["id"]}: item art must reference an exact declared SVG/PNG asset')
            if not any(row['effects'].values()):
                raise BuilderError(f'{row["id"]}: item needs at least one supported effect')
            if row['effects']['focus'] and not config['features']['mechanic']:
                raise BuilderError(f'{row["id"]}: focus requires the mechanic feature')
    starter = items.get('starting_relic')
    starters = [r['id'] for r in items['relics'] if r['rarity'] == 'Starter']
    if starters != ([starter] if starter else []):
        raise BuilderError('starting_relic must select the single authored Starter relic, or omit both')
    return items


def load_events(toolkit, root, config=None):
    path = contained(root, 'design/events.json')
    events = read_json(path) if path.exists() else []
    check_schema(events, read_json(toolkit / 'builder/events.schema.json'), '$events')
    if config is None:
        config = read_json(contained(root, 'character.json'))
    if events and not config['features']['events']:
        raise BuilderError('Custom events disabled: clear design/events.json')
    def unique(rows, label):
        ids = [r['id'].replace('_', '').casefold() for r in rows]
        if len(ids) != len(set(ids)):
            raise BuilderError(f'Duplicate {label} IDs (including case/underscore variants)')
    unique(events, 'event')
    for event in events:
        if len(event['acts']) != len(set(event['acts'])):
            raise BuilderError(f'{event["id"]}: duplicate act eligibility')
        unique(event['choices'], f'{event["id"]} choice')
        for choice in event['choices']:
            if choice['id'].replace('_', '').casefold() == 'leave':
                raise BuilderError('Leave is reserved for the always-available exit')
            if not any(choice['cost'].values()) and not any(choice['reward'].values()):
                raise BuilderError(f'{event["id"]}/{choice["id"]}: choice needs a supported cost or reward')
    return events


def load_dialogue(toolkit, root, config=None):
    path = contained(root, 'design/dialogue.json')
    rows = read_json(path) if path.exists() else []
    check_schema(rows, read_json(toolkit / 'builder/dialogue.schema.json'), '$dialogue')
    config = config or read_json(contained(root, 'character.json'))
    if rows and not config['features']['dialogue']:
        raise BuilderError('Custom dialogue disabled: clear design/dialogue.json')
    keys = [(r['ancient'], r['visit']) for r in rows]
    if len(keys) != len(set(keys)):
        raise BuilderError('Duplicate Ancient/visit dialogue')
    for row in rows:
        if 'next' in row['lines'][-1]:
            raise BuilderError('Final dialogue line cannot specify next; native reward options follow')
    return rows


def load_sprites(toolkit, root, config=None):
    path = contained(root, 'design/sprites.json')
    data = read_json(path) if path.exists() else {}
    if not data:
        if type(data) is not dict:
            raise BuilderError('$sprites: expected object')
        return None
    check_schema(data, read_json(toolkit / 'builder/sprites.schema.json'), '$sprites')
    config = config or read_json(contained(root, 'character.json'))
    if not config['features']['sprites']:
        raise BuilderError('Custom sprites disabled: clear design/sprites.json')
    validate_atlas(root, data)
    return data


def load_presentation(toolkit, root, config=None):
    path = contained(root, 'design/presentation.json')
    data = read_json(path) if path.exists() else {}
    if data == {}:
        return None
    check_schema(data, read_json(toolkit / 'builder/presentation.schema.json'), '$presentation')
    config = config or read_json(contained(root, 'character.json'))
    if not config['features']['presentation']:
        raise BuilderError('Custom presentation disabled: clear design/presentation.json')
    if not data.get('rooms') and not data.get('selection'):
        raise BuilderError('Presentation needs room or selection data, or an empty object for native fallbacks')
    selection = data.get('selection', {})
    if 'background_fit' in selection and 'background' not in selection:
        raise BuilderError('Selection background_fit requires a background asset')
    declared = {a['path'] for a in read_json(contained(root, 'assets/manifest.json'))}
    for role, asset in selection.items():
        if role == 'background_fit':
            continue
        if asset not in declared or Path(asset).suffix.lower() not in {'.svg', '.png'}:
            raise BuilderError('Selection art must reference an exact declared SVG/PNG asset')
    for actor in data.get('rooms', {}).values():
        validate_atlas(root, actor, loops={'idle'})
    return data


def validate_atlas(root, data, loops=frozenset({'idle', 'victory'})):
    atlas = data['atlas']
    manifest = read_json(contained(root, 'assets/manifest.json'))
    if atlas not in {a['path'] for a in manifest} or Path(atlas).suffix.lower() not in {'.svg', '.png'}:
        raise BuilderError('Sprite atlas must reference an exact declared SVG/PNG asset')
    raw = contained(root, atlas).read_bytes()
    if atlas.lower().endswith('.png'):
        import struct
        size = struct.unpack('>II', raw[16:24]) if len(raw) >= 24 else ()
    else:
        import xml.etree.ElementTree as ET
        try:
            svg = ET.fromstring(raw)
            size = tuple(int(svg.attrib[k].removesuffix('px')) for k in ('width', 'height'))
        except (ET.ParseError, KeyError, ValueError) as error:
            raise BuilderError('Sprite SVG needs explicit integer width and height') from error
    if size != (data['width'], data['height']):
        raise BuilderError('Sprite atlas dimensions differ from declared width/height')
    left = top = 0
    right = bottom = 0
    for frame in data['frames']:
        x, y, w, h = frame['rect']
        ax, ay = frame['anchor']
        if not w or not h or x + w > size[0] or y + h > size[1] or ax > w or ay > h:
            raise BuilderError('Sprite frame rectangle/anchor outside atlas or frame')
        left, top = min(left, -ax), min(top, -ay)
        right, bottom = max(right, w - ax), max(bottom, h - ay)
    scale = data['scale_percent'] / 100
    if (right - left) * scale > 512 or (bottom - top) * scale > 512:
        raise BuilderError('Sprite display bounds exceed 512 pixels; reduce scale or frame extent')
    for name, state in data['states'].items():
        if any(i >= len(data['frames']) for i in state['frames']):
            raise BuilderError('Sprite animation references a missing frame')
        if name not in loops and len(state['frames']) / state['fps'] > 5:
            raise BuilderError('Sprite one-shot duration exceeds five seconds')
    return data


def load_audio(toolkit, root, config=None):
    path = contained(root, 'design/audio.json')
    data = read_json(path) if path.exists() else {}
    if data == {}:
        return None
    check_schema(data, read_json(toolkit / 'builder/audio.schema.json'), '$audio')
    config = config or read_json(contained(root, 'character.json'))
    if not config['features']['audio']:
        raise BuilderError('Custom audio disabled: clear design/audio.json')
    if not data['cues']:
        raise BuilderError('Audio needs at least one cue, or an empty object to retain native sounds')
    declared = {a['path'] for a in read_json(contained(root, 'assets/manifest.json'))}
    for cue in data['cues'].values():
        asset = cue['asset']
        if asset not in declared or Path(asset).suffix.lower() != '.wav':
            raise BuilderError('Audio cue must reference an exact declared PCM WAV asset')
        audio_pcm(contained(root, asset).read_bytes())
    return data


def audio_pcm(raw):
    """Bounded RIFF PCM16 clips; walk chunks rather than assume a 44-byte header."""
    import struct
    if len(raw) < 12 or raw[:4] != b'RIFF' or raw[8:12] != b'WAVE' or int.from_bytes(raw[4:8], 'little') + 8 != len(raw):
        raise BuilderError('Audio needs a complete RIFF WAV')
    offset, chunks = 12, {}
    while offset + 8 <= len(raw):
        kind, size = raw[offset:offset + 4], int.from_bytes(raw[offset + 4:offset + 8], 'little')
        end = offset + 8 + size
        if end + size % 2 > len(raw) or kind in chunks:
            raise BuilderError('Truncated or duplicate WAV chunk')
        chunks[kind] = raw[offset + 8:end]
        offset = end + size % 2
    fmt, pcm = chunks.get(b'fmt ', b''), chunks.get(b'data', b'')
    if offset != len(raw) or len(fmt) not in (16, 18) or not pcm:
        raise BuilderError('Audio needs PCM format and sample data')
    codec, channels, rate, byte_rate, align, bits = struct.unpack('<HHIIHH', fmt[:16])
    if (codec != 1 or channels not in (1, 2) or not 8000 <= rate <= 48000 or bits != 16
            or align != channels * 2 or byte_rate != rate * align or len(pcm) % align
            or len(pcm) > rate * align * 10 or (len(fmt) == 18 and fmt[16:] != b'\0\0')):
        raise BuilderError('Audio supports 1-2 channels, 8-48 kHz PCM16 and at most ten seconds')
    samples = struct.unpack('<' + 'h' * (len(pcm) // 2), pcm)
    if not any(samples) or min(samples) == -32768 or max(samples) == 32767:
        raise BuilderError('Audio samples are silent or reach clipping endpoints')
    return pcm


def validate(toolkit, root):
    config = read_json(contained(root, 'character.json'))
    check_schema(config, read_json(toolkit / 'builder/character.schema.json'))
    if config['id'].lower() in {'spirelegacy', 'baselib', 'sts2'} or config['namespace'].lower().startswith('spirelegacy'):
        raise BuilderError('Choose a new mod ID and namespace; reference/dependency identities are reserved')
    if config['namespace'] in {'abstract', 'class', 'namespace', 'public', 'private', 'internal', 'void', 'int', 'string', 'new', 'base', 'using', 'static'}:
        raise BuilderError('Namespace must be a C# identifier, not a keyword')
    if re.fullmatch(r'(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])', config['id']):
        raise BuilderError('Mod ID is a reserved Windows device name')
    lock = read_json(contained(root, 'builder.lock.json'))
    if not isinstance(lock, dict) or lock.get('schema_version') != 1 or not isinstance(lock.get('toolkit_commit'), str) or not re.fullmatch('[0-9a-f]{40}', lock['toolkit_commit']):
        raise BuilderError('Invalid toolkit lock')
    if lock.get('baselib') != '3.4.7' or lock.get('target_framework') != 'net9.0':
        raise BuilderError('Dependency upgrade requires a reviewed toolkit update')
    load_items(toolkit, root, config)
    load_events(toolkit, root, config)
    load_dialogue(toolkit, root, config)
    cards = read_json(contained(root, 'design/cards.json'))
    check_schema(cards, read_json(toolkit / 'builder/cards.schema.json'), '$cards')
    ids = [c['id'] for c in cards]
    if len(set(x.casefold() for x in ids)) != len(ids):
        raise BuilderError('Duplicate card IDs (including case collisions)')
    if not config['features']['cards'] and cards:
        raise BuilderError('Custom cards disabled: design/cards.json must be empty')
    by_id = {c['id']: c for c in cards}
    if config['features']['cards']:
        if not config['starting_deck']:
            raise BuilderError('Custom-card projects need an explicit starting deck')
        for key in config['starting_deck']:
            if key not in by_id:
                raise BuilderError(f'Dangling starting card: {key}')
    elif config['starting_deck']:
        raise BuilderError('Native fallback uses a fixed native deck; clear starting_deck')
    for card in cards:
        for version in ('base', 'upgrade'):
            values = card[version]
            if values['damage'] and card['target'] == 'Self':
                raise BuilderError(f'{card["id"]}: damage needs an enemy target')
            if card['type'] == 'Attack' and not values['damage']:
                raise BuilderError(f'{card["id"]}: an Attack must deal damage')
        if not config['features']['mechanic'] and any(card[v]['focus'] for v in ('base', 'upgrade')):
            raise BuilderError(f'{card["id"]}: focus requires the mechanic feature')
    manifest = read_json(contained(root, 'assets/manifest.json'))
    check_schema(manifest, read_json(toolkit / 'builder/assets.schema.json'), '$assets')
    paths = set()
    for asset in manifest:
        path = asset['path']
        if not path.startswith('assets/') or path.casefold() in paths:
            raise BuilderError(f'Asset path must be unique and inside assets/: {path}')
        paths.add(path.casefold())
        data = contained(root, path).read_bytes()
        if digest(data) != asset['sha256']:
            raise BuilderError(f'Asset hash changed: {path}; update provenance after review')
        if Path(path).suffix.lower() not in {'.svg', '.png', '.wav', '.ogg'}:
            raise BuilderError(f'Unsupported asset format: {path}')
        suffix = Path(path).suffix.lower()
        if suffix == '.svg':
            import xml.etree.ElementTree as ET
            try:
                svg = ET.fromstring(data)
            except ET.ParseError as error:
                raise BuilderError(f'Invalid SVG: {path}') from error
            if svg.tag.split('}')[-1] != 'svg' or 'viewBox' not in svg.attrib:
                raise BuilderError(f'SVG needs a viewBox: {path}')
            if re.search(rb'<\s*(script|foreignObject)|(?:href|url\s*\()\s*[=:]?\s*[\"\']?(?:https?:|file:|//)', data, re.I):
                raise BuilderError(f'External/active SVG content: {path}')
        elif suffix == '.png':
            import struct
            import zlib
            if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                raise BuilderError(f'Invalid PNG: {path}')
            offset = 8
            kinds = []
            while offset + 12 <= len(data):
                size = struct.unpack('>I', data[offset:offset + 4])[0]
                kind = data[offset + 4:offset + 8]
                payload = data[offset + 8:offset + 8 + size]
                crc = data[offset + 8 + size:offset + 12 + size]
                if len(payload) != size or len(crc) != 4 or zlib.crc32(kind + payload) != int.from_bytes(crc, 'big'):
                    raise BuilderError(f'Corrupt PNG chunk: {path}')
                if not kinds:
                    if kind != b'IHDR' or size != 13 or not all(0 < d <= 8192 for d in struct.unpack('>II', payload[:8])):
                        raise BuilderError(f'Invalid PNG dimensions/header: {path}')
                kinds.append(kind)
                offset += 12 + size
                if kind == b'IEND':
                    break
            if not kinds or kinds[-1] != b'IEND' or b'IDAT' not in kinds or offset != len(data):
                raise BuilderError(f'Truncated or incomplete PNG: {path}')
        elif suffix == '.wav':
            import io
            import wave
            try:
                with wave.open(io.BytesIO(data)) as sound:
                    if sound.getnchannels() not in (1, 2) or not 8000 <= sound.getframerate() <= 96000 or not sound.getnframes():
                        raise BuilderError(f'Unsupported WAV channels/rate/length: {path}')
                    expected = sound.getnframes() * sound.getnchannels() * sound.getsampwidth()
                    if len(sound.readframes(sound.getnframes())) != expected:
                        raise BuilderError(f'Truncated WAV: {path}')
            except (wave.Error, EOFError) as error:
                raise BuilderError(f'Invalid PCM WAV: {path}') from error
        elif suffix == '.ogg' and (not data.startswith(b'OggS\x00') or len(data) < 27):
            raise BuilderError(f'Invalid Ogg header: {path}')
    if not {'assets/icon.svg', 'assets/card.svg'} <= paths:
        raise BuilderError('Required visible fallback assets: assets/icon.svg and assets/card.svg')
    load_sprites(toolkit, root, config)
    load_presentation(toolkit, root, config)
    load_audio(toolkit, root, config)
    load_playtests(toolkit, root, config, cards)
    declared = {asset['path'] for asset in manifest}
    for card in cards:
        if 'portrait' not in card:
            continue
        portrait = card['portrait']
        contained(root, portrait)
        if not config['features']['art']:
            raise BuilderError(f'{card["id"]}: portrait requires the art feature; remove portrait to use the fallback')
        if portrait not in declared or Path(portrait).suffix.lower() not in {'.svg', '.png'}:
            raise BuilderError(f'{card["id"]}: portrait must reference a declared SVG/PNG asset with exact path casing')
    # Narrative/custom code are authored by their skills; the small generator never half-registers them.
    return config, cards, manifest, lock


def input_hash(root):
    root = Path(root).resolve()
    files = [contained(root, p) for p in ('character.json', 'builder.lock.json', 'design/cards.json', 'assets/manifest.json')]
    for relative in ('design/items.json', 'design/events.json', 'design/dialogue.json', 'design/sprites.json', 'design/audio.json', 'design/presentation.json', 'design/playtests.json'):
        optional = contained(root, relative)
        if optional.exists():
            files.append(optional)
    files += [contained(root, a['path']) for a in read_json(contained(root, 'assets/manifest.json'))]
    files += sorted((Path(root) / 'src').rglob('*.cs'))
    files += [contained(root, 'Character.csproj'), contained(root, 'design/model-ids.json'), contained(root, 'design/generated-files.json')]
    return digest(encoded({p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in files}))
