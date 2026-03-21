import pygame

from scopone.config.ui import ACCENT_COLOR, BG_COLOR, TEXT_COLOR, TEXT_DIM_COLOR
from scopone.ui.scene_manager import Scene


class SetupScene(Scene):
    """Collects match settings before entering gameplay."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self.difficulties = [
            ("Facile", "easy"),
            ("Normale", "normal"),
            ("Esperto", "expert"),
            ("Adattivo", "adaptive"),
        ]
        self.player_options = [2, 4]
        self.difficulty_index = 1
        self.player_index = 1
        self.show_all_cards = True
        self.buttons = {}

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.request_quit()
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        for action, rect in self.buttons.items():
            if not rect.collidepoint(event.pos):
                continue

            if action == "difficulty":
                self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)
            elif action == "players":
                self.player_index = (self.player_index + 1) % len(self.player_options)
            elif action == "visibility":
                self.show_all_cards = not self.show_all_cards
            elif action == "fullscreen":
                # The app recreates the display surface so every Rect gets recomputed
                # from the new screen size during the next render pass.
                self.app.toggle_fullscreen()
            elif action == "start":
                _, difficulty = self.difficulties[self.difficulty_index]
                self.app.start_match(self.player_options[self.player_index], difficulty, self.show_all_cards)
            elif action == "quit":
                self.app.request_quit()
            break

    def render(self, renderer) -> None:
        width, height = renderer.surface.get_size()
        layout = self._calculate_layout(width, height)
        mouse_pos = pygame.mouse.get_pos()

        renderer.clear(BG_COLOR)
        self._draw_background_accents(renderer, width, height)

        renderer.draw_text(
            "PYSCOPONE",
            layout["title_center"],
            size=layout["title_size"],
            color=TEXT_COLOR,
            bold=True,
            align="center",
            font_role="title",
        )
        renderer.draw_multiline(
            (
                "Gioco di carte Scopone. Configurare la partita cliccando sui "
                "pulsanti e avviare la partita."
            ),
            layout["subtitle_rect"],
            size=layout["subtitle_size"],
            color=TEXT_DIM_COLOR,
            align="center",
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
        visibility_label = "Carte IA: Visibili" if self.show_all_cards else "Carte IA: Nascoste"
        fullscreen_label = "Finestra" if self.app.is_fullscreen else "Schermo intero"

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
            "fullscreen": renderer.draw_button(
                fullscreen_label,
                layout["fullscreen_button"],
                hovered=layout["fullscreen_button"].collidepoint(mouse_pos),
                tone="warning",
                font_size=layout["fullscreen_font_size"],
            ),
        }

        renderer.draw_text(
            "F11 alterna rapidamente tra finestra e schermo intero",
            layout["footer_hint"],
            size=layout["hint_size"],
            color=TEXT_DIM_COLOR,
            align="center",
        )

    def _calculate_layout(self, width: int, height: int):
        # The menu uses percentages of the current display size instead of fixed
        # coordinates, so the same composition stays centered in windowed mode
        # and after a fullscreen switch.
        side_margin = self._clamp(int(width * 0.04), 24, 64)
        title_size = self._clamp(int(width * 0.075), 84, 104)
        subtitle_size = self._clamp(int(width * 0.02), 24, 30)
        section_size = self._clamp(int(width * 0.018), 18, 24)
        hint_size = self._clamp(int(width * 0.012), 16, 20)

        title_center = (width // 2, int(height * 0.15))
        subtitle_width = min(int(width * 0.72), 980)
        subtitle_rect = pygame.Rect(
            width // 2 - subtitle_width // 2,
            int(height * 0.22),
            subtitle_width,
            self._clamp(int(height * 0.12), 72, 120),
        )

        config_heading = (width // 2, subtitle_rect.bottom + self._clamp(int(height * 0.06), 32, 56))
        config_row_width = min(int(width * 0.82), 1180)
        config_gap = self._clamp(int(width * 0.018), 18, 30)
        config_button_height = self._clamp(int(height * 0.085), 62, 82)
        config_button_width = int((config_row_width - (config_gap * 2)) / 3)
        config_row_top = int(height * 0.5)
        config_row_left = width // 2 - config_row_width // 2

        action_width = min(int(width * 0.34), 420)
        action_height = self._clamp(int(height * 0.085), 62, 78)
        action_gap = self._clamp(int(height * 0.024), 16, 26)
        action_top = config_row_top + config_button_height + self._clamp(int(height * 0.09), 54, 84)
        action_left = width // 2 - action_width // 2

        fullscreen_width = self._clamp(int(width * 0.15), 190, 250)
        fullscreen_height = self._clamp(int(height * 0.06), 44, 54)

        return {
            "title_center": title_center,
            "title_size": title_size,
            "subtitle_rect": subtitle_rect,
            "subtitle_size": subtitle_size,
            "config_heading": config_heading,
            "section_size": section_size,
            "hint_size": hint_size,
            "config_font_size": self._clamp(int(width * 0.014), 18, 22),
            "action_font_size": self._clamp(int(width * 0.018), 22, 28),
            "fullscreen_font_size": self._clamp(int(width * 0.013), 16, 20),
            "difficulty_button": pygame.Rect(
                config_row_left,
                config_row_top,
                config_button_width,
                config_button_height,
            ),
            "players_button": pygame.Rect(
                config_row_left + config_button_width + config_gap,
                config_row_top,
                config_button_width,
                config_button_height,
            ),
            "visibility_button": pygame.Rect(
                config_row_left + ((config_button_width + config_gap) * 2),
                config_row_top,
                config_button_width,
                config_button_height,
            ),
            "start_button": pygame.Rect(
                action_left,
                action_top,
                action_width,
                action_height,
            ),
            "quit_button": pygame.Rect(
                action_left,
                action_top + action_height + action_gap,
                action_width,
                action_height,
            ),
            "fullscreen_button": pygame.Rect(
                width - side_margin - fullscreen_width,
                side_margin,
                fullscreen_width,
                fullscreen_height,
            ),
            "footer_hint": (width // 2, height - self._clamp(int(height * 0.05), 26, 40)),
        }

    def _draw_background_accents(self, renderer, width: int, height: int) -> None:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        pygame.draw.circle(
            overlay,
            (69, 170, 242, 38),
            (int(width * 0.14), int(height * 0.2)),
            int(min(width, height) * 0.12),
        )
        pygame.draw.circle(
            overlay,
            (30, 214, 167, 28),
            (int(width * 0.88), int(height * 0.22)),
            int(min(width, height) * 0.1),
        )
        pygame.draw.ellipse(
            overlay,
            (255, 255, 255, 18),
            pygame.Rect(int(width * 0.2), int(height * 0.73), int(width * 0.6), int(height * 0.12)),
            width=2,
        )
        pygame.draw.line(
            overlay,
            (69, 170, 242, 26),
            (int(width * 0.12), int(height * 0.34)),
            (int(width * 0.88), int(height * 0.34)),
            2,
        )

        renderer.surface.blit(overlay, (0, 0))

    def _clamp(self, value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))
