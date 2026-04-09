import sys
import unittest
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ui.assets import AssetManager


class UIAssetAtlasCellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def _build_mock_atlas(self):
        atlas = pygame.Surface((100, 50), pygame.SRCALPHA)
        for row in range(5):
            for col in range(10):
                color = (row * 40, col * 20, 150, 255)
                cell_rect = pygame.Rect(col * 10, row * 10, 10, 10)
                atlas.fill(color, cell_rect)

        # Add foreground detail to the highlight cell (row 5, col 10) so
        # background keying keeps a visible overlay payload.
        pygame.draw.circle(atlas, (24, 214, 182, 255), (95, 45), 3)
        return atlas

    def _assert_color_close(self, actual, expected, tolerance=8):
        for channel in range(3):
            self.assertLessEqual(abs(actual[channel] - expected[channel]), tolerance)

    def test_card_back_uses_configured_atlas_cell(self):
        manager = AssetManager()
        manager.atlas_surface = self._build_mock_atlas()
        manager.surface_cache.pop(("card-back", (60, 90)), None)

        surface = manager.get_card_back_surface((60, 90))
        sampled = surface.get_at((surface.get_width() // 2, surface.get_height() // 2))

        self._assert_color_close(sampled, (160, 40, 150))

    def test_capture_highlight_uses_configured_atlas_cell(self):
        manager = AssetManager()
        manager.atlas_surface = self._build_mock_atlas()
        manager.surface_cache.pop(("capture-highlight", (60, 90)), None)

        surface = manager.get_capture_highlight_surface((60, 90))
        sampled = surface.get_at((surface.get_width() // 2, surface.get_height() // 2))

        self._assert_color_close(sampled, (24, 214, 182), tolerance=24)


if __name__ == "__main__":
    unittest.main()
