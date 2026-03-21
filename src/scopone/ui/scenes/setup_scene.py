import pygame

from scopone.config.ui import ACCENT_COLOR, BG_COLOR, PANEL_ALT_COLOR, PANEL_COLOR, TEXT_COLOR, TEXT_DIM_COLOR
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
        renderer.clear(BG_COLOR)

        width, height = renderer.surface.get_size()
        panel = pygame.Rect(width // 2 - 450, height // 2 - 260, 900, 520)
        renderer.draw_panel(panel, PANEL_COLOR)

        renderer.draw_text("PYSCOPONE", (panel.centerx, panel.top + 50), size=52, bold=True, align="center")
        renderer.draw_text(
            "Migrazione Pygame con logica di gioco invariata",
            (panel.centerx, panel.top + 104),
            size=22,
            color=TEXT_DIM_COLOR,
            align="center",
        )

        info_panel = pygame.Rect(panel.left + 36, panel.top + 150, panel.width - 72, 190)
        renderer.draw_panel(info_panel, PANEL_ALT_COLOR)
        renderer.draw_multiline(
            "\n".join(
                [
                    "Configura una partita e avvia il nuovo client Pygame.",
                    "Il motore di gioco, il sistema di punteggio e le strategie AI restano separati dalla UI.",
                    "Clicca sui pulsanti per cambiare impostazioni.",
                ]
            ),
            info_panel.inflate(-24, -24),
            size=20,
            color=TEXT_DIM_COLOR,
            max_chars=58,
        )

        mouse_pos = pygame.mouse.get_pos()
        button_width = 380
        button_height = 62
        left_x = panel.left + 70
        right_x = panel.centerx + 10
        top_y = panel.top + 370

        difficulty_label, _ = self.difficulties[self.difficulty_index]
        beginner_label = "Mostra carte IA" if self.show_all_cards else "Nascondi carte IA"

        self.buttons = {
            "difficulty": renderer.draw_button(
                f"Difficolta AI: {difficulty_label}",
                (left_x, top_y, button_width, button_height),
                hovered=pygame.Rect(left_x, top_y, button_width, button_height).collidepoint(mouse_pos),
                tone="accent",
            ),
            "players": renderer.draw_button(
                f"Modalita: {self.player_options[self.player_index]} giocatori",
                (right_x, top_y, button_width, button_height),
                hovered=pygame.Rect(right_x, top_y, button_width, button_height).collidepoint(mouse_pos),
            ),
            "visibility": renderer.draw_button(
                beginner_label,
                (left_x, top_y + 82, button_width, button_height),
                hovered=pygame.Rect(left_x, top_y + 82, button_width, button_height).collidepoint(mouse_pos),
            ),
            "start": renderer.draw_button(
                "Inizia partita",
                (right_x, top_y + 82, button_width, button_height),
                hovered=pygame.Rect(right_x, top_y + 82, button_width, button_height).collidepoint(mouse_pos),
                tone="success",
            ),
            "quit": renderer.draw_button(
                "Esci",
                (panel.centerx - 120, panel.bottom - 70, 240, 48),
                hovered=pygame.Rect(panel.centerx - 120, panel.bottom - 70, 240, 48).collidepoint(mouse_pos),
                tone="danger",
            ),
        }

        renderer.draw_text(
            "Scorciatoia: ESC chiude il gioco",
            (panel.centerx, panel.bottom - 24),
            size=16,
            color=TEXT_DIM_COLOR,
            align="center",
        )

        pygame.draw.circle(renderer.surface, ACCENT_COLOR, (panel.left + 24, panel.top + 24), 6)
        pygame.draw.circle(renderer.surface, ACCENT_COLOR, (panel.right - 24, panel.bottom - 24), 6)
