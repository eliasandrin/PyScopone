import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ui.match_coordinator import MatchCoordinator


class _DummyAnimations:
    def has_active(self):
        return False


class _DummyRoundOverlay:
    active = False


class _DummyPlayer:
    def __init__(self):
        self.id = 0
        self.name = "Tu"
        self.is_human = True
        self.hand = [(7, "Denari")]


class _DummyEngine:
    def __init__(self):
        self.game_active = True
        self.table = [(7, "Spade"), (4, "Denari"), (3, "Coppe")]
        self.seen_cards = set()
        self.player = _DummyPlayer()
        self.last_move_result = {"restocked": False}
        self.play_calls = []

    def get_current_player(self):
        return self.player

    def play_card(self, player_idx, card, capture_combo=None, decision_log=None):
        self.play_calls.append((player_idx, card, capture_combo, decision_log))
        return True


class _DummyScene:
    def __init__(self):
        self.menu_open = False
        self.deal_sequence_pending = False
        self.animations = _DummyAnimations()
        self.round_overlay = _DummyRoundOverlay()
        self.capture_choice_active = False
        self.settings = {"difficulty": "normale"}
        self.requested_choice = None
        self.queued = None
        self.logs = []

    def request_capture_choice(self, card, options):
        self.capture_choice_active = True
        self.requested_choice = (card, options)

    def _get_hand_card_rect(self, player_id, card):
        return None

    def _get_table_source_rects(self, cards):
        return {}

    def _queue_move_sequence(self, player, card, source_rect, captured_cards, captured_rects, move_result):
        self.queued = (player, card, captured_cards, move_result)

    def _append_log(self, message):
        self.logs.append(message)

    def _format_card(self, card):
        return str(card)


class _DummyApp:
    pass


class MatchCoordinatorTests(unittest.TestCase):
    def test_on_player_move_does_not_request_choice_when_minimum_capture_is_unique(self):
        engine = _DummyEngine()
        engine.table = [(8, "Spade"), (1, "Denari"), (2, "Coppe"), (5, "Bastoni")]
        scene = _DummyScene()
        coordinator = MatchCoordinator(_DummyApp(), engine, scene)

        coordinator.on_player_move((8, "Denari"))

        self.assertIsNone(scene.requested_choice)
        self.assertEqual(len(engine.play_calls), 1)
        _, _, capture_combo, _ = engine.play_calls[0]
        self.assertEqual(capture_combo, [(8, "Spade")])

    def test_on_player_move_requests_choice_when_multiple_minimum_captures_exist(self):
        engine = _DummyEngine()
        engine.table = [(7, "Spade"), (7, "Coppe"), (4, "Denari"), (3, "Bastoni")]
        scene = _DummyScene()
        coordinator = MatchCoordinator(_DummyApp(), engine, scene)

        coordinator.on_player_move((7, "Denari"))

        self.assertIsNotNone(scene.requested_choice)
        self.assertEqual(len(engine.play_calls), 0)
        _, options = scene.requested_choice
        self.assertEqual(len(options), 2)
        self.assertEqual(sorted(options), sorted([[(7, "Spade")], [(7, "Coppe")]]))

    def test_on_player_move_uses_explicit_selected_combo(self):
        engine = _DummyEngine()
        scene = _DummyScene()
        coordinator = MatchCoordinator(_DummyApp(), engine, scene)

        selected_combo = [(4, "Denari"), (3, "Coppe")]
        coordinator.on_player_move((7, "Denari"), capture_combo=selected_combo)

        self.assertEqual(len(engine.play_calls), 1)
        player_idx, card, capture_combo, decision_log = engine.play_calls[0]
        self.assertEqual(player_idx, 0)
        self.assertEqual(card, (7, "Denari"))
        self.assertEqual(capture_combo, selected_combo)
        self.assertIsInstance(decision_log, dict)
        self.assertEqual(decision_log.get("strategy"), "human")
        self.assertEqual(decision_log.get("chosen_combo"), selected_combo)


if __name__ == "__main__":
    unittest.main()
