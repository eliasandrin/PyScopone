import pygame

from scopone.config.game import SIMBOLI
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
        }

        renderer.draw_text(
            "Premi F11 per attivare o disattivare la modalita schermo intero",
            layout["footer_hint"],
            size=layout["hint_size"],
            color=TEXT_DIM_COLOR,
            align="center",
        )

    def _calculate_layout(self, width: int, height: int):
        # The menu uses percentages of the current display size instead of fixed
        # coordinates, so the same composition stays centered in windowed mode
        # and after a fullscreen switch.
        title_size = self._clamp(int(width * 0.075), 84, 104)
        section_size = self._clamp(int(width * 0.018), 18, 24)
        hint_size = self._clamp(int(width * 0.012), 16, 20)

        title_center = (width // 2, int(height * 0.18))

        config_heading = (width // 2, int(height * 0.34))
        pair_width = min(int(width * 0.58), 900)
        pair_gap = self._clamp(int(width * 0.02), 18, 30)
        button_height = self._clamp(int(height * 0.085), 62, 82)
        pair_button_width = int((pair_width - pair_gap) / 2)
        pair_left = width // 2 - pair_width // 2
        top_row_y = int(height * 0.42)

        players_width = min(int(width * 0.32), 420)
        players_x = width // 2 - players_width // 2
        players_y = top_row_y + button_height + self._clamp(int(height * 0.03), 20, 28)

        action_pair_width = min(int(width * 0.42), 620)
        action_gap = self._clamp(int(width * 0.018), 18, 28)
        action_button_width = int((action_pair_width - action_gap) / 2)
        action_height = self._clamp(int(height * 0.09), 64, 80)
        action_left = width // 2 - action_pair_width // 2
        action_y = players_y + button_height + self._clamp(int(height * 0.08), 54, 86)

        return {
            "title_center": title_center,
            "title_size": title_size,
            "config_heading": config_heading,
            "section_size": section_size,
            "hint_size": hint_size,
            "config_font_size": self._clamp(int(width * 0.014), 18, 22),
            "action_font_size": self._clamp(int(width * 0.018), 22, 28),
            "difficulty_button": pygame.Rect(
                pair_left,
                top_row_y,
                pair_button_width,
                button_height,
            ),
            "visibility_button": pygame.Rect(
                pair_left + pair_button_width + pair_gap,
                top_row_y,
                pair_button_width,
                button_height,
            ),
            "players_button": pygame.Rect(
                players_x,
                players_y,
                players_width,
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
            "footer_hint": (width // 2, height - self._clamp(int(height * 0.05), 26, 40)),
        }

    def _draw_background_accents(self, renderer, width: int, height: int) -> None:
        # Visual direction inferred from green/gold art deco and casino references:
        # darker emerald base, subtle golden geometry, and card-suit motifs kept
        # low-contrast so the UI remains readable.
        self._draw_vertical_gradient(
            renderer.surface,
            (5, 16, 20),
            (9, 44, 36),
        )

        glow = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.circle(
            glow,
            (201, 170, 93, 42),
            (width // 2, int(height * 0.2)),
            int(min(width, height) * 0.23),
        )
        pygame.draw.circle(
            glow,
            (19, 115, 88, 54),
            (int(width * 0.18), int(height * 0.78)),
            int(min(width, height) * 0.18),
        )
        pygame.draw.circle(
            glow,
            (19, 115, 88, 46),
            (int(width * 0.84), int(height * 0.18)),
            int(min(width, height) * 0.16),
        )
        renderer.surface.blit(glow, (0, 0))

        self._draw_art_deco_fans(renderer.surface, width, height)
        self._draw_suit_motifs(renderer, width, height)

    def _draw_vertical_gradient(self, surface, top_color, bottom_color) -> None:
        width, height = surface.get_size()
        for y in range(height):
            ratio = float(y) / max(height - 1, 1)
            color = (
                int(top_color[0] + ((bottom_color[0] - top_color[0]) * ratio)),
                int(top_color[1] + ((bottom_color[1] - top_color[1]) * ratio)),
                int(top_color[2] + ((bottom_color[2] - top_color[2]) * ratio)),
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

    def _draw_art_deco_fans(self, surface, width: int, height: int) -> None:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        gold = (201, 170, 93, 56)
        soft_gold = (201, 170, 93, 24)

        for index in range(6):
            inset = index * self._clamp(int(width * 0.015), 12, 20)
            rect = pygame.Rect(
                int(width * 0.11) + inset,
                int(height * 0.08) + inset,
                int(width * 0.78) - (inset * 2),
                int(height * 0.64) - (inset * 2),
            )
            pygame.draw.arc(overlay, gold if index % 2 == 0 else soft_gold, rect, 3.45, 5.98, 2)

        for y_ratio in (0.36, 0.38, 0.4):
            pygame.draw.line(
                overlay,
                soft_gold,
                (int(width * 0.12), int(height * y_ratio)),
                (int(width * 0.88), int(height * y_ratio)),
                1,
            )

        frame_rect = pygame.Rect(int(width * 0.05), int(height * 0.06), int(width * 0.9), int(height * 0.86))
        pygame.draw.rect(overlay, (201, 170, 93, 28), frame_rect, width=2, border_radius=28)
        pygame.draw.rect(overlay, (255, 255, 255, 12), frame_rect.inflate(-18, -18), width=1, border_radius=24)
        surface.blit(overlay, (0, 0))

    def _draw_suit_motifs(self, renderer, width: int, height: int) -> None:
        motifs = [
            (SIMBOLI["Denari"], (int(width * 0.14), int(height * 0.24)), 64),
            (SIMBOLI["Coppe"], (int(width * 0.86), int(height * 0.28)), 58),
            (SIMBOLI["Bastoni"], (int(width * 0.18), int(height * 0.72)), 62),
            (SIMBOLI["Spade"], (int(width * 0.82), int(height * 0.7)), 60),
        ]
        for symbol, position, size in motifs:
            renderer.draw_text(
                symbol,
                position,
                size=size,
                color=(255, 255, 255, 80),
                align="center",
                font_role="title",
            )

    def _clamp(self, value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))
