"""Input controller for dispatching Pygame events to the active scene."""


class InputController:
    """Forwards raw Pygame events to the active scene."""

    def process(self, events, scene) -> None:
        if scene is None:
            return
        for event in events:
            scene.handle_event(event)
