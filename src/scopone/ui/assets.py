"""Asset loading and caching for the Pygame UI."""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame

from scopone.config.game import SIMBOLI
from scopone.config.ui import CARD_BACK_COLOR, CARD_BORDER_COLOR, CARD_FACE_COLOR, FONT_NAME, TEXT_COLOR
from scopone.types import Card


LOGGER = logging.getLogger(__name__)


class AssetManager:
    """Loads fonts and card images with in-memory caches."""

    ATLAS_COLUMNS = 10
    ATLAS_ROWS = 5
    ATLAS_CARD_ROWS = 4
    ATLAS_BASENAME = "trevisane"
    ATLAS_EXTENSIONS = (".jpg", ".jpeg", ".png")
    ATLAS_ROW_TO_SUIT = {
        0: "Denari",
        1: "Coppe",
        2: "Spade",
        3: "Bastoni",
    }
    ATLAS_COL_TO_VALUE = {
        0: 1,
        1: 2,
        2: 3,
        3: 4,
        4: 5,
        5: 6,
        6: 7,
        7: 8,
        8: 9,
        9: 10,
    }

    def __init__(self) -> None:
        self.assets_root = Path(__file__).resolve().parents[3] / "assets"
        self.cards_root = self.assets_root / "cards"
        self.fonts_root = self.assets_root / "fonts"
        self.font_cache = {}  # type: Dict[Tuple[str, int, bool], pygame.font.Font]
        self.surface_cache = {}  # type: Dict[Tuple[str, Tuple[int, int]], pygame.Surface]
        self.base_card_cache = {}  # type: Dict[str, pygame.Surface]
        self.rendered_card_cache = {}  # type: Dict[Tuple[str, Tuple[int, int], bool], pygame.Surface]
        self._warned = set()
        self.card_index = self._build_card_index()
        self.atlas_metrics = {}  # type: Dict[str, int]
        self.atlas_surface = self._load_atlas_surface()
        self.atlas_index = self._build_atlas_index(self.atlas_surface)
        self.custom_title_font = self._find_custom_title_font()

    def _build_card_index(self):
        index = {}  # type: Dict[str, Path]
        if not self.cards_root.exists():
            return index

        for path in self.cards_root.iterdir():
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            index[path.name.lower()] = path
        return index

    def _load_atlas_surface(self) -> Optional[pygame.Surface]:
        atlas_candidates = []
        for root in (self.cards_root, self.assets_root):
            for ext in self.ATLAS_EXTENSIONS:
                atlas_candidates.append(root / "{0}{1}".format(self.ATLAS_BASENAME, ext))

            # Accept files like trevisane.anything as a last-resort compatibility path.
            atlas_candidates.extend(sorted(root.glob("{0}.*".format(self.ATLAS_BASENAME))))

        for atlas_path in atlas_candidates:
            if not atlas_path.exists():
                continue

            try:
                loaded = pygame.image.load(str(atlas_path))
                if pygame.display.get_surface() is not None:
                    return loaded.convert_alpha()
                return loaded
            except pygame.error:
                continue

        self._warn_once(
            "atlas-not-found",
            "Card atlas not found. Falling back to per-card files or generated faces.",
        )
        return None

    def _build_atlas_index(self, atlas_surface: Optional[pygame.Surface]) -> Dict[str, pygame.Rect]:
        if atlas_surface is None:
            return {}

        atlas_width, atlas_height = atlas_surface.get_size()
        if atlas_width <= 0 or atlas_height <= 0:
            return {}

        self.atlas_metrics = {
            "width": atlas_width,
            "height": atlas_height,
            "columns": self.ATLAS_COLUMNS,
            "rows": self.ATLAS_ROWS,
            "base_cell_width": atlas_width // self.ATLAS_COLUMNS,
            "base_cell_height": atlas_height // self.ATLAS_ROWS,
            "extra_width_pixels": atlas_width % self.ATLAS_COLUMNS,
            "extra_height_pixels": atlas_height % self.ATLAS_ROWS,
        }

        column_bounds = self._split_axis(atlas_width, self.ATLAS_COLUMNS)
        row_bounds = self._split_axis(atlas_height, self.ATLAS_ROWS)
        index = {}

        # Atlas row order is Denari, Coppe, Spade, Bastoni and is mapped explicitly.
        for row in range(self.ATLAS_CARD_ROWS):
            suit = self.ATLAS_ROW_TO_SUIT.get(row)
            if suit is None:
                continue

            y0, y1 = row_bounds[row]
            for col in range(self.ATLAS_COLUMNS):
                value = self.ATLAS_COL_TO_VALUE[col]
                x0, x1 = column_bounds[col]

                crop = self._inset_crop_rect(x0, y0, x1 - x0, y1 - y0)
                if crop.width <= 0 or crop.height <= 0:
                    continue

                key = self._card_filename(value, suit)
                index[key] = crop

        return index

    def _split_axis(self, axis_size: int, segments: int) -> Tuple[Tuple[int, int], ...]:
        if segments <= 0 or axis_size <= 0:
            return tuple()

        bounds = []
        for i in range(segments):
            start = round((i * axis_size) / segments)
            end = round(((i + 1) * axis_size) / segments)
            bounds.append((start, end))
        return tuple(bounds)

    def _inset_crop_rect(self, x: int, y: int, w: int, h: int) -> pygame.Rect:
        if w <= 0 or h <= 0:
            return pygame.Rect(x, y, 0, 0)

        # Trim a small border per cell to avoid atlas separators/margins when present.
        pad_x = max(0, min(3, w // 20))
        pad_y = max(0, min(3, h // 20))
        rect = pygame.Rect(x + pad_x, y + pad_y, w - (pad_x * 2), h - (pad_y * 2))

        if rect.width <= 0 or rect.height <= 0:
            return pygame.Rect(x, y, w, h)
        return rect

    def _card_filename(self, value: int, suit: str) -> str:
        return "{0}_{1}.jpg".format(value, suit.lower())

    def _warn_once(self, key: str, message: str) -> None:
        if key in self._warned:
            return
        self._warned.add(key)
        LOGGER.warning(message)

    def get_font(self, size: int, bold: bool = False, role: str = "body") -> pygame.font.Font:
        cache_key = (role, size, bold)
        if cache_key not in self.font_cache:
            self.font_cache[cache_key] = self._load_font(size, bold=bold, role=role)
        return self.font_cache[cache_key]

    def _find_custom_title_font(self):
        if not self.fonts_root.exists():
            return None

        for extension in ("*.ttf", "*.otf"):
            matches = sorted(self.fonts_root.glob(extension))
            if matches:
                return matches[0]
        return None

    def _load_font(self, size: int, bold: bool = False, role: str = "body") -> pygame.font.Font:
        if role == "title":
            if self.custom_title_font is not None:
                return pygame.font.Font(str(self.custom_title_font), size)

            for family in ("impact", "haettenschweiler", "arialblack", "verdana"):
                path = pygame.font.match_font(family, bold=bold)
                if path:
                    return pygame.font.Font(path, size)

        return pygame.font.SysFont(FONT_NAME, size, bold=bold)

    def get_card_surface(self, card: Card, size: Tuple[int, int], face_up: bool = True) -> pygame.Surface:
        cache_key = (f"{card}-{face_up}", size)
        if cache_key in self.surface_cache:
            return self.surface_cache[cache_key]

        surface = self._load_card_image(card, size) if face_up else self._build_card_back(size)
        self.surface_cache[cache_key] = surface
        return surface

    def get_card_back_surface(self, size: Tuple[int, int]) -> pygame.Surface:
        cache_key = ("card-back", size)
        cached = self.surface_cache.get(cache_key)
        if cached is not None:
            return cached

        surface = self._build_card_back(size)
        self.surface_cache[cache_key] = surface
        return surface

    def get_card(
        self,
        suit: str,
        value: int,
        target_size: Optional[Tuple[int, int]] = None,
        preserve_aspect_ratio: bool = True,
    ) -> Optional[pygame.Surface]:
        cache_key = self._card_filename(value, suit)
        if target_size is not None:
            if target_size[0] <= 0 or target_size[1] <= 0:
                self._warn_once(
                    "invalid-target-size",
                    "Invalid card target size requested. Falling back to source card surface.",
                )
                target_size = None
            else:
                rendered_key = (cache_key, target_size, preserve_aspect_ratio)
                cached_rendered = self.rendered_card_cache.get(rendered_key)
                if cached_rendered is not None:
                    return cached_rendered

        cached = self.base_card_cache.get(cache_key)
        if cached is None:
            atlas_crop = self._get_atlas_card(cache_key)
            if atlas_crop is not None:
                cached = atlas_crop
            else:
                cached = self._load_card_file(cache_key, suit, value)

            if cached is None:
                return None

            self.base_card_cache[cache_key] = cached

        if target_size is None:
            return cached

        rendered = self._render_card_to_target(cached, target_size, preserve_aspect_ratio=preserve_aspect_ratio)
        self.rendered_card_cache[(cache_key, target_size, preserve_aspect_ratio)] = rendered
        return rendered

    def _render_card_to_target(
        self,
        source: pygame.Surface,
        target_size: Tuple[int, int],
        preserve_aspect_ratio: bool = True,
    ) -> pygame.Surface:
        target_w, target_h = target_size
        source_w, source_h = source.get_size()

        if source_w <= 0 or source_h <= 0:
            return pygame.Surface(target_size, pygame.SRCALPHA)

        if not preserve_aspect_ratio:
            return pygame.transform.smoothscale(source, target_size)

        scale = min(target_w / float(source_w), target_h / float(source_h))
        scaled_w = max(1, int(round(source_w * scale)))
        scaled_h = max(1, int(round(source_h * scale)))
        scaled = pygame.transform.smoothscale(source, (scaled_w, scaled_h))

        canvas = pygame.Surface(target_size, pygame.SRCALPHA)
        offset_x = (target_w - scaled_w) // 2
        offset_y = (target_h - scaled_h) // 2
        canvas.blit(scaled, (offset_x, offset_y))
        return canvas

    def _load_card_image(self, card: Card, size: Tuple[int, int]) -> pygame.Surface:
        value, suit = card
        base = self.get_card(
            suit,
            value,
            target_size=size,
            preserve_aspect_ratio=True,
        )
        if base is not None:
            return base

        self._warn_once(
            "card-fallback-render",
            "Card image not found in atlas/files for one or more cards. Using generated fallback rendering.",
        )
        return self._build_card_fallback(card, size)

    def _get_atlas_card(self, cache_key: str) -> Optional[pygame.Surface]:
        if self.atlas_surface is None:
            return None

        rect = self.atlas_index.get(cache_key)
        if rect is None:
            return None

        atlas_rect = self.atlas_surface.get_rect()
        if not atlas_rect.contains(rect):
            self._warn_once(
                "atlas-invalid-rect",
                "Invalid card coordinates detected in atlas index. Falling back to file/generic card rendering.",
            )
            return None

        try:
            return self.atlas_surface.subsurface(rect).copy()
        except ValueError:
            self._warn_once(
                "atlas-subsurface-error",
                "Failed to crop atlas subsurface. Falling back to file/generic card rendering.",
            )
            return None

    def _load_card_file(self, cache_key: str, suit: str, value: int) -> Optional[pygame.Surface]:
        for candidate in self._card_candidates(value, suit):
            path = self.card_index.get(candidate.lower())
            if path is None:
                continue
            try:
                return pygame.image.load(str(path)).convert_alpha()
            except pygame.error:
                continue

        path = self.card_index.get(cache_key.lower())
        if path is None:
            return None

        try:
            return pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            return None

    def _card_candidates(self, value, suit):
        suit_lower = suit.lower()
        suit_title = suit.capitalize()
        return [
            f"{value}_{suit_lower}.jpg",
            f"{value}_{suit_lower}.jpeg",
            f"{value}_{suit_lower}.png",
            f"{value}_{suit_title}.jpg",
            f"{value}_{suit_title}.jpeg",
            f"{value}_{suit_title}.png",
        ]

    def _build_card_fallback(self, card: Card, size: Tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(CARD_FACE_COLOR)
        pygame.draw.rect(surface, CARD_BORDER_COLOR, surface.get_rect(), width=2, border_radius=10)

        value, suit = card
        color = (184, 45, 45) if suit in {"Denari", "Coppe"} else (34, 40, 48)
        title_font = self.get_font(max(18, size[0] // 4), bold=True)
        symbol_font = self.get_font(max(24, size[1] // 4), bold=True)
        surface.blit(title_font.render(str(value), True, color), (10, 8))

        symbol = symbol_font.render(SIMBOLI[suit], True, color)
        symbol_rect = symbol.get_rect(center=(size[0] // 2, size[1] // 2))
        surface.blit(symbol, symbol_rect)
        return surface

    def _build_card_back(self, size: Tuple[int, int]) -> pygame.Surface:
        custom_back_path = self.assets_root / "retro carte.png"
        if custom_back_path.exists():
            loaded = pygame.image.load(str(custom_back_path)).convert_alpha()
            return pygame.transform.smoothscale(loaded, size)

        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(CARD_BACK_COLOR)
        pygame.draw.rect(surface, CARD_BORDER_COLOR, surface.get_rect(), width=2, border_radius=10)
        inner = surface.get_rect().inflate(-20, -20)
        pygame.draw.rect(surface, (238, 225, 225), inner, width=2, border_radius=10)
        label = self.get_font(max(24, size[0] // 4), bold=True).render("SC", True, TEXT_COLOR)
        surface.blit(label, label.get_rect(center=surface.get_rect().center))
        return surface
