"""Turn-flow coordinator for the live match scene."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from scopone.ai.strategies import get_ai_strategy
from scopone.config.game import MODE_TOURNAMENT
from scopone.config.ui import AI_THINKING_DELAY_MS

if TYPE_CHECKING:
    from scopone.engine.game_engine import GameEngine
    from scopone.types import Card
    from scopone.ui.game_app import GameApp
    from scopone.ui.scenes.match_scene import MatchScene


class MatchCoordinator:
    """Owns turn sequencing, AI pacing, and game-resolution transitions."""

    STATE_WAITING_INPUT = "waiting_input"
    STATE_ANIMATING_MOVE = "animating_move"
    STATE_AI_THINKING = "ai_thinking"
    STATE_RESOLVING = "resolving"
    STATE_WAITING_ROUND_CONFIRM = "waiting_round_confirm"
    STATE_GAME_OVER = "game_over"

    def __init__(self, app: "GameApp", engine: Optional["GameEngine"], scene: "MatchScene") -> None:
        self.app = app
        self.engine = engine
        self.scene = scene
        self.state = self.STATE_WAITING_INPUT
        self.pending_ai_player_id = None
        self.ai_thinking_timer = 0.0
        self.result_dispatched = False
        self.pending_resolution_result = None

    def bind_engine(self, engine: Optional["GameEngine"]) -> None:
        self.engine = engine
        self.pending_ai_player_id = None
        self.ai_thinking_timer = 0.0
        self.result_dispatched = False
        self.pending_resolution_result = None
        if engine is None:
            self.state = self.STATE_WAITING_INPUT
        elif self.scene.deal_sequence_pending:
            self.state = self.STATE_ANIMATING_MOVE
        elif not engine.game_active:
            self.state = self.STATE_GAME_OVER
        else:
            self.state = self.STATE_WAITING_INPUT

    def can_accept_player_input(self) -> bool:
        if self.engine is None or not self.engine.game_active:
            return False
        if self.scene.menu_open or self.scene.deal_sequence_pending or self.scene.animations.has_active() or self.scene.round_end_overlay_active:
            return False
        current_player = self.engine.get_current_player()
        return current_player.is_human and self.state == self.STATE_WAITING_INPUT

    def on_player_move(self, card: "Card") -> None:
        if self.engine is None or not self.can_accept_player_input():
            return

        current_player = self.engine.get_current_player()
        source_rect = self.scene._get_hand_card_rect(current_player.id, card)
        captured_cards = self.scene._preview_captured_cards(card)
        captured_rects = self.scene._get_table_source_rects(captured_cards)
        if not self.engine.play_card(current_player.id, card):
            self.scene._append_log("Mossa non valida.")
            return

        self.scene._append_log("Tu giochi {0}".format(self.scene._format_card(card)))
        self.pending_ai_player_id = None
        self.ai_thinking_timer = 0.0
        self.state = self.STATE_ANIMATING_MOVE
        self.scene._queue_move_sequence(current_player, card, source_rect, captured_cards, captured_rects, self.engine.last_move_result)

    def update(self, dt: float) -> None:
        if self.engine is None or self.result_dispatched:
            return

        if self.scene.round_end_overlay_active:
            self.state = self.STATE_WAITING_ROUND_CONFIRM
            return

        if self.scene.deal_sequence_pending or self.scene.animations.has_active():
            self.state = self.STATE_ANIMATING_MOVE
            return

        if not self.engine.game_active:
            self.state = self.STATE_GAME_OVER
            self._dispatch_results()
            return

        current_player = self.engine.get_current_player()
        if current_player.is_human:
            self.pending_ai_player_id = None
            self.ai_thinking_timer = 0.0
            self.state = self.STATE_WAITING_INPUT
            return

        if not current_player.hand:
            self.pending_ai_player_id = None
            self.ai_thinking_timer = 0.0
            self.state = self.STATE_RESOLVING
            return

        if self.pending_ai_player_id != current_player.id:
            self.pending_ai_player_id = current_player.id
            self.ai_thinking_timer = AI_THINKING_DELAY_MS / 1000.0
            self.state = self.STATE_AI_THINKING
            self.scene._append_log("{0} sta pensando...".format(current_player.name))
            return

        self.state = self.STATE_AI_THINKING
        self.ai_thinking_timer -= dt
        if self.ai_thinking_timer <= 0.0:
            self._play_ai_turn()

    def on_move_animation_finished(self, move_result) -> None:
        if self.engine is None or move_result is None:
            return

        self.pending_resolution_result = move_result
        self.state = self.STATE_RESOLVING
        if move_result.get("restocked") and self.scene.last_layout is not None:
            self.state = self.STATE_ANIMATING_MOVE
            self.scene._schedule_deal_sequence(
                self.scene.last_layout,
                include_table=False,
                only_player_ids=[player.id for player in self.engine.players],
                on_complete=self.complete_turn_resolution,
            )
            return

        self.complete_turn_resolution()

    def complete_turn_resolution(self) -> None:
        if self.engine is None:
            return

        move_result = self.pending_resolution_result or {}
        self.pending_resolution_result = None
        self.state = self.STATE_RESOLVING

        if self.scene.settings.get("game_mode") == MODE_TOURNAMENT and move_result.get("round_ended"):
            self.scene.show_round_end_overlay(move_result)
            self.pending_ai_player_id = None
            self.ai_thinking_timer = 0.0
            self.state = self.STATE_WAITING_ROUND_CONFIRM
            return

        if self.engine.game_active:
            self.engine.next_player()
        self.pending_ai_player_id = None
        self.ai_thinking_timer = 0.0

        if not self.engine.game_active:
            self.state = self.STATE_GAME_OVER
            self._dispatch_results()
            return

        current_player = self.engine.get_current_player()
        self.state = self.STATE_WAITING_INPUT if current_player.is_human else self.STATE_AI_THINKING

    def on_round_confirmed(self, move_result) -> None:
        self.pending_ai_player_id = None
        self.ai_thinking_timer = 0.0
        self.pending_resolution_result = None
        self.result_dispatched = False

        if move_result.get("game_ended"):
            self.state = self.STATE_GAME_OVER
            self._dispatch_results()
            return

        self.state = self.STATE_ANIMATING_MOVE if self.scene.deal_sequence_pending else self.STATE_WAITING_INPUT

    def _play_ai_turn(self) -> None:
        if self.engine is None:
            return

        current_player = self.engine.get_current_player()
        strategy = get_ai_strategy(self.scene.settings["difficulty"])
        selected_card = strategy.choose_card(
            current_player.hand,
            self.engine.table,
            player_scores=self._build_ai_player_scores(current_player),
            seen_cards=self.engine.seen_cards,
        )
        if selected_card is None:
            return

        source_rect = self.scene._get_hand_card_rect(current_player.id, selected_card)
        captured_cards = self.scene._preview_captured_cards(selected_card)
        captured_rects = self.scene._get_table_source_rects(captured_cards)
        self.engine.play_card(current_player.id, selected_card)
        self.scene._append_log("{0} gioca {1}".format(current_player.name, self.scene._format_card(selected_card)))
        self.scene._append_log("AI: {0}".format(strategy.get_last_decision_reason()))
        self.pending_ai_player_id = None
        self.ai_thinking_timer = 0.0
        self.state = self.STATE_ANIMATING_MOVE
        self.scene._queue_move_sequence(
            current_player,
            selected_card,
            source_rect,
            captured_cards,
            captured_rects,
            self.engine.last_move_result,
        )

    def _build_ai_player_scores(self, player) -> dict:
        team_captured = list(player.captured)
        if self.engine is not None and self.engine.num_players == 4 and player.team is not None:
            team_captured = []
            for teammate in self.engine.players:
                if teammate.team == player.team:
                    team_captured.extend(teammate.captured)
        return {"team_captured": team_captured}

    def _dispatch_results(self) -> None:
        if self.engine is None or self.result_dispatched:
            return

        self.result_dispatched = True
        settings = dict(self.scene.settings)
        settings["round_history"] = list(self.engine.round_history)
        self.app.show_results(self.engine.final_scores, settings, self.scene.log_messages)
