"""Scene manager for the Pygame application."""

from __future__ import annotations


class Scene:
    """Base scene interface."""

    def __init__(self, app) -> None:
        """Memorizza riferimento all'applicazione host della scena."""
        self.app = app

    def on_enter(self, previous_scene) -> None:
        """Hook chiamato quando la scena diventa attiva."""
        del previous_scene

    def on_exit(self, next_scene) -> None:
        """Hook chiamato prima di lasciare la scena corrente."""
        del next_scene

    def handle_event(self, event) -> None:
        """Gestione input/eventi; override nelle scene concrete."""
        del event

    def update(self, dt: float) -> None:
        """Aggiorna logica scena con delta-time frame."""
        del dt

    def render(self, renderer) -> None:
        """Disegna il frame corrente della scena."""
        del renderer


class SceneManager:
    """Tracks the active scene and scene transitions."""

    def __init__(self, app) -> None:
        """Inizializza manager con nessuna scena attiva."""
        self.app = app
        self.current_scene = None

    def change(self, scene: Scene) -> None:
        """Esegue transizione scena invocando hook di uscita/ingresso."""
        previous = self.current_scene
        if previous is not None:
            previous.on_exit(scene)
        self.current_scene = scene
        self.current_scene.on_enter(previous)

    def update(self, dt: float) -> None:
        """Propaga update alla scena attiva se presente."""
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def render(self, renderer) -> None:
        """Propaga render alla scena attiva se presente."""
        if self.current_scene is not None:
            self.current_scene.render(renderer)
