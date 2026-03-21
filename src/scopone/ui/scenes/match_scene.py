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
from scopone.ui.backgrounds import draw_prismatic_background
from scopone.ui.scene_manager import Scene


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

    def _append_log(self, message: str) -> None:
        self.log_messages.append(message)
        if len(self.log_messages) > 36:
            self.log_messages = self.log_messages[-36:]

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
            new_x = event.pos[0] - self.log_drag_offset[0]
            new_y = event.pos[1] - self.log_drag_offset[1]
            self.log_rect.topleft = (new_x, new_y)
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
            elif action == "new_game":
                self._start_new_game()
            elif action == "quit":
                self.app.request_quit()
            return

    def _cycle_difficulty(self) -> None:
        difficulties = ["easy", "normal", "expert", "adaptive"]
        current = difficulties.index(self.settings["difficulty"])
        next_value = difficulties[(current + 1) % len(difficulties)]
        self.settings["difficulty"] = next_value
        self._append_log("Difficolta AI impostata su {0}.".format(next_value))

    def update(self, dt: float) -> None:
        if self.engine is None or self.result_dispatched:
            return

        if not self.engine.game_active:
            self.result_dispatched = True
            self.app.show_results(self.engine.final_scores, self.settings, self.log_messages)
            return

        if self.menu_open:
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
        if not self.engine.play_card(current_player.id, card):
            self._append_log("Mossa non valida.")
            return

        self._append_log("Tu giochi {0}".format(self._format_card(card)))
        if self.engine.game_active:
            self.engine.next_player()
        self.pending_ai_player_id = None
        self.ai_timer = 0.0

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

        self.engine.play_card(current_player.id, selected_card)
        self._append_log("{0} gioca {1}".format(current_player.name, self._format_card(selected_card)))
        self._append_log("AI: {0}".format(strategy.get_last_decision_reason()))
        if self.engine.game_active:
            self.engine.next_player()
        self.pending_ai_player_id = None
        self.ai_timer = 0.0

    def _format_card(self, card) -> str:
        return "{0}{1}".format(card[0], SIMBOLI[card[1]])

    def render(self, renderer) -> None:
        assert self.engine is not None

        draw_prismatic_background(renderer.surface, variant="game")
        width, height = renderer.surface.get_size()
        layout = self._calculate_layout(width, height)
        self._ensure_log_rect(width, height)
        mouse_pos = pygame.mouse.get_pos()

        self.card_hitboxes = []
        self.menu_button_rect = layout["menu_button"]

        self._draw_table(renderer, layout["table_rect"])
        self._draw_live_score_panel(renderer, layout["score_panel"])
        self._draw_menu_button(renderer, layout["menu_button"], mouse_pos)
        self._draw_players(renderer, layout)
        self._draw_table_cards(renderer, layout["table_rect"])
        self._draw_human_hand(renderer, layout["bottom_player_rect"])

        if self.log_visible:
            self._draw_log_overlay(renderer)

        if self.menu_open:
            self._draw_menu_overlay(renderer, layout["overlay_rect"], mouse_pos)

    def _calculate_layout(self, width: int, height: int):
        margin = self._clamp(int(min(width, height) * 0.018), 12, 26)
        top_band = self._clamp(int(height * 0.16), 110, 150)
        bottom_band = self._clamp(int(height * 0.24), 170, 230)
        side_band = self._clamp(int(width * 0.13), 120, 170)

        table_rect = pygame.Rect(
            side_band + (margin * 2),
            top_band + (margin * 2),
            width - ((side_band + (margin * 2)) * 2),
            height - top_band - bottom_band - (margin * 4),
        )
        top_player_rect = pygame.Rect(side_band + margin, margin + 8, width - ((side_band + margin) * 2), top_band - margin)
        bottom_player_rect = pygame.Rect(side_band + margin, height - bottom_band + 18, width - ((side_band + margin) * 2), bottom_band - 24)
        left_player_rect = pygame.Rect(margin, top_band + margin, side_band, height - top_band - bottom_band - (margin * 2))
        right_player_rect = pygame.Rect(width - side_band - margin, top_band + margin, side_band, height - top_band - bottom_band - (margin * 2))

        return {
            "table_rect": table_rect,
            "top_player_rect": top_player_rect,
            "bottom_player_rect": bottom_player_rect,
            "left_player_rect": left_player_rect,
            "right_player_rect": right_player_rect,
            "score_panel": pygame.Rect(margin, margin, 276, 122),
            "menu_button": pygame.Rect(width - margin - 92, margin, 92, 38),
            "overlay_rect": pygame.Rect(width // 2 - 320, height // 2 - 150, 640, 300),
        }

    def _draw_table(self, renderer, rect: pygame.Rect) -> None:
        table_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(table_surface, (14, 32, 68, 134), table_surface.get_rect(), border_radius=32)
        pygame.draw.rect(table_surface, (176, 214, 255, 72), table_surface.get_rect(), width=2, border_radius=32)
        pygame.draw.ellipse(
            table_surface,
            (199, 233, 255, 22),
            pygame.Rect(rect.width * 0.18, rect.height * 0.18, rect.width * 0.64, rect.height * 0.64),
        )
        renderer.surface.blit(table_surface, rect.topleft)
        renderer.draw_text("Tavolo", (rect.centerx, rect.top + 16), size=26, bold=True, align="center")

    def _draw_table_cards(self, renderer, table_rect: pygame.Rect) -> None:
        if not self.engine.table:
            renderer.draw_text("Tavolo vuoto", table_rect.center, size=22, color=TEXT_DIM_COLOR, align="center")
            return

        card_width, card_height = CARD_SIZE_TABLE
        max_spacing = max(18, min(110, (table_rect.width - card_width) // max(len(self.engine.table), 1)))
        total_width = card_width + (max_spacing * (len(self.engine.table) - 1))
        start_x = table_rect.centerx - (total_width // 2)
        y = table_rect.centery - (card_height // 2)
        for index, card in enumerate(self.engine.table):
            card_rect = pygame.Rect(start_x + (index * max_spacing), y, card_width, card_height)
            renderer.draw_card(card, card_rect, face_up=True)

    def _draw_players(self, renderer, layout) -> None:
        if self.engine.num_players == 2:
            self._draw_horizontal_ai_hand(renderer, self.engine.players[1], layout["top_player_rect"], top=True)
        else:
            self._draw_horizontal_ai_hand(renderer, self.engine.players[2], layout["top_player_rect"], top=True)
            self._draw_vertical_ai_hand(renderer, self.engine.players[1], layout["left_player_rect"], side="left")
            self._draw_vertical_ai_hand(renderer, self.engine.players[3], layout["right_player_rect"], side="right")

    def _draw_horizontal_ai_hand(self, renderer, player, rect: pygame.Rect, top: bool = False) -> None:
        self._draw_player_badge(renderer, player, (rect.centerx, rect.top + 10), align="midtop")

        if not player.hand:
            return

        card_width, card_height = CARD_SIZE_SMALL
        show_cards = self.settings["show_all_cards"]
        spacing = max(18, min(48, (rect.width - card_width) // max(len(player.hand), 1)))
        total_width = card_width + (spacing * (len(player.hand) - 1))
        start_x = rect.centerx - (total_width // 2)
        y = rect.bottom - card_height - 6
        for index, card in enumerate(player.hand):
            card_rect = pygame.Rect(start_x + (index * spacing), y, card_width, card_height)
            renderer.draw_card(card, card_rect, face_up=show_cards)

    def _draw_vertical_ai_hand(self, renderer, player, rect: pygame.Rect, side: str) -> None:
        badge_pos = (rect.centerx, rect.top + 12)
        self._draw_player_badge(renderer, player, badge_pos, align="midtop")

        if not player.hand:
            return

        rotated_width = CARD_SIZE_SMALL[1]
        rotated_height = CARD_SIZE_SMALL[0]
        show_cards = self.settings["show_all_cards"]
        spacing = max(16, min(34, (rect.height - rotated_height - 54) // max(len(player.hand), 1)))
        total_height = rotated_height + (spacing * (len(player.hand) - 1))
        start_y = rect.centery - (total_height // 2) + 20
        x = rect.centerx - (rotated_width // 2)
        angle = 90 if side == "left" else 270

        for index, card in enumerate(player.hand):
            card_rect = pygame.Rect(x, start_y + (index * spacing), rotated_width, rotated_height)
            renderer.draw_card(card, card_rect, face_up=show_cards, angle=angle)

    def _draw_human_hand(self, renderer, rect: pygame.Rect) -> None:
        human = self.engine.get_human_player()
        self._draw_player_badge(renderer, human, (rect.centerx, rect.top + 8), align="midtop")

        if not human.hand:
            renderer.draw_text("Mano vuota", rect.center, size=22, color=TEXT_DIM_COLOR, align="center")
            return

        card_width, card_height = CARD_SIZE_HAND
        spacing = max(32, min(88, (rect.width - card_width) // max(len(human.hand), 1)))
        total_width = card_width + (spacing * (len(human.hand) - 1))
        start_x = rect.centerx - (total_width // 2)
        y = rect.bottom - card_height - 8
        current_human_turn = self.engine.game_active and self.engine.get_current_player().is_human and not self.menu_open
        for index, card in enumerate(human.hand):
            lift = 10 if current_human_turn else 0
            card_rect = pygame.Rect(start_x + (index * spacing), y - lift, card_width, card_height)
            renderer.draw_card(card, card_rect, face_up=True)
            if current_human_turn:
                self.card_hitboxes.append((card_rect, card))

    def _draw_player_badge(self, renderer, player, anchor, align="midtop") -> None:
        badge = pygame.Rect(0, 0, 184, 54)
        setattr(badge, align, anchor)
        is_current = player == self.engine.get_current_player() and self.engine.game_active and not self.menu_open
        border = HIGHLIGHT_COLOR if is_current else (108, 147, 204)
        self._draw_glass_panel(renderer, badge, PANEL_ALT_COLOR, border, alpha=188)
        renderer.draw_text(player.name, (badge.left + 14, badge.top + 8), size=18, bold=True)
        renderer.draw_text(
            "Mano {0} | Prese {1} | Scope {2}".format(len(player.hand), len(player.captured), player.sweeps),
            (badge.left + 14, badge.top + 30),
            size=13,
            color=TEXT_DIM_COLOR,
        )

    def _draw_live_score_panel(self, renderer, rect: pygame.Rect) -> None:
        self._draw_glass_panel(renderer, rect, PANEL_COLOR, HIGHLIGHT_COLOR, alpha=190)
        renderer.draw_text("Punteggi live", (rect.left + 14, rect.top + 10), size=20, bold=True)
        current_player = self.engine.get_current_player()
        renderer.draw_text("Turno: {0}".format(current_player.name), (rect.left + 14, rect.top + 34), size=15, color=TEXT_DIM_COLOR)

        live_scores = ScoringEngine.calculate_final_scores(self.engine.players)
        y = rect.top + 62
        for score in live_scores[:3]:
            renderer.draw_text(
                "{0}: {1} pt".format(score["player"], score["total"]),
                (rect.left + 14, y),
                size=16,
                color=TEXT_COLOR,
            )
            y += 22

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
        renderer.draw_text("Menu partita", (rect.centerx, rect.top + 26), size=30, bold=True, align="center")
        renderer.draw_text("La partita e in pausa", (rect.centerx, rect.top + 58), size=16, color=TEXT_DIM_COLOR, align="center")

        difficulty_labels = {
            "easy": "Facile",
            "normal": "Normale",
            "expert": "Esperto",
            "adaptive": "Adattivo",
        }
        difficulty_text = "Difficolta: {0}".format(difficulty_labels.get(self.settings["difficulty"], self.settings["difficulty"]))
        visibility_text = "Visibilita: {0}".format("Completa" if self.settings["show_all_cards"] else "Nascosta")

        row_gap = 18
        button_gap = 16
        top_row_width = rect.width - 96
        top_button_width = int((top_row_width - button_gap) / 2)
        top_y = rect.top + 98
        left_x = rect.left + 48

        second_row_width = rect.width - 96
        second_button_width = int((second_row_width - (button_gap * 2)) / 3)
        second_y = top_y + 72 + row_gap

        top_buttons = {
            "difficulty": pygame.Rect(left_x, top_y, top_button_width, 72),
            "toggle_cards": pygame.Rect(left_x + top_button_width + button_gap, top_y, top_button_width, 72),
        }
        second_buttons = {
            "resume": pygame.Rect(left_x, second_y, second_button_width, 70),
            "quit": pygame.Rect(left_x + second_button_width + button_gap, second_y, second_button_width, 70),
            "new_game": pygame.Rect(left_x + ((second_button_width + button_gap) * 2), second_y, second_button_width, 70),
        }
        self.menu_buttons = {}

        self.menu_buttons["difficulty"] = renderer.draw_button(
            difficulty_text,
            top_buttons["difficulty"],
            hovered=top_buttons["difficulty"].collidepoint(mouse_pos),
            tone="accent",
            font_size=18,
        )
        self.menu_buttons["toggle_cards"] = renderer.draw_button(
            visibility_text,
            top_buttons["toggle_cards"],
            hovered=top_buttons["toggle_cards"].collidepoint(mouse_pos),
            tone="neutral",
            font_size=18,
        )
        self.menu_buttons["resume"] = renderer.draw_button(
            "Continua partita",
            second_buttons["resume"],
            hovered=second_buttons["resume"].collidepoint(mouse_pos),
            tone="success",
            font_size=18,
        )
        self.menu_buttons["quit"] = renderer.draw_button(
            "Esci",
            second_buttons["quit"],
            hovered=second_buttons["quit"].collidepoint(mouse_pos),
            tone="danger",
            font_size=18,
        )
        self.menu_buttons["new_game"] = renderer.draw_button(
            "Nuova partita",
            second_buttons["new_game"],
            hovered=second_buttons["new_game"].collidepoint(mouse_pos),
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
