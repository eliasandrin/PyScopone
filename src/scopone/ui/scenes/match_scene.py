import pygame

from scopone.ai.strategies import get_ai_strategy
from scopone.config.game import DEFAULT_PLAYER_NAMES, INITIAL_HAND_CARDS, SIMBOLI
from scopone.config.ui import (
    AI_THINKING_DELAY_MS,
    CARD_SIZE_HAND,
    CARD_SIZE_SMALL,
    CARD_SIZE_TABLE,
    FONT_NAME,
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
CAPTURE_HOLD_DELAY = 0.65
CAPTURE_CARD_DURATION = 0.90
CAPTURE_ACTIVE_RAISE = 20
CAPTURE_PILE_GAP = 40
CAPTURE_PILE_STACK_STEP = 3
CAPTURE_PILE_BUMP_DURATION = 0.10
CAPTURE_PILE_BUMP_SCALE = 1.05


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
        self.audio_button_rect = pygame.Rect(0, 0, 0, 0)
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
        self.capture_pile_rects = {}
        self.capture_pile_bump = {0: 0.0, 1: 0.0}
        self.visual_capture_counts = {0: 0, 1: 0}
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
        self.capture_pile_rects = {}
        self.capture_pile_bump = {0: 0.0, 1: 0.0}
        self.visual_capture_counts = {0: 0, 1: 0}
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

        if self.audio_button_rect.collidepoint(event.pos):
            self.app.toggle_mute()
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
                self._return_to_setup()
            return

    def _return_to_setup(self) -> None:
        self.menu_open = False
        self.log_visible = False
        self.log_dragging = False
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self.result_dispatched = False
        self.animations.clear()
        self.card_hitboxes = []
        self.card_position_map = {"hands": {}, "table": {}}
        self.capture_pile_targets = {}
        self.capture_pile_rects = {}
        self.capture_pile_bump = {0: 0.0, 1: 0.0}
        self.visual_capture_counts = {0: 0, 1: 0}
        self.last_layout = None
        self.engine = None
        self.app.show_setup()

    def _cycle_difficulty(self) -> None:
        difficulties = ["divertimento", "normale", "esperto"]
        current = difficulties.index(self.settings["difficulty"]) if self.settings["difficulty"] in difficulties else 1
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
        for team_id in list(self.capture_pile_bump.keys()):
            self.capture_pile_bump[team_id] = max(0.0, self.capture_pile_bump[team_id] - dt)
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
        captured_rects = self._get_table_source_rects(captured_cards)
        if not self.engine.play_card(current_player.id, card):
            self._append_log("Mossa non valida.")
            return

        self._append_log("Tu giochi {0}".format(self._format_card(card)))
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self._queue_move_sequence(current_player, card, source_rect, captured_cards, captured_rects, self.engine.last_move_result)

    def _play_ai_turn(self) -> None:
        assert self.engine is not None
        current_player = self.engine.get_current_player()
        strategy = get_ai_strategy(self.settings["difficulty"])
        selected_card = strategy.choose_card(
            current_player.hand,
            self.engine.table,
            player_scores=self._build_ai_player_scores(current_player),
            seen_cards=self.engine.seen_cards,
        )
        if selected_card is None:
            return

        source_rect = self._get_hand_card_rect(current_player.id, selected_card)
        captured_cards = self._preview_captured_cards(selected_card)
        captured_rects = self._get_table_source_rects(captured_cards)
        self.engine.play_card(current_player.id, selected_card)
        self._append_log("{0} gioca {1}".format(current_player.name, self._format_card(selected_card)))
        self._append_log("AI: {0}".format(strategy.get_last_decision_reason()))
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self._queue_move_sequence(current_player, selected_card, source_rect, captured_cards, captured_rects, self.engine.last_move_result)

    def _build_ai_player_scores(self, player) -> dict:
        team_captured = list(player.captured)
        if self.engine.num_players == 4 and player.team is not None:
            team_captured = []
            for teammate in self.engine.players:
                if teammate.team == player.team:
                    team_captured.extend(teammate.captured)
        return {"team_captured": team_captured}

    def _queue_move_sequence(self, player, card, source_rect, captured_cards, captured_rects, move_result) -> None:
        # Nasconde subitissimo le nuove carte ri-distribuite prima del volo animato della carta giocata.
        if move_result is not None and move_result.get("restocked"):
            self._prepare_restock_visibility()

        if source_rect is None or self.last_layout is None or move_result is None:
            self._after_move_animations(move_result)
            return

        start_angle = self._get_player_angle(player.id)
        table_card_size = self.last_layout["table_card_size"]
        if captured_cards:
            target_rect = self._get_table_stack_rect(
                self.last_layout["table_rect"],
                0,
                len(captured_cards) + 1,
                table_card_size,
            ).move(0, -CAPTURE_ACTIVE_RAISE)
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
                    on_complete=lambda: self._queue_capture_sequence(player.id, card, captured_cards, captured_rects, target_rect, move_result),
                    layer=3,
                )
            )
            return

        self.hidden_table_cards.add(card)
        table_rects = self._get_table_card_rects(
            self.last_layout["table_rect"],
            move_result["table_cards_after"],
            table_card_size,
        )
        target_rect = table_rects.get(card, self._get_table_stack_rect(self.last_layout["table_rect"], 0, 1, table_card_size))
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

    def _queue_capture_sequence(self, player_id: int, played_card, captured_cards, captured_rects, played_rect, move_result) -> None:
        if self.last_layout is None:
            self._after_move_animations(move_result)
            return

        cards_to_collect = [played_card] + list(captured_cards)
        if not cards_to_collect:
            self._after_move_animations(move_result)
            return

        remaining = {"count": len(cards_to_collect)}
        table_card_size = self.last_layout["table_card_size"]
        small_card_size = self.last_layout["small_card_size"]
        team_id = self._get_capture_team_id(player_id)
        capture_center = self.capture_pile_targets.get(
            team_id,
            self._get_default_capture_target(self.last_layout["table_rect"], small_card_size).center,
        )
        vertical_target = self._is_vertical_capture_target(team_id)

        def handle_complete():
            remaining["count"] -= 1
            if remaining["count"] <= 0:
                # Update visual pile state only when the full capture animation has landed.
                self.visual_capture_counts[team_id] = self.visual_capture_counts.get(team_id, 0) + len(cards_to_collect)
                self.app.audio.play("capture")
                self.capture_pile_bump[team_id] = CAPTURE_PILE_BUMP_DURATION
                self._after_move_animations(move_result)

        for index, current_card in enumerate(cards_to_collect):
            if index == 0:
                start_rect = played_rect
            else:
                start_rect = captured_rects.get(
                    current_card,
                    self._get_table_stack_rect(self.last_layout["table_rect"], index, len(cards_to_collect), table_card_size),
                )
            target_rect = start_rect.copy()
            target_rect.center = capture_center
            self.animations.add(
                CardTween(
                    card=current_card,
                    start_rect=start_rect,
                    target_rect=target_rect,
                    duration=CAPTURE_CARD_DURATION,
                    face_up=True,
                    start_angle=0,
                    target_angle=90 if vertical_target else 0,
                    delay=CAPTURE_HOLD_DELAY,
                    on_complete=handle_complete,
                    layer=5 if index == 0 else 4,
                    easing="ease_out",
                    shadow=index == 0,
                    shadow_alpha=96 if index == 0 else 0,
                    interpolate_size=False,
                )
            )

    def _after_move_animations(self, move_result) -> None:
        if move_result is None:
            return

        if move_result.get("restocked") and self.last_layout is not None:
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

    def _get_table_source_rects(self, cards):
        table_rects = self.card_position_map.get("table", {})
        return dict((card, table_rects.get(card)) for card in cards if table_rects.get(card) is not None)

    def _format_card(self, card) -> str:
        return "{0}{1}".format(card[0], SIMBOLI[card[1]])

    def render(self, renderer) -> None:
        assert self.engine is not None

        draw_prismatic_background(renderer.surface, variant="game")
        width, height = renderer.surface.get_size()
        layout = self._calculate_layout(width, height)
        self.last_layout = layout
        self.capture_pile_targets = layout["capture_targets"]
        self.capture_pile_rects = layout["capture_piles"]
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
        self.audio_button_rect = layout["audio_button"]

        self._draw_table(renderer, layout["table_rect"])
        self._draw_deck_anchor(renderer, layout["deck_rect"])
        self._draw_table_cards(renderer, layout["table_rect"])
        self._draw_live_score_panel(renderer, layout["score_panel"])
        self._draw_menu_button(renderer, layout["menu_button"], mouse_pos)
        renderer.draw_audio_toggle(
            layout["audio_button"],
            muted=self.app.is_muted,
            hovered=layout["audio_button"].collidepoint(mouse_pos),
        )
        self._draw_players(renderer, layout)
        self.draw_captured_piles(renderer.surface)
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
            table_rects = self._get_table_card_rects(layout["table_rect"], self.engine.table, layout["table_card_size"])
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
        ui_scale = self._clamp_float(min(width / 1920.0, height / 1080.0), 0.85, 1.4)
        card_presence_scale = self._clamp_float(ui_scale * 1.14, 0.95, 1.6)
        hand_card_size = self._scale_card_size(CARD_SIZE_HAND, card_presence_scale, minimum=(100, 150))
        table_card_size = self._scale_card_size(CARD_SIZE_TABLE, card_presence_scale, minimum=(116, 174))
        small_card_size = self._scale_card_size(CARD_SIZE_SMALL, card_presence_scale, minimum=(78, 117))

        min_gap = self._clamp(int(min(width, height) * 0.015), 10, 24)

        bottom_label_rect = self._estimate_player_label_rect(0, hand_card_size)
        top_player_id = 1 if self.engine.num_players == 2 else 2
        top_label_rect_est = self._estimate_player_label_rect(top_player_id, hand_card_size)
        left_label_rect_est = self._estimate_player_label_rect(1, hand_card_size)
        right_label_rect_est = self._estimate_player_label_rect(3, hand_card_size) if self.engine.num_players == 4 else left_label_rect_est

        bottom_cards_block_h = hand_card_size[1] + 8
        top_cards_block_h = small_card_size[1] + 2
        left_cards_block_w = small_card_size[1]
        right_cards_block_w = small_card_size[1]
        left_label_block_w = left_label_rect_est.height
        right_label_block_w = right_label_rect_est.height

        reserve_top = (top_cards_block_h + top_label_rect_est.height + (min_gap * 3))
        reserve_bottom = (bottom_cards_block_h + bottom_label_rect.height + (min_gap * 3))
        reserve_left = (left_cards_block_w + left_label_block_w + (min_gap * 3))
        reserve_right = reserve_left if self.engine.num_players == 2 else (right_cards_block_w + right_label_block_w + (min_gap * 3))

        min_table_width = self._clamp(int(width * 0.38), 520, 980)
        min_table_height = self._clamp(int(height * 0.30), 220, 540)

        overflow_x = max(0, (reserve_left + reserve_right + min_table_width) - width)
        overflow_y = max(0, (reserve_top + reserve_bottom + min_table_height) - height)

        if overflow_x:
            reduce_each = int((overflow_x + 1) / 2)
            reserve_left = max(min_gap * 2 + left_cards_block_w + left_label_block_w, reserve_left - reduce_each)
            reserve_right = max(min_gap * 2 + right_cards_block_w + right_label_block_w, reserve_right - reduce_each)

        if overflow_y:
            reduce_each = int((overflow_y + 1) / 2)
            reserve_top = max(min_gap * 2 + top_cards_block_h + top_label_rect_est.height, reserve_top - reduce_each)
            reserve_bottom = max(min_gap * 2 + bottom_cards_block_h + bottom_label_rect.height, reserve_bottom - reduce_each)

        table_rect = pygame.Rect(
            reserve_left,
            reserve_top,
            max(min_table_width, width - reserve_left - reserve_right),
            max(min_table_height, height - reserve_top - reserve_bottom),
        )

        score_panel = pygame.Rect(
            min_gap,
            min_gap,
            self._clamp(int(322 * ui_scale), 312, 428),
            self._clamp(int(132 * ui_scale), 126, 176),
        )
        menu_button = pygame.Rect(
            width - min_gap - self._clamp(int(92 * ui_scale), 90, 124),
            min_gap,
            self._clamp(int(92 * ui_scale), 90, 124),
            self._clamp(int(38 * ui_scale), 36, 50),
        )
        audio_button = pygame.Rect(menu_button.left - 44, min_gap + 1, 36, 36)

        available_top_y = table_rect.top
        gap_top = self._equidistant_gap(available_top_y, top_label_rect_est.height, top_cards_block_h, min_gap)
        top_player_rect = pygame.Rect(
            table_rect.left,
            gap_top,
            table_rect.width,
            top_cards_block_h,
        )
        top_label_rect = pygame.Rect(
            table_rect.centerx - (top_label_rect_est.width // 2),
            top_player_rect.bottom + gap_top,
            top_label_rect_est.width,
            top_label_rect_est.height,
        )

        available_bottom_y = height - table_rect.bottom
        gap_bottom = self._equidistant_gap(available_bottom_y, bottom_label_rect.height, bottom_cards_block_h, min_gap)
        bottom_label_rect = pygame.Rect(
            table_rect.centerx - (bottom_label_rect.width // 2),
            table_rect.bottom + gap_bottom,
            bottom_label_rect.width,
            bottom_label_rect.height,
        )
        bottom_player_rect = pygame.Rect(
            table_rect.left,
            bottom_label_rect.bottom + gap_bottom,
            table_rect.width,
            bottom_cards_block_h,
        )

        available_left_x = table_rect.left
        gap_left = self._equidistant_gap(available_left_x, left_label_block_w, left_cards_block_w, min_gap)
        left_player_rect = pygame.Rect(
            gap_left,
            table_rect.centery - (table_rect.height // 2),
            left_cards_block_w,
            table_rect.height,
        )
        left_label_rect = pygame.Rect(
            left_player_rect.right + gap_left,
            table_rect.centery - (left_label_rect_est.width // 2),
            left_label_block_w,
            left_label_rect_est.width,
        )

        available_right_x = width - table_rect.right
        gap_right = self._equidistant_gap(available_right_x, right_label_block_w, right_cards_block_w, min_gap)
        right_label_rect = pygame.Rect(
            table_rect.right + gap_right,
            table_rect.centery - (right_label_rect_est.width // 2),
            right_label_block_w,
            right_label_rect_est.width,
        )
        right_player_rect = pygame.Rect(
            right_label_rect.right + gap_right,
            table_rect.centery - (table_rect.height // 2),
            right_cards_block_w,
            table_rect.height,
        )

        deck_rect = pygame.Rect(
            table_rect.right - small_card_size[0] - 22,
            table_rect.centery - (small_card_size[1] // 2),
            small_card_size[0],
            small_card_size[1],
        )
        capture_piles = self._build_capture_pile_layout(
            width,
            height,
            bottom_player_rect,
            top_player_rect,
            right_player_rect,
            hand_card_size,
            small_card_size,
        )
        capture_targets = dict((team_id, pile_rect.center) for team_id, pile_rect in capture_piles.items())
        overlay_rect = pygame.Rect(width // 2 - 340, height // 2 - 180, 680, 360)

        return {
            "table_rect": table_rect,
            "deck_rect": deck_rect,
            "capture_piles": capture_piles,
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
            "audio_button": audio_button,
            "overlay_rect": overlay_rect,
            "hand_card_size": hand_card_size,
            "table_card_size": table_card_size,
            "small_card_size": small_card_size,
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

    def _should_draw_deck_anchor(self) -> bool:
        if self.engine.num_players != 2:
            return False
        if self.engine.deck_remaining:
            return True
        return any(self.hidden_hand_cards.get(player.id) for player in self.engine.players)

    def _draw_deck_anchor(self, renderer, deck_rect: pygame.Rect) -> None:
        # Draw the deck anchor only in 2-player mode.
        # Using animations.has_active() here caused a ghost card-back during play tweens.
        if self._should_draw_deck_anchor():
            renderer.draw_card((1, "Denari"), deck_rect, face_up=False)

    def _draw_table_cards(self, renderer, table_rect: pygame.Rect) -> None:
        table_card_size = self.last_layout["table_card_size"] if self.last_layout is not None else CARD_SIZE_TABLE
        rect_map = self._get_table_card_rects(table_rect, self.engine.table, table_card_size)
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
        panel_scale = self._clamp_float(rect.width / 322.0, 0.95, 1.35)
        title_size = self._clamp(int(20 * panel_scale), 18, 24)
        header_size = self._clamp(int(14 * panel_scale), 13, 18)
        row_label_size = self._clamp(int(17 * panel_scale), 15, 20)
        row_value_size = self._clamp(int(16 * panel_scale), 14, 19)
        total_size = self._clamp(int(18 * panel_scale), 16, 22)
        row_gap = self._clamp(int(30 * panel_scale), 28, 36)

        self._draw_glass_panel(renderer, rect, PANEL_COLOR, HIGHLIGHT_COLOR, alpha=198)
        renderer.draw_text("Live", (rect.left + 14, rect.top + 10), size=title_size, bold=True)

        headers = [
            ("Car", rect.left + int(92 * panel_scale)),
            ("Den", rect.left + int(126 * panel_scale)),
            ("Pri", rect.left + int(160 * panel_scale)),
            ("7B", rect.left + int(194 * panel_scale)),
            ("Scp", rect.left + int(228 * panel_scale)),
            ("TOT", rect.left + int(286 * panel_scale)),
        ]
        for label, x in headers:
            renderer.draw_text(label, (x, rect.top + 16), size=header_size, color=TEXT_DIM_COLOR, align="midtop")

        rows = self._get_live_team_rows()
        y = rect.top + int(52 * panel_scale)
        for row in rows:
            renderer.draw_text(row["label"], (rect.left + 16, y), size=row_label_size, color=row["color"], bold=True)
            renderer.draw_text(str(row["cards"]), (rect.left + int(92 * panel_scale), y), size=row_value_size, color=TEXT_COLOR, align="midtop")
            renderer.draw_text(str(row["coins"]), (rect.left + int(126 * panel_scale), y), size=row_value_size, color=TEXT_COLOR, align="midtop")
            renderer.draw_text(str(row["primiera"]), (rect.left + int(160 * panel_scale), y), size=row_value_size, color=TEXT_COLOR, align="midtop")
            renderer.draw_text(str(row["settebello"]), (rect.left + int(194 * panel_scale), y), size=row_value_size, color=TEXT_COLOR, align="midtop")
            renderer.draw_text(str(row["sweeps"]), (rect.left + int(228 * panel_scale), y), size=row_value_size, color=TEXT_COLOR, align="midtop")
            renderer.draw_text(str(row["total"]), (rect.left + int(286 * panel_scale), y), size=total_size, color=TEXT_COLOR, bold=True, align="midtop")
            y += row_gap

    def _get_live_team_rows(self):
        rows = []
        show_final_total = not self.engine.game_active

        if self.engine.num_players == 4:
            final_scores = {
                score["team"]: score
                for score in ScoringEngine.calculate_final_scores(self.engine.players)
            }
            for team_id in (0, 1):
                score = final_scores.get(team_id, {})
                sweeps_value = score.get("sweeps", 0)
                rows.append(
                    {
                        "label": "Sq {0}".format(team_id + 1),
                        "color": TEAM_COLORS[team_id],
                        "cards": score.get("captured_cards", 0),
                        "coins": score.get("coins", 0),
                        "primiera": score.get("primiera_value", 0),
                        "settebello": 1 if score.get("has_settebello") else 0,
                        "sweeps": sweeps_value,
                        "total": score.get("total", 0) if show_final_total else sweeps_value,
                    }
                )
            return rows

        player_scores = {
            score["player"]: score
            for score in ScoringEngine.calculate_final_scores(self.engine.players)
        }
        for player in self.engine.players[:2]:
            team_id = player.id
            score = player_scores.get(player.name, {})
            sweeps_value = score.get("sweeps", 0)
            rows.append(
                {
                    "label": "Sq {0}".format(team_id + 1),
                    "color": TEAM_COLORS[team_id],
                    "cards": score.get("captured_cards", 0),
                    "coins": score.get("coins", 0),
                    "primiera": score.get("primiera_value", 0),
                    "settebello": 1 if score.get("has_settebello") else 0,
                    "sweeps": sweeps_value,
                    "total": score.get("total", 0) if show_final_total else sweeps_value,
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
            "divertimento": "Divertimento",
            "normale": "Normale",
            "esperto": "Esperto",
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

    def _clamp_float(self, value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    def _scale_card_size(self, base_size, scale: float, minimum) -> tuple:
        return (
            self._clamp(int(base_size[0] * scale), minimum[0], int(base_size[0] * 1.6)),
            self._clamp(int(base_size[1] * scale), minimum[1], int(base_size[1] * 1.6)),
        )

    def _equidistant_gap(self, available_space: int, text_extent: int, cards_extent: int, minimum_gap: int) -> int:
        gap = int((available_space - text_extent - cards_extent) / 3)
        return max(minimum_gap, gap)

    def _estimate_player_label_rect(self, player_id: int, hand_card_size) -> pygame.Rect:
        player = None
        for current in self.engine.players:
            if current.id == player_id:
                player = current
                break

        if player is None:
            label_text = "Giocatore"
            team_text = "Squadra"
        else:
            team_text, _ = self._get_player_team_meta(player)
            label_text = player.name

        label_scale = self._clamp_float(hand_card_size[0] / float(CARD_SIZE_HAND[0]), 0.95, 1.3)
        name_size = self._clamp(int(22 * label_scale), 20, 28)
        team_size = self._clamp(int(16 * label_scale), 15, 21)
        line_gap = self._clamp(int(5 * label_scale), 4, 8)
        padding_x = self._clamp(int(20 * label_scale), 18, 28)
        padding_y = self._clamp(int(13 * label_scale), 12, 20)

        name_font = pygame.font.SysFont(FONT_NAME, name_size, bold=True)
        team_font = pygame.font.SysFont(FONT_NAME, team_size, bold=False)
        name_width, name_height = name_font.size(label_text)
        team_width, team_height = team_font.size(team_text)

        width = max(name_width, team_width) + (padding_x * 2)
        height = name_height + line_gap + team_height + (padding_y * 2)
        return pygame.Rect(0, 0, width, height)

    def _build_player_label_surface(self, renderer, player_name: str, team_label: str, team_color, current: bool) -> pygame.Surface:
        label_scale = 1.0
        if self.last_layout is not None:
            label_scale = self._clamp_float(self.last_layout["hand_card_size"][0] / float(CARD_SIZE_HAND[0]), 0.95, 1.3)

        name_size = self._clamp(int(22 * label_scale), 20, 28)
        team_size = self._clamp(int(16 * label_scale), 15, 21)

        name_font = renderer.assets.get_font(name_size, bold=True)
        team_font = renderer.assets.get_font(team_size, bold=False)
        name_surface = name_font.render(player_name, True, team_color)
        team_surface = team_font.render(team_label, True, team_color)

        line_gap = self._clamp(int(5 * label_scale), 4, 8)
        padding_x = self._clamp(int(20 * label_scale), 18, 28)
        padding_y = self._clamp(int(13 * label_scale), 12, 20)

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
        hand_card_size = layout["hand_card_size"]
        small_card_size = layout["small_card_size"]
        for player in self.engine.players:
            side = self._get_player_side(player.id)
            if side == "bottom":
                current_turn = self.engine.game_active and self.engine.get_current_player().id == player.id and not self.menu_open
                rect_maps[player.id] = self._get_horizontal_hand_rects(
                    layout["bottom_player_rect"],
                    player.hand,
                    hand_card_size,
                    40,
                    96,
                    bottom_padding=8,
                    lift=10 if current_turn else 0,
                )
            elif side == "top":
                rect_maps[player.id] = self._get_horizontal_hand_rects(
                    layout["top_player_rect"],
                    player.hand,
                    small_card_size,
                    22,
                    54,
                    bottom_padding=2,
                    lift=0,
                )
            else:
                player_rect = layout["left_player_rect"] if side == "left" else layout["right_player_rect"]
                rect_maps[player.id] = self._get_vertical_hand_rects(player_rect, player.hand, small_card_size)
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
        spacing = max(50, min(92, (rect.height - rotated_height) // max(len(cards), 1)))
        total_height = rotated_height + (spacing * (len(cards) - 1))
        start_y = rect.centery - (total_height // 2)
        x = rect.centerx - (rotated_width // 2)
        for index, card in enumerate(cards):
            rect_map[card] = pygame.Rect(x, start_y + (index * spacing), rotated_width, rotated_height)
        return rect_map

    def _get_table_card_rects(self, table_rect: pygame.Rect, cards, card_size):
        rect_map = {}
        if not cards:
            return rect_map

        card_width, card_height = card_size
        spacing = max(24, min(108, (table_rect.width - card_width) // max(len(cards), 1)))
        total_width = card_width + (spacing * (len(cards) - 1))
        start_x = table_rect.centerx - (total_width // 2)
        y = table_rect.centery - (card_height // 2)
        for index, card in enumerate(cards):
            rect_map[card] = pygame.Rect(start_x + (index * spacing), y, card_width, card_height)
        return rect_map

    def _get_table_stack_rect(self, table_rect: pygame.Rect, index: int, total_cards: int, card_size) -> pygame.Rect:
        card_width, card_height = card_size
        spread = min(14, max(4, total_cards * 2))
        start_x = table_rect.centerx - (card_width // 2) - ((total_cards - 1) * spread // 2)
        start_y = table_rect.centery - (card_height // 2) - ((total_cards - 1) * spread // 3)
        return pygame.Rect(start_x + (index * spread), start_y + (index * max(3, spread // 2)), card_width, card_height)

    def _build_capture_pile_layout(
        self,
        screen_width: int,
        screen_height: int,
        bottom_player_rect: pygame.Rect,
        top_player_rect: pygame.Rect,
        right_player_rect: pygame.Rect,
        hand_card_size,
        small_card_size,
    ):
        hand_slots = INITIAL_HAND_CARDS.get(self.engine.num_players, 9)
        pile_w, pile_h = small_card_size
        piles = {}

        tu_fixed_centery = bottom_player_rect.centery
        tu_hand_fixed_left = self._get_fixed_horizontal_hand_left(
            bottom_player_rect,
            hand_card_size,
            hand_slots,
            spacing_min=40,
            spacing_max=96,
        )
        team1_rect = pygame.Rect(0, 0, pile_w, pile_h)
        team1_rect.centery = tu_fixed_centery
        team1_rect.right = tu_hand_fixed_left - CAPTURE_PILE_GAP
        team1_rect = self._clamp_rect_inside_screen(team1_rect, screen_width, screen_height)
        piles[0] = team1_rect

        if self.engine.num_players == 4:
            ai3_fixed_centerx = right_player_rect.centerx
            ai3_hand_fixed_top = self._get_fixed_vertical_hand_top(
                right_player_rect,
                small_card_size,
                hand_slots,
            )
            team2_rect = pygame.Rect(0, 0, pile_h, pile_w)
            team2_rect.centerx = ai3_fixed_centerx
            team2_rect.bottom = ai3_hand_fixed_top - CAPTURE_PILE_GAP
            team2_rect = self._clamp_rect_inside_screen(team2_rect, screen_width, screen_height)
        else:
            ai1_fixed_centery = top_player_rect.centery
            ai1_hand_fixed_right = self._get_fixed_horizontal_hand_right(
                top_player_rect,
                small_card_size,
                hand_slots,
                spacing_min=22,
                spacing_max=54,
            )
            team2_rect = pygame.Rect(0, 0, pile_w, pile_h)
            team2_rect.centery = ai1_fixed_centery
            team2_rect.left = ai1_hand_fixed_right + CAPTURE_PILE_GAP
            team2_rect = self._clamp_rect_inside_screen(team2_rect, screen_width, screen_height)
        piles[1] = team2_rect

        return piles

    def draw_captured_piles(self, screen) -> None:
        if self.last_layout is None:
            return

        small_card_size = self.last_layout["small_card_size"]
        card_back = self.app.assets.get_card_back_surface(small_card_size)
        for team_id in (0, 1):
            captured_count = self.visual_capture_counts.get(team_id, 0)
            if captured_count <= 0:
                continue

            pile_rect = self.capture_pile_rects.get(team_id)
            if pile_rect is None:
                continue

            pile_surface = card_back
            if self._is_vertical_capture_target(team_id):
                pile_surface = pygame.transform.rotate(card_back, 90)

            render_rect = pile_surface.get_rect(center=pile_rect.center)
            bump_remaining = self.capture_pile_bump.get(team_id, 0.0)
            if bump_remaining > 0.0:
                bump_factor = 1.0 + ((CAPTURE_PILE_BUMP_SCALE - 1.0) * (bump_remaining / CAPTURE_PILE_BUMP_DURATION))
                bumped_size = (
                    max(1, int(render_rect.width * bump_factor)),
                    max(1, int(render_rect.height * bump_factor)),
                )
                pile_surface = pygame.transform.smoothscale(pile_surface, bumped_size)
                render_rect = pile_surface.get_rect(center=render_rect.center)

            stack_layers = max(0, captured_count // CAPTURE_PILE_STACK_STEP)
            for layer in range(stack_layers, -1, -1):
                layer_pos = (render_rect.x + (layer * -1), render_rect.y + (layer * -2))
                screen.blit(pile_surface, layer_pos)

            label_y = render_rect.bottom + 8
            if self._is_vertical_capture_target(team_id):
                label_y = render_rect.top - 20
            self.app.renderer.draw_text(
                "Squadra {0}".format(team_id + 1),
                (render_rect.centerx, label_y),
                size=16,
                color=TEAM_COLORS[team_id],
                bold=True,
                align="midtop" if label_y >= render_rect.bottom else "midbottom",
            )

    def _get_capture_team_id(self, player_id: int) -> int:
        player = self.engine.players[player_id]
        if self.engine.num_players == 4 and player.team is not None:
            return player.team
        return player.id if player.id in (0, 1) else 0

    def _is_vertical_capture_target(self, team_id: int) -> bool:
        return self.engine.num_players == 4 and team_id == 1

    def _get_fixed_horizontal_hand_left(self, rect: pygame.Rect, card_size, slot_count: int, spacing_min: int, spacing_max: int) -> int:
        card_width = card_size[0]
        slots = max(1, slot_count)
        spacing = max(spacing_min, min(spacing_max, (rect.width - card_width) // slots))
        total_width = card_width + (spacing * (slots - 1))
        return rect.centerx - (total_width // 2)

    def _get_fixed_horizontal_hand_right(self, rect: pygame.Rect, card_size, slot_count: int, spacing_min: int, spacing_max: int) -> int:
        card_width = card_size[0]
        slots = max(1, slot_count)
        spacing = max(spacing_min, min(spacing_max, (rect.width - card_width) // slots))
        total_width = card_width + (spacing * (slots - 1))
        return rect.centerx + (total_width // 2)

    def _get_fixed_vertical_hand_top(self, rect: pygame.Rect, card_size, slot_count: int) -> int:
        rotated_height = card_size[0]
        slots = max(1, slot_count)
        spacing = max(50, min(92, (rect.height - rotated_height) // slots))
        total_height = rotated_height + (spacing * (slots - 1))
        return rect.centery - (total_height // 2)

    def _clamp_rect_inside_screen(self, rect: pygame.Rect, width: int, height: int, padding: int = 8) -> pygame.Rect:
        clamped = rect.copy()
        clamped.x = max(padding, min(clamped.x, width - clamped.width - padding))
        clamped.y = max(padding, min(clamped.y, height - clamped.height - padding))
        return clamped

    def _get_default_capture_target(self, table_rect: pygame.Rect, small_card_size) -> pygame.Rect:
        return pygame.Rect(table_rect.right - small_card_size[0], table_rect.top, small_card_size[0], small_card_size[1])

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
