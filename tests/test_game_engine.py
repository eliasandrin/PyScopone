import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.config.game import FULL_DECK
from scopone.config.game import MODE_TOURNAMENT
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

    def test_play_card_respects_selected_capture_combo(self):
        engine = GameEngine(2, ["Tu", "AI"])
        engine.reset()
        engine.table = [(7, "Denari"), (7, "Coppe"), (4, "Spade"), (3, "Bastoni")]
        engine.players[0].hand = [(7, "Spade")]
        engine.players[1].hand = [(1, "Coppe")]
        engine.current_player_idx = 0

        moved = engine.play_card(0, (7, "Spade"), capture_combo=[(4, "Spade"), (3, "Bastoni")])

        self.assertTrue(moved)
        self.assertIn((7, "Spade"), engine.players[0].captured)
        self.assertIn((4, "Spade"), engine.players[0].captured)
        self.assertIn((3, "Bastoni"), engine.players[0].captured)
        self.assertEqual(sorted(engine.table), sorted([(7, "Denari"), (7, "Coppe")]))

    def test_play_card_default_capture_prefers_equal_value_settebello(self):
        engine = GameEngine(2, ["Tu", "AI"])
        engine.reset()
        engine.table = [(7, "Denari"), (7, "Coppe"), (4, "Spade"), (3, "Bastoni")]
        engine.players[0].hand = [(7, "Spade")]
        engine.players[1].hand = [(1, "Coppe")]
        engine.current_player_idx = 0

        moved = engine.play_card(0, (7, "Spade"))

        self.assertTrue(moved)
        self.assertIn((7, "Denari"), engine.players[0].captured)
        self.assertNotIn((7, "Coppe"), engine.players[0].captured)
        self.assertNotIn((4, "Spade"), engine.players[0].captured)
        self.assertNotIn((3, "Bastoni"), engine.players[0].captured)

    def test_live_tournament_scores_returns_dict(self):
        engine = GameEngine(4, ["Tu", "AI 1", "AI 2", "AI 3"], game_mode=MODE_TOURNAMENT)
        engine.reset()

        live_scores = engine.get_live_tournament_scores()

        self.assertIsInstance(live_scores, dict)
        self.assertEqual(live_scores.get(0), 0)
        self.assertEqual(live_scores.get(1), 0)

    def test_tournament_round_end_pauses_until_next_round_is_requested(self):
        engine = GameEngine(4, ["Tu", "AI 1", "AI 2", "AI 3"], game_mode=MODE_TOURNAMENT)
        engine.reset()
        initial_round = engine.round_number
        initial_dealer = engine.dealer_idx

        # Force a deterministic end-round state with low points so nobody reaches 21.
        engine.table = []
        for player in engine.players:
            player.hand = []
            player.captured = []
            player.sweeps = 0
        engine.players[0].captured = [(7, "Denari")]

        summary = engine.end_game()

        self.assertFalse(summary["next_round_started"])
        self.assertFalse(engine.game_active)
        self.assertEqual(engine.round_number, initial_round)
        self.assertEqual(engine.dealer_idx, initial_dealer)
        self.assertEqual(len(engine.round_history), 1)

        engine.start_next_round()

        self.assertTrue(engine.game_active)
        self.assertEqual(engine.round_number, initial_round + 1)
        self.assertEqual(engine.dealer_idx, (initial_dealer - 1) % engine.num_players)


if __name__ == "__main__":
    unittest.main()
