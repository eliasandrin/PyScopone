import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ai.strategies import get_ai_strategy
from scopone.engine.game_engine import GameEngine
from scopone.engine.scoring import ScoringEngine


class AIBalanceSimulationTests(unittest.TestCase):
    def _play_duel(self, left_difficulty: str, right_difficulty: str, seed: int) -> str:
        random.seed(seed)
        engine = GameEngine(2, ["Left", "Right"])
        engine.reset()
        engine.deal_cards()

        max_turns = 400
        turns = 0
        while engine.game_active and turns < max_turns:
            current = engine.get_current_player()
            difficulty = left_difficulty if current.id == 0 else right_difficulty
            strategy = get_ai_strategy(difficulty)
            selected_card, selected_combo = strategy.choose_move(
                current.hand,
                engine.table,
                player_scores={"team_captured": list(current.captured)},
                seen_cards=engine.seen_cards,
            )
            if selected_card is None:
                break
            engine.play_card(
                current.id,
                selected_card,
                capture_combo=selected_combo or None,
                decision_log=strategy.get_last_decision_log(),
            )
            if engine.game_active:
                engine.next_player()
            turns += 1

        self.assertLess(turns, max_turns, "Simulation exceeded max turns, potential loop in turn flow")

        winners = ScoringEngine.get_game_winners(engine.final_scores)
        if winners == ["Left"]:
            return left_difficulty
        if winners == ["Right"]:
            return right_difficulty
        return "draw"

    def _run_balanced_series(self, difficulty_a: str, difficulty_b: str, seeds: int = 60) -> dict:
        wins_a = 0
        wins_b = 0
        draws = 0
        for seed in range(seeds):
            outcomes = (
                self._play_duel(difficulty_a, difficulty_b, seed),
                self._play_duel(difficulty_b, difficulty_a, seed),
            )
            for outcome in outcomes:
                if outcome == difficulty_a:
                    wins_a += 1
                elif outcome == difficulty_b:
                    wins_b += 1
                else:
                    draws += 1
        return {"wins_a": wins_a, "wins_b": wins_b, "draws": draws, "games": seeds * 2}

    def test_expert_is_stronger_than_normal_in_balanced_series(self):
        stats = self._run_balanced_series("esperto", "normale", seeds=60)
        self.assertGreaterEqual(stats["wins_a"], 78)
        self.assertGreater(stats["wins_a"], stats["wins_b"])

    def test_normal_outperforms_easy_in_balanced_series(self):
        stats = self._run_balanced_series("normale", "divertimento", seeds=60)
        self.assertGreaterEqual(stats["wins_a"], 66)
        self.assertGreater(stats["wins_a"], stats["wins_b"])


if __name__ == "__main__":
    unittest.main()
