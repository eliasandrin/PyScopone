import pygame

from scopone.ai.strategies import get_ai_strategy
from scopone.config.game import DEFAULT_PLAYER_NAMES, SIMBOLI
from scopone.config.ui import (
    AI_THINKING_DELAY_MS,
    CARD_SIZE_HAND,
    CARD_SIZE_SMALL,
    CARD_SIZE_TABLE,
    HIGHLIGHT_COLOR,
    PANEL_ALT_COLOR,
    PANEL_COLOR,
    TEXT_COLOR,
    TEXT_DIM_COLOR,
)
from scopone.engine.game_engine import GameEngine
from scopone.engine.scoring import ScoringEngine
from scopone.ui.animation import AnimationManager, CardTween
from scopone.ui.backgrounds import draw_prismatic_background
from scopone.ui.scene_manager import Scene


TEAM_COLORS = {
    0: (117, 185, 255),
    1: (255, 176, 96),
}

PLAYER_FRAME_IDLE_COLOR = (214, 222, 234)
PLAYER_FRAME_ACTIVE_COLOR = (223, 188, 96)
BLOCK_Y_OFFSET = -50

DEAL_CARD_DELAY = 0.075
DEAL_CARD_DURATION = 0.28
PLAY_CARD_DURATION = 0.24
CAPTURE_CARD_DURATION = 0.30


class MatchScene(Scene):
    """Renders the live match and translates user actions into engine calls."""

    def __init__(self, app, settings: dict) -> None:
        super().__init__(app)
        self.settings = dict(settings)
        self.engine = None
        self.log_messages = []
        self.card_hitboxes = []
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self.result_dispatched = False

        self.menu_open = False
        self.menu_button_rect = pygame.Rect(0, 0, 0, 0)
        self.menu_buttons = {}

        self.log_visible = False
        self.log_rect = None
        self.log_dragging = False
        self.log_drag_offset = (0, 0)
        self.log_header_rect = pygame.Rect(0, 0, 0, 0)

        self.animations = AnimationManager()
        self.hidden_hand_cards = {}
        self.hidden_table_cards = set()
        self.card_position_map = {"hands": {}, "table": {}}
        self.capture_pile_targets = {}
        self.last_layout = None
        self.deal_sequence_pending = False

        self._start_new_game()

    def _start_new_game(self) -> None:
        player_names = [DEFAULT_PLAYER_NAMES[index] if index > 0 else "Tu" for index in range(self.settings["num_players"])]
        self.engine = GameEngine(self.settings["num_players"], player_names)
        self.engine.reset()
        self.engine.deal_cards()
        self.log_messages = [
            "Nuova partita avviata.",
            "Modalita: {0} giocatori".format(self.settings["num_players"]),
            "Difficolta AI: {0}".format(self.settings["difficulty"]),
        ]
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self.result_dispatched = False
        self.menu_open = False
        self.log_visible = False
        self.animations.clear()
        self.card_hitboxes = []
        self.last_layout = None
        self.card_position_map = {"hands": {}, "table": {}}
        self.capture_pile_targets = {}
        self.hidden_hand_cards = dict((player.id, set(player.hand)) for player in self.engine.players)
        self.hidden_table_cards = set(self.engine.table)
        self.deal_sequence_pending = True

    def _append_log(self, message: str) -> None:
        self.log_messages.append(message)
        if len(self.log_messages) > 40:
            self.log_messages = self.log_messages[-40:]

    def handle_event(self, event) -> None:
        if self.engine is None:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.menu_open = not self.menu_open
                return
            if event.key == pygame.K_F12:
                self.log_visible = not self.log_visible
                return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.log_dragging = False
            return

        if event.type == pygame.MOUSEMOTION and self.log_dragging and self.log_rect is not None:
            self.log_rect.topleft = (
                event.pos[0] - self.log_drag_offset[0],
                event.pos[1] - self.log_drag_offset[1],
            )
            self._clamp_log_rect()
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self.log_visible and self.log_header_rect.collidepoint(event.pos) and self.log_rect is not None:
            self.log_dragging = True
            self.log_drag_offset = (
                event.pos[0] - self.log_rect.x,
                event.pos[1] - self.log_rect.y,
            )
            return

        if self.menu_button_rect.collidepoint(event.pos):
            self.menu_open = not self.menu_open
            return

        if self.menu_open:
            self._handle_menu_click(event.pos)
            return

        if self.deal_sequence_pending or self.animations.has_active():
            return

        current_player = self.engine.get_current_player()
        if not self.engine.game_active or not current_player.is_human:
            return

        for rect, card in reversed(self.card_hitboxes):
            if rect.collidepoint(event.pos):
                self._play_human_card(card)
                return

    def _handle_menu_click(self, pos) -> None:
        for action, rect in self.menu_buttons.items():
            if not rect.collidepoint(pos):
                continue

            if action == "difficulty":
                self._cycle_difficulty()
            elif action == "toggle_cards":
                self.settings["show_all_cards"] = not self.settings["show_all_cards"]
                mode = "attiva" if self.settings["show_all_cards"] else "disattiva"
                self._append_log("Visualizzazione carte IA {0}.".format(mode))
            elif action == "resume":
                self.menu_open = False
            elif action == "log":
                self.log_visible = True
                self.menu_open = False
            elif action == "new_game":
                self._start_new_game()
            elif action == "quit":
                self.app.request_quit()
            return

    def _cycle_difficulty(self) -> None:
        difficulties = ["easy", "normal", "expert", "adaptive"]
        current = difficulties.index(self.settings["difficulty"])
        self.settings["difficulty"] = difficulties[(current + 1) % len(difficulties)]
        self._append_log("Difficolta AI impostata su {0}.".format(self.settings["difficulty"]))

    def update(self, dt: float) -> None:
        if self.engine is None or self.result_dispatched:
            return

        if self.menu_open:
            return

        if self.deal_sequence_pending:
            return

        self.animations.update(dt)
        if self.animations.has_active():
            return

        if not self.engine.game_active:
            self.result_dispatched = True
            self.app.show_results(self.engine.final_scores, self.settings, self.log_messages)
            return

        current_player = self.engine.get_current_player()
        if not current_player.is_ai or not current_player.hand:
            self.pending_ai_player_id = None
            self.ai_timer = 0.0
            return

        if self.pending_ai_player_id != current_player.id:
            self.pending_ai_player_id = current_player.id
            self.ai_timer = AI_THINKING_DELAY_MS / 1000.0
            self._append_log("{0} sta pensando...".format(current_player.name))
            return

        self.ai_timer -= dt
        if self.ai_timer <= 0:
            self._play_ai_turn()

    def _play_human_card(self, card) -> None:
        assert self.engine is not None
        current_player = self.engine.get_current_player()
        source_rect = self._get_hand_card_rect(current_player.id, card)
        captured_cards = self._preview_captured_cards(card)
        if not self.engine.play_card(current_player.id, card):
            self._append_log("Mossa non valida.")
            return

        self._append_log("Tu giochi {0}".format(self._format_card(card)))
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self._queue_move_sequence(current_player, card, source_rect, captured_cards, self.engine.last_move_result)

    def _play_ai_turn(self) -> None:
        assert self.engine is not None
        current_player = self.engine.get_current_player()
        strategy = get_ai_strategy(self.settings["difficulty"])
        selected_card = strategy.choose_card(
            current_player.hand,
            self.engine.table,
            seen_cards=self.engine.seen_cards,
        )
        if selected_card is None:
            return

        source_rect = self._get_hand_card_rect(current_player.id, selected_card)
        captured_cards = self._preview_captured_cards(selected_card)
        self.engine.play_card(current_player.id, selected_card)
        self._append_log("{0} gioca {1}".format(current_player.name, self._format_card(selected_card)))
        self._append_log("AI: {0}".format(strategy.get_last_decision_reason()))
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self._queue_move_sequence(current_player, selected_card, source_rect, captured_cards, self.engine.last_move_result)

    def _queue_move_sequence(self, player, card, source_rect, captured_cards, move_result) -> None:
        if source_rect is None or self.last_layout is None or move_result is None:
            self._after_move_animations(move_result)
            return

        start_angle = self._get_player_angle(player.id)
        if captured_cards:
            target_rect = self._get_table_stack_rect(self.last_layout["table_rect"], 0, len(captured_cards) + 1)
            self.animations.add(
                CardTween(
                    card=card,
                    start_rect=source_rect,
                    target_rect=target_rect,
                    duration=PLAY_CARD_DURATION,
                    face_up=True,
                    start_angle=start_angle,
                    target_angle=0,
                    on_start=lambda: self.app.audio.play("play"),
                    on_complete=lambda: self._queue_capture_sequence(player.id, card, captured_cards, move_result),
                    layer=3,
                )
            )
            return

        self.hidden_table_cards.add(card)
        table_rects = self._get_table_card_rects(self.last_layout["table_rect"], move_result["table_cards_after"])
        target_rect = table_rects.get(card, self._get_table_stack_rect(self.last_layout["table_rect"], 0, 1))
        self.animations.add(
            CardTween(
                card=card,
                start_rect=source_rect,
                target_rect=target_rect,
                duration=PLAY_CARD_DURATION,
                face_up=True,
                start_angle=start_angle,
                target_angle=0,
                on_start=lambda: self.app.audio.play("play"),
                on_complete=lambda: self._finish_table_play(card, move_result),
                layer=3,
            )
        )

    def _finish_table_play(self, card, move_result) -> None:
        self.hidden_table_cards.discard(card)
        self._after_move_animations(move_result)

    def _queue_capture_sequence(self, player_id: int, played_card, captured_cards, move_result) -> None:
        if self.last_layout is None:
            self._after_move_animations(move_result)
            return

        cards_to_collect = [played_card] + list(captured_cards)
        if not cards_to_collect:
            self._after_move_animations(move_result)
            return

        remaining = {"count": len(cards_to_collect)}
        capture_target = self.capture_pile_targets.get(player_id, self._get_default_capture_target(self.last_layout["table_rect"]))

        def handle_complete():
            remaining["count"] -= 1
            if remaining["count"] <= 0:
                self._after_move_animations(move_result)

        for index, current_card in enumerate(cards_to_collect):
            start_rect = self._get_table_stack_rect(self.last_layout["table_rect"], index, len(cards_to_collect))
            target_rect = capture_target.move(index * 2, index * 2)
            self.animations.add(
                CardTween(
                    card=current_card,
                    start_rect=start_rect,
                    target_rect=target_rect,
                    duration=CAPTURE_CARD_DURATION,
                    face_up=True,
                    start_angle=0,
                    target_angle=0,
                    on_start=(lambda: self.app.audio.play("capture")) if index == 0 else None,
                    on_complete=handle_complete,
                    layer=4,
                )
            )

    def _after_move_animations(self, move_result) -> None:
        if move_result is None:
            return

        if move_result.get("restocked") and self.last_layout is not None:
            self._prepare_restock_visibility()
            self._schedule_deal_sequence(
                self.last_layout,
                include_table=False,
                only_player_ids=[player.id for player in self.engine.players],
                on_complete=self._finalize_turn_after_animation,
            )
            return

        self._finalize_turn_after_animation()

    def _prepare_restock_visibility(self) -> None:
        for player in self.engine.players:
            self.hidden_hand_cards.setdefault(player.id, set()).update(player.hand)

    def _finalize_turn_after_animation(self) -> None:
        if self.engine is None:
            return
        if self.engine.game_active:
            self.engine.next_player()
        self.pending_ai_player_id = None
        self.ai_timer = 0.0

    def _preview_captured_cards(self, card):
        capture_options = ScoringEngine.find_captures(card, self.engine.table)
        if capture_options and capture_options[0]:
            return list(capture_options[0])
        return []

    def _format_card(self, card) -> str:
        return "{0}{1}".format(card[0], SIMBOLI[card[1]])

    def render(self, renderer) -> None:
        assert self.engine is not None

        draw_prismatic_background(renderer.surface, variant="game")
        width, height = renderer.surface.get_size()
        layout = self._calculate_layout(width, height)
        self.last_layout = layout
        self.capture_pile_targets = layout["capture_targets"]
        self._ensure_log_rect(width, height)
        mouse_pos = pygame.mouse.get_pos()

        if self.deal_sequence_pending:
            self._schedule_deal_sequence(
                layout,
                include_table=True,
                only_player_ids=[player.id for player in self.engine.players],
            )
            self.deal_sequence_pending = False

        self.card_hitboxes = []
        self.card_position_map = {"hands": {}, "table": {}}
        self.menu_button_rect = layout["menu_button"]

        self._draw_table(renderer, layout["table_rect"])
        self._draw_deck_anchor(renderer, layout["deck_rect"])
        self._draw_table_cards(renderer, layout["table_rect"])
        self._draw_live_score_panel(renderer, layout["score_panel"])
        self._draw_menu_button(renderer, layout["menu_button"], mouse_pos)
        self._draw_players(renderer, layout)
        self.animations.render(renderer)

        if self.log_visible:
            self._draw_log_overlay(renderer)

        if self.menu_open:
            self._draw_menu_overlay(renderer, layout["overlay_rect"], mouse_pos)

    def _schedule_deal_sequence(self, layout, include_table: bool, only_player_ids, on_complete=None) -> None:
        deck_rect = layout["deck_rect"]
        reveal_registry = []
        sequence_index = 0

        if include_table:
            table_rects = self._get_table_card_rects(layout["table_rect"], self.engine.table)
            for card in self.engine.table:
                target_rect = table_rects.get(card)
                if target_rect is None:
                    continue
                reveal_registry.append(("table", None, card))
                self.animations.add(
                    CardTween(
                        card=card,
                        start_rect=deck_rect,
                        target_rect=target_rect,
                        duration=DEAL_CARD_DURATION,
                        face_up=True,
                        delay=sequence_index * DEAL_CARD_DELAY,
                        on_start=lambda: self.app.audio.play("deal"),
                        on_complete=self._make_reveal_callback("table", None, card, reveal_registry, on_complete),
                        layer=2,
                    )
                )
                sequence_index += 1

        hand_rect_maps = self._get_all_hand_rect_maps(layout)
        player_lookup = dict((player.id, player) for player in self.engine.players)
        ordered_ids = [player.id for player in self.engine.players if player.id in only_player_ids]
        max_cards = 0
        for player_id in ordered_ids:
            max_cards = max(max_cards, len(player_lookup[player_id].hand))

        for card_index in range(max_cards):
            for player_id in ordered_ids:
                player = player_lookup[player_id]
                if card_index >= len(player.hand):
                    continue
                card = player.hand[card_index]
                target_rect = hand_rect_maps.get(player_id, {}).get(card)
                if target_rect is None:
                    continue
                reveal_registry.append(("hand", player_id, card))
                self.animations.add(
                    CardTween(
                        card=card,
                        start_rect=deck_rect,
                        target_rect=target_rect,
                        duration=DEAL_CARD_DURATION,
                        face_up=self._is_face_up_player(player),
                        start_angle=0,
                        target_angle=self._get_player_angle(player.id),
                        delay=sequence_index * DEAL_CARD_DELAY,
                        on_start=lambda: self.app.audio.play("deal"),
                        on_complete=self._make_reveal_callback("hand", player_id, card, reveal_registry, on_complete),
                        layer=2,
                    )
                )
                sequence_index += 1

        if not reveal_registry and on_complete is not None:
            on_complete()

    def _make_reveal_callback(self, area: str, player_id, card, registry, final_callback):
        def callback():
            if area == "table":
                self.hidden_table_cards.discard(card)
            else:
                self.hidden_hand_cards.setdefault(player_id, set()).discard(card)

            try:
                registry.remove((area, player_id, card))
            except ValueError:
                pass

            if not registry and final_callback is not None:
                final_callback()

        return callback

    def _calculate_layout(self, width: int, height: int):
        margin = self._clamp(int(min(width, height) * 0.02), 14, 28)
        label_lane = self._clamp(int(min(width, height) * 0.06), 48, 64)
        top_cards_height = self._clamp(int(height * 0.1), 84, 108)
        bottom_cards_height = self._clamp(int(height * 0.18), 150, 208)
        side_cards_width = self._clamp(int(width * 0.145), 138, 182)

        score_panel = pygame.Rect(margin, margin, 322, 132)
        menu_button = pygame.Rect(width - margin - 92, margin, 92, 38)
        top_cards_top = score_panel.bottom + 18

        horizontal_left = side_cards_width + label_lane + (margin * 2)
        horizontal_width = width - (horizontal_left * 2)
        top_player_rect = pygame.Rect(horizontal_left, top_cards_top, horizontal_width, top_cards_height)
        top_label_rect = pygame.Rect(horizontal_left, top_player_rect.bottom + 8, horizontal_width, 46)

        bottom_player_rect = pygame.Rect(horizontal_left, height - bottom_cards_height - margin, horizontal_width, bottom_cards_height)
        bottom_label_rect = pygame.Rect(horizontal_left, bottom_player_rect.top - 54, horizontal_width, 46)

        table_rect = pygame.Rect(
            horizontal_left + 42,
            top_label_rect.bottom + margin,
            horizontal_width - 84,
            bottom_label_rect.top - top_label_rect.bottom - (margin * 2),
        )

        left_player_rect = pygame.Rect(margin, table_rect.top, side_cards_width, table_rect.height)
        left_label_rect = pygame.Rect(left_player_rect.right + 8, table_rect.top, table_rect.left - left_player_rect.right - 16, table_rect.height)
        right_label_rect = pygame.Rect(table_rect.right + 8, table_rect.top, width - margin - side_cards_width - table_rect.right - 16, table_rect.height)
        right_player_rect = pygame.Rect(width - side_cards_width - margin, table_rect.top, side_cards_width, table_rect.height)

        for rect in (
            top_player_rect,
            top_label_rect,
            table_rect,
            left_player_rect,
            left_label_rect,
            right_label_rect,
            right_player_rect,
            bottom_label_rect,
            bottom_player_rect,
        ):
            rect.move_ip(0, BLOCK_Y_OFFSET)

        deck_rect = pygame.Rect(
            table_rect.right - CARD_SIZE_SMALL[0] - 22,
            table_rect.centery - (CARD_SIZE_SMALL[1] // 2),
            CARD_SIZE_SMALL[0],
            CARD_SIZE_SMALL[1],
        )
        capture_targets = {
            0: pygame.Rect(bottom_player_rect.left + 18, bottom_label_rect.top - 16, CARD_SIZE_SMALL[0], CARD_SIZE_SMALL[1]),
            1: pygame.Rect(left_player_rect.centerx - (CARD_SIZE_SMALL[0] // 2), table_rect.bottom - CARD_SIZE_SMALL[1] - 18, CARD_SIZE_SMALL[0], CARD_SIZE_SMALL[1]),
            2: pygame.Rect(top_player_rect.left + 18, top_player_rect.top + 6, CARD_SIZE_SMALL[0], CARD_SIZE_SMALL[1]),
            3: pygame.Rect(right_player_rect.centerx - (CARD_SIZE_SMALL[0] // 2), table_rect.top + 18, CARD_SIZE_SMALL[0], CARD_SIZE_SMALL[1]),
        }
        overlay_rect = pygame.Rect(width // 2 - 340, height // 2 - 180, 680, 360)

        return {
            "table_rect": table_rect,
            "deck_rect": deck_rect,
            "capture_targets": capture_targets,
            "top_player_rect": top_player_rect,
            "bottom_player_rect": bottom_player_rect,
            "left_player_rect": left_player_rect,
            "right_player_rect": right_player_rect,
            "top_label_rect": top_label_rect,
            "bottom_label_rect": bottom_label_rect,
            "left_label_rect": left_label_rect,
            "right_label_rect": right_label_rect,
            "score_panel": score_panel,
            "menu_button": menu_button,
            "overlay_rect": overlay_rect,
        }

    def _draw_table(self, renderer, rect: pygame.Rect) -> None:
        table_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(table_surface, (14, 32, 68, 118), table_surface.get_rect(), border_radius=34)
        pygame.draw.rect(table_surface, (176, 214, 255, 62), table_surface.get_rect(), width=2, border_radius=34)
        pygame.draw.ellipse(
            table_surface,
            (201, 232, 255, 18),
            pygame.Rect(rect.width * 0.2, rect.height * 0.22, rect.width * 0.6, rect.height * 0.56),
        )
        renderer.surface.blit(table_surface, rect.topleft)
        renderer.draw_text("Tavolo", (rect.centerx, rect.top + 14), size=24, bold=True, align="center")

    def _draw_deck_anchor(self, renderer, deck_rect: pygame.Rect) -> None:
        if self.engine.num_players == 2 or self.animations.has_active():
            renderer.draw_card((1, "Denari"), deck_rect, face_up=False)

    def _draw_table_cards(self, renderer, table_rect: pygame.Rect) -> None:
        rect_map = self._get_table_card_rects(table_rect, self.engine.table)
        self.card_position_map["table"] = rect_map

        visible_cards = [card for card in self.engine.table if card not in self.hidden_table_cards]
        if not visible_cards:
            renderer.draw_text("Tavolo vuoto", table_rect.center, size=22, color=TEXT_DIM_COLOR, align="center")
            return

        for card in self.engine.table:
            if card in self.hidden_table_cards:
                continue
            renderer.draw_card(card, rect_map[card], face_up=True)

    def _draw_players(self, renderer, layout) -> None:
        hand_rect_maps = self._get_all_hand_rect_maps(layout)
        self.card_position_map["hands"] = hand_rect_maps

        if self.engine.num_players == 2:
            self._draw_horizontal_ai_hand(renderer, self.engine.players[1], hand_rect_maps[self.engine.players[1].id])
            self._draw_horizontal_label(renderer, self.engine.players[1], layout["top_label_rect"])
        else:
            self._draw_horizontal_ai_hand(renderer, self.engine.players[2], hand_rect_maps[self.engine.players[2].id])
            self._draw_horizontal_label(renderer, self.engine.players[2], layout["top_label_rect"])
            self._draw_vertical_ai_hand(renderer, self.engine.players[1], hand_rect_maps[self.engine.players[1].id], side="left")
            self._draw_vertical_label(renderer, self.engine.players[1], layout["left_label_rect"], side="left")
            self._draw_vertical_ai_hand(renderer, self.engine.players[3], hand_rect_maps[self.engine.players[3].id], side="right")
            self._draw_vertical_label(renderer, self.engine.players[3], layout["right_label_rect"], side="right")

        self._draw_human_hand(renderer, self.engine.get_human_player(), hand_rect_maps[self.engine.get_human_player().id])
        self._draw_horizontal_label(renderer, self.engine.get_human_player(), layout["bottom_label_rect"])

    def _draw_horizontal_ai_hand(self, renderer, player, rect_map) -> None:
        show_cards = self._is_face_up_player(player)
        for card in player.hand:
            if card in self.hidden_hand_cards.get(player.id, set()):
                continue
            renderer.draw_card(card, rect_map[card], face_up=show_cards)

    def _draw_vertical_ai_hand(self, renderer, player, rect_map, side: str) -> None:
        del side
        show_cards = self._is_face_up_player(player)
        angle = self._get_player_angle(player.id)
        for card in player.hand:
            if card in self.hidden_hand_cards.get(player.id, set()):
                continue
            renderer.draw_card(card, rect_map[card], face_up=show_cards, angle=angle)

    def _draw_human_hand(self, renderer, player, rect_map) -> None:
        visible_cards = [card for card in player.hand if card not in self.hidden_hand_cards.get(player.id, set())]
        if not visible_cards:
            if self.last_layout is not None:
                renderer.draw_text("Mano vuota", self.last_layout["bottom_player_rect"].center, size=22, color=TEXT_DIM_COLOR, align="center")
            return

        current_human_turn = (
            self.engine.game_active
            and self.engine.get_current_player().is_human
            and not self.menu_open
            and not self.animations.has_active()
        )
        for card in player.hand:
            if card in self.hidden_hand_cards.get(player.id, set()):
                continue
            card_rect = rect_map[card]
            renderer.draw_card(card, card_rect, face_up=True)
            if current_human_turn:
                self.card_hitboxes.append((card_rect, card))

    def _draw_horizontal_label(self, renderer, player, rect: pygame.Rect) -> None:
        team_label, team_color = self._get_player_team_meta(player)
        current = player == self.engine.get_current_player() and self.engine.game_active and not self.menu_open
        label_surface = self._build_player_label_surface(renderer, player.name, team_label, team_color, current)
        label_rect = label_surface.get_rect(center=rect.center)
        renderer.surface.blit(label_surface, label_rect)

    def _draw_vertical_label(self, renderer, player, rect: pygame.Rect, side: str) -> None:
        team_label, team_color = self._get_player_team_meta(player)
        current = player == self.engine.get_current_player() and self.engine.game_active and not self.menu_open
        base_surface = self._build_player_label_surface(renderer, player.name, team_label, team_color, current)
        rotated = pygame.transform.rotate(base_surface, 90 if side == "left" else -90)
        rotated_rect = rotated.get_rect(center=rect.center)
        renderer.surface.blit(rotated, rotated_rect)

    def _draw_live_score_panel(self, renderer, rect: pygame.Rect) -> None:
        self._draw_glass_panel(renderer, rect, PANEL_COLOR, HIGHLIGHT_COLOR, alpha=198)
        renderer.draw_text("Live", (rect.left + 14, rect.top + 10), size=18, bold=True)

        headers = [("Tot", rect.left + 136), ("Scope", rect.left + 198), ("Carte", rect.left + 264)]
        for label, x in headers:
            renderer.draw_text(label, (x, rect.top + 16), size=14, color=TEXT_DIM_COLOR, align="midtop")

        rows = self._get_live_team_rows()
        y = rect.top + 50
        for row in rows:
            renderer.draw_text(row["label"], (rect.left + 16, y), size=16, color=row["color"], bold=True)
            renderer.draw_text(str(row["total"]), (rect.left + 136, y), size=16, color=TEXT_COLOR)
            renderer.draw_text(str(row["sweeps"]), (rect.left + 206, y), size=16, color=TEXT_COLOR, align="midtop")
            renderer.draw_text(str(row["cards"]), (rect.left + 272, y), size=16, color=TEXT_COLOR, align="midtop")
            y += 28

    def _get_live_team_rows(self):
        rows = []
        if self.engine.num_players == 4:
            final_scores = {
                score["team"]: score
                for score in ScoringEngine.calculate_final_scores(self.engine.players)
            }
            for team_id in (0, 1):
                members = [player for player in self.engine.players if player.team == team_id]
                rows.append(
                    {
                        "label": "Sq {0}".format(team_id + 1),
                        "color": TEAM_COLORS[team_id],
                        "total": final_scores.get(team_id, {}).get("total", 0),
                        "sweeps": sum(player.sweeps for player in members),
                        "cards": sum(len(player.captured) for player in members),
                    }
                )
            return rows

        player_scores = {
            score["player"]: score
            for score in ScoringEngine.calculate_final_scores(self.engine.players)
        }
        for player in self.engine.players[:2]:
            team_id = player.id
            rows.append(
                {
                    "label": "Sq {0}".format(team_id + 1),
                    "color": TEAM_COLORS[team_id],
                    "total": player_scores.get(player.name, {}).get("total", 0),
                    "sweeps": player.sweeps,
                    "cards": len(player.captured),
                }
            )
        return rows

    def _get_player_team_meta(self, player):
        if self.engine.num_players == 4 and player.team is not None:
            return "Squadra {0}".format(player.team + 1), TEAM_COLORS[player.team]

        team_id = player.id if player.id in TEAM_COLORS else 0
        return "Squadra {0}".format(team_id + 1), TEAM_COLORS[team_id]

    def _draw_menu_button(self, renderer, rect: pygame.Rect, mouse_pos) -> None:
        hovered = rect.collidepoint(mouse_pos)
        self._draw_glass_panel(
            renderer,
            rect,
            (36, 55, 88),
            HIGHLIGHT_COLOR if hovered or self.menu_open else (106, 144, 194),
            alpha=170,
        )
        renderer.draw_text("Menu", rect.center, size=17, color=TEXT_COLOR, bold=True, align="center")

    def _draw_menu_overlay(self, renderer, rect: pygame.Rect, mouse_pos) -> None:
        dimmer = pygame.Surface(renderer.surface.get_size(), pygame.SRCALPHA)
        dimmer.fill((0, 0, 0, 132))
        renderer.surface.blit(dimmer, (0, 0))

        self._draw_glass_panel(renderer, rect, PANEL_COLOR, HIGHLIGHT_COLOR, alpha=224)
        renderer.draw_text("Menu partita", (rect.centerx, rect.top + 24), size=30, bold=True, align="center")
        renderer.draw_text("La partita e in pausa", (rect.centerx, rect.top + 56), size=16, color=TEXT_DIM_COLOR, align="center")

        difficulty_labels = {
            "easy": "Facile",
            "normal": "Normale",
            "expert": "Esperto",
            "adaptive": "Adattivo",
        }
        difficulty_text = "Difficolta: {0}".format(difficulty_labels.get(self.settings["difficulty"], self.settings["difficulty"]))
        visibility_text = "Visibilita: {0}".format("Completa" if self.settings["show_all_cards"] else "Nascosta")

        button_gap = 18
        row_width = rect.width - 96
        button_width = int((row_width - button_gap) / 2)
        left_x = rect.left + 48

        row1_y = rect.top + 96
        row2_y = row1_y + 86
        row3_y = row2_y + 86

        self.menu_buttons = {}
        row1 = {
            "difficulty": pygame.Rect(left_x, row1_y, button_width, 68),
            "toggle_cards": pygame.Rect(left_x + button_width + button_gap, row1_y, button_width, 68),
        }
        row2 = {
            "resume": pygame.Rect(left_x, row2_y, button_width, 68),
            "log": pygame.Rect(left_x + button_width + button_gap, row2_y, button_width, 68),
        }
        row3 = {
            "quit": pygame.Rect(left_x, row3_y, button_width, 68),
            "new_game": pygame.Rect(left_x + button_width + button_gap, row3_y, button_width, 68),
        }

        self.menu_buttons["difficulty"] = renderer.draw_button(
            difficulty_text,
            row1["difficulty"],
            hovered=row1["difficulty"].collidepoint(mouse_pos),
            tone="accent",
            font_size=18,
        )
        self.menu_buttons["toggle_cards"] = renderer.draw_button(
            visibility_text,
            row1["toggle_cards"],
            hovered=row1["toggle_cards"].collidepoint(mouse_pos),
            tone="neutral",
            font_size=18,
        )
        self.menu_buttons["resume"] = renderer.draw_button(
            "Continua partita",
            row2["resume"],
            hovered=row2["resume"].collidepoint(mouse_pos),
            tone="success",
            font_size=18,
        )
        self.menu_buttons["log"] = renderer.draw_button(
            "Log Partita",
            row2["log"],
            hovered=row2["log"].collidepoint(mouse_pos),
            tone="warning",
            font_size=18,
        )
        self.menu_buttons["quit"] = renderer.draw_button(
            "Esci",
            row3["quit"],
            hovered=row3["quit"].collidepoint(mouse_pos),
            tone="danger",
            font_size=18,
        )
        self.menu_buttons["new_game"] = renderer.draw_button(
            "Nuova partita",
            row3["new_game"],
            hovered=row3["new_game"].collidepoint(mouse_pos),
            tone="warning",
            font_size=18,
        )

    def _draw_log_overlay(self, renderer) -> None:
        if self.log_rect is None:
            return

        self._draw_glass_panel(renderer, self.log_rect, PANEL_COLOR, (120, 161, 220), alpha=216)
        self.log_header_rect = pygame.Rect(self.log_rect.left, self.log_rect.top, self.log_rect.width, 34)
        renderer.draw_text("Debug Log", (self.log_header_rect.left + 12, self.log_header_rect.top + 8), size=17, bold=True)
        renderer.draw_text("F12", (self.log_header_rect.right - 12, self.log_header_rect.top + 8), size=13, color=TEXT_DIM_COLOR, align="topright")

        line_area = self.log_rect.inflate(-16, -50)
        y = line_area.top
        for message in self.log_messages[-12:]:
            if y > line_area.bottom - 20:
                break
            row = renderer.draw_text(message, (line_area.left, y), size=15, color=TEXT_DIM_COLOR)
            y = row.bottom + 6

    def _ensure_log_rect(self, width: int, height: int) -> None:
        if self.log_rect is None:
            self.log_rect = pygame.Rect(width - 388, height - 286, 360, 250)
        self._clamp_log_rect()

    def _clamp_log_rect(self) -> None:
        if self.log_rect is None:
            return
        surface = self.app.renderer.surface
        width, height = surface.get_size()
        self.log_rect.x = max(12, min(self.log_rect.x, width - self.log_rect.width - 12))
        self.log_rect.y = max(12, min(self.log_rect.y, height - self.log_rect.height - 12))

    def _draw_glass_panel(self, renderer, rect: pygame.Rect, color, border, alpha: int = 180) -> None:
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        fill = (color[0], color[1], color[2], alpha)
        pygame.draw.rect(panel, fill, panel.get_rect(), border_radius=18)
        pygame.draw.rect(panel, border, panel.get_rect(), width=2, border_radius=18)
        renderer.surface.blit(panel, rect.topleft)

    def _clamp(self, value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))

    def _build_player_label_surface(self, renderer, player_name: str, team_label: str, team_color, current: bool) -> pygame.Surface:
        name_font = renderer.assets.get_font(19, bold=True)
        team_font = renderer.assets.get_font(14, bold=False)
        name_surface = name_font.render(player_name, True, team_color)
        team_surface = team_font.render(team_label, True, team_color)

        line_gap = 4
        padding_x = 18
        padding_y = 12

        text_block_rect = pygame.Rect(
            0,
            0,
            max(name_surface.get_width(), team_surface.get_width()),
            name_surface.get_height() + line_gap + team_surface.get_height(),
        )
        box_rect = text_block_rect.inflate(padding_x * 2, padding_y * 2)
        surface = pygame.Surface(box_rect.size, pygame.SRCALPHA)

        fill = (PANEL_ALT_COLOR[0], PANEL_ALT_COLOR[1], PANEL_ALT_COLOR[2], 194)
        pygame.draw.rect(surface, fill, surface.get_rect())
        pygame.draw.rect(
            surface,
            PLAYER_FRAME_ACTIVE_COLOR if current else PLAYER_FRAME_IDLE_COLOR,
            surface.get_rect(),
            width=6 if current else 2,
        )

        text_block_rect.center = surface.get_rect().center
        name_rect = name_surface.get_rect(midtop=(text_block_rect.centerx, text_block_rect.top))
        team_rect = team_surface.get_rect(midtop=(text_block_rect.centerx, name_rect.bottom + line_gap))
        surface.blit(name_surface, name_rect)
        surface.blit(team_surface, team_rect)
        return surface

    def _get_all_hand_rect_maps(self, layout):
        rect_maps = {}
        for player in self.engine.players:
            side = self._get_player_side(player.id)
            if side == "bottom":
                current_turn = self.engine.game_active and self.engine.get_current_player().id == player.id and not self.menu_open
                rect_maps[player.id] = self._get_horizontal_hand_rects(
                    layout["bottom_player_rect"],
                    player.hand,
                    CARD_SIZE_HAND,
                    34,
                    82,
                    bottom_padding=8,
                    lift=10 if current_turn else 0,
                )
            elif side == "top":
                rect_maps[player.id] = self._get_horizontal_hand_rects(
                    layout["top_player_rect"],
                    player.hand,
                    CARD_SIZE_SMALL,
                    18,
                    44,
                    bottom_padding=2,
                    lift=0,
                )
            else:
                player_rect = layout["left_player_rect"] if side == "left" else layout["right_player_rect"]
                rect_maps[player.id] = self._get_vertical_hand_rects(player_rect, player.hand, CARD_SIZE_SMALL)
        return rect_maps

    def _get_horizontal_hand_rects(self, rect: pygame.Rect, cards, card_size, spacing_min: int, spacing_max: int, bottom_padding: int, lift: int):
        rect_map = {}
        if not cards:
            return rect_map

        card_width, card_height = card_size
        spacing = max(spacing_min, min(spacing_max, (rect.width - card_width) // max(len(cards), 1)))
        total_width = card_width + (spacing * (len(cards) - 1))
        start_x = rect.centerx - (total_width // 2)
        y = rect.bottom - card_height - bottom_padding - lift
        for index, card in enumerate(cards):
            rect_map[card] = pygame.Rect(start_x + (index * spacing), y, card_width, card_height)
        return rect_map

    def _get_vertical_hand_rects(self, rect: pygame.Rect, cards, card_size):
        rect_map = {}
        if not cards:
            return rect_map

        rotated_width = card_size[1]
        rotated_height = card_size[0]
        spacing = max(28, min(56, (rect.height - rotated_height) // max(len(cards), 1)))
        total_height = rotated_height + (spacing * (len(cards) - 1))
        start_y = rect.centery - (total_height // 2)
        x = rect.centerx - (rotated_width // 2)
        for index, card in enumerate(cards):
            rect_map[card] = pygame.Rect(x, start_y + (index * spacing), rotated_width, rotated_height)
        return rect_map

    def _get_table_card_rects(self, table_rect: pygame.Rect, cards):
        rect_map = {}
        if not cards:
            return rect_map

        card_width, card_height = CARD_SIZE_TABLE
        spacing = max(18, min(92, (table_rect.width - card_width) // max(len(cards), 1)))
        total_width = card_width + (spacing * (len(cards) - 1))
        start_x = table_rect.centerx - (total_width // 2)
        y = table_rect.centery - (card_height // 2)
        for index, card in enumerate(cards):
            rect_map[card] = pygame.Rect(start_x + (index * spacing), y, card_width, card_height)
        return rect_map

    def _get_table_stack_rect(self, table_rect: pygame.Rect, index: int, total_cards: int) -> pygame.Rect:
        spread = min(14, max(4, total_cards * 2))
        start_x = table_rect.centerx - (CARD_SIZE_TABLE[0] // 2) - ((total_cards - 1) * spread // 2)
        start_y = table_rect.centery - (CARD_SIZE_TABLE[1] // 2) - ((total_cards - 1) * spread // 3)
        return pygame.Rect(start_x + (index * spread), start_y + (index * max(3, spread // 2)), CARD_SIZE_TABLE[0], CARD_SIZE_TABLE[1])

    def _get_default_capture_target(self, table_rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(table_rect.right - CARD_SIZE_SMALL[0], table_rect.top, CARD_SIZE_SMALL[0], CARD_SIZE_SMALL[1])

    def _get_hand_card_rect(self, player_id: int, card):
        return self.card_position_map.get("hands", {}).get(player_id, {}).get(card)

    def _get_player_side(self, player_id: int) -> str:
        if player_id == 0:
            return "bottom"
        if self.engine.num_players == 2:
            return "top"
        if player_id == 1:
            return "left"
        if player_id == 2:
            return "top"
        return "right"

    def _get_player_angle(self, player_id: int) -> int:
        side = self._get_player_side(player_id)
        if side == "left":
            return 90
        if side == "right":
            return 270
        return 0

    def _is_face_up_player(self, player) -> bool:
        return player.is_human or self.settings["show_all_cards"]
