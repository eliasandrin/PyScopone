import pygame

from scopone.config.game import MODE_QUICK, MODE_TOURNAMENT
from scopone.config.ui import ACCENT_COLOR, BG_COLOR, TEXT_COLOR, TEXT_DIM_COLOR
from scopone.ui.backgrounds import draw_prismatic_background
from scopone.ui.scene_manager import Scene


class SetupScene(Scene):
    """Collects match settings before entering gameplay."""

    def __init__(self, app) -> None:
        """Inizializza opzioni configurazione pre-partita."""
        super().__init__(app)
        self.difficulties = [
            ("Divertimento", "divertimento"),
            ("Normale", "normale"),
            ("Esperto", "esperto"),
        ]
        self.player_options = [2, 4]
        self.game_modes = [
            ("Partita Rapida (1 Smazzata)", MODE_QUICK),
            ("Torneo a punti (A 21 Punti)", MODE_TOURNAMENT),
        ]
        self.difficulty_index = 1
        self.player_index = 1
        self.game_mode_index = 0
        self.show_all_cards = True
        self.buttons = {}
        self.audio_button_rect = pygame.Rect(0, 0, 0, 0)

    def handle_event(self, event) -> None:
        """Gestisce click sui controlli della schermata di setup."""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self.audio_button_rect.collidepoint(event.pos):
            self.app.toggle_mute()
            return

        for action, rect in self.buttons.items():
            if not rect.collidepoint(event.pos):
                continue

            if action == "difficulty":
                self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)
            elif action == "players":
                self.player_index = (self.player_index + 1) % len(self.player_options)
            elif action == "game_mode":
                self.game_mode_index = (self.game_mode_index + 1) % len(self.game_modes)
            elif action == "visibility":
                self.show_all_cards = not self.show_all_cards
            elif action == "start":
                _, difficulty = self.difficulties[self.difficulty_index]
                _, game_mode = self.game_modes[self.game_mode_index]
                self.app.start_match(
                    self.player_options[self.player_index],
                    difficulty,
                    self.show_all_cards,
                    game_mode,
                )
            elif action == "quit":
                self.app.request_quit()
            break

    def render(self, renderer) -> None:
        """Renderizza schermata setup con opzioni e azioni principali."""
        width, height = renderer.surface.get_size()
        layout = self._calculate_layout(width, height)
        mouse_pos = pygame.mouse.get_pos()
        self.audio_button_rect = layout["audio_button"]

        draw_prismatic_background(renderer.surface, variant="menu")

        renderer.draw_text(
            "PYSCOPONE",
            layout["title_center"],
            size=layout["title_size"],
            color=TEXT_COLOR,
            bold=True,
            align="center",
            font_role="title",
        )

        renderer.draw_text(
            "Configurazione partita",
            layout["config_heading"],
            size=layout["section_size"],
            color=ACCENT_COLOR,
            bold=True,
            align="center",
        )

        difficulty_label, _ = self.difficulties[self.difficulty_index]
        game_mode_label, _ = self.game_modes[self.game_mode_index]
        visibility_label = "Carte IA: Visibili" if self.show_all_cards else "Carte IA: Nascoste"

        self.buttons = {
            "difficulty": renderer.draw_button(
                "Difficolta AI: {0}".format(difficulty_label),
                layout["difficulty_button"],
                hovered=layout["difficulty_button"].collidepoint(mouse_pos),
                tone="accent",
                font_size=layout["config_font_size"],
            ),
            "players": renderer.draw_button(
                "Giocatori: {0}".format(self.player_options[self.player_index]),
                layout["players_button"],
                hovered=layout["players_button"].collidepoint(mouse_pos),
                tone="neutral",
                font_size=layout["config_font_size"],
            ),
            "game_mode": renderer.draw_button(
                "Modalita: {0}".format(game_mode_label),
                layout["game_mode_button"],
                hovered=layout["game_mode_button"].collidepoint(mouse_pos),
                tone="accent",
                font_size=layout["config_font_size"],
            ),
            "visibility": renderer.draw_button(
                visibility_label,
                layout["visibility_button"],
                hovered=layout["visibility_button"].collidepoint(mouse_pos),
                tone="neutral",
                font_size=layout["config_font_size"],
            ),
            "start": renderer.draw_button(
                "Inizia Partita",
                layout["start_button"],
                hovered=layout["start_button"].collidepoint(mouse_pos),
                tone="success",
                font_size=layout["action_font_size"],
            ),
            "quit": renderer.draw_button(
                "Esci",
                layout["quit_button"],
                hovered=layout["quit_button"].collidepoint(mouse_pos),
                tone="danger",
                font_size=layout["action_font_size"],
            ),
        }

        renderer.draw_text(
            "Premi F11 per attivare o disattivare la modalita schermo intero",
            layout["footer_hint"],
            size=layout["hint_size"],
            color=TEXT_DIM_COLOR,
            align="center",
        )
        renderer.draw_audio_toggle(
            layout["audio_button"],
            muted=self.app.is_muted,
            hovered=layout["audio_button"].collidepoint(mouse_pos),
        )

    def _calculate_layout(self, width: int, height: int):
        """Calcola layout responsivo dei controlli setup."""
        # The menu uses percentages of the current display size instead of fixed
        # coordinates, so the same composition stays centered in windowed mode
        # and after a fullscreen switch.
        title_size = self._clamp(int(width * 0.075), 84, 104)
        section_size = self._clamp(int(width * 0.018), 20, 26)
        hint_size = self._clamp(int(width * 0.012), 17, 21)

        title_center = (width // 2, int(height * 0.18))

        config_heading = (width // 2, int(height * 0.34))
        pair_gap = self._clamp(int(width * 0.02), 16, 26)
        button_height = self._clamp(int(height * 0.085), 62, 82)
        selection_button_width = self._clamp(int(width * 0.28), 320, 500)
        pair_width = (selection_button_width * 2) + pair_gap
        pair_left = width // 2 - pair_width // 2
        top_row_y = int(height * 0.42)
        second_row_y = top_row_y + button_height + self._clamp(int(height * 0.03), 20, 28)

        action_pair_width = min(int(width * 0.42), 620)
        action_gap = self._clamp(int(width * 0.018), 18, 28)
        action_button_width = int((action_pair_width - action_gap) / 2)
        action_height = self._clamp(int(height * 0.09), 64, 80)
        action_left = width // 2 - action_pair_width // 2
        action_y = second_row_y + button_height + self._clamp(int(height * 0.065), 44, 78)

        return {
            "title_center": title_center,
            "title_size": title_size,
            "config_heading": config_heading,
            "section_size": section_size,
            "hint_size": hint_size,
            "config_font_size": self._clamp(int(width * 0.014), 19, 24),
            "action_font_size": self._clamp(int(width * 0.018), 23, 30),
            "difficulty_button": pygame.Rect(
                pair_left,
                top_row_y,
                selection_button_width,
                button_height,
            ),
            "visibility_button": pygame.Rect(
                pair_left + selection_button_width + pair_gap,
                top_row_y,
                selection_button_width,
                button_height,
            ),
            "players_button": pygame.Rect(
                pair_left,
                second_row_y,
                selection_button_width,
                button_height,
            ),
            "game_mode_button": pygame.Rect(
                pair_left + selection_button_width + pair_gap,
                second_row_y,
                selection_button_width,
                button_height,
            ),
            "start_button": pygame.Rect(
                action_left,
                action_y,
                action_button_width,
                action_height,
            ),
            "quit_button": pygame.Rect(
                action_left + action_button_width + action_gap,
                action_y,
                action_button_width,
                action_height,
            ),
            "audio_button": pygame.Rect(
                width - 54,
                height - 54,
                36,
                36,
            ),
            "footer_hint": (width // 2, height - self._clamp(int(height * 0.05), 26, 40)),
        }

    def _clamp(self, value: int, minimum: int, maximum: int) -> int:
        """Clamp intero helper per i calcoli di layout."""
        return max(minimum, min(maximum, value))
