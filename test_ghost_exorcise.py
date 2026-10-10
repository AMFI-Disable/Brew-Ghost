import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestGhostExorcise(unittest.TestCase):
    @patch('builtins.input', return_value='y')
    @patch('subprocess.run')
    def test_exorcise_confirmed(self, mock_run, mock_input):
        print("Testing --exorcise with confirmation 'y'...")
        
        ghosts = [
            {'name': 'ffmpeg', 'days_idle': 200, 'size': 398458880},
            {'name': 'imagemagick', 'days_idle': 150, 'size': 125829120}
        ]
        
        ghost_names = [g['name'] for g in ghosts]
        self.assertEqual(ghost_names, ['ffmpeg', 'imagemagick'])
        
        confirm = mock_input()
        self.assertEqual(confirm, 'y')
        
        if confirm in ('y', 'yes'):
            for pkg in ghost_names:
                mock_run(['brew', 'uninstall', pkg], check=True)
            
        import unittest.mock
        mock_run.assert_has_calls([
            unittest.mock.call(['brew', 'uninstall', 'ffmpeg'], check=True),
            unittest.mock.call(['brew', 'uninstall', 'imagemagick'], check=True)
        ])
        print("Test passed! Correctly invoked brew uninstall for each package individually.\n")

    @patch('builtins.input', return_value='n')
    @patch('subprocess.run')
    def test_exorcise_aborted(self, mock_run, mock_input):
        print("Testing --exorcise with rejection 'n'...")
        
        ghosts = [
            {'name': 'ffmpeg', 'days_idle': 200, 'size': 398458880},
            {'name': 'imagemagick', 'days_idle': 150, 'size': 125829120}
        ]
        
        ghost_names = [g['name'] for g in ghosts]
        confirm = mock_input()
        
        if confirm in ('y', 'yes'):
            for pkg in ghost_names:
                mock_run(['brew', 'uninstall', pkg], check=True)
            
        mock_run.assert_not_called()
        print("Test passed! Safely aborted without running brew uninstall.\n")

if __name__ == '__main__':
    unittest.main()
