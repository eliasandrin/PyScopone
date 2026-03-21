"""Scene manager for the Pygame application."""

from __future__ import annotations


class Scene:
    """Base scene interface."""

    def __init__(self, app) -> None:
        self.app = app

    def on_enter(self, previous_scene) -> None:
        del previous_scene

    def on_exit(self, next_scene) -> None:
        del next_scene

    def handle_event(self, event) -> None:
        del event

    def update(self, dt: float) -> None:
        del dt

    def render(self, renderer) -> None:
        del renderer


class SceneManager:
    """Tracks the active scene and scene transitions."""

    def __init__(self, app) -> None:
        self.app = app
        self.current_scene = None

    def change(self, scene: Scene) -> None:
        previous = self.current_scene
        if previous is not None:
            previous.on_exit(scene)
        self.current_scene = scene
        self.current_scene.on_enter(previous)

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def render(self, renderer) -> None:
        if self.current_scene is not None:
            self.current_scene.render(renderer)
