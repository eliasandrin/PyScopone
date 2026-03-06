# PyScopone

A Python command-line implementation of the classic Italian card game **Scopone**.

## Game Rules

Scopone is a 4-player trick-taking card game played with a traditional Italian
40-card deck (Coins, Cups, Swords, Clubs – ranks Ace through King).

### Setup

* **Players**: 4 players split into 2 teams of 2 (partners sit across from each other).
  In this implementation you play against 3 AI opponents:
  `You + CPU-2` form **Team A**, `CPU-1 + CPU-3` form **Team B**.
* **Deal**: All 40 cards are dealt – 10 cards to each player.  The table starts empty.

### Turn

On your turn you play one card from your hand:

1. **Capture** – If a card on the table has the same value as the card you played,
   you *must* capture it (if multiple singles match, you choose which one).
   If no single-card match exists but a *combination* of table cards sums to your
   card's value, you may capture that combination.
2. **No capture** – If neither is possible, your card is left on the table.

### Scopa (Sweep)

If your capture clears all cards from the table you score a **scopa** (bonus point).

### Scoring (per round)

| Category | Winner | Points |
|---|---|---|
| **Cards** (Carte) | Team with more captured cards (21+) | 1 |
| **Coins** (Ori) | Team with more captured Coins (6+) | 1 |
| **Sette Bello** | Team that captured the 7 of Coins | 1 |
| **Primiera** | Team with higher primiera total* | 1 |
| **Scope** | Each scopa earned | 1 each |

*Primiera values: 7=21, 6=18, Ace=16, 5=15, 4=14, 3=13, 2=12, face cards=10.
The team's best card from each suit is used; the sum of the four values is compared.

### Winning

The first team to reach **11 points** across rounds wins the game.

---

## Project Structure

```
PyScopone/
├── main.py              # Entry point – run this to play
├── scopone/
│   ├── __init__.py
│   ├── card.py          # Card, Deck, find_capture_combinations
│   ├── player.py        # Player, Team
│   └── game.py          # Game loop and scoring
└── tests/
    ├── test_card.py
    └── test_game.py
```

## How to Play

```bash
python main.py
```

On your turn:
1. The table cards are shown.
2. Your hand is displayed with numbered slots.
3. Enter the number of the card you want to play.
4. If a capture is possible (and multiple options exist) you will be asked to
   choose one.

## Running the Tests

```bash
pip install pytest
python -m pytest tests/ -v
```
