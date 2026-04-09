# PROJECT MAP - PyScopone

## 1. Panoramica

Questo file descrive i file importanti del repository, le classi principali e il flusso architetturale.

## 2. File Root

| File | Ruolo |
|---|---|
| `main.py` | Entry point desktop. Imposta DPI awareness su Windows e avvia `GameApp`. |
| `README.md` | Guida rapida progetto, avvio, test e link documentazione finale. |
| `requirements.txt` | Dipendenze runtime (`pygame`). |
| `LICENSE` | Licenza del progetto. |
| `AGENTS.md` | Linee guida operative per coding agent (non influenza il gameplay). |

## 3. Source Map (`src/scopone`)

### 3.1 Package `scopone`

| File | Ruolo | Classi |
|---|---|---|
| `src/scopone/__init__.py` | Marker package. | - |
| `src/scopone/types.py` | Tipi condivisi (`Card`, `Suit`, `TeamId`). | - |

### 3.2 Package `scopone/config`

| File | Ruolo | Classi |
|---|---|---|
| `src/scopone/config/__init__.py` | Marker package config. | - |
| `src/scopone/config/game.py` | Costanti regole, deck, modalita, target torneo, team setup. | - |
| `src/scopone/config/ui.py` | Costanti visuali UI (colori, dimensioni, fps, timing UI). | - |

### 3.3 Package `scopone/models`

| File | Ruolo | Classi |
|---|---|---|
| `src/scopone/models/__init__.py` | Marker package model. | - |
| `src/scopone/models/player.py` | Entita giocatore: mano, prese, scope, metodi utility. | `Player` |

### 3.4 Package `scopone/engine`

| File | Ruolo | Classi |
|---|---|---|
| `src/scopone/engine/__init__.py` | Marker package engine. | - |
| `src/scopone/engine/game_engine.py` | Stato partita, distribuzione, play card, restock 2-player, round/torneo lifecycle. | `GameEngine` |
| `src/scopone/engine/scoring.py` | Ricerca prese legali, punteggio finale, primiera, tie-handling deterministico. | `ScorePoints`, `PointsBreakdown`, `Bonuses`, `RawStats`, `ScoreEntry`, `SupportsScoringPlayer`, `ScoringEngine` |

### 3.5 Package `scopone/ai`

| File | Ruolo | Classi |
|---|---|---|
| `src/scopone/ai/__init__.py` | Marker package AI. | - |
| `src/scopone/ai/strategies.py` | Strategie AI e factory difficolta. | `AIStrategy`, `EasyAI`, `NormalAI`, `ExpertAI` |

### 3.6 Package `scopone/ui`

| File | Ruolo | Classi |
|---|---|---|
| `src/scopone/ui/__init__.py` | Marker package UI. | - |
| `src/scopone/ui/game_app.py` | Bootstrap Pygame, game loop, scene switching globale, lifecycle app. | `GameApp` |
| `src/scopone/ui/controller.py` | Dispatch eventi alla scena attiva. | `InputController` |
| `src/scopone/ui/scene_manager.py` | Interfaccia scene e manager transizioni. | `Scene`, `SceneManager` |
| `src/scopone/ui/renderer.py` | Primitive rendering (panel, testo, pulsanti, carte, shadow, highlight). | `Renderer` |
| `src/scopone/ui/assets.py` | Caricamento/caching asset (atlas carte, font, fallback). | `AssetManager` |
| `src/scopone/ui/audio.py` | Effetti audio con fallback PCM procedurale. | `AudioManager` |
| `src/scopone/ui/backgrounds.py` | Background dinamico condiviso scene. | - |
| `src/scopone/ui/animation.py` | Tween e manager animazioni non bloccanti. | `CardTween`, `AnimationManager` |
| `src/scopone/ui/board_view.py` | Layout board responsivo e render orchestrator stato statico. | `RenderBoard`, `BoardView` |
| `src/scopone/ui/match_coordinator.py` | Orchestrazione turni umano/AI e transizioni round/game over. | `MatchCoordinator` |
| `src/scopone/ui/round_overlay_manager.py` | Overlay fine smazzata e prompt conferma round successivo. | `RoundOverlayManager` |

### 3.7 Package `scopone/ui/scenes`

| File | Ruolo | Classi |
|---|---|---|
| `src/scopone/ui/scenes/__init__.py` | Marker package scene. | - |
| `src/scopone/ui/scenes/setup_scene.py` | Configurazione partita prima dell'avvio. | `SetupScene` |
| `src/scopone/ui/scenes/match_scene.py` | Scena di gioco live: rendering tavolo, input, menu, log, overlay scelta prese. | `MatchScene` |
| `src/scopone/ui/scenes/results_scene.py` | Scena risultati finali e azioni post-match. | `ResultsScene` |

## 4. Test Map (`tests`)

| File | Ruolo |
|---|---|
| `tests/test_game_engine.py` | Regressioni engine (play, restock, round end, decision logs). |
| `tests/test_scoring.py` | Regressioni punteggi, primiera, winners, tie handling. |
| `tests/test_ai_strategies.py` | Comportamento AI per livello e motivazioni decision log. |
| `tests/test_ai_latency.py` | Guardrail latenza `ExpertAI` su scenari realistici. |
| `tests/test_ai_balance_simulation.py` | Bilanciamento probabilistico esperto>normale>easy. |
| `tests/test_animation_manager.py` | Tween/animation manager correctness. |
| `tests/test_match_coordinator.py` | Orchestrazione scelta prese e move dispatch in scena match. |
| `tests/test_match_scene_live_scores.py` | Integrita punteggi live in torneo dopo fine round. |
| `tests/test_match_scene_capture_preview.py` | Regole preview highlight prese minime non ambigue. |
| `tests/test_ui_asset_atlas_cells.py` | Mapping celle atlas per retro/highlight. |
| `tests/test_ui_card_shape_and_highlight.py` | Trasparenza angoli carta e sanitizzazione highlight. |
| `tests/test_pygame_app_smoke.py` | Smoke test headless startup/render 1 frame. |

## 5. Flusso Architetturale

1. `main.py` prepara ambiente e avvia `GameApp`.
2. `GameApp` crea `AssetManager`, `Renderer`, `SceneManager`.
3. `SceneManager` attiva `SetupScene`.
4. Da setup si entra in `MatchScene` con parametri partita.
5. `MatchScene` usa:
   - `GameEngine` per stato e regole,
   - `MatchCoordinator` per turn-flow,
   - `BoardView` + `Renderer` per output video,
   - `AnimationManager` per tweens.
6. A fine partita, `ResultsScene` mostra score e consente restart/menu.

## 6. Stato Cleanup (verificato)

- Moduli Python orfani trovati: `0`.
- Nessuna classe core attiva rimossa in questa fase.
- Test mantenuti: tutti, perche legati a codice attivo e utili in regressione/demo.
