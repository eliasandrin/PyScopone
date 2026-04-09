import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.config.game import MODE_TOURNAMENT
from scopone.engine.game_engine import GameEngine
from scopone.ui.scenes.match_scene import MatchScene


class _SceneLike:
    pass


class MatchSceneLiveScoresTests(unittest.TestCase):
    def _build_scene_like(self, engine):
        scene_like = _SceneLike()
        scene_like.engine = engine
        scene_like.settings = {"game_mode": MODE_TOURNAMENT}
        return scene_like

    def _end_single_round_with_team_one_scoring(self, engine):
        engine.reset()
        engine.table = []
        for player in engine.players:
            player.hand = []
            player.captured = []
            player.sweeps = 0

        engine.players[0].captured = [(7, "Denari"), (6, "Denari"), (1, "Coppe"), (5, "Bastoni")]
        engine.players[0].sweeps = 1
        engine.players[1].captured = [(2, "Spade")]

        summary = engine.end_game()
        self.assertTrue(summary.get("round_complete"))
        self.assertFalse(engine.game_active)

    def test_tournament_live_rows_after_round_end_do_not_double_count_two_player(self):
        engine = GameEngine(2, ["Tu", "AI"], game_mode=MODE_TOURNAMENT)
        self._end_single_round_with_team_one_scoring(engine)

        scene_like = self._build_scene_like(engine)
        rows = MatchScene._get_live_team_rows(scene_like)

        totals = {index: row["total"] for index, row in enumerate(rows)}
        live_base = engine.get_live_tournament_scores()

        self.assertGreater(live_base[0], 0)
        self.assertEqual(totals[0], live_base[0])
        self.assertEqual(totals[1], live_base[1])

    def test_tournament_live_rows_after_round_end_do_not_double_count_four_player(self):
        engine = GameEngine(4, ["Tu", "AI 1", "AI 2", "AI 3"], game_mode=MODE_TOURNAMENT)
        self._end_single_round_with_team_one_scoring(engine)

        scene_like = self._build_scene_like(engine)
        rows = MatchScene._get_live_team_rows(scene_like)

        totals = {int(row["label"].split(" ")[1]) - 1: row["total"] for row in rows}
        live_base = engine.get_live_tournament_scores()

        self.assertGreater(live_base[0], 0)
        self.assertEqual(totals[0], live_base[0])
        self.assertEqual(totals[1], live_base[1])


if __name__ == "__main__":
    unittest.main()
