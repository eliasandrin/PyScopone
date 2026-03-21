import sys
import unittest
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scopone.ui.animation import AnimationManager, CardTween


class AnimationManagerTests(unittest.TestCase):
    def test_card_tween_interpolates_rect_and_angle(self):
        tween = CardTween(
            card=(1, "Denari"),
            start_rect=pygame.Rect(0, 0, 10, 20),
            target_rect=pygame.Rect(100, 40, 30, 50),
            duration=1.0,
            start_angle=90,
            target_angle=0,
        )

        tween.update(0.5)
        halfway = tween.get_rect()

        self.assertEqual(halfway.x, 50)
        self.assertEqual(halfway.y, 20)
        self.assertEqual(halfway.width, 20)
        self.assertEqual(halfway.height, 35)
        self.assertEqual(tween.get_angle(), 45)

    def test_manager_preserves_animations_added_from_completion_callback(self):
        manager = AnimationManager()

        def chain():
            manager.add(
                CardTween(
                    card=(2, "Coppe"),
                    start_rect=pygame.Rect(10, 0, 10, 10),
                    target_rect=pygame.Rect(20, 0, 10, 10),
                    duration=0.2,
                )
            )

        manager.add(
            CardTween(
                card=(1, "Denari"),
                start_rect=pygame.Rect(0, 0, 10, 10),
                target_rect=pygame.Rect(10, 0, 10, 10),
                duration=0.2,
                on_complete=chain,
            )
        )

        manager.update(0.2)
        self.assertTrue(manager.has_active())
        manager.update(0.2)
        self.assertFalse(manager.has_active())


if __name__ == "__main__":
    unittest.main()
