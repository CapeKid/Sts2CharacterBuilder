"""Project bootstrap and ownership-aware generation. No game content is copied."""
import os
import json
import shutil
import subprocess
import tempfile
import re
from pathlib import Path
from xml.sax.saxutils import escape

from .contracts import BuilderError, contained, digest, encoded, load_audio, load_dialogue, load_events, load_items, load_presentation, load_sprites, read_json, validate

STEPS = ['setup', 'mechanics', 'cards', 'art', 'items', 'events', 'dialogue', 'sprites',
         'presentation', 'audio', 'verify', 'balance', 'publish']
OPTIONAL = dict(mechanics='mechanic', **{x: x for x in STEPS[2:10]})


def run(command, cwd=None):
    result = subprocess.run([str(x) for x in command], cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise BuilderError(f'{command[0]} failed: {result.stderr or result.stdout}')
    return result.stdout.strip()


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Same-directory replacement; a failed write leaves the previous file intact.
    fd, name = tempfile.mkstemp(prefix='.builder-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def defaults(mod_id, name, idea, mode, author):
    features = {x: x in {'mechanic', 'cards', 'art', 'items', 'presentation'} for x in OPTIONAL.values()}
    return dict(schema_version=1, id=mod_id, namespace=mod_id, name=name, author=author,
                idea=idea, description=idea, version='0.1.0', mode=mode, target='public-beta',
                hp=70, color='57B8A7', features=features,
                starting_deck=['Strike'] * 5 + ['Guard'] * 4 + ['Practice'],
                choices=[dict(step='intake', decision='ai' if mode == 'expedited' else 'user',
                              notes='Bootstrap defaults are a small-pool prototype; continue the entry skill.')])


def starter_cards():
    def card(key, kind, rarity, cost, effect, amount, extra, exhaust=False):
        basic = dict(cost=cost, damage=0, block=0, draw=0, energy=0, focus=0)
        basic[effect] = amount
        upgraded = {**basic, effect: amount + extra}
        return dict(id=key, name=key, type=kind, rarity=rarity, target='AnyEnemy' if effect == 'damage' else 'Self',
                    exhaust=exhaust, base=basic, upgrade=upgraded)
    return [card('Strike', 'Attack', 'Basic', 1, 'damage', 6, 3),
            card('Guard', 'Skill', 'Basic', 1, 'block', 5, 3),
            card('Practice', 'Skill', 'Basic', 1, 'focus', 1, 1, True),
            card('Swing', 'Attack', 'Common', 1, 'damage', 9, 3),
            card('Breathe', 'Skill', 'Uncommon', 1, 'draw', 2, 1),
            card('Composure', 'Power', 'Rare', 2, 'focus', 2, 1),
            card('Lunge', 'Attack', 'Common', 2, 'damage', 14, 5),
            card('Brace', 'Skill', 'Common', 1, 'block', 8, 3)]


def placeholder(kind, color):
    # Original deterministic vector geometry; deliberately labeled rather than claiming finished art.
    width, height = (256, 256) if kind == 'icon' else (500, 380)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<rect width="{width}" height="{height}" fill="#17212B"/>'
            f'<circle cx="{width//2}" cy="{height//2-20}" r="70" fill="#{color}"/>'
            f'<path d="M {width//2-45} {height//2} L {width//2} {height//2-70} L {width//2+45} {height//2} Z" fill="#17212B"/>'
            f'<text x="50%" y="85%" text-anchor="middle" fill="white" font-size="20">PLACEHOLDER</text></svg>\n').encode()


def bootstrap(toolkit, target, args):
    target = target.absolute()
    if target.exists():
        raise BuilderError('Project destination must not exist; existing work is never reset')
    target.parent.mkdir(parents=True, exist_ok=True)
    # A local source is explicit and supports offline fixtures; production defaults to this repository.
    source = args.toolkit_source
    if Path(source).is_dir():
        source = str(Path(source).resolve())
    current_commit = run(['git', 'rev-parse', 'HEAD'], toolkit)
    commit = args.toolkit_commit or current_commit
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise BuilderError('Pin a full toolkit commit SHA')
    if commit != current_commit or run(['git', 'status', '--porcelain', '--untracked-files=normal'], toolkit):
        raise BuilderError('Bootstrap from a clean checkout of the selected toolkit commit')
    config = defaults(args.id, args.name or args.id, args.idea, args.mode, args.author)
    from .contracts import check_schema
    check_schema(config, read_json(toolkit / 'builder/character.schema.json'))
    if config['id'].lower() in {'spirelegacy', 'baselib', 'sts2'}:
        raise BuilderError('Choose an independent mod identity')
    temporary = Path(tempfile.mkdtemp(prefix='.character-init-', dir=target.parent))
    try:
        run(['git', 'init', '-b', 'main', temporary])
        local = Path(source).is_dir()
        command = ['git'] + (['-c', 'protocol.file.allow=always'] if local else [])
        run(command + ['submodule', 'add', '--', source, 'tools/character-builder'], temporary)
        submodule = temporary / 'tools/character-builder'
        run(['git', 'checkout', '--detach', commit], submodule)
        if not (submodule / 'builder/skills/create-character/SKILL.md').is_file():
            raise BuilderError('Pinned toolkit does not contain the entry workflow; commit the implementation first')
        atomic(temporary / 'character.json', encoded(config))
        atomic(temporary / 'builder.lock.json', encoded(dict(schema_version=1, toolkit_commit=commit,
               toolkit_url=source, baselib='3.4.7', target_framework='net9.0',
               reference_commit='f46c3eaf8c76c43c6a70d0713f855760b96fec19')))
        atomic(temporary / 'design/cards.json', encoded(starter_cards()))
        atomic(temporary / 'design/items.json', encoded(dict(schema_version=1, relics=[], potions=[])))
        atomic(temporary / 'design/events.json', encoded([]))
        atomic(temporary / 'design/dialogue.json', encoded([]))
        atomic(temporary / 'design/sprites.json', encoded({}))
        atomic(temporary / 'design/audio.json', encoded({}))
        atomic(temporary / 'design/presentation.json', encoded({}))
        manifest = []
        for kind in ('icon', 'card'):
            data = placeholder(kind, config['color'])
            path = f'assets/{kind}.svg'
            atomic(temporary / path, data)
            manifest.append(dict(path=path, sha256=digest(data), method='original-placeholder',
                                 license='MIT', credit='Sts2CharacterBuilder original geometric placeholder'))
        atomic(temporary / 'assets/manifest.json', encoded(manifest))
        atomic(temporary / '.gitignore', b'.builder/\nprivate/\nbuild/\ndist/\nbin/\nobj/\n*.log\n')
        atomic(temporary / '.gitattributes', b'* text eol=lf\n*.svg -text\n*.png -text\n*.wav -text\n*.ogg -text\n')
        atomic(temporary / 'AGENTS.md', b'# Character project\n\nRead character.json, then tools/character-builder/builder/skills/create-character/SKILL.md.\nRun the toolkit CLI with --project set to this root. Resume before changing work.\nThe submodule is pinned; customizations belong in this repository.\n')
        atomic(temporary / 'README.md', f'# {config["name"]}\n\nCharacter prototype created with Sts2CharacterBuilder.\n\nClone with `git clone --recurse-submodules <this-project-url>`. For an existing checkout run `git submodule update --init --recursive`.\n\nStart at [the entry workflow](tools/character-builder/builder/skills/create-character/SKILL.md).\nUse `python tools/character-builder/scripts/character-builder.py --project . resume`.\n\nInstall BaseLib 3.4.7 separately. Native character presentation, item/power icons and disabled custom content use runtime placeholders/native fallbacks. See the toolkit item contract for optional authored relics and potions.\nThis small card pool is a prototype, not a balanced release. See the verification report before distribution.\n'.encode())
        atomic(temporary / 'LICENSE', (toolkit / 'LICENSE').read_bytes())
        (temporary / 'src/Extensions').mkdir(parents=True)
        generate(toolkit, temporary)
        run(['git', 'add', '.'], temporary)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return dict(project=str(target), toolkit_commit=commit, status='prototype', next='resume')


def generated(toolkit, root):
    config, cards, assets, lock = validate(toolkit, root)
    items = load_items(toolkit, root, config)
    events = load_events(toolkit, root, config)
    quote = lambda v: __import__('json').dumps(v, ensure_ascii=True)
    custom = config['features']['cards']
    mechanic = config['features']['mechanic']
    relic = config['features']['items'] and mechanic
    replacements = {
        'NAMESPACE': config['namespace'], 'MOD_ID': quote(config['id']), 'COLOR': quote(config['color']),
        'HP': str(config['hp']), 'NAME': quote(config['name']), 'DESCRIPTION': quote(config['description']),
        'CARD_POOL': 'ModelDb.CardPool<CharacterCardPool>()' if custom else 'ModelDb.CardPool<IroncladCardPool>()',
        'RELIC_POOL': 'ModelDb.RelicPool<AuthoredRelicPool>()' if items['relics'] else
                      'ModelDb.RelicPool<CharacterRelicPool>()' if relic else 'ModelDb.RelicPool<IroncladRelicPool>()',
        'START_RELIC': f'ModelDb.Relic<Relic_{items["starting_relic"]}>()' if 'starting_relic' in items else
                       'ModelDb.Relic<StarterRelic>()' if relic else 'ModelDb.Relic<BurningBlood>()',
        'POTION_POOL': 'ModelDb.PotionPool<AuthoredPotionPool>()' if items['potions'] else 'ModelDb.PotionPool<IroncladPotionPool>()',
        'DECK': ', '.join(f'ModelDb.Card<Card_{key}>()' for key in config['starting_deck']) if custom else
                ', '.join(['ModelDb.Card<StrikeIronclad>()'] * 5 + ['ModelDb.Card<DefendIronclad>()'] * 4 + ['ModelDb.Card<Bash>()']),
        'POOL_CARDS': ''.join(f'ModelDb.Card<Card_{c["id"]}>(), ' for c in cards),
        'TEXTURE_ASSETS': ', '.join(quote(a['path'][7:]) for a in assets if Path(a['path']).suffix.lower() in {'.svg', '.png'}),
        'CARD_TYPES': '\n'.join(f'public sealed class Card_{c["id"]}() : CharacterCard({quote(c["id"])});' for c in cards)
    }
    cs = (toolkit / 'builder/templates/Character.cs.txt').read_text()
    # Replace only tokens in the template, never token-like text inside supplied names/descriptions.
    cs = re.sub(r'@([A-Z_]+)@', lambda match: replacements[match[1]], cs)
    if not mechanic:
        start = cs.index('// Amount is the native saved')
        end = cs.index('internal static class CardData')
        cs = cs[:start] + cs[end:]
        cs = cs.replace('        if (Number("focus") > 0) await PowerCmd.Apply<FocusPower>(context, Owner.Creature, Number("focus"), Owner.Creature, this);', '')
    if not relic:
        start = cs.index('public sealed class CharacterRelicPool')
        end = cs.index('// Amount is the native saved') if mechanic else cs.index('internal static class CardData')
        cs = cs[:start] + cs[end:]
    project = (toolkit / 'builder/templates/Character.csproj.txt').read_text()
    for key in ('ID', 'NAMESPACE'):
        project = project.replace('@' + key + '@', escape(config['id' if key == 'ID' else 'namespace']))
    mod = dict(id=config['id'], name=config['name'], author=config['author'], description=config['description'],
               version=config['version'], has_pck=False, has_dll=True, affects_gameplay=True,
               min_game_version='0.107.1', dependencies=[dict(id='BaseLib', min_version=lock['baselib'])])
    outputs = {'src/Generated/Character.cs': cs.encode(), 'Character.csproj': project.encode(),
               f'{config["id"]}.json': encoded(mod)}
    if items['relics'] or items['potions']:
        relic_models = ([f'ModelDb.Relic<Relic_{r["id"]}>()' for r in items['relics']]
                        + (['ModelDb.Relic<StarterRelic>()'] if relic else []))
        item_replacements = dict(NAMESPACE=config['namespace'], ITEMS_JSON=quote(json.dumps(items, ensure_ascii=True)),
            FOCUS_EFFECT='if (Number("focus") > 0) await PowerCmd.Apply<FocusPower>(context, player.Creature, Number("focus"), player.Creature, null);' if mechanic else '',
            RELIC_POOL_TYPE=('public sealed class AuthoredRelicPool : RelicPoolModel {\n'
                '    public override string EnergyColorName => ModelDb.RelicPool<IroncladRelicPool>().EnergyColorName;\n'
                '    protected override RelicModel[] GenerateAllRelics() => [' + ', '.join(relic_models) + '];\n}') if items['relics'] else '',
            POTION_POOL_TYPE=('public sealed class AuthoredPotionPool : PotionPoolModel {\n'
                '    public override string EnergyColorName => ModelDb.PotionPool<IroncladPotionPool>().EnergyColorName;\n'
                '    protected override IEnumerable<PotionModel> GenerateAllPotions() => [' +
                ', '.join(f'ModelDb.Potion<Potion_{p["id"]}>()' for p in items['potions']) + '];\n}') if items['potions'] else '',
            ITEM_TYPES='\n'.join([f'public sealed class Relic_{r["id"]} : AuthoredRelic {{ }}' for r in items['relics']] +
                                 [f'public sealed class Potion_{p["id"]} : AuthoredPotion {{ }}' for p in items['potions']]))
        template = (toolkit / 'builder/templates/Items.cs.txt').read_text()
        outputs['src/Generated/Items.cs'] = re.sub(r'@([A-Z_]+)@', lambda match: item_replacements[match[1]], template).encode()
    if events:
        replacements = dict(NAMESPACE=config['namespace'], EVENTS_JSON=quote(json.dumps(events, ensure_ascii=True)),
            EVENT_TYPES='\n'.join(f'public sealed class Event_{e["id"]} : AuthoredEvent {{ }}' for e in events))
        template = (toolkit / 'builder/templates/Events.cs.txt').read_text()
        outputs['src/Generated/Events.cs'] = re.sub(r'@([A-Z_]+)@', lambda match: replacements[match[1]], template).encode()
    dialogue = load_dialogue(toolkit, root, config)
    if dialogue:
        replacements = dict(NAMESPACE=config['namespace'], MOD_ID=quote(config['id']),
                            DIALOGUE_JSON=quote(json.dumps(dialogue, ensure_ascii=True)))
        template = (toolkit / 'builder/templates/Dialogue.cs.txt').read_text()
        outputs['src/Generated/Dialogue.cs'] = re.sub(r'@([A-Z_]+)@', lambda m: replacements[m[1]], template).encode()
    sprites = load_sprites(toolkit, root, config)
    if sprites:
        replacements = dict(NAMESPACE=config['namespace'], MOD_ID=quote(config['id']), SPRITES_JSON=quote(json.dumps(sprites, ensure_ascii=True)))
        template = (toolkit / 'builder/templates/Sprites.cs.txt').read_text()
        outputs['src/Generated/Sprites.cs'] = re.sub(r'@([A-Z_]+)@', lambda m: replacements[m[1]], template).encode()
    audio = load_audio(toolkit, root, config)
    if audio:
        properties = {'select': 'CharacterSelectSfx', 'transition': 'CharacterTransitionSfx',
                      'attack': 'CustomAttackSfx', 'cast': 'CustomCastSfx', 'death': 'CustomDeathSfx'}
        replacements = dict(NAMESPACE=config['namespace'], MOD_ID=quote(config['id']),
                            AUDIO_JSON=quote(json.dumps(audio, ensure_ascii=True)),
                            AUDIO_PROPERTIES='\n'.join(f'    public override string {properties[k]} => CharacterAudio.Uri({quote(k)});' for k in audio['cues']))
        template = (toolkit / 'builder/templates/Audio.cs.txt').read_text()
        outputs['src/Generated/Audio.cs'] = re.sub(r'@([A-Z_]+)@', lambda m: replacements[m[1]], template).encode()
    presentation = load_presentation(toolkit, root, config)
    if presentation:
        replacements = dict(NAMESPACE=config['namespace'], MOD_ID=quote(config['id']),
                            PRESENTATION_JSON=quote(json.dumps(presentation, ensure_ascii=True)))
        template = (toolkit / 'builder/templates/Presentation.cs.txt').read_text()
        outputs['src/Generated/Presentation.cs'] = re.sub(r'@([A-Z_]+)@', lambda m: replacements[m[1]], template).encode()
    return outputs


def generate(toolkit, root, check=False, freeze=False):
    outputs = generated(toolkit, root)
    marker = contained(root, 'design/generated-files.json')
    old = read_json(marker) if marker.exists() else {}
    identities = contained(root, 'design/model-ids.json')
    config, cards, _, _ = validate(toolkit, root)
    items = load_items(toolkit, root, config)
    events = load_events(toolkit, root, config)
    previous = read_json(identities) if identities.exists() else None
    frozen = freeze or bool(previous and previous.get('frozen'))
    ids = dict(namespace=config['namespace'], mod_id=config['id'], frozen=frozen, models=['Character'] +
               (['StarterRelic'] if config['features']['items'] and config['features']['mechanic'] else []) +
               (['FocusPower'] if config['features']['mechanic'] else []) + ['Card_' + c['id'] for c in cards] +
               ['Relic_' + r['id'] for r in items['relics']] + ['Potion_' + p['id'] for p in items['potions']] +
               ['Event_' + e['id'] for e in events])
    if previous and previous.get('frozen'):
        if previous['namespace'] != ids['namespace'] or previous['mod_id'] != ids['mod_id'] or not set(previous['models']) <= set(ids['models']):
            raise BuilderError('Saved model identity removed or renamed; an explicit migration is required')
    outputs['design/model-ids.json'] = encoded(ids)
    expected_hashes = {p: digest(data) for p, data in outputs.items()}
    # Validate all ownership before the first mutation, including stale files.
    for path in outputs.keys() | old.keys():
        target = contained(root, path)
        if target.exists():
            actual = digest(target.read_bytes())
            desired = digest(outputs[path]) if path in outputs else None
            if actual != desired and old.get(path) != actual:
                raise BuilderError(f'Hand-edited/unowned generated file: {path}; preserve it in src/Extensions before regenerating')
        if check and (path not in outputs or not target.exists() or target.read_bytes() != outputs[path]):
            raise BuilderError(f'Stale generated output: {path}; run generate')
    if check and old != expected_hashes:
        raise BuilderError('Stale generated-file manifest; run generate')
    if not check:
        for path, data in outputs.items():
            atomic(contained(root, path), data)
        for path in old.keys() - outputs.keys():
            contained(root, path).unlink(missing_ok=True)
        atomic(marker, encoded(expected_hashes))
    return dict(status='current' if check else 'generated', files=list(outputs))
