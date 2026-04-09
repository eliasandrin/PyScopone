import statistics
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ai.strategies import ExpertAI


class ExpertAILatencyTests(unittest.TestCase):
    def _scenario_empty_table(self):
        hand = [
            (1, "Denari"),
            (2, "Coppe"),
            (3, "Bastoni"),
            (4, "Spade"),
            (5, "Denari"),
            (6, "Coppe"),
            (7, "Bastoni"),
            (8, "Spade"),
            (9, "Denari"),
            (10, "Coppe"),
        ]
        return hand, [], set(), {"team_captured": []}

    def _scenario_full_table(self):
        hand = [
            (10, "Denari"),
            (9, "Coppe"),
            (8, "Bastoni"),
            (7, "Spade"),
            (6, "Denari"),
            (5, "Coppe"),
            (4, "Bastoni"),
            (3, "Spade"),
            (2, "Denari"),
            (1, "Coppe"),
        ]
        table = [
            (1, "Denari"),
            (2, "Denari"),
            (3, "Denari"),
            (4, "Coppe"),
            (5, "Coppe"),
            (6, "Bastoni"),
            (7, "Bastoni"),
            (8, "Spade"),
            (9, "Spade"),
            (10, "Denari"),
        ]
        seen_cards = {
            (1, "Coppe"),
            (2, "Coppe"),
            (3, "Coppe"),
            (4, "Denari"),
            (5, "Denari"),
            (6, "Spade"),
        }
        return hand, table, seen_cards, {"team_captured": []}

    def _scenario_four_player_team(self):
        hand, table, _, _ = self._scenario_full_table()
        team_captured = [
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
        seen_cards = set(team_captured + table + hand[:4])
        return hand, table, seen_cards, {"team_captured": team_captured}

    def _measure_ms(self, ai, hand, table, seen_cards, player_scores, loops):
        samples = []
        for _ in range(loops):
            start = time.perf_counter()
            ai.choose_move(hand, table, seen_cards=seen_cards, player_scores=player_scores)
            samples.append((time.perf_counter() - start) * 1000.0)
        samples.sort()
        p95_index = int(0.95 * (len(samples) - 1))
        return {
            "avg_ms": statistics.mean(samples),
            "p95_ms": samples[p95_index],
            "max_ms": max(samples),
        }

    def test_expert_latency_cache_off_under_500ms(self):
        scenarios = [
            self._scenario_empty_table(),
            self._scenario_full_table(),
            self._scenario_four_player_team(),
        ]

        for hand, table, seen_cards, player_scores in scenarios:
            ai = ExpertAI(enable_scopa_cache=False)
            metrics = self._measure_ms(ai, hand, table, seen_cards, player_scores, loops=20)
            self.assertLess(metrics["p95_ms"], 500.0)
            self.assertLess(metrics["max_ms"], 1000.0)

    def test_expert_latency_cache_on_under_100ms(self):
        scenarios = [
            self._scenario_empty_table(),
            self._scenario_full_table(),
            self._scenario_four_player_team(),
        ]

        for hand, table, seen_cards, player_scores in scenarios:
            ai = ExpertAI(enable_scopa_cache=True, scopa_cache_size=128)
            ai.choose_move(hand, table, seen_cards=seen_cards, player_scores=player_scores)
            metrics = self._measure_ms(ai, hand, table, seen_cards, player_scores, loops=30)
            self.assertLess(metrics["p95_ms"], 100.0)


if __name__ == "__main__":
    unittest.main()
