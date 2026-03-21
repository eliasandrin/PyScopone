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

    def draw_text(
        self,
        text: str,
        pos,
        size: int = 24,
        color=TEXT_COLOR,
        bold: bool = False,
        align: str = "topleft",
        font_role: str = "body",
    ):
        font = self.assets.get_font(size, bold=bold, role=font_role)
        rendered = font.render(text, True, color)
        rect = rendered.get_rect()
        setattr(rect, align, pos)
        self.surface.blit(rendered, rect)
        return rect

    def draw_multiline(
        self,
        text: str,
        rect,
        size: int = 18,
        color=TEXT_DIM_COLOR,
        bold: bool = False,
        max_chars: int = 48,
        align: str = "topleft",
        font_role: str = "body",
        line_spacing: int = 4,
    ) -> None:
        rect = pygame.Rect(rect)
        font = self.assets.get_font(size, bold=bold, role=font_role)
        lines = self._wrap_text_to_width(text, font, rect.width, fallback_chars=max_chars)

        y = rect.top
        for line in lines:
            rendered = font.render(line, True, color)
            line_rect = rendered.get_rect()
            if align == "center":
                line_rect.midtop = (rect.centerx, y)
            else:
                setattr(line_rect, "topleft", (rect.left, y))
            self.surface.blit(rendered, line_rect)
            y = line_rect.bottom + line_spacing
            if y > rect.bottom:
                break

    def draw_button(
        self,
        label: str,
        rect,
        hovered: bool = False,
        tone: str = "neutral",
        font_size: int = 20,
    ) -> pygame.Rect:
        rect = pygame.Rect(rect)
        if tone == "accent":
            background = ACCENT_ALT_COLOR if hovered else ACCENT_COLOR
            text_color = (248, 252, 255)
        elif tone == "success":
            background = (74, 146, 228) if hovered else SUCCESS_COLOR
            text_color = (248, 252, 255)
        elif tone == "danger":
            background = (172, 87, 112) if hovered else DANGER_COLOR
            text_color = (248, 252, 255)
        elif tone == "warning":
            background = (176, 208, 248) if hovered else WARNING_COLOR
            text_color = (15, 28, 49)
        else:
            background = (38, 60, 94) if hovered else (26, 43, 71)
            text_color = (236, 244, 255)

        self.draw_panel(rect, background, border=(134, 176, 230))
        self.draw_text(label, rect.center, size=font_size, color=text_color, bold=True, align="center")
        return rect

    def draw_card(self, card, rect, face_up: bool = True, angle: int = 0) -> pygame.Rect:
        rect = pygame.Rect(rect)
        source_size = rect.size
        normalized_angle = angle % 360
        if normalized_angle in (90, 270):
            source_size = (rect.height, rect.width)

        surface = self.assets.get_card_surface(card, source_size, face_up=face_up)
        if normalized_angle:
            surface = pygame.transform.rotate(surface, angle)
        self.surface.blit(surface, rect)
        if face_up:
            pygame.draw.rect(self.surface, CARD_BORDER_COLOR, rect, width=1, border_radius=12)
        return rect

    def draw_audio_toggle(self, rect, muted: bool = False, hovered: bool = False) -> pygame.Rect:
        rect = pygame.Rect(rect)
        background = (34, 51, 80) if hovered else (22, 35, 58)
        border = (130, 170, 220) if hovered else (96, 130, 178)
        if muted:
            border = (212, 112, 112) if hovered else (178, 92, 92)

        self.draw_panel(rect, background, border=border, border_width=2, radius=10)

        speaker = [
            (rect.left + 10, rect.centery - 4),
            (rect.left + 15, rect.centery - 4),
            (rect.left + 20, rect.centery - 10),
            (rect.left + 20, rect.centery + 10),
            (rect.left + 15, rect.centery + 4),
            (rect.left + 10, rect.centery + 4),
        ]
        pygame.draw.polygon(self.surface, TEXT_COLOR, speaker)
        pygame.draw.line(self.surface, TEXT_COLOR, (rect.left + 22, rect.centery - 7), (rect.left + 26, rect.centery - 3), 2)
        pygame.draw.line(self.surface, TEXT_COLOR, (rect.left + 22, rect.centery + 7), (rect.left + 26, rect.centery + 3), 2)

        if muted:
            pygame.draw.line(self.surface, (224, 88, 88), (rect.left + 24, rect.top + 9), (rect.right - 8, rect.bottom - 9), 3)
            pygame.draw.line(self.surface, (224, 88, 88), (rect.left + 24, rect.bottom - 9), (rect.right - 8, rect.top + 9), 3)
        else:
            pygame.draw.arc(self.surface, TEXT_COLOR, pygame.Rect(rect.left + 18, rect.top + 7, 12, 20), -0.9, 0.9, 2)
            pygame.draw.arc(self.surface, TEXT_COLOR, pygame.Rect(rect.left + 20, rect.top + 4, 16, 26), -0.9, 0.9, 2)

        return rect

    def _wrap_text_to_width(self, text: str, font: pygame.font.Font, max_width: int, fallback_chars: int = 48):
        lines = []
        for paragraph in text.splitlines() or [""]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current = words[0]
            for word in words[1:]:
                candidate = current + " " + word
                if font.size(candidate)[0] <= max_width:
                    current = candidate
                else:
                    lines.append(current)
                    current = word
            lines.append(current)

        if not lines:
            return textwrap.wrap(text, width=fallback_chars) or [""]
        return lines
