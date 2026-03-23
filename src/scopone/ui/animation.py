"""Non-blocking tween helpers for card motion."""

from __future__ import annotations

from typing import Callable, List, Optional

import pygame


def _lerp(start: float, end: float, progress: float) -> float:
    return start + ((end - start) * progress)


def _apply_easing(progress: float, easing: str) -> float:
    progress = min(max(progress, 0.0), 1.0)
    if easing == "ease_out":
        inverse = 1.0 - progress
        return 1.0 - (inverse * inverse * inverse)
    return progress


class CardTween:
    """Interpolates a card rect and angle over time without blocking the game loop."""

    def __init__(
        self,
        card,
        start_rect,
        target_rect,
        duration: float,
        face_up: bool = True,
        start_angle: float = 0.0,
        target_angle: float = 0.0,
        delay: float = 0.0,
        on_start: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
        layer: int = 0,
        easing: str = "linear",
        shadow: bool = False,
        shadow_alpha: int = 90,
        shadow_offset=(0, 6),
        interpolate_size: bool = True,
    ) -> None:
        self.card = card
        self.start_rect = pygame.Rect(start_rect)
        self.target_rect = pygame.Rect(target_rect)
        self.duration = max(duration, 0.001)
        self.face_up = face_up
        self.start_angle = float(start_angle)
        self.target_angle = float(target_angle)
        self.delay = max(delay, 0.0)
        self.on_start = on_start
        self.on_complete = on_complete
        self.layer = layer
        self.easing = easing
        self.shadow = shadow
        self.shadow_alpha = shadow_alpha
        self.shadow_offset = shadow_offset
        self.interpolate_size = interpolate_size

        self.elapsed = 0.0
        self.started = False
        self.completed = False

    def update(self, dt: float) -> bool:
        if self.completed:
            return True

        self.elapsed += dt

        if not self.started and self.elapsed >= self.delay:
            self.started = True
            if self.on_start is not None:
                self.on_start()

        if self.elapsed < self.delay:
            return False

        progress = min((self.elapsed - self.delay) / self.duration, 1.0)
        if progress >= 1.0:
            self.completed = True
            return True

        return False

    def get_rect(self) -> pygame.Rect:
        if not self.started and self.delay > 0.0:
            return self.start_rect.copy()

        progress = min(max((self.elapsed - self.delay) / self.duration, 0.0), 1.0)
        progress = _apply_easing(progress, self.easing)
        if self.interpolate_size:
            width = int(_lerp(self.start_rect.width, self.target_rect.width, progress))
            height = int(_lerp(self.start_rect.height, self.target_rect.height, progress))
        else:
            width = self.start_rect.width
            height = self.start_rect.height

        return pygame.Rect(
            int(_lerp(self.start_rect.x, self.target_rect.x, progress)),
            int(_lerp(self.start_rect.y, self.target_rect.y, progress)),
            width,
            height,
        )

    def get_angle(self) -> int:
        if not self.started and self.delay > 0.0:
            return int(round(self.start_angle))

        progress = min(max((self.elapsed - self.delay) / self.duration, 0.0), 1.0)
        progress = _apply_easing(progress, self.easing)
        return int(round(_lerp(self.start_angle, self.target_angle, progress)))


class AnimationManager:
    """Tracks active card tweens and renders them above the static board."""

    def __init__(self) -> None:
        self.animations = []  # type: List[CardTween]
        self._pending_additions = []  # type: List[CardTween]
        self._updating = False

    def clear(self) -> None:
        self.animations = []
        self._pending_additions = []

    def add(self, animation: CardTween) -> CardTween:
        if self._updating:
            self._pending_additions.append(animation)
        else:
            self.animations.append(animation)
        return animation

    def has_active(self) -> bool:
        return bool(self.animations)

    def update(self, dt: float) -> None:
        active = []
        completed = []
        self._updating = True
        for animation in self.animations:
            if animation.update(dt):
                completed.append(animation)
            else:
                active.append(animation)
        self._updating = False
        self.animations = active

        if self._pending_additions:
            self.animations.extend(self._pending_additions)
            self._pending_additions = []

        for animation in completed:
            if animation.on_complete is not None:
                animation.on_complete()

    def render(self, renderer) -> None:
        # Hard cleanup guard: completed tweens must never be rendered again.
        self.animations = [animation for animation in self.animations if not animation.completed]
        for animation in sorted(self.animations, key=lambda item: item.layer):
            if animation.shadow and (animation.get_angle() % 360 == 0):
                renderer.draw_card_shadow(
                    animation.get_rect(),
                    alpha=animation.shadow_alpha,
                    offset=animation.shadow_offset,
                )
            renderer.draw_card(
                animation.card,
                animation.get_rect(),
                face_up=animation.face_up,
                angle=animation.get_angle(),
                is_animating=True,
            )
