"""Round-end overlay manager for MatchScene."""

from __future__ import annotations

import pygame

from scopone.config.ui import HIGHLIGHT_COLOR, PANEL_COLOR, TEXT_COLOR, TEXT_DIM_COLOR

ROUND_OVERLAY_BLINK_MS = 520


class RoundOverlayManager:
    """Tracks round-end overlay state, text rows, and rendering."""

    def __init__(self, scene) -> None:
        self.scene = scene
        self.active = False
        self.rows = []
        self.result = {}
        self.prompt_visible = True
        self.prompt_timer = 0.0

    def reset(self) -> None:
        self.active = False
        self.rows = []
        self.result = {}
        self.prompt_visible = True
        self.prompt_timer = 0.0

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.prompt_timer += dt * 1000.0
        if self.prompt_timer >= ROUND_OVERLAY_BLINK_MS:
            self.prompt_visible = not self.prompt_visible
            self.prompt_timer = 0.0

    def show(self, move_result) -> None:
        self.active = True
        self.prompt_visible = True
        self.prompt_timer = 0.0
        self.result = dict(move_result or {})
        self.rows = self._build_rows(self.result.get("round_scores", []))

    def consume_result(self):
        result = dict(self.result)
        self.reset()
        return result

    def draw(self, renderer) -> None:
        width, height = renderer.surface.get_size()
        dimmer = pygame.Surface((width, height), pygame.SRCALPHA)
        dimmer.fill((0, 0, 0, 170))
        renderer.surface.blit(dimmer, (0, 0))

        overlay_width = self._clamp(int(width * 0.62), 740, 1100)
        overlay_height = self._clamp(int(height * 0.42), 360, 520)
        overlay_rect = pygame.Rect(
            (width - overlay_width) // 2,
            (height - overlay_height) // 2,
            overlay_width,
            overlay_height,
        )
        self.scene._draw_glass_panel(renderer, overlay_rect, PANEL_COLOR, HIGHLIGHT_COLOR, alpha=236)

        round_number = max(1, self.scene.engine.round_number)
        renderer.draw_text(
            "Fine Smazzata - Round {0}".format(round_number),
            (overlay_rect.centerx, overlay_rect.top + 26),
            size=34,
            color=TEXT_COLOR,
            bold=True,
            align="center",
            font_role="title",
        )

        y = overlay_rect.top + 84
        for row_text in self.rows:
            renderer.draw_text(
                row_text,
                (overlay_rect.centerx, y),
                size=23,
                color=TEXT_DIM_COLOR,
                align="center",
            )
            y += 42

        if self.prompt_visible:
            renderer.draw_text(
                "Premi INVIO per giocare la prossima smazzata",
                (overlay_rect.centerx, overlay_rect.bottom - 38),
                size=24,
                color=TEXT_COLOR,
                bold=True,
                align="center",
            )

    def _build_rows(self, round_scores):
        rows = []
        if not round_scores:
            return rows

        ordered_scores = sorted(round_scores, key=lambda score: score.get("team_id", 0))
        for score in ordered_scores:
            team_id = score.get("team_id", 0)
            settebello_str = "Si" if score.get("has_settebello") else "No"
            rows.append(
                "Sq {0}  Carte: {1}  Denari: {2}  Primiera: {3}  Settebello: {4}  Scope: {5}  Totale: {6}".format(
                    team_id + 1,
                    score.get("captured_cards", 0),
                    score.get("coins", 0),
                    score.get("primiera_value", 0),
                    settebello_str,
                    score.get("sweeps", 0),
                    score.get("total", 0),
                )
            )
        return rows

    def _clamp(self, value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))
