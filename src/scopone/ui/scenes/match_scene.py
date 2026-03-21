import pygame

from scopone.ai.strategies import get_ai_strategy
from scopone.config.game import DEFAULT_PLAYER_NAMES, SIMBOLI
from scopone.config.ui import (
    AI_THINKING_DELAY_MS,
    BG_COLOR,
    BOTTOM_BAR_HEIGHT,
    HIGHLIGHT_COLOR,
    LOG_BG_COLOR,
    PANEL_ALT_COLOR,
    PANEL_COLOR,
    SIDE_BAR_WIDTH,
    TABLE_FELT_COLOR,
    TEXT_COLOR,
    TEXT_DIM_COLOR,
    TOP_BAR_HEIGHT,
    WARNING_COLOR,
    CARD_SIZE_HAND,
    CARD_SIZE_SMALL,
    CARD_SIZE_TABLE,
)
from scopone.engine.game_engine import GameEngine
from scopone.ui.backgrounds import draw_prismatic_background
from scopone.ui.scene_manager import Scene


class MatchScene(Scene):
    """Renders the live match and translates user actions into engine calls."""

    def __init__(self, app, settings: dict) -> None:
        super().__init__(app)
        self.settings = dict(settings)
        self.engine = None
        self.log_messages = []
        self.buttons = {}
        self.card_hitboxes = []
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self.result_dispatched = False
        self._start_new_game()

    def _start_new_game(self) -> None:
        player_names = [DEFAULT_PLAYER_NAMES[index] if index > 0 else "Tu" for index in range(self.settings["num_players"])]
        self.engine = GameEngine(self.settings["num_players"], player_names)
        self.engine.reset()
        self.engine.deal_cards()
        self.log_messages = [
            "Nuova partita avviata.",
            f"Modalita: {self.settings['num_players']} giocatori",
            f"Difficolta AI: {self.settings['difficulty']}",
        ]
        self.pending_ai_player_id = None
        self.ai_timer = 0.0
        self.result_dispatched = False

    def _append_log(self, message: str) -> None:
        self.log_messages.append(message)
        if len(self.log_messages) > 28:
            self.log_messages = self.log_messages[-28:]

    def handle_event(self, event) -> None:
        if self.engine is None:
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.show_setup()
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        for action, rect in self.buttons.items():
            if not rect.collidepoint(event.pos):
                continue
            if action == "new_game":
                self._start_new_game()
            elif action == "toggle_cards":
                self.settings["show_all_cards"] = not self.settings["show_all_cards"]
                mode = "attiva" if self.settings["show_all_cards"] else "disattiva"
                self._append_log(f"Visualizzazione carte IA {mode}.")
            elif action == "menu":
                self.app.show_setup()
            elif action == "quit":
                self.app.request_quit()
            return

        current_player = self.engine.get_current_player()
        if not self.engine.game_active or not current_player.is_human:
            return

        for rect, card in reversed(self.card_hitboxes):
            if rect.collidepoint(event.pos):
                self._play_human_card(card)
                return

    def update(self, dt: float) -> None:
        if self.engine is None or self.result_dispatched:
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
            self._append_log(f"{current_player.name} sta pensando...")
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

        self._append_log(f"Tu giochi {self._format_card(card)}")
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
        self._append_log(f"{current_player.name} gioca {self._format_card(selected_card)}")
        self._append_log(f"AI: {strategy.get_last_decision_reason()}")
        if self.engine.game_active:
            self.engine.next_player()
        self.pending_ai_player_id = None
        self.ai_timer = 0.0

    def _format_card(self, card) -> str:
        return f"{card[0]}{SIMBOLI[card[1]]}"

    def render(self, renderer) -> None:
        assert self.engine is not None

        draw_prismatic_background(renderer.surface, variant="game")
        width, height = renderer.surface.get_size()
        mouse_pos = pygame.mouse.get_pos()

        top_bar = pygame.Rect(16, 16, width - 32, TOP_BAR_HEIGHT)
        log_rect = pygame.Rect(width - SIDE_BAR_WIDTH - 16, top_bar.bottom + 16, SIDE_BAR_WIDTH, height - top_bar.bottom - 32)
        center_width = width - SIDE_BAR_WIDTH - 48
        center_area = pygame.Rect(16, top_bar.bottom + 16, center_width, height - top_bar.bottom - BOTTOM_BAR_HEIGHT - 32)
        hand_area = pygame.Rect(16, height - BOTTOM_BAR_HEIGHT - 16, center_width, BOTTOM_BAR_HEIGHT)

        self._draw_top_bar(renderer, top_bar, mouse_pos)
        self._draw_center_area(renderer, center_area)
        self._draw_hand_area(renderer, hand_area)
        self._draw_log(renderer, log_rect)

    def _draw_top_bar(self, renderer, rect: pygame.Rect, mouse_pos) -> None:
        renderer.draw_panel(rect, PANEL_COLOR, border=HIGHLIGHT_COLOR)
        current_player = self.engine.get_current_player()
        status = f"Turno di {current_player.name}" if self.engine.game_active else "Partita terminata"
        mode = "Visibilita completa" if self.settings["show_all_cards"] else "Modalita competitiva"

        renderer.draw_text(status, (rect.left + 24, rect.top + 18), size=28, bold=True)
        renderer.draw_text(
            f"{self.settings['num_players']} giocatori | {self.settings['difficulty']} | {mode}",
            (rect.left + 24, rect.top + 50),
            size=16,
            color=TEXT_DIM_COLOR,
        )

        button_specs = [
            ("new_game", "Nuova partita", "success"),
            ("toggle_cards", "Mostra/Nascondi", "neutral"),
            ("menu", "Menu", "warning"),
            ("quit", "Esci", "danger"),
        ]
        self.buttons = {}
        button_width = 146
        button_height = 46
        x = rect.right - 24 - button_width
        y = rect.centery - button_height // 2
        for action, label, tone in reversed(button_specs):
            button_rect = pygame.Rect(x, y, button_width, button_height)
            self.buttons[action] = renderer.draw_button(
                label,
                button_rect,
                hovered=button_rect.collidepoint(mouse_pos),
                tone=tone,
            )
            x -= button_width + 12

    def _draw_center_area(self, renderer, rect: pygame.Rect) -> None:
        renderer.draw_panel(rect, PANEL_COLOR, border=(116, 156, 214))
        players = self.engine.players
        num_players = len(players)

        if num_players == 2:
            top_panel = pygame.Rect(rect.left + 140, rect.top + 16, rect.width - 280, 124)
            table_rect = pygame.Rect(rect.left + 120, rect.top + 170, rect.width - 240, rect.height - 210)
            self._draw_player_panel(renderer, top_panel, players[1], face_up=self.settings["show_all_cards"])
        else:
            top_panel = pygame.Rect(rect.left + 220, rect.top + 16, rect.width - 440, 110)
            left_panel = pygame.Rect(rect.left + 16, rect.top + 154, 190, 180)
            right_panel = pygame.Rect(rect.right - 206, rect.top + 154, 190, 180)
            table_rect = pygame.Rect(rect.left + 220, rect.top + 154, rect.width - 440, rect.height - 170)
            self._draw_player_panel(renderer, top_panel, players[2], face_up=self.settings["show_all_cards"])
            self._draw_player_panel(renderer, left_panel, players[1], face_up=self.settings["show_all_cards"])
            self._draw_player_panel(renderer, right_panel, players[3], face_up=self.settings["show_all_cards"])

        self._draw_table(renderer, table_rect)

    def _draw_player_panel(self, renderer, rect: pygame.Rect, player, face_up: bool) -> None:
        border = HIGHLIGHT_COLOR if player == self.engine.get_current_player() else TEXT_DIM_COLOR
        renderer.draw_panel(rect, PANEL_ALT_COLOR, border=border)
        renderer.draw_text(player.name, (rect.left + 18, rect.top + 14), size=22, bold=True)
        renderer.draw_text(
            f"Mano {len(player.hand)} | Prese {len(player.captured)} | Scope {player.sweeps}",
            (rect.left + 18, rect.top + 44),
            size=16,
            color=TEXT_DIM_COLOR,
        )

        if not player.hand:
            renderer.draw_text("Nessuna carta", rect.center, size=18, color=TEXT_DIM_COLOR, align="center")
            return

        card_width, card_height = CARD_SIZE_SMALL
        cards_region = pygame.Rect(rect.left + 12, rect.top + 74, rect.width - 24, rect.height - 86)
        spacing = min(48, max(20, (cards_region.width - card_width) // max(len(player.hand) - 1, 1)))
        total_width = card_width + spacing * (len(player.hand) - 1)
        start_x = cards_region.centerx - total_width // 2
        y = cards_region.top
        for index, card in enumerate(player.hand):
            card_rect = pygame.Rect(start_x + index * spacing, y, card_width, card_height)
            renderer.draw_card(card, card_rect, face_up=face_up)

    def _draw_table(self, renderer, rect: pygame.Rect) -> None:
        renderer.draw_panel(rect, TABLE_FELT_COLOR, border=WARNING_COLOR)
        renderer.draw_text("Tavolo", (rect.centerx, rect.top + 18), size=28, bold=True, align="center")

        if not self.engine.table:
            renderer.draw_text("Tavolo vuoto", rect.center, size=22, color=TEXT_DIM_COLOR, align="center")
            return

        card_width, card_height = CARD_SIZE_TABLE
        spacing = min(120, max(36, (rect.width - card_width) // max(len(self.engine.table), 1)))
        total_width = card_width + spacing * (len(self.engine.table) - 1)
        start_x = rect.centerx - total_width // 2
        y = rect.centery - card_height // 2
        for index, card in enumerate(self.engine.table):
            renderer.draw_card(card, (start_x + index * spacing, y, card_width, card_height))

    def _draw_hand_area(self, renderer, rect: pygame.Rect) -> None:
        human = self.engine.get_human_player()
        renderer.draw_panel(rect, PANEL_COLOR, border=HIGHLIGHT_COLOR if human == self.engine.get_current_player() else (116, 156, 214))
        renderer.draw_text("La tua mano", (rect.left + 18, rect.top + 16), size=26, bold=True)
        renderer.draw_text(
            f"Carte catturate: {len(human.captured)} | Scope: {human.sweeps}",
            (rect.left + 18, rect.top + 50),
            size=16,
            color=TEXT_DIM_COLOR,
        )

        self.card_hitboxes = []
        if not human.hand:
            renderer.draw_text("Mano vuota", rect.center, size=22, color=TEXT_DIM_COLOR, align="center")
            return

        card_width, card_height = CARD_SIZE_HAND
        available_width = rect.width - 60
        spacing = min(108, max(60, (available_width - card_width) // max(len(human.hand) - 1, 1)))
        total_width = card_width + spacing * (len(human.hand) - 1)
        start_x = rect.centerx - total_width // 2
        y = rect.bottom - card_height - 18
        current_human_turn = self.engine.game_active and self.engine.get_current_player().is_human
        for index, card in enumerate(human.hand):
            card_rect = pygame.Rect(start_x + index * spacing, y, card_width, card_height)
            renderer.draw_card(card, card_rect, face_up=True)
            if current_human_turn:
                self.card_hitboxes.append((card_rect, card))

    def _draw_log(self, renderer, rect: pygame.Rect) -> None:
        renderer.draw_panel(rect, LOG_BG_COLOR, border=(120, 157, 214))
        renderer.draw_text("Log Partita", (rect.left + 18, rect.top + 16), size=26, bold=True)
        renderer.draw_text("ESC torna al menu", (rect.left + 18, rect.top + 48), size=15, color=TEXT_DIM_COLOR)

        line_area = rect.inflate(-24, -92)
        y = line_area.top
        for message in self.log_messages[-18:]:
            if y > line_area.bottom - 28:
                break
            line = renderer.draw_text(message, (line_area.left, y), size=17, color=TEXT_COLOR if "AI:" not in message else TEXT_DIM_COLOR)
            y = line.bottom + 8
