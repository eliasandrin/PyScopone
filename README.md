# PyScopone

Un'implementazione completa e professionale del tradizionale gioco di carte italiano "Scopone", con un motore logico disaccoppiato, intelligenza artificiale modulare e un'interfaccia grafica moderna basata su Pygame.

## Caratteristiche Principali

*   **Modalità di Gioco:** Supporta sia la **Partita Rapida** (singola smazzata da 40 carte) sia il **Torneo** a 21 punti (con memorizzazione dello storico punti round per round).
*   **Decoupling Totale:** L'interfaccia utente visiva e l'engine che fa i calcoli sono completamente slegati, facilitando l'estensione del codice.
*   **Animazioni Fluide:** Le animazioni a schermo non bloccano la logica ("tweening asincrono" integrato).
*   **Statistiche Dinamiche:** Visualizzazione live di Carte, Denari, Primiera, Settebello e Scope.

## Intelligenza Artificiale (AI)

Il gioco vanta una suite di avversari artificiali strutturati in scala di difficoltà:

*   🟢 **Divertimento (EasyAI)**: L'IA per chi vuole vincere facile o imparare le regole. Fa prese in maniera distratta (sceglie a caso tra quelle disponibili senza ottimizzare) e se non può prendere scarta carte casuali, rischiando di farvi regali.
*   🟡 **Normale (NormalAI)**: Un giocatore "avido" e concentrato. Cerca sempre di massimizzare la propria mossa calcolando chi cattura più carte, più Denari o il Settebello. *Punto debole:* non possiede una "memoria". Se non può fare punti immediati, scarta senza calcolare se l'avversario potrebbe fargli scopa.
*   🔴 **Esperto (ExpertAI)**: Un giocatore veterano e matematico. Usa le memorie del tavolo per calcolare il *Rischio Scopa* (Scopa Probability). Cerca sempre la mossa migliore ma se capisce matematicamente che scartare regalerà una scopa, opta per mosse difensive estreme e sacrifici. L'IA Esperta è anche capace di calcolare il **Guadagno Marginale della Primiera**: eviterà di fare prese con carte apparentemente forti (es. un 6) se la sua squadra possiede già una carta migliore (es. un 7) per quel particolare seme.

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
│       ├── ai/          # Strategie AI descritte sopra
│       ├── config/      # Costanti UI e Game Rules
│       ├── engine/      # Core logic, Tornei e Punteggi
│       ├── models/      # Entità dei Giocatori
│       ├── ui/          # Client Pygame, Animazioni, Scene
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

- `src/scopone/engine`: stato partita, tornei, turni, distribuzione, controlli di fine partita.
- `src/scopone/engine/scoring.py`: conteggio prese, primiera e aggregazione punteggi finali.
- `src/scopone/ui`: client Pygame con `GameApp`, sistema Multi-Scena, `MatchCoordinator` e renderer.

La UI segue un game loop esplicito:
1. `process_input()`
2. `update_logic()` (con interpolazione su delta-time `dt`)
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
