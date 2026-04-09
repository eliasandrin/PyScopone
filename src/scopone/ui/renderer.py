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
        """Inizializza helper di rendering con surface attiva e asset manager."""
        self.surface = surface
        self.assets = assets
        self._audio_icon_cache = {}

    def set_surface(self, surface: pygame.Surface) -> None:
        """Aggiorna la surface target dopo resize/fullscreen switch."""
        self.surface = surface

    def clear(self, color=BG_COLOR) -> None:
        """Pulisce frame corrente con colore di sfondo."""
        self.surface.fill(color)

    def draw_panel(self, rect, background, border=BORDER_COLOR, border_width=2, radius=PANEL_RADIUS) -> pygame.Rect:
        """Disegna pannello arrotondato con bordo e restituisce rect normalizzato."""
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
        """Renderizza testo allineato usando font cache dell'AssetManager."""
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
        """Renderizza testo multilinea con wrapping basato su larghezza disponibile."""
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
        """Disegna bottone tematizzato (accent/success/danger/warning/neutral)."""
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

    def draw_card(self, card, rect, face_up: bool = True, angle: int = 0, is_animating: bool = False) -> pygame.Rect:
        """Disegna carta con gestione rotazione, ombra e cornice dinamica."""
        rect = pygame.Rect(rect)
        source_size = rect.size
        normalized_angle = angle % 360
        frame_radius = self.assets.get_card_corner_radius(source_size)

        # Ignora l'inversione di bounding box per le carte in volo: il loro rect sorgente
        # è sempre basato sull'asset di partenza, evitando double-rotations fallate a fine corsa.
        if not is_animating and normalized_angle in (90, 270):
            source_size = (rect.height, rect.width)

        if not is_animating:
            shadow_alpha = 76 if face_up else 64
            self.draw_card_shadow(rect, alpha=shadow_alpha, offset=(0, 6))

        original_card_image = self.assets.get_card_surface(card, source_size, face_up=face_up)
        content_local_rect = original_card_image.get_bounding_rect()
        if content_local_rect.width <= 0 or content_local_rect.height <= 0:
            content_local_rect = original_card_image.get_rect()

        blit_rect = rect
        frame_rect = content_local_rect.move(rect.left, rect.top)
        if normalized_angle:
            rotated_image = pygame.transform.rotate(original_card_image, angle)
            blit_rect = rotated_image.get_rect(center=rect.center)
            self.surface.blit(rotated_image, blit_rect)

            rotated_content_rect = rotated_image.get_bounding_rect()
            if rotated_content_rect.width <= 0 or rotated_content_rect.height <= 0:
                rotated_content_rect = rotated_image.get_rect()
            frame_rect = rotated_content_rect.move(blit_rect.left, blit_rect.top)
        else:
            self.surface.blit(original_card_image, rect)

        if face_up and not is_animating:
            pygame.draw.rect(self.surface, CARD_BORDER_COLOR, frame_rect, width=2, border_radius=frame_radius)

            # Add a soft top sheen to improve card readability and depth on high-resolution displays.
            highlight = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(
                highlight,
                (255, 255, 255, 34),
                pygame.Rect(
                    int(frame_rect.width * 0.1),
                    -int(frame_rect.height * 0.22),
                    int(frame_rect.width * 0.9),
                    int(frame_rect.height * 0.6),
                ),
            )
            self.surface.blit(highlight, frame_rect.topleft)
        elif not is_animating:
            pygame.draw.rect(self.surface, CARD_BORDER_COLOR, frame_rect, width=2, border_radius=frame_radius)
        return blit_rect

    def draw_card_shadow(self, rect, alpha: int = 90, offset=(0, 6)) -> None:
        """Disegna ombra multilayer soft sotto la carta per migliorare profondita."""
        rect = pygame.Rect(rect)
        shadow_rect = rect.move(offset).inflate(-8, -10)
        if shadow_rect.width <= 0 or shadow_rect.height <= 0:
            return

        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        layers = (
            (12, int(alpha * 0.18)),
            (6, int(alpha * 0.32)),
            (2, int(alpha * 0.50)),
        )
        for inset, layer_alpha in layers:
            layer_rect = shadow_surface.get_rect().inflate(-inset, -inset)
            if layer_rect.width <= 0 or layer_rect.height <= 0:
                continue
            radius = max(8, min(layer_rect.width, layer_rect.height) // 7)
            pygame.draw.rect(shadow_surface, (4, 9, 18, layer_alpha), layer_rect, border_radius=radius)

        self.surface.blit(shadow_surface, shadow_rect.topleft)

    def draw_card_capture_highlight(self, rect, alpha: int = 112) -> None:
        """Sovrappone highlight trasparente sulle carte selezionate in preview presa."""
        rect = pygame.Rect(rect)
        applied_alpha = max(0, min(255, alpha))

        overlay = self.assets.get_capture_highlight_surface(rect.size).copy()
        overlay.set_alpha(applied_alpha)
        self.surface.blit(overlay, rect.topleft)

    def draw_audio_toggle(self, rect, muted: bool = False, hovered: bool = False) -> pygame.Rect:
        """Disegna pulsante audio con stato mute e hover."""
        rect = pygame.Rect(rect)
        background = (34, 51, 80) if hovered else (22, 35, 58)
        border = (130, 170, 220) if hovered else (96, 130, 178)
        if muted:
            border = (212, 112, 112) if hovered else (178, 92, 92)

        self.draw_panel(rect, background, border=border, border_width=2, radius=10)
        content_box = rect.inflate(-12, -12)
        icon_size = max(12, min(content_box.width, content_box.height))
        icon_surface = self._get_audio_icon_surface(icon_size, muted)
        icon_rect = icon_surface.get_rect(center=content_box.center)
        self.surface.blit(icon_surface, icon_rect)

        return rect

    def _get_audio_icon_surface(self, size: int, muted: bool) -> pygame.Surface:
        """Genera o recupera da cache l'icona audio rasterizzata."""
        cache_key = (size, muted)
        cached = self._audio_icon_cache.get(cache_key)
        if cached is not None:
            return cached

        hi_res_size = 96
        hi_res = pygame.Surface((hi_res_size, hi_res_size), pygame.SRCALPHA)
        icon_color = (243, 248, 255)
        mute_color = (226, 90, 90)

        speaker = [
            (18, 38),
            (30, 38),
            (48, 24),
            (48, 72),
            (30, 58),
            (18, 58),
        ]
        pygame.draw.polygon(hi_res, icon_color, speaker)
        pygame.draw.line(hi_res, icon_color, (46, 36), (56, 28), 5)
        pygame.draw.line(hi_res, icon_color, (46, 60), (56, 68), 5)

        if muted:
            pygame.draw.line(hi_res, mute_color, (56, 28), (80, 68), 8)
            pygame.draw.line(hi_res, mute_color, (56, 68), (80, 28), 8)
        else:
            pygame.draw.arc(hi_res, icon_color, pygame.Rect(42, 24, 24, 48), -0.9, 0.9, 6)
            pygame.draw.arc(hi_res, icon_color, pygame.Rect(44, 14, 34, 68), -0.9, 0.9, 6)

        scaled = pygame.transform.smoothscale(hi_res, (size, size))
        self._audio_icon_cache[cache_key] = scaled
        return scaled

    def _wrap_text_to_width(self, text: str, font: pygame.font.Font, max_width: int, fallback_chars: int = 48):
        """Effettua wrapping testuale rispettando width in pixel del font corrente."""
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
