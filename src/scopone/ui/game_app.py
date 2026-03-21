import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from scopone.config.ui import FPS, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from scopone.ui.assets import AssetManager
from scopone.ui.controller import InputController
from scopone.ui.renderer import Renderer
from scopone.ui.scene_manager import SceneManager
from scopone.ui.scenes.setup_scene import SetupScene


class GameApp:
    """Coordinates the Pygame lifecycle, scenes, and rendering loop."""

    def __init__(self, headless: bool = False) -> None:
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

        pygame.init()
        pygame.font.init()

        self.display_flags = pygame.RESIZABLE
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), self.display_flags)
        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.assets = AssetManager()
        self.renderer = Renderer(self.screen, self.assets)
        self.controller = InputController()
        self.scene_manager = SceneManager(self)
        self.scene_manager.change(SetupScene(self))

    def show_setup(self) -> None:
        from scopone.ui.scenes.setup_scene import SetupScene

        self.scene_manager.change(SetupScene(self))

    def start_match(self, num_players: int, difficulty: str, show_all_cards: bool) -> None:
        from scopone.ui.scenes.match_scene import MatchScene

        self.scene_manager.change(
            MatchScene(
                self,
                {
                    "num_players": num_players,
                    "difficulty": difficulty,
                    "show_all_cards": show_all_cards,
                },
            )
        )

    def show_results(self, final_scores, settings, log_messages):
        from scopone.ui.scenes.results_scene import ResultsScene

        self.scene_manager.change(ResultsScene(self, final_scores, settings, log_messages))

    def request_quit(self) -> None:
        self.running = False

    def process_input(self) -> None:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                width = max(event.w, MIN_WINDOW_WIDTH)
                height = max(event.h, MIN_WINDOW_HEIGHT)
                self.screen = pygame.display.set_mode((width, height), self.display_flags)
                self.renderer.set_surface(self.screen)

        self.controller.process(events, self.scene_manager.current_scene)

    def update_logic(self, dt: float) -> None:
        self.scene_manager.update(dt)

    def render_graphics(self) -> None:
        self.scene_manager.render(self.renderer)
        pygame.display.flip()

    def run(self, max_frames=None):
        frames = 0
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.process_input()
            self.update_logic(dt)
            self.render_graphics()
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
        return 0

    def shutdown(self) -> None:
        pygame.quit()


def main() -> int:
    app = GameApp()
    try:
        return app.run()
    finally:
        app.shutdown()
