import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from scopone.config.game import MODE_QUICK
from scopone.config.ui import FPS, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from scopone.ui.audio import AudioManager
from scopone.ui.assets import AssetManager
from scopone.ui.controller import InputController
from scopone.ui.renderer import Renderer
from scopone.ui.scene_manager import SceneManager
from scopone.ui.scenes.setup_scene import SetupScene


class GameApp:
    """Coordinates the Pygame lifecycle, scenes, and rendering loop."""

    def __init__(self, headless: bool = False) -> None:
        """Inizializza sottosistemi Pygame, manager UI e scena iniziale."""
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.font.init()
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except pygame.error:
            pass

        self.clock = pygame.time.Clock()
        self.running = True
        self.is_fullscreen = False
        self.is_muted = False
        self.windowed_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.assets = AssetManager()
        self.audio = AudioManager()
        self.screen = self._set_display_mode(self.windowed_size, fullscreen=False)
        self.renderer = Renderer(self.screen, self.assets)
        self.controller = InputController()
        self.scene_manager = SceneManager(self)
        self.scene_manager.change(SetupScene(self))

    def show_setup(self) -> None:
        """Passa alla scena di configurazione partita."""
        from scopone.ui.scenes.setup_scene import SetupScene

        self.scene_manager.change(SetupScene(self))

    def start_match(
        self,
        num_players: int,
        difficulty: str,
        show_all_cards: bool,
        game_mode: str = MODE_QUICK,
    ) -> None:
        """Crea e attiva la MatchScene con i parametri scelti dall'utente."""
        from scopone.ui.scenes.match_scene import MatchScene

        self.scene_manager.change(
            MatchScene(
                self,
                {
                    "num_players": num_players,
                    "difficulty": difficulty,
                    "show_all_cards": show_all_cards,
                    "game_mode": game_mode,
                },
            )
        )

    def show_results(self, final_scores, settings, log_messages):
        """Apre la scena risultati passando punteggi e storico utile alla UI."""
        from scopone.ui.scenes.results_scene import ResultsScene

        self.scene_manager.change(ResultsScene(self, final_scores, settings, log_messages))

    def request_quit(self) -> None:
        """Richiede uscita pulita dal loop principale."""
        self.running = False

    def toggle_mute(self) -> None:
        """Attiva/disattiva audio globale mantenendo stato coerente in UI."""
        self.is_muted = not self.is_muted
        self.audio.set_muted(self.is_muted)

    def toggle_fullscreen(self) -> None:
        """Alterna fullscreen/windowed e riallinea renderer sulla nuova surface."""
        target_fullscreen = not self.is_fullscreen
        self.screen = self._set_display_mode(self.windowed_size, fullscreen=target_fullscreen)
        self.renderer.set_surface(self.screen)
        self.is_fullscreen = target_fullscreen

    def _set_display_mode(self, size, fullscreen=False):
        """Configura modalita finestra e restituisce nuova display surface."""
        # Rebuilding the display surface forces every scene to recompute its layout
        # against the new screen size on the next render pass.
        if fullscreen:
            info = pygame.display.Info()
            size = (info.current_w, info.current_h)
            flags = pygame.FULLSCREEN
        else:
            width = max(size[0], MIN_WINDOW_WIDTH)
            height = max(size[1], MIN_WINDOW_HEIGHT)
            size = (width, height)
            self.windowed_size = size
            flags = pygame.RESIZABLE

        screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption(WINDOW_TITLE)
        return screen

    def process_input(self) -> None:
        """Raccoglie eventi globali e delega input alla scena attiva."""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                width = max(event.w, MIN_WINDOW_WIDTH)
                height = max(event.h, MIN_WINDOW_HEIGHT)
                self.screen = self._set_display_mode((width, height), fullscreen=False)
                self.renderer.set_surface(self.screen)

        self.controller.process(events, self.scene_manager.current_scene)

    def update_logic(self, dt: float) -> None:
        """Aggiorna la logica della scena attiva con delta-time."""
        self.scene_manager.update(dt)

    def render_graphics(self) -> None:
        """Renderizza frame corrente e presenta il buffer video."""
        self.scene_manager.render(self.renderer)
        pygame.display.flip()

    def run(self, max_frames=None):
        """Esegue game loop principale fino a richiesta uscita o frame limite."""
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
        """Rilascia risorse Pygame a fine applicazione."""
        pygame.quit()


def main() -> int:
    """Entry point applicativo per avvio client Pygame."""
    app = GameApp()
    try:
        return app.run()
    finally:
        app.shutdown()
