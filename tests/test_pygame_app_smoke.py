import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ui.game_app import GameApp


class PygameSmokeTests(unittest.TestCase):
    def test_app_initializes_and_runs_one_frame_headless(self):
        app = GameApp(headless=True)
        try:
            result = app.run(max_frames=1)
        finally:
            app.shutdown()
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
