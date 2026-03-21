# Pygame UI Architecture

## Overview

Il client Pygame e organizzato in livelli:

- `game_app.py`: bootstrap, finestra, clock, loop applicativo
- `controller.py`: dispatch degli eventi Pygame verso la scena attiva
- `scene_manager.py`: transizioni tra setup, match e risultati
- `renderer.py`: primitive di rendering per pannelli, testo, pulsanti e carte
- `assets.py`: cache di font e immagini carte

## Scene Flow

1. `SetupScene` raccoglie impostazioni della partita.
2. `MatchScene` collega input umano, turni AI e rendering del tavolo.
3. `ResultsScene` mostra classifica finale e azioni successive.

## Game Loop

`GameApp.run()` mantiene tre fasi distinte per frame:

1. `process_input()`
2. `update_logic()`
3. `render_graphics()`

Questo mantiene la logica di gioco del package `engine` completamente separata dal rendering.
