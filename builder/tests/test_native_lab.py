"""Isolation and one-shot transport checks without owned game files."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from builder.contracts import BuilderError
from builder.native_lab import accounts, check_target, copy_lab, file_hash, PROFILE_PREFIX, run_native, workshop_catalog


class NativeLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='builder-lab-tests-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.game = self.root / 'owned game'
        self.game.mkdir()
        (self.game / 'SlayTheSpire2.exe').write_bytes(b'owned executable fixture')
        (self.game / 'data_sts2_windows_x86_64').mkdir()
        (self.game / 'data_sts2_windows_x86_64/sts2.dll').write_bytes(b'owned assembly fixture')
        (self.game / 'mods').mkdir()
        (self.game / 'mods/private-save.txt').write_text('must not be copied')
        (self.game / 'override.cfg').write_text('personal override must not be copied')
        self.baselib = self.root / 'baselib'
        for name in ('lib/net9.0/BaseLib.dll', 'Content/BaseLib.json', 'Content/BaseLib.pck'):
            path = self.baselib / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'BaseLib fixture')
        self.lab = self.root / 'project/private/labs/test'
        self.token = '1' * 32
        self.profile = self.root / (PROFILE_PREFIX + self.token)

    def prepare(self, **changes):
        args = dict(lab=self.lab, game=self.game, baselib=self.baselib, profile=self.profile,
                    account_paths=['default/1', 'steam/123'], catalog=[dict(id='UnrelatedMod')], mod_id='TestHero',
                    dll=b'test-only DLL', payloads={'TestHero.json': b'{"id":"TestHero"}'}, token=self.token)
        return copy_lab(**(args | changes))

    def test_independent_exact_copy_and_separate_profile(self):
        inventory = self.prepare()
        copied = self.lab / 'game/SlayTheSpire2.exe'
        self.assertFalse(os.path.samefile(copied, self.game / 'SlayTheSpire2.exe'))
        copied.write_bytes(b'changed copy')
        self.assertEqual((self.game / 'SlayTheSpire2.exe').read_bytes(), b'owned executable fixture')
        self.assertNotEqual(file_hash(copied), inventory['game/SlayTheSpire2.exe'])
        self.assertFalse((self.lab / 'game/mods/private-save.txt').exists())
        self.assertIn(self.profile.name, (self.lab / 'game/override.cfg').read_text())
        settings = json.loads((self.profile / 'steam/123/settings.save').read_text())
        self.assertEqual(settings['mod_settings']['mod_list'], [dict(id='UnrelatedMod', source=2, is_enabled=False),
                         dict(id='BaseLib', source=1, is_enabled=True), dict(id='TestHero', source=1, is_enabled=True)])
        self.assertEqual(json.loads((self.profile / 'builder-lab.json').read_text())['token'], self.token)

    def test_existing_lab_or_profile_never_overwritten(self):
        self.prepare()
        sentinel = self.profile / 'sentinel'
        sentinel.write_text('preserve')
        with self.assertRaisesRegex(BuilderError, 'fresh'):
            self.prepare()
        self.assertEqual(sentinel.read_text(), 'preserve')

    def test_overlap_and_unsafe_payload_fail_before_copying(self):
        with self.assertRaisesRegex(BuilderError, 'overlap'):
            self.prepare(lab=self.game / 'nested lab')
        with self.assertRaisesRegex(BuilderError, 'Unsafe'):
            self.prepare(payloads={'../outside.dll': b'bad'})
        with self.assertRaisesRegex(BuilderError, 'Unsafe'):
            self.prepare(account_paths=['../personal-profile'])
        self.assertFalse(self.lab.exists())
        self.assertFalse(self.profile.exists())

    def test_workshop_catalog_detects_changed_or_new_manifests(self):
        workshop = self.root / 'workshop'
        workshop.mkdir()
        (workshop / 'other.json').write_text('{"id":"Other","has_dll":true}')
        before = workshop_catalog(workshop)
        (workshop / 'other.json').write_text('{"id":"Other","has_dll":false}')
        self.assertNotEqual(before, workshop_catalog(workshop))
        (workshop / 'broken.json').write_text('not json')
        self.assertEqual(len(workshop_catalog(workshop)), 1)

    def test_linked_source_rejected_before_copy(self):
        outside = self.root / 'unrelated files'
        outside.mkdir()
        try:
            (self.game / 'linked').symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('Host cannot create test symlinks')
        with self.assertRaisesRegex(BuilderError, 'links'):
            self.prepare()
        self.assertFalse(self.lab.exists())

    def test_account_discovery_has_no_machine_specific_identity(self):
        userdata = self.root / 'userdata'
        userdata.mkdir()
        (userdata / '123').mkdir()
        (userdata / 'not-an-account').mkdir()
        self.assertEqual(accounts(userdata), ['default/1', 'steam/76561197960265851'])

    def test_started_lab_never_replays_even_if_previous_result_timed_out(self):
        self.lab.mkdir(parents=True)
        (self.lab / 'run.json').write_text('{"status":"timeout"}')
        with patch('builder.native_lab.subprocess.Popen') as launch:
            with self.assertRaisesRegex(BuilderError, 'never replay'):
                run_native(self.root / 'toolkit', self.root / 'project', 'test')
            launch.assert_not_called()

    def test_native_branch_claim_requires_matching_game_version(self):
        toolkit = Path(__file__).resolve().parents[2]
        check_target(toolkit, 'public-beta', {'version': 'v0.111.0'})
        with self.assertRaisesRegex(BuilderError, 'does not match'):
            check_target(toolkit, 'regular', {'version': 'v0.111.0'})
        with self.assertRaisesRegex(BuilderError, 'review compatibility'):
            check_target(toolkit, 'public-beta', {'version': 'v9.0.0'})


if __name__ == '__main__':
    unittest.main()
