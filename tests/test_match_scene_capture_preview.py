import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.engine.game_engine import GameEngine
from scopone.ui.scenes.match_scene import MatchScene


class _SceneLike:
    pass


class MatchSceneCapturePreviewTests(unittest.TestCase):
    def _build_scene_like(self, table_cards):
        engine = GameEngine(2, ["Tu", "AI"])
        engine.reset()
        engine.table = list(table_cards)

        scene_like = _SceneLike()
        scene_like.engine = engine
        return scene_like

    def test_preview_highlight_returns_unique_minimum_capture(self):
        scene = self._build_scene_like(
            [(8, "Spade"), (1, "Denari"), (2, "Coppe"), (5, "Bastoni")]
        )

        captured = MatchScene._get_hover_capture_preview_cards(scene, (8, "Denari"))

        self.assertEqual(captured, [(8, "Spade")])

    def test_preview_highlight_hides_when_capture_choice_is_ambiguous(self):
        scene = self._build_scene_like(
            [(7, "Spade"), (7, "Coppe"), (4, "Denari"), (3, "Bastoni")]
        )

        captured = MatchScene._get_hover_capture_preview_cards(scene, (7, "Denari"))

        self.assertEqual(captured, [])


if __name__ == "__main__":
    unittest.main()
