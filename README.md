# PyScopone

Implementazione di Scopone in Python con GUI Pygame, engine separato dalla UI e livelli AI multipli.

## Obiettivo del progetto

- riprodurre il gioco in modo fedele
- mantenere codice modulare e didattico
- supportare demo live (2 o 4 giocatori)

## Funzionalita attive

- Modalita Partita Rapida
- Modalita Torneo a punteggio target (configurabile in [src/scopone/config/game.py](src/scopone/config/game.py#L1))
- AI a 3 livelli: Divertimento, Normale, Esperto
- UI Pygame con scene dedicate: setup, partita, risultati
- animazioni non bloccanti e overlay di fine smazzata

## Avvio rapido

1. Crea/attiva ambiente virtuale Python 3.13+
2. Installa dipendenze:

```bash
pip install -r requirements.txt
```

3. Avvia:

```bash
python main.py
```

## Test

Esegui tutta la suite:

```bash
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Struttura essenziale

```text
PyScopone/
|-- main.py
|-- src/scopone/
|   |-- ai/
|   |-- config/
|   |-- engine/
|   |-- models/
|   |-- ui/
|   `-- types.py
|-- tests/
|-- assets/
`-- docs/
```

## Documentazione finale

- [docs/PROJECT_MAP.md](docs/PROJECT_MAP.md): mappa completa file/classi/responsabilita e flusso architetturale
- [docs/PRESENTAZIONE.md](docs/PRESENTAZIONE.md): testo pronto per esposizione in classe

## Note di manutenzione

- Nessuna logica di gioco e stata rimossa in questa fase di cleanup.
- La documentazione legacy e stata eliminata per evitare contraddizioni con lo stato attuale del codice.
