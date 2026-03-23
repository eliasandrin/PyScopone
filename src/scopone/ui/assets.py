"""Asset loading and caching for the Pygame UI."""

from pathlib import Path
from typing import Dict, Tuple

import pygame

from scopone.config.game import SIMBOLI
from scopone.config.ui import CARD_BACK_COLOR, CARD_BORDER_COLOR, CARD_FACE_COLOR, FONT_NAME, TEXT_COLOR
from scopone.types import Card


class AssetManager:
    """Loads fonts and card images with in-memory caches."""

    def __init__(self) -> None:
        self.assets_root = Path(__file__).resolve().parents[3] / "assets"
        self.cards_root = self.assets_root / "cards"
        self.fonts_root = self.assets_root / "fonts"
        self.font_cache = {}  # type: Dict[Tuple[str, int, bool], pygame.font.Font]
        self.surface_cache = {}  # type: Dict[Tuple[str, Tuple[int, int]], pygame.Surface]
        self.card_index = self._build_card_index()
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

    def _load_card_image(self, card: Card, size: Tuple[int, int]) -> pygame.Surface:
        value, suit = card
        for candidate in self._card_candidates(value, suit):
            path = self.card_index.get(candidate.lower())
            if path is None:
                continue
            loaded = pygame.image.load(str(path)).convert_alpha()
            return pygame.transform.smoothscale(loaded, size)
        return self._build_card_fallback(card, size)

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
