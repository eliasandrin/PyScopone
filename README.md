# PyScopone

Refactor architetturale di Scopone con package `src/`, motore UI/rendering in Pygame e logica di gioco isolata dal frontend.

## Struttura

```text
PyScopone/
├── assets/
│   ├── cards/
│   ├── audio/
│   └── fonts/
├── docs/
│   ├── architecture/
│   └── legacy/
├── src/
│   └── scopone/
│       ├── ai/
│       ├── config/
│       ├── engine/
│       ├── models/
│       ├── ui/
│       └── types.py
├── tests/
├── main.py
└── requirements.txt
```

## Avvio

1. Attiva l'ambiente virtuale del progetto.
2. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

3. Avvia il gioco:

```bash
python main.py
```

## Architettura

- `src/scopone/engine`: stato partita, turni, distribuzione, fine partita
- `src/scopone/engine/scoring.py`: prese, primiera e punteggi finali
- `src/scopone/ai`: strategie AI `easy`, `normal`, `expert`, `adaptive`
- `src/scopone/ui`: client Pygame con `GameApp`, scene, renderer e asset cache
- `assets/cards`: deck italiano da 40 carte usato dal renderer

La UI segue un game loop esplicito:

1. `process_input()`
2. `update_logic()`
3. `render_graphics()`

## Test

I test di regressione coprono:

- risoluzione delle prese
- regola “ultima carta non vale scopa”
- restock in modalita 2 giocatori
- punteggio a squadre in modalita 4 giocatori
- primiera, Denari, Carte e Settebello
- decisioni AI su stati fissi
- smoke test del client Pygame in modalita headless

Esecuzione:

```bash
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Documentazione

- `docs/architecture/pygame-ui.md`: panoramica della nuova architettura
- `docs/legacy/`: documentazione CustomTkinter archiviata e non piu sorgente di verita
