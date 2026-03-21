import pygame

from scopone.config.ui import BG_COLOR, LOG_BG_COLOR, PANEL_ALT_COLOR, PANEL_COLOR, TEXT_COLOR, TEXT_DIM_COLOR
from scopone.ui.backgrounds import draw_prismatic_background
from scopone.ui.scene_manager import Scene


class ResultsScene(Scene):
    """Shows the final scores and next actions."""

    def __init__(self, app, final_scores, settings, log_messages):
        super().__init__(app)
        self.final_scores = final_scores
        self.settings = dict(settings)
        self.log_messages = list(log_messages)
        self.buttons = {}

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.show_setup()
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        for action, rect in self.buttons.items():
            if not rect.collidepoint(event.pos):
                continue
            if action == "play_again":
                self.app.start_match(
                    self.settings["num_players"],
                    self.settings["difficulty"],
                    self.settings["show_all_cards"],
                )
            elif action == "menu":
                self.app.show_setup()
            elif action == "quit":
                self.app.request_quit()
            return

    def render(self, renderer) -> None:
        draw_prismatic_background(renderer.surface, variant="game")
        width, height = renderer.surface.get_size()
        mouse_pos = pygame.mouse.get_pos()

        panel = pygame.Rect(32, 32, width - 64, height - 64)
        summary_rect = pygame.Rect(panel.left + 18, panel.top + 18, panel.width - 36, panel.height - 36)
        left_rect = pygame.Rect(summary_rect.left, summary_rect.top, summary_rect.width - 340, summary_rect.height)
        right_rect = pygame.Rect(left_rect.right + 18, summary_rect.top, 322, summary_rect.height)

        renderer.draw_panel(panel, PANEL_COLOR, border=(133, 176, 235))
        renderer.draw_text("Risultati finali", (left_rect.left + 12, left_rect.top + 10), size=42, bold=True)
        renderer.draw_text(
            f"{self.settings['num_players']} giocatori | {self.settings['difficulty']} | "
            f"{'visibilita completa' if self.settings['show_all_cards'] else 'visibilita standard'}",
            (left_rect.left + 12, left_rect.top + 58),
            size=18,
            color=TEXT_DIM_COLOR,
        )

        card_top = left_rect.top + 100
        for index, score in enumerate(self.final_scores):
            card_rect = pygame.Rect(left_rect.left + 8, card_top + index * 136, left_rect.width - 16, 118)
            renderer.draw_panel(card_rect, PANEL_ALT_COLOR, border=(118, 162, 224))

            renderer.draw_text(f"{index + 1}. {score['player']}", (card_rect.left + 18, card_rect.top + 16), size=28, bold=True)
            renderer.draw_text(f"{score['total']} punti", (card_rect.right - 20, card_rect.top + 18), size=28, bold=True, align="topright")

            details = [
                f"Carte: {score['captured_cards']}",
                f"Denari: {score['coins']}",
                f"Scope: {score['sweeps']}",
                f"Primiera: {score.get('primiera_value', 0)}",
            ]
            if "members" in score:
                details.insert(0, "Giocatori: " + ", ".join(score["members"]))

            renderer.draw_multiline(" | ".join(details), card_rect.inflate(-18, -54), size=18, color=TEXT_DIM_COLOR, max_chars=66)

            points = score.get("points", {})
            breakdown = []
            for key in ["cards", "coins", "settebello", "primiera", "sweeps"]:
                value = points.get(key, 0)
                if value:
                    breakdown.append(f"{key}: +{value}")
            renderer.draw_text("  ".join(breakdown) or "Nessun bonus", (card_rect.left + 18, card_rect.bottom - 26), size=17, color=TEXT_COLOR)

        renderer.draw_panel(right_rect, LOG_BG_COLOR, border=(118, 162, 224))
        renderer.draw_text("Ultimi eventi", (right_rect.left + 18, right_rect.top + 16), size=28, bold=True)

        y = right_rect.top + 56
        for message in self.log_messages[-18:]:
            if y > right_rect.bottom - 170:
                break
            row = renderer.draw_text(message, (right_rect.left + 18, y), size=16, color=TEXT_DIM_COLOR)
            y = row.bottom + 8

        button_y = right_rect.bottom - 150
        self.buttons = {}
        for action, label, tone, offset in [
            ("play_again", "Gioca ancora", "success", 0),
            ("menu", "Menu principale", "neutral", 58),
            ("quit", "Esci", "danger", 116),
        ]:
            button_rect = pygame.Rect(right_rect.left + 18, button_y + offset, right_rect.width - 36, 46)
            self.buttons[action] = renderer.draw_button(
                label,
                button_rect,
                hovered=button_rect.collidepoint(mouse_pos),
                tone=tone,
            )
