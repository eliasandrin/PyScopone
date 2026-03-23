import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ai.strategies import AIStrategy, EasyAI, ExpertAI, NormalAI, get_ai_strategy


class AIStrategyTests(unittest.TestCase):
    def test_base_ai_strategy_raises_not_implemented(self):
        strategy = AIStrategy()
        with self.assertRaises(NotImplementedError):
            strategy.choose_card([], [])

    def test_base_ai_strategy_default_reason_when_not_set(self):
        strategy = AIStrategy()
        self.assertEqual(strategy.get_last_decision_reason(), "Nessuna motivazione disponibile")

    def test_easy_ai_returns_none_on_empty_hand(self):
        strategy = EasyAI()
        self.assertIsNone(strategy.choose_card([], []))
        self.assertIn("mano vuota", strategy.get_last_decision_reason())

    def test_easy_ai_prefers_random_capture_when_available(self):
        strategy = EasyAI()
        hand = [(7, "Denari"), (4, "Coppe")]
        table = [(7, "Spade")]
        with patch("scopone.ai.strategies.random.choice", side_effect=lambda seq: seq[0]):
            chosen = strategy.choose_card(hand, table)
        self.assertEqual(chosen, (7, "Denari"))
        self.assertIn("presa casuale", strategy.get_last_decision_reason())

    def test_easy_ai_random_discard_when_no_capture(self):
        strategy = EasyAI()
        hand = [(2, "Coppe"), (8, "Bastoni")]
        table = [(7, "Spade")]
        with patch("scopone.ai.strategies.random.choice", side_effect=lambda seq: seq[-1]):
            chosen = strategy.choose_card(hand, table)
        self.assertEqual(chosen, (8, "Bastoni"))
        self.assertIn("scarto casuale", strategy.get_last_decision_reason())

    def test_normal_ai_prefers_capture(self):
        strategy = NormalAI()
        chosen = strategy.choose_card([(2, "Coppe"), (7, "Denari")], [(7, "Spade")])
        self.assertEqual(chosen, (7, "Denari"))
        self.assertIn("cattura", strategy.get_last_decision_reason())

    def test_normal_ai_discards_high_card_when_no_capture(self):
        strategy = NormalAI()
        chosen = strategy.choose_card([(2, "Coppe"), (8, "Bastoni"), (5, "Denari")], [(7, "Spade")])
        self.assertEqual(chosen, (8, "Bastoni"))
        self.assertIn("scarico carta alta", strategy.get_last_decision_reason())

    def test_normal_ai_returns_none_on_empty_hand(self):
        strategy = NormalAI()
        self.assertIsNone(strategy.choose_card([], []))
        self.assertIn("mano vuota", strategy.get_last_decision_reason())

    def test_expert_ai_prefers_richer_capture(self):
        strategy = ExpertAI()
        chosen = strategy.choose_card([(6, "Coppe"), (8, "Bastoni")], [(4, "Denari"), (4, "Coppe"), (6, "Spade")])
        self.assertEqual(chosen, (8, "Bastoni"))

    def test_expert_ai_returns_none_on_empty_hand(self):
        strategy = ExpertAI()
        self.assertIsNone(strategy.choose_card([], []))
        self.assertIn("mano vuota", strategy.get_last_decision_reason())

    def test_expert_ai_empty_table_avoids_risk(self):
        strategy = ExpertAI()
        hand = [(7, "Denari"), (2, "Coppe")]
        chosen = strategy.choose_card(hand, [], seen_cards=set())
        self.assertIn(chosen, hand)
        self.assertIn("tavolo vuoto", strategy.get_last_decision_reason())

    def test_get_ai_strategy_uses_supported_difficulties_and_fallback(self):
        self.assertIsInstance(get_ai_strategy("divertimento"), EasyAI)
        self.assertIsInstance(get_ai_strategy("normale"), NormalAI)
        self.assertIsInstance(get_ai_strategy("esperto"), ExpertAI)
        self.assertIsInstance(get_ai_strategy("adaptive"), ExpertAI)
        self.assertIsInstance(get_ai_strategy("non-esiste"), NormalAI)


if __name__ == "__main__":
    unittest.main()
