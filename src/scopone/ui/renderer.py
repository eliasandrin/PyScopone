"""Rendering helpers for the Pygame UI."""

from __future__ import annotations

import textwrap

import pygame

from scopone.config.ui import (
    ACCENT_ALT_COLOR,
    ACCENT_COLOR,
    BG_COLOR,
    BORDER_COLOR,
    CARD_BORDER_COLOR,
    DANGER_COLOR,
    PANEL_RADIUS,
    SUCCESS_COLOR,
    TEXT_COLOR,
    TEXT_DIM_COLOR,
    WARNING_COLOR,
)


class Renderer:
    """Draws panels, text, buttons and cards."""

    def __init__(self, surface: pygame.Surface, assets) -> None:
        self.surface = surface
        self.assets = assets

    def set_surface(self, surface: pygame.Surface) -> None:
        self.surface = surface

    def clear(self, color=BG_COLOR) -> None:
        self.surface.fill(color)

    def draw_panel(self, rect, background, border=BORDER_COLOR, border_width=2, radius=PANEL_RADIUS) -> pygame.Rect:
        rect = pygame.Rect(rect)
        pygame.draw.rect(self.surface, background, rect, border_radius=radius)
        pygame.draw.rect(self.surface, border, rect, width=border_width, border_radius=radius)
        return rect

    def draw_text(self, text: str, pos, size: int = 24, color=TEXT_COLOR, bold: bool = False, align: str = "topleft"):
        font = self.assets.get_font(size, bold=bold)
        rendered = font.render(text, True, color)
        rect = rendered.get_rect()
        setattr(rect, align, pos)
        self.surface.blit(rendered, rect)
        return rect

    def draw_multiline(self, text: str, rect, size: int = 18, color=TEXT_DIM_COLOR, bold: bool = False, max_chars: int = 48) -> None:
        rect = pygame.Rect(rect)
        lines = []
        for paragraph in text.splitlines() or [""]:
            lines.extend(textwrap.wrap(paragraph, width=max_chars) or [""])

        y = rect.top
        for line in lines:
            line_rect = self.draw_text(line, (rect.left, y), size=size, color=color, bold=bold)
            y = line_rect.bottom + 4
            if y > rect.bottom:
                break

    def draw_button(self, label: str, rect, hovered: bool = False, tone: str = "neutral") -> pygame.Rect:
        rect = pygame.Rect(rect)
        if tone == "accent":
            background = ACCENT_ALT_COLOR if hovered else ACCENT_COLOR
            text_color = (255, 255, 255)
        elif tone == "success":
            background = (46, 147, 98) if hovered else SUCCESS_COLOR
            text_color = (255, 255, 255)
        elif tone == "danger":
            background = (160, 56, 56) if hovered else DANGER_COLOR
            text_color = (255, 255, 255)
        elif tone == "warning":
            background = (170, 130, 45) if hovered else WARNING_COLOR
            text_color = (24, 24, 24)
        else:
            background = (44, 58, 82) if hovered else (34, 45, 64)
            text_color = TEXT_COLOR

        self.draw_panel(rect, background, border=(90, 112, 144))
        self.draw_text(label, rect.center, size=20, color=text_color, bold=True, align="center")
        return rect

    def draw_card(self, card, rect, face_up: bool = True) -> pygame.Rect:
        rect = pygame.Rect(rect)
        surface = self.assets.get_card_surface(card, rect.size, face_up=face_up)
        self.surface.blit(surface, rect)
        if face_up:
            pygame.draw.rect(self.surface, CARD_BORDER_COLOR, rect, width=1, border_radius=12)
        return rect
