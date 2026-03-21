import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ai.strategies import AdaptiveAI, ExpertAI, NormalAI


class AIStrategyTests(unittest.TestCase):
    def test_normal_ai_prefers_capture(self):
        strategy = NormalAI()
        chosen = strategy.choose_card([(2, "Coppe"), (7, "Denari")], [(7, "Spade")])
        self.assertEqual(chosen, (7, "Denari"))
        self.assertIn("cattura", strategy.get_last_decision_reason())

    def test_expert_ai_prefers_richer_capture(self):
        strategy = ExpertAI()
        chosen = strategy.choose_card([(6, "Coppe"), (8, "Bastoni")], [(4, "Denari"), (4, "Coppe"), (6, "Spade")])
        self.assertEqual(chosen, (8, "Bastoni"))

    def test_adaptive_ai_returns_reasoned_choice(self):
        strategy = AdaptiveAI()
        chosen = strategy.choose_card(
            [(7, "Denari"), (3, "Coppe"), (6, "Spade")],
            [(2, "Denari"), (4, "Bastoni")],
            seen_cards={(1, "Denari")},
        )
        self.assertIn(chosen, [(6, "Spade"), (3, "Coppe"), (7, "Denari")])
        self.assertTrue(strategy.get_last_decision_reason())


if __name__ == "__main__":
    unittest.main()
