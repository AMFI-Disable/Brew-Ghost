import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class TestSettingsCLI(unittest.TestCase):
    def setUp(self):
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        self.home = Path(home.name)
        self.config = self.home / '.config/brew-ghost/config.json'
        self.config.parent.mkdir(parents=True)

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(Path(__file__).with_name('ghost.py')), *args],
            env={**os.environ, 'HOME': str(self.home), 'PATH': str(self.home)},
            capture_output=True, text=True, timeout=10,
        )

    def test_json_before_and_after_days(self):
        for args in [('--days', '91', '--json'), ('--json', '-d', '91')]:
            with self.subTest(args=args):
                self.config.write_text('{"other": true}')
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), {'status': 'success', 'days_threshold': 91})
                self.assertEqual(json.loads(self.config.read_text()), {'other': True, 'days_threshold': 91})

    def test_invalid_options_leave_settings_intact(self):
        self.config.write_text('{"days_threshold": 14}')
        for args in [('--days', '30', '--unknown'), ('--days', '30', '-d', '181'),
                     ('--days', '0'), ('--days', 'invalid'), ('--days',)]:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
                self.assertEqual(self.config.read_text(), '{"days_threshold": 14}')

    def test_failed_replacement_reports_error(self):
        self.config.mkdir()
        result = self.run_cli('--days', '45', '--json')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Could not save', result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(list(self.config.parent.iterdir()), [self.config])

    def test_plain_output_and_help(self):
        result = self.run_cli('--days', '180')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('180 days', result.stdout)
        result = self.run_cli('--days', '1', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Usage:', result.stdout)
        self.assertEqual(json.loads(self.config.read_text()), {'days_threshold': 180})
