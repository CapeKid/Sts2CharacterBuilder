"""Behavioral tests using real repositories, submodules and separate project roots."""
import argparse
import copy
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

from builder.contracts import BuilderError, digest, encoded, input_hash, read_json, validate
from builder.project import atomic, bootstrap, generate, run
from builder.verification import balance, build, compare_delivery, pin_check, record, resume, source_hash, stage, verify

REPO = Path(__file__).resolve().parents[2]


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

    @unittest.skipUnless(os.environ.get('BUILDER_TEST_GAME_DATA'), 'Owned-game compilation is opt-in')
    def test_native_compile(self):
        try:
            receipt = build(self.toolkit, self.project, os.environ['BUILDER_TEST_GAME_DATA'])
        except BuilderError:
            print((self.project / 'private/build.log').read_text())
            raise
        self.assertEqual(receipt['kind'], 'compile')
        self.assertEqual(receipt['native_gameplay'], 'unperformed')
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


if __name__ == '__main__':
    unittest.main()
