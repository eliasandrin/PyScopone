import sys
from itertools import permutations
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.engine.scoring import ScoringEngine
from scopone.models.player import Player


class ScoringTests(unittest.TestCase):
    def _normalize_capture_result(self, captures):
        return {tuple(combo) for combo in captures}

    def test_find_captures_returns_combination_when_no_equal_card_exists(self):
        captures = ScoringEngine.find_captures((7, "Spade"), [(3, "Denari"), (4, "Coppe"), (8, "Bastoni")])
        self.assertEqual(captures, [[(3, "Denari"), (4, "Coppe")]])

    def test_find_captures_returns_all_legal_combinations(self):
        table = [
            (6, "Denari"),
            (4, "Coppe"),
            (2, "Spade"),
            (5, "Bastoni"),
            (1, "Denari"),
            (3, "Coppe"),
        ]
        captures = ScoringEngine.find_captures((6, "Spade"), table)
        expected = {
            ((6, "Denari"),),
            ((4, "Coppe"), (2, "Spade")),
            ((5, "Bastoni"), (1, "Denari")),
            ((2, "Spade"), (1, "Denari"), (3, "Coppe")),
        }
        self.assertEqual(self._normalize_capture_result(captures), expected)

    def test_find_captures_includes_all_equal_value_options(self):
        table = [
            (7, "Denari"),
            (7, "Coppe"),
            (4, "Spade"),
            (3, "Bastoni"),
        ]
        captures = ScoringEngine.find_captures((7, "Spade"), table)
        expected = {
            ((7, "Denari"),),
            ((7, "Coppe"),),
            ((4, "Spade"), (3, "Bastoni")),
        }
        self.assertEqual(self._normalize_capture_result(captures), expected)

    def test_calculate_primiera_uses_best_card_per_suit(self):
        cards = [(7, "Denari"), (6, "Denari"), (1, "Coppe"), (5, "Bastoni"), (4, "Spade")]
        self.assertEqual(ScoringEngine.calculate_primiera(cards), 21 + 16 + 15 + 14)

    def test_four_player_team_scoring_aggregates_members(self):
        players = [
            Player("P1", 0, team=0),
            Player("P2", 1, team=1),
            Player("P3", 2, team=0),
            Player("P4", 3, team=1),
        ]
        players[0].captured = [
            (7, "Denari"),
            (6, "Denari"),
            (1, "Coppe"),
            (5, "Bastoni"),
            (4, "Spade"),
            (2, "Denari"),
            (3, "Denari"),
            (8, "Denari"),
            (9, "Denari"),
            (10, "Denari"),
            (1, "Denari"),
        ]
        players[2].captured = [
            (7, "Coppe"),
            (7, "Bastoni"),
            (7, "Spade"),
            (6, "Coppe"),
            (6, "Bastoni"),
            (6, "Spade"),
            (1, "Bastoni"),
            (1, "Spade"),
            (5, "Coppe"),
            (4, "Bastoni"),
        ]
        players[0].sweeps = 2
        players[2].sweeps = 1
        players[1].captured = [(2, "Coppe"), (3, "Coppe")]
        players[3].captured = [(2, "Spade"), (3, "Spade")]

        scores = ScoringEngine.calculate_final_scores(players)

        self.assertEqual(scores[0]["player"], "Team 1")
        self.assertEqual(scores[0]["captured_cards"], 21)
        self.assertEqual(scores[0]["coins"], 8)
        self.assertEqual(scores[0]["points"]["settebello"], 1)
        self.assertEqual(scores[0]["points"]["sweeps"], 3)

    def test_team_scoring_tie_gives_no_points_for_cards_coins_or_primiera(self):
        players = [
            Player("P1", 0, team=0),
            Player("P2", 1, team=1),
            Player("P3", 2, team=0),
            Player("P4", 3, team=1),
        ]

        team_zero_cards = [
            (1, "Denari"), (2, "Denari"), (3, "Denari"), (4, "Denari"), (5, "Denari"),
            (1, "Coppe"), (2, "Coppe"), (3, "Coppe"), (4, "Coppe"), (5, "Coppe"),
            (1, "Bastoni"), (2, "Bastoni"), (3, "Bastoni"), (4, "Bastoni"), (7, "Bastoni"),
            (1, "Spade"), (2, "Spade"), (5, "Spade"), (6, "Spade"), (7, "Spade"),
        ]
        team_one_cards = [
            (6, "Denari"), (7, "Denari"), (8, "Denari"), (9, "Denari"), (10, "Denari"),
            (6, "Coppe"), (7, "Coppe"), (8, "Coppe"), (9, "Coppe"), (10, "Coppe"),
            (5, "Bastoni"), (6, "Bastoni"), (8, "Bastoni"), (9, "Bastoni"), (10, "Bastoni"),
            (3, "Spade"), (4, "Spade"), (8, "Spade"), (9, "Spade"), (10, "Spade"),
        ]

        players[0].captured = team_zero_cards[:10]
        players[2].captured = team_zero_cards[10:]
        players[1].captured = team_one_cards[:10]
        players[3].captured = team_one_cards[10:]

        scores = sorted(ScoringEngine.calculate_final_scores(players), key=lambda score: score["team"])

        self.assertEqual(scores[0]["captured_cards"], 20)
        self.assertEqual(scores[1]["captured_cards"], 20)
        self.assertEqual(scores[0]["coins"], 5)
        self.assertEqual(scores[1]["coins"], 5)
        self.assertEqual(scores[0]["primiera_value"], scores[1]["primiera_value"])
        self.assertEqual(scores[0]["points"]["cards"], 0)
        self.assertEqual(scores[1]["points"]["cards"], 0)
        self.assertEqual(scores[0]["points"]["coins"], 0)
        self.assertEqual(scores[1]["points"]["coins"], 0)
        self.assertEqual(scores[0]["points"]["primiera"], 0)
        self.assertEqual(scores[1]["points"]["primiera"], 0)
        self.assertEqual(scores[1]["points"]["settebello"], 1)
        self.assertTrue(scores[1]["has_settebello"])

    def test_get_game_winners_is_deterministic_across_24_tie_permutations(self):
        score_entries = [
            {"player": "Gamma", "total": 9},
            {"player": "Alpha", "total": 12},
            {"player": "Beta", "total": 12},
            {"player": "Delta", "total": 12},
        ]

        for perm in permutations(score_entries, 4):
            winners = ScoringEngine.get_game_winners(list(perm))
            self.assertEqual(winners, ["Alpha", "Beta", "Delta"])

    def test_get_game_winners_uses_highest_total_even_when_input_is_unsorted(self):
        final_scores = [
            {"player": "Player 3", "total": 2},
            {"player": "Player 1", "total": 7},
            {"player": "Player 2", "total": 7},
        ]

        self.assertEqual(ScoringEngine.get_game_winners(final_scores), ["Player 1", "Player 2"])

    def test_get_game_winners_two_way_tie_when_cards_denari_settebello_are_equal(self):
        final_scores = [
            {
                "player": "Team 1",
                "captured_cards": 20,
                "coins": 5,
                "has_settebello": True,
                "primiera_value": 72,
                "total": 2,
            },
            {
                "player": "Team 2",
                "captured_cards": 20,
                "coins": 5,
                "has_settebello": True,
                "primiera_value": 72,
                "total": 2,
            },
        ]

        self.assertEqual(ScoringEngine.get_game_winners(final_scores), ["Team 1", "Team 2"])


if __name__ == "__main__":
    unittest.main()
