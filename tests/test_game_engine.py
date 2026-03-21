import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.config.game import FULL_DECK
from scopone.engine.game_engine import GameEngine


class GameEngineTests(unittest.TestCase):
    def test_play_card_captures_matching_value(self):
        engine = GameEngine(2, ["Tu", "AI"])
        engine.reset()
        engine.table = [(4, "Denari")]
        engine.players[0].hand = [(4, "Coppe")]
        engine.players[1].hand = [(9, "Spade")]
        engine.current_player_idx = 0

        moved = engine.play_card(0, (4, "Coppe"))

        self.assertTrue(moved)
        self.assertEqual(engine.table, [])
        self.assertIn((4, "Coppe"), engine.players[0].captured)
        self.assertIn((4, "Denari"), engine.players[0].captured)
        self.assertEqual(engine.players[0].sweeps, 1)

    def test_last_card_that_clears_table_does_not_score_scopa(self):
        engine = GameEngine(2, ["Tu", "AI"])
        engine.reset()
        engine.table = [(4, "Denari")]
        engine.players[0].hand = [(4, "Coppe")]
        engine.players[1].hand = []
        engine.current_player_idx = 0
        engine.game_active = True

        engine.play_card(0, (4, "Coppe"))

        self.assertFalse(engine.game_active)
        self.assertEqual(engine.players[0].sweeps, 0)

    def test_two_player_restock_flow_keeps_match_active(self):
        engine = GameEngine(2, ["Tu", "AI"])
        engine.reset()
        engine.table = []
        engine.players[0].hand = [(1, "Denari")]
        engine.players[1].hand = []
        engine.current_player_idx = 0
        engine.deck_remaining = FULL_DECK[1:21]

        engine.play_card(0, (1, "Denari"))

        self.assertTrue(engine.game_active)
        self.assertEqual(len(engine.players[0].hand), 10)
        self.assertEqual(len(engine.players[1].hand), 10)
        self.assertEqual(engine.deck_remaining, [])


if __name__ == "__main__":
    unittest.main()
