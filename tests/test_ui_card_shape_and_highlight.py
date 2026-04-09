import sys
import unittest
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ui.assets import AssetManager


class UICardShapeAndHighlightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_card_back_has_transparent_rounded_corners(self):
        manager = AssetManager()
        card_back = manager.get_card_back_surface((96, 144))

        self.assertEqual(card_back.get_at((0, 0)).a, 0)
        self.assertEqual(card_back.get_at((95, 0)).a, 0)
        self.assertEqual(card_back.get_at((0, 143)).a, 0)
        self.assertEqual(card_back.get_at((95, 143)).a, 0)
        self.assertGreater(card_back.get_at((48, 72)).a, 0)

    def test_face_up_card_has_transparent_rounded_corners(self):
        manager = AssetManager()
        card_front = manager.get_card_surface((7, "Denari"), (96, 144), face_up=True)

        self.assertEqual(card_front.get_at((0, 0)).a, 0)
        self.assertEqual(card_front.get_at((95, 0)).a, 0)
        self.assertEqual(card_front.get_at((0, 143)).a, 0)
        self.assertEqual(card_front.get_at((95, 143)).a, 0)
        self.assertGreater(card_front.get_at((48, 72)).a, 0)

    def test_highlight_sanitizer_removes_uniform_corner_background(self):
        manager = AssetManager()
        raw = pygame.Surface((20, 20), pygame.SRCALPHA)
        raw.fill((255, 255, 255, 255))
        pygame.draw.circle(raw, (30, 180, 220, 255), (10, 10), 6)

        sanitized = manager._sanitize_highlight_surface(raw)

        self.assertEqual(sanitized.get_at((0, 0)).a, 0)
        self.assertGreater(sanitized.get_at((10, 10)).a, 0)


if __name__ == "__main__":
    unittest.main()
