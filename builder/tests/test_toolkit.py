"""Behavioral tests using real repositories, submodules and separate project roots."""
import argparse
import copy
import os
from pathlib import Path
import shutil
import subprocess
import struct
import tempfile
import unittest
import zipfile
import zlib

from builder.contracts import BuilderError, digest, encoded, input_hash, load_dialogue, load_events, load_items, read_json, validate
from builder.project import atomic, bootstrap, generate, run
from builder.verification import balance, build, compare_delivery, native_evidence, pin_check, record, resume, source_hash, stage, verify

REPO = Path(__file__).resolve().parents[2]


def portrait_png():
    """Two distinct RGBA pixels, built without an image-library dependency."""
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 1, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b'\x00\xff\x00\x00\xff\x00\xff\x00\xff')) + chunk(b'IEND', b''))


def authored_items():
    def effects(block=0, draw=0, energy=0, focus=0):
        return dict(block=block, draw=draw, energy=energy, focus=focus)
    return dict(schema_version=1, starting_relic='Primer', relics=[
        dict(id='Primer', name='Primer', rarity='Starter', trigger='first-turn', effects=effects(2, 1, 1, 1)),
        dict(id='Rhythm', name='Rhythm', rarity='Common', trigger='turn-start', effects=effects(1, 1, 1, 1)),
        dict(id='PocketGuide', name='Pocket Guide', rarity='Uncommon', trigger='first-turn', effects=effects(3)),
        dict(id='Reserve', name='Reserve', rarity='Rare', trigger='turn-start', effects=effects(energy=1)),
        dict(id='LuckyCharm', name='Lucky Charm', rarity='Shop', trigger='first-turn', effects=effects(draw=1))], potions=[
        dict(id='Reset', name='Reset', rarity='Common', effects=effects(6, 2, 1, 2)),
        dict(id='Shield', name='Shield', rarity='Uncommon', effects=effects(block=8)),
        dict(id='Clarity', name='Clarity', rarity='Rare', effects=effects(draw=2, energy=2))])


def authored_events():
    def choice(key, gold=0, hp=0, gain=0, heal=0):
        return dict(id=key, name=key, result='The meeting is over.', cost=dict(gold=gold, hp=hp), reward=dict(gold=gain, heal=heal))
    return [dict(id='QuietCamp', name='A Quiet Camp', body='A traveler offers a moment of rest.', acts=[1, 2, 3],
                 choices=[choice('Rest', gold=30, heal=12), choice('Trade', hp=5, gain=25),
                          choice('Exchange', gold=10, hp=3, gain=15, heal=4)]),
            dict(id='LastLesson', name='A Last Lesson', body='A final lesson awaits.', acts=[3],
                 choices=[choice('Listen', heal=8)])]


def authored_dialogue():
    rows = [dict(ancient=ancient, visit=visit, lines=[
        dict(speaker='Ancient', text='A quiet moment before the climb.', next='Answer'),
        dict(speaker='Character', text='I will use it well.'),
        dict(speaker='Ancient', text='Then take your next step.')])
        for ancient, visit in [('NEOW', 'first'), ('NEOW', 'repeat'), ('DARV', 'first')]]
    rows[-1]['lines'] = [dict(speaker='Character', text='Let the next step speak for itself.')]
    return rows


class ToolkitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='character-builder-tests-')
        cls.base = Path(cls.temp.name)
        cls.source = cls.base / 'Toolkit source'
        cls.source.mkdir()
        shutil.copytree(REPO / 'builder', cls.source / 'builder', ignore=shutil.ignore_patterns('__pycache__'))
        (cls.source / 'scripts').mkdir()
        shutil.copy2(REPO / 'scripts/character-builder.py', cls.source / 'scripts')
        shutil.copy2(REPO / 'LICENSE', cls.source)
        shutil.copy2(REPO / '.gitignore', cls.source)
        run(['git', 'init', '-b', 'main', cls.source])
        run(['git', 'add', '.'], cls.source)
        run(['git', '-c', 'user.name=Toolkit Fixture', '-c', 'user.email=fixture@example.invalid',
             'commit', '-m', 'Fixture toolkit'], cls.source)
        cls.commit = run(['git', 'rev-parse', 'HEAD'], cls.source)

    @classmethod
    def tearDownClass(cls):
        # Git object files can be read-only on Windows. Temporary test roots only.
        def writable(function, path, info):
            os.chmod(path, 0o700)
            function(path)
        shutil.rmtree(cls.base, onerror=writable)
        cls.temp.cleanup()

    def setUp(self):
        self.project = self.base / self._testMethodName / 'Character with spaces'
        args = argparse.Namespace(id='TestHero', name='Test Hero', idea='A patient defender', author='Fixture',
                                  mode='guided', toolkit_source=str(self.source), toolkit_commit=self.commit)
        bootstrap(self.source, self.project, args)
        self.toolkit = self.project / 'tools/character-builder'

    def edit(self, path, change):
        value = read_json(self.project / path)
        change(value)
        atomic(self.project / path, encoded(value))

    def test_two_projects_and_recursive_clone(self):
        other = self.project.parent / 'Second hero'
        args = argparse.Namespace(id='OtherHero', name='Other Hero', idea='A fast trickster', author='Other',
                                  mode='expedited', toolkit_source=str(self.source), toolkit_commit=self.commit)
        bootstrap(self.source, other, args)
        self.assertEqual(read_json(other / 'character.json')['mode'], 'expedited')
        self.assertNotEqual((other / 'src/Generated/Character.cs').read_bytes(),
                            (self.project / 'src/Generated/Character.cs').read_bytes())
        pin_check(self.toolkit, self.project, read_json(self.project / 'builder.lock.json'))
        self.assertIn('160000', run(['git', 'ls-files', '--stage', 'tools/character-builder'], self.project))
        run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'Character'], self.project)
        clone = self.project.parent / 'Recursive clone'
        run(['git', '-c', 'protocol.file.allow=always', 'clone', '--recurse-submodules', self.project, clone])
        generate(clone / 'tools/character-builder', clone, check=True)
        self.assertEqual(resume(clone / 'tools/character-builder', clone)['next'], 'setup')
        result = subprocess.run([os.sys.executable, str(clone / 'tools/character-builder/scripts/character-builder.py'),
                                 '--project', str(clone), 'test'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        # Ownership information must survive cloning, not live only in ignored workflow state.
        config = read_json(clone / 'character.json')
        config['hp'] = 74
        atomic(clone / 'character.json', encoded(config))
        generate(clone / 'tools/character-builder', clone)
        generate(clone / 'tools/character-builder', clone, freeze=True)
        generate(clone / 'tools/character-builder', clone, check=True)

    def test_existing_destination_preserved(self):
        sentinel = self.project / 'sentinel'
        sentinel.write_text('keep')
        with self.assertRaises(BuilderError):
            bootstrap(self.source, self.project, argparse.Namespace())
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_unknown_duplicate_and_dangling_data(self):
        original = (self.project / 'design/cards.json').read_bytes()
        self.edit('design/cards.json', lambda cards: cards.append(copy.deepcopy(cards[0])))
        with self.assertRaisesRegex(BuilderError, 'Duplicate'):
            validate(self.toolkit, self.project)
        atomic(self.project / 'design/cards.json', original)
        self.edit('character.json', lambda c: c['starting_deck'].append('Missing'))
        with self.assertRaisesRegex(BuilderError, 'Dangling'):
            validate(self.toolkit, self.project)
        (self.project / 'character.json').write_text('{"id": "a", "id": "b"}')
        with self.assertRaisesRegex(BuilderError, 'duplicate property'):
            validate(self.toolkit, self.project)

    def test_bounds_types_and_unsupported_effects(self):
        original = (self.project / 'design/cards.json').read_bytes()
        for key, value in [('cost', True), ('draw', -1), ('damage', 101), ('poison', 2)]:
            with self.subTest(key=key):
                atomic(self.project / 'design/cards.json', original)
                self.edit('design/cards.json', lambda c: c[0]['base'].__setitem__(key, value))
                with self.assertRaises(BuilderError):
                    validate(self.toolkit, self.project)

    def test_item_contract_references_effects_and_skip(self):
        items = authored_items()
        for mutate in (
            lambda x: x['relics'].append(copy.deepcopy(x['relics'][0])),
            lambda x: x['relics'].append({**x['relics'][2], 'id': 'Pocket_Guide'}),
            lambda x: x.update(starting_relic='Missing'),
            lambda x: x['relics'][0].update(rarity='Common'),
            lambda x: x['potions'][0]['effects'].update(energy=True),
            lambda x: x['potions'][0]['effects'].update(energy=4),
            lambda x: x['potions'][0]['effects'].update(heal=1),
            lambda x: x['relics'][0].update(trigger='cross-run'),
            lambda x: x['relics'][0]['effects'].update(block=0, draw=0, energy=0, focus=0),
        ):
            value = copy.deepcopy(items)
            mutate(value)
            atomic(self.project / 'design/items.json', encoded(value))
            with self.assertRaises(BuilderError):
                validate(self.toolkit, self.project)
        atomic(self.project / 'design/items.json', encoded(items))
        self.edit('character.json', lambda c: c['features'].update(items=False))
        with self.assertRaisesRegex(BuilderError, 'items disabled'):
            validate(self.toolkit, self.project)
        self.edit('character.json', lambda c: c['features'].update(items=True, mechanic=False))
        with self.assertRaisesRegex(BuilderError, 'focus requires'):
            validate(self.toolkit, self.project)

    def test_item_ownership_ids_and_fingerprint(self):
        before = input_hash(self.project)
        atomic(self.project / 'design/items.json', encoded(authored_items()))
        self.assertNotEqual(before, input_hash(self.project))
        generate(self.toolkit, self.project, freeze=True)
        ids = read_json(self.project / 'design/model-ids.json')['models']
        self.assertIn('Relic_Primer', ids)
        self.assertIn('Potion_Reset', ids)
        self.edit('design/items.json', lambda i: i['potions'].pop())
        with self.assertRaisesRegex(BuilderError, 'identity'):
            generate(self.toolkit, self.project)
        atomic(self.project / 'design/items.json', encoded(authored_items()))
        path = self.project / 'src/Generated/Items.cs'
        path.write_bytes(path.read_bytes() + b'// handwritten\n')
        self.edit('design/items.json', lambda i: i['potions'][0]['effects'].update(block=7))
        with self.assertRaisesRegex(BuilderError, 'Hand-edited'):
            generate(self.toolkit, self.project)

    def test_optional_item_file_and_owned_output_removal(self):
        (self.project / 'design/items.json').unlink()
        generate(self.toolkit, self.project, check=True)
        self.assertEqual(load_items(self.toolkit, self.project)['relics'], [])
        atomic(self.project / 'design/items.json', encoded(authored_items()))
        generate(self.toolkit, self.project)
        self.assertTrue((self.project / 'src/Generated/Items.cs').exists())
        atomic(self.project / 'design/items.json', encoded(dict(schema_version=1, relics=[], potions=[])))
        generate(self.toolkit, self.project)
        self.assertFalse((self.project / 'src/Generated/Items.cs').exists())

    def test_independent_item_groups_and_literal_names(self):
        items = authored_items()
        for group in ('relics', 'potions'):
            value = copy.deepcopy(items)
            value[group] = []
            if group == 'relics':
                value.pop('starting_relic')
            else:
                value['relics'][0]['name'] = 'Literal @ITEMS_JSON@ and "quotes"'
            atomic(self.project / 'design/items.json', encoded(value))
            generate(self.toolkit, self.project)
            generate(self.toolkit, self.project, check=True)
            character = (self.project / 'src/Generated/Character.cs').read_text()
            self.assertEqual('ModelDb.RelicPool<AuthoredRelicPool>()' in character, group != 'relics')
            self.assertEqual('ModelDb.PotionPool<AuthoredPotionPool>()' in character, group != 'potions')
            if group == 'potions':
                self.assertIn('@ITEMS_JSON@', (self.project / 'src/Generated/Items.cs').read_text())

    def test_event_contract_and_disabled_features(self):
        self.edit('character.json', lambda c: c['features'].update(events=True))
        for mutate in (
            lambda e: e.append(copy.deepcopy(e[0])),
            lambda e: e[0]['acts'].append(1),
            lambda e: e[0]['acts'].append(4),
            lambda e: e[0]['choices'].append(copy.deepcopy(e[0]['choices'][0])),
            lambda e: e[0]['choices'][0].update(id='Leave'),
            lambda e: e[0]['choices'][0]['cost'].update(hp=True),
            lambda e: e[0]['choices'][0]['reward'].update(heal=51),
            lambda e: e[0]['choices'][0]['reward'].update(inheritance=1),
            lambda e: e[0]['choices'][0].update(cost=dict(hp=0, gold=0), reward=dict(heal=0, gold=0)),
        ):
            events = authored_events()
            mutate(events)
            atomic(self.project / 'design/events.json', encoded(events))
            with self.assertRaises(BuilderError):
                validate(self.toolkit, self.project)
        atomic(self.project / 'design/events.json', encoded(authored_events()))
        self.edit('character.json', lambda c: c['features'].update(events=False))
        with self.assertRaisesRegex(BuilderError, 'events disabled'):
            validate(self.toolkit, self.project)

    def test_event_ownership_ids_and_fingerprint(self):
        self.edit('character.json', lambda c: c['features'].update(events=True))
        before = input_hash(self.project)
        events = authored_events()
        events[0]['body'] = 'Literal @EVENTS_JSON@ and "quotes"'
        atomic(self.project / 'design/events.json', encoded(events))
        self.assertNotEqual(before, input_hash(self.project))
        generate(self.toolkit, self.project, freeze=True)
        self.assertIn('Event_QuietCamp', read_json(self.project / 'design/model-ids.json')['models'])
        self.assertIn('@EVENTS_JSON@', (self.project / 'src/Generated/Events.cs').read_text())
        self.edit('design/events.json', lambda e: e.pop())
        with self.assertRaisesRegex(BuilderError, 'identity'):
            generate(self.toolkit, self.project)
        atomic(self.project / 'design/events.json', encoded(events))
        path = self.project / 'src/Generated/Events.cs'
        path.write_bytes(path.read_bytes() + b'// handwritten\n')
        self.edit('design/events.json', lambda e: e[0].update(name='Changed'))
        with self.assertRaisesRegex(BuilderError, 'Hand-edited'):
            generate(self.toolkit, self.project)

    def test_optional_event_file_and_output_removal(self):
        (self.project / 'design/events.json').unlink()
        self.assertEqual(load_events(self.toolkit, self.project), [])
        generate(self.toolkit, self.project, check=True)
        self.edit('character.json', lambda c: c['features'].update(events=True))
        atomic(self.project / 'design/events.json', encoded(authored_events()))
        generate(self.toolkit, self.project)
        self.assertTrue((self.project / 'src/Generated/Events.cs').exists())
        atomic(self.project / 'design/events.json', encoded([]))
        generate(self.toolkit, self.project)
        self.assertFalse((self.project / 'src/Generated/Events.cs').exists())

    def test_generation_preserves_hand_edits_and_saved_ids(self):
        generate(self.toolkit, self.project, freeze=True)
        path = self.project / 'src/Generated/Character.cs'
        edited = path.read_bytes() + b'// custom edit\n'
        path.write_bytes(edited)
        self.edit('character.json', lambda c: c.__setitem__('hp', 72))
        with self.assertRaisesRegex(BuilderError, 'Hand-edited'):
            generate(self.toolkit, self.project)
        self.assertEqual(path.read_bytes(), edited)
        self.edit('character.json', lambda c: c.__setitem__('namespace', 'RenamedHero'))
        with self.assertRaisesRegex(BuilderError, 'identity'):
            generate(self.toolkit, self.project)

    def test_changed_input_and_missing_evidence_invalidate_resume(self):
        evidence = self.project / 'design/mechanics.md'
        evidence.write_text('Verified mechanics design')
        record(self.toolkit, self.project, 'mechanics', 'complete', ['design/mechanics.md'], 'Review')
        self.assertEqual(resume(self.toolkit, self.project)['steps']['mechanics']['status'], 'complete')
        evidence.write_text('Changed evidence')
        self.assertEqual(resume(self.toolkit, self.project)['steps']['mechanics']['status'], 'pending')
        record(self.toolkit, self.project, 'mechanics', 'complete', ['design/mechanics.md'], 'Review')
        self.edit('character.json', lambda c: c.__setitem__('hp', 71))
        self.assertEqual(resume(self.toolkit, self.project)['steps']['mechanics']['status'], 'pending')
        with self.assertRaises(BuilderError):
            record(self.toolkit, self.project, 'verify', 'complete', [], 'No evidence')

    def test_equivalent_root_spellings_produce_identical_evidence(self):
        alias = self.project / '..' / self.project.name
        self.assertEqual(input_hash(alias), input_hash(self.project.resolve()))
        self.assertEqual(source_hash(alias), source_hash(self.project.resolve()))

    def test_asset_hashes_paths_and_disabled_features(self):
        self.edit('assets/manifest.json', lambda a: a[0].__setitem__('path', '../outside.svg'))
        with self.assertRaises(BuilderError):
            validate(self.toolkit, self.project)
        self.edit('assets/manifest.json', lambda a: a[0].__setitem__('path', 'assets/icon.svg'))
        (self.project / 'assets/icon.svg').write_text('changed')
        with self.assertRaisesRegex(BuilderError, 'hash changed'):
            validate(self.toolkit, self.project)

    def test_malformed_png_rejected_with_matching_provenance(self):
        malformed = b'Not a PNG despite its filename'
        atomic(self.project / 'assets/broken.png', malformed)
        self.edit('assets/manifest.json', lambda a: a.append(dict(path='assets/broken.png', sha256=digest(malformed),
                  method='supplied', license='MIT', credit='Fixture')))
        with self.assertRaisesRegex(BuilderError, 'Invalid PNG'):
            validate(self.toolkit, self.project)

    def add_portrait(self, path='assets/cards/Strike art.png', data=None):
        data = portrait_png() if data is None else data
        atomic(self.project / path, data)
        self.edit('assets/manifest.json', lambda a: a.append(dict(path=path, sha256=digest(data),
                  method='original', license='MIT', credit='Fixture')))
        self.edit('design/cards.json', lambda c: c[0].update(portrait=path))
        return data

    def test_portrait_assets_preserved_packaged_and_invalidate_build(self):
        png = self.add_portrait()
        svg = (self.project / 'assets/card.svg').read_bytes().replace(b'57B8A7', b'AA3355')
        atomic(self.project / 'assets/cards/guard.svg', svg)
        self.edit('assets/manifest.json', lambda a: a.append(dict(path='assets/cards/guard.svg', sha256=digest(svg),
                  method='original', license='MIT', credit='Fixture')))
        self.edit('design/cards.json', lambda c: c[1].update(portrait='assets/cards/guard.svg'))
        generate(self.toolkit, self.project, freeze=True)
        ids = (self.project / 'design/model-ids.json').read_bytes()
        self.mock_build()
        with zipfile.ZipFile(stage(self.toolkit, self.project)['archive']) as archive:
            self.assertEqual(archive.read('TestHero/assets/cards/Strike art.png'), png)
            self.assertEqual(archive.read('TestHero/assets/cards/guard.svg'), svg)
        self.edit('design/cards.json', lambda c: c[0].pop('portrait'))
        generate(self.toolkit, self.project)
        self.assertEqual((self.project / 'design/model-ids.json').read_bytes(), ids)
        self.assertEqual((self.project / 'assets/cards/Strike art.png').read_bytes(), png)
        with self.assertRaisesRegex(BuilderError, 'stale'):
            stage(self.toolkit, self.project)

    def test_invalid_portrait_references_and_disabled_art(self):
        self.add_portrait()
        for path in ('../outside.png', 'assets/cards/strike art.png', 'assets/missing.svg', 'assets/card.svg/../card.svg', ''):
            with self.subTest(path=path):
                self.edit('design/cards.json', lambda c: c[0].update(portrait=path))
                with self.assertRaises(BuilderError):
                    validate(self.toolkit, self.project)
        self.edit('design/cards.json', lambda c: c[0].update(portrait='assets/cards/Strike art.png'))
        self.edit('character.json', lambda c: c['features'].update(art=False))
        with self.assertRaisesRegex(BuilderError, 'art feature'):
            validate(self.toolkit, self.project)
        self.edit('design/cards.json', lambda c: c[0].pop('portrait'))
        generate(self.toolkit, self.project)
        # A declared sound is valid in the manifest but cannot serve as a portrait.
        self.edit('character.json', lambda c: c['features'].update(art=True))
        atomic(self.project / 'assets/test.ogg', b'OggS\x00' + b'\x00' * 22)
        self.edit('assets/manifest.json', lambda a: a.append(dict(path='assets/test.ogg',
                  sha256=digest(b'OggS\x00' + b'\x00' * 22), method='original', license='MIT', credit='Fixture')))
        self.edit('design/cards.json', lambda c: c[0].update(portrait='assets/test.ogg'))
        with self.assertRaisesRegex(BuilderError, 'SVG/PNG'):
            validate(self.toolkit, self.project)

    def test_native_fallback_generation(self):
        # Feature choices may change freely until the first successful native build.
        self.edit('character.json', lambda c: (c['features'].update(cards=False, mechanic=False, items=False), c.update(starting_deck=[])))
        atomic(self.project / 'design/cards.json', encoded([]))
        generate(self.toolkit, self.project)
        cs = (self.project / 'src/Generated/Character.cs').read_text()
        self.assertNotIn('class FocusPower', cs)
        self.assertNotIn('class StarterRelic', cs)
        self.assertIn('ModelDb.CardPool<IroncladCardPool>()', cs)
        self.assertEqual(resume(self.toolkit, self.project)['steps']['cards']['status'], 'skipped')

    def test_regeneration_preserves_extensions_and_literal_input(self):
        extension = self.project / 'src/Extensions/Notes.cs'
        extension.write_text('// project-owned source\n')
        self.edit('character.json', lambda c: c.update(description='Literal @CARD_POOL@ and "quotes"', hp=72))
        generate(self.toolkit, self.project)
        generate(self.toolkit, self.project, check=True)
        self.assertEqual(extension.read_text(), '// project-owned source\n')
        self.assertIn('@CARD_POOL@', (self.project / 'src/Generated/Character.cs').read_text())

    def test_optional_intent_remains_an_explicit_gap(self):
        self.edit('character.json', lambda c: c['features'].update(events=True, dialogue=True, audio=True))
        generate(self.toolkit, self.project)
        report = verify(self.toolkit, self.project)
        self.assertFalse(report['release_ready'])
        self.assertTrue(any(gap.startswith('events:') for gap in report['gaps']))
        (self.toolkit / 'untracked.txt').write_text('local toolkit edit')
        with self.assertRaisesRegex(BuilderError, 'modified'):
            resume(self.toolkit, self.project)

    def test_balance_flags_both_extremes_without_tuning(self):
        self.edit('design/cards.json', lambda c: c[3]['base'].update(cost=0, draw=2, energy=1))
        self.edit('design/cards.json', lambda c: c[4]['base'].update(cost=3, draw=0))
        original = (self.project / 'design/cards.json').read_bytes()
        codes = {f['code'] for f in balance(self.toolkit, self.project)['findings']}
        self.assertIn('repeatable_draw_energy_loop_risk', codes)
        self.assertIn('no_payoff', codes)
        self.assertEqual((self.project / 'design/cards.json').read_bytes(), original)

    def mock_build(self):
        # Explicit synthetic compile receipt for packaging tests; never native evidence.
        atomic(self.project / 'build/native/TestHero.dll', b'fixture DLL bytes')
        atomic(self.project / '.builder/build.json', encoded(dict(input_sha256=input_hash(self.project),
               source_sha256=source_hash(self.project), dll_sha256=digest(b'fixture DLL bytes'), kind='fixture')))

    def test_closed_deterministic_package_and_stale_build(self):
        self.mock_build()
        atomic(self.project / 'build/native/sts2.dll', b'Must not ship')
        atomic(self.project / 'private/secret.txt', b'Must not ship')
        first = stage(self.toolkit, self.project)
        second = stage(self.toolkit, self.project)
        self.assertEqual(first['sha256'], second['sha256'])
        with zipfile.ZipFile(first['archive']) as archive:
            self.assertNotIn('TestHero/sts2.dll', archive.namelist())
            extracted = self.project / 'private/download'
            archive.extractall(extracted)
        self.assertEqual(compare_delivery(self.project, extracted)['status'], 'match')
        (extracted / 'unexpected.txt').write_text('unexpected')
        with self.assertRaises(BuilderError):
            compare_delivery(self.project, extracted)
        self.edit('character.json', lambda c: c.__setitem__('hp', 75))
        generate(self.toolkit, self.project)
        with self.assertRaisesRegex(BuilderError, 'stale'):
            stage(self.toolkit, self.project)

    def test_dialogue_contract_and_optional_generation(self):
        self.edit('character.json', lambda c: c['features'].update(dialogue=True))
        invalid = [lambda r: r.append(copy.deepcopy(r[0])),
                   lambda r: r[0].update(ancient='THE_ARCHITECT'),
                   lambda r: r[0].update(visit='victory'),
                   lambda r: r[0].update(lines=[]),
                   lambda r: r[0]['lines'][0].update(speaker='Other'),
                   lambda r: r[0]['lines'][0].update(text=' '),
                   lambda r: r[0]['lines'][-1].update(next='Invalid'),
                   lambda r: r[0].update(progression=True)]
        for mutate in invalid:
            rows = authored_dialogue()
            mutate(rows)
            atomic(self.project / 'design/dialogue.json', encoded(rows))
            with self.assertRaises(BuilderError):
                validate(self.toolkit, self.project)
        rows = authored_dialogue()
        rows[0]['lines'][0]['text'] = 'Literal @DIALOGUE_JSON@ and "quotes"'
        atomic(self.project / 'design/dialogue.json', encoded(rows))
        generate(self.toolkit, self.project)
        generated = self.project / 'src/Generated/Dialogue.cs'
        self.assertIn('@DIALOGUE_JSON@', generated.read_text())
        before = input_hash(self.project)
        self.edit('design/dialogue.json', lambda r: r[0]['lines'][0].update(text='Changed'))
        self.assertNotEqual(before, input_hash(self.project))
        with self.assertRaisesRegex(BuilderError, 'Stale generated'):
            generate(self.toolkit, self.project, check=True)
        self.edit('character.json', lambda c: c['features'].update(dialogue=False))
        with self.assertRaisesRegex(BuilderError, 'dialogue disabled'):
            validate(self.toolkit, self.project)
        atomic(self.project / 'design/dialogue.json', encoded([]))
        original = generated.read_bytes()
        generated.write_bytes(original + b'// hand edit')
        with self.assertRaisesRegex(BuilderError, 'Hand-edited'):
            generate(self.toolkit, self.project)
        generated.write_bytes(original)
        generate(self.toolkit, self.project)
        self.assertFalse(generated.exists())
        (self.project / 'design/dialogue.json').unlink()
        self.assertEqual(load_dialogue(self.toolkit, self.project), [])
        generate(self.toolkit, self.project, check=True)

    def test_native_evidence_requires_complete_current_coverage(self):
        atomic(self.project / 'design/items.json', encoded(authored_items()))
        self.edit('character.json', lambda c: c['features'].update(events=True))
        atomic(self.project / 'design/events.json', encoded(authored_events()))
        self.edit('character.json', lambda c: c['features'].update(dialogue=True))
        atomic(self.project / 'design/dialogue.json', encoded(authored_dialogue()))
        generate(self.toolkit, self.project)
        self.mock_build()
        cards = read_json(self.project / 'design/cards.json')
        # Synthetic envelope tests evidence handling only; it is not gameplay evidence.
        checks = [dict(check=label) for label in ('registration', 'starting-kit', 'starter-trigger', 'resource-turn', 'rewards-shop', 'native-save-resume', 'item-pools', 'event-pools', 'dialogue-controls')]
        checks += [dict(check='paid-card', card=card['id'], upgraded=upgrade) for card in cards for upgrade in (False, True)]
        checks += [dict(check='card-portrait', card=card['id'], upgraded=upgrade, asset='assets/card.svg')
                   for card in cards for upgrade in (False, True)]
        checks += [dict(check=label, id=row['id']) for group, label in (('relics', 'authored-relic'), ('potions', 'authored-potion'))
                   for row in authored_items()[group]]
        checks += [dict(check='authored-event', id=event['id'], choice=choice['id'])
                   for event in authored_events() for choice in event['choices']]
        checks += [dict(check=label, id=event['id']) for event in authored_events() for label in ('event-leave', 'event-resume')]
        checks += [dict(check=label, ancient=r['ancient'], visit=r['visit']) for r in authored_dialogue()
                   for label in ('authored-dialogue', 'dialogue-resume')]
        receipt = dict(kind='native', ok=True, process_exit=0, failures=[], checks=list(checks),
                       input_sha256=input_hash(self.project), source_sha256=source_hash(self.project),
                       toolkit_commit=self.commit, release_dll_sha256=digest(b'fixture DLL bytes'), game={'version': 'fixture'},
                       native_comparators=[dict(character='CHARACTER.FIXTURE', cards=[dict(type='Attack', rarity='Common')] * 3)])
        def publish():
            data = encoded(receipt)
            atomic(self.project / 'private/synthetic-evidence.json', data)
            atomic(self.project / '.builder/native-evidence.json', encoded(dict(path='private/synthetic-evidence.json', sha256=digest(data))))
        publish()
        self.assertIsNotNone(native_evidence(self.toolkit, self.project))
        self.assertEqual(verify(self.toolkit, self.project)['native']['status'], 'pass')
        parity = balance(self.toolkit, self.project, 'CHARACTER.FIXTURE')['native_parity']
        self.assertEqual(parity['expected'], 3)
        self.assertEqual(parity['deficits'], {'Common/Attack': 1})
        receipt['checks'].pop()
        publish()
        with self.assertRaisesRegex(BuilderError, 'cover'):
            native_evidence(self.toolkit, self.project)
        receipt['checks'] = checks[:-1] + [dict(check='card-portrait', card=cards[-1]['id'], upgraded=True, asset='assets/wrong.svg')]
        publish()
        with self.assertRaisesRegex(BuilderError, 'portrait'):
            native_evidence(self.toolkit, self.project)
        receipt['checks'] = [check for check in checks if check.get('check') != 'authored-relic']
        publish()
        with self.assertRaisesRegex(BuilderError, 'relics'):
            native_evidence(self.toolkit, self.project)
        receipt['checks'] = [check for check in checks if check.get('check') != 'event-resume']
        publish()
        with self.assertRaisesRegex(BuilderError, 'event-resume'):
            native_evidence(self.toolkit, self.project)
        receipt['checks'] = [check for check in checks if not (check.get('check') == 'authored-event' and check.get('choice') == 'Trade')]
        publish()
        with self.assertRaisesRegex(BuilderError, 'authored-event'):
            native_evidence(self.toolkit, self.project)
        receipt['checks'] = checks
        publish()
        self.assertIsNotNone(native_evidence(self.toolkit, self.project))
        for label in ('authored-dialogue', 'dialogue-resume'):
            receipt['checks'] = [c for c in checks if c.get('check') != label]
            publish()
            with self.assertRaisesRegex(BuilderError, label):
                native_evidence(self.toolkit, self.project)
        receipt['checks'] = checks
        publish()
        self.edit('character.json', lambda c: c.__setitem__('hp', 72))
        generate(self.toolkit, self.project)
        self.assertEqual(verify(self.toolkit, self.project)['native']['status'], 'stale')

    @unittest.skipUnless(os.environ.get('BUILDER_TEST_GAME_DATA'), 'Owned-game compilation is opt-in')
    def test_native_compile(self):
        self.add_portrait()
        atomic(self.project / 'design/items.json', encoded(authored_items()))
        self.edit('character.json', lambda c: c['features'].update(events=True))
        atomic(self.project / 'design/events.json', encoded(authored_events()))
        self.edit('character.json', lambda c: c['features'].update(dialogue=True))
        atomic(self.project / 'design/dialogue.json', encoded(authored_dialogue()))
        generate(self.toolkit, self.project)
        try:
            receipt = build(self.toolkit, self.project, os.environ['BUILDER_TEST_GAME_DATA'])
        except BuilderError:
            print((self.project / 'private/build.log').read_text())
            raise
        self.assertEqual(receipt['kind'], 'compile')
        self.assertEqual(receipt['native_gameplay'], 'unperformed')
        self.assertNotIn(b'NativeProbe', (self.project / 'build/native/TestHero.dll').read_bytes())
        self.assertTrue(read_json(self.project / 'design/model-ids.json')['frozen'])
        stage(self.toolkit, self.project)

    @unittest.skipUnless(os.environ.get('BUILDER_TEST_GAME_DATA'), 'Owned-game compilation is opt-in')
    def test_native_compile_fallback_and_extension(self):
        self.edit('character.json', lambda c: (c['features'].update(cards=False, mechanic=False, items=False), c.update(starting_deck=[])))
        atomic(self.project / 'design/cards.json', encoded([]))
        extension = b'''namespace TestHero;
public static partial class ModEntry
{
    static partial void Configure() { ExtensionHooks.StartingRelics = () => []; }
}
'''
        atomic(self.project / 'src/Extensions/Configure.cs', extension)
        generate(self.toolkit, self.project)
        try:
            build(self.toolkit, self.project, os.environ['BUILDER_TEST_GAME_DATA'])
        except BuilderError:
            print((self.project / 'private/build.log').read_text())
            raise
        self.assertEqual((self.project / 'src/Extensions/Configure.cs').read_bytes(), extension)
        # Compile the other probe preprocessor branch without creating a game copy.
        probe = (self.toolkit / 'builder/templates/NativeProbe.cs.txt').read_text().replace('@NAMESPACE@', 'TestHero')
        probe = probe.replace('@ITEM_PROBE@', (self.toolkit / 'builder/templates/NativeItems.cs.txt').read_text())
        probe = probe.replace('@EVENT_PROBE@', (self.toolkit / 'builder/templates/NativeEvents.cs.txt').read_text())
        probe = probe.replace('@DIALOGUE_PROBE@', (self.toolkit / 'builder/templates/NativeDialogue.cs.txt').read_text())
        atomic(self.project / 'private/NativeProbe.cs', probe.encode())
        run(['dotnet', 'build', self.project / 'Character.csproj', '--configuration', 'Release',
             '--output', self.project / 'private/probe-compile', '-p:Sts2DataDir=' + os.environ['BUILDER_TEST_GAME_DATA'],
             '-p:BuilderNativeTests=true', '-p:BuilderProbeSource=' + str(self.project / 'private/NativeProbe.cs')], self.project)

    @unittest.skipUnless(os.environ.get('BUILDER_TEST_GAME_DATA'), 'Owned-game compilation is opt-in')
    def test_native_compile_items_without_focus_or_cards(self):
        self.edit('character.json', lambda c: (c['features'].update(cards=False, mechanic=False), c.update(starting_deck=[])))
        self.edit('character.json', lambda c: c['features'].update(events=True))
        atomic(self.project / 'design/events.json', encoded(authored_events()))
        atomic(self.project / 'design/cards.json', encoded([]))
        items = authored_items()
        for row in items['relics'] + items['potions']:
            row['effects']['focus'] = 0
        atomic(self.project / 'design/items.json', encoded(items))
        generate(self.toolkit, self.project)
        build(self.toolkit, self.project, os.environ['BUILDER_TEST_GAME_DATA'])
        self.assertNotIn('FocusPower', (self.project / 'src/Generated/Items.cs').read_text())


if __name__ == '__main__':
    unittest.main()
