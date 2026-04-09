# Struttura Professionale del Progetto SCOPONE

## 📐 Architettura Modulare

Questa è una struttura **Enterprise-Grade** seguendo i pattern professionali:

### 1. **config/** - Centralizzazione delle Configurazioni
Tutti i parametri, costanti e settings in un unico luogo.

```
config/
├── __init__.py          # Esporta tutte le costanti
└── constants.py         # Costanti di gioco, colori, font, etc
```

**Vantaggi**:
- Facile modificare i parametri senza cercare nel codice
- Evita magic numbers sparsi
- Facile gestire diverse configurazioni (dev, prod, test)

---

### 2. **models/** - Entità di Dominio
Definisce gli oggetti di business (Player, Card).

```
models/
├── __init__.py          # Esporta Player e Card
├── player.py            # Classe Player con tutta la logica del giocatore
└── card.py              # Classe Card con utility per le carte
```

**Responsabilità**:
- `Player`: Stato e comportamento del giocatore
- `Card`: Rappresentazione e utility della carta

**Pattern**: Data Model / Entity

---

### 3. **engine/** - Core Business Logic
La logica di gioco pura, indipendente dalla UI.

```
engine/
├── __init__.py          # Esporta GameEngine e ScoringEngine
├── game_engine.py       # Orchestrazione del gioco
└── scoring.py           # Calcolo dei punti
```

**Components**:
- `GameEngine`: Gestore del flusso e stato di gioco
  - Gestisce turni
  - Gestisce carte
  - Gestisce tavolo
  - Emite eventi di gioco

- `ScoringEngine`: Calcolo punti (static methods)
  - Primiera calculation
  - Catture legali
  - Score finale
  - Ranking

**Pattern**: Game Engine / Business Logic

---

### 4. **ai/** - Intelligenza Artificiale
Strategie AI plug-and-play, facilmente estensibili.

```
ai/
├── __init__.py          # Esporta tutte le strategie
└── strategies.py        # Diverse difficoltà AI
```

**Strategie Disponibili**:

```
AIStrategy (Abstract)
├── EasyAI           → Casuale
├── NormalAI         → Cattura + carta bassa
└── ExpertAI         → Strategia avanzata
```

**Pattern**: Strategy Pattern + Factory Pattern

**Estensibilità**: Aggiungere nuova IA è semplice:
```python
class AdvancedAI(AIStrategy):
    def choose_card(self, hand, table):
        # Logica personalizzata
        pass
```

---

### 5. **ui/** - User Interface
Interfaccia grafica Tkinter, disaccoppiata dalla logica di gioco.

```
ui/
├── __init__.py          # Esporta ScoponeApp
└── app.py               # Classe principale GUI
```

**Responsabilità**:
- Rendering dell'interfaccia
- Gestione input utente
- Comunicazione con GameEngine
- Visualizzazione di stato

**Pattern**: MVC (Model-View-Controller)
- Model: `engine.GameEngine`
- View: `ui.ScoponeApp`
- Controller: `ui.ScoponeApp` (gestisce input → logica)

---

### 6. **utils/** - Funzioni Utility
Helpers e utility functions riutilizzabili.

```
utils/
├── __init__.py          # Esporta ImageLoader
└── image_loader.py      # Caricamento e caching immagini
```

**Responsabilità**:
- Gestione file system
- Caching
- Conversione dati

---

### 7. **main.py** - Entry Point
Punto di ingresso singolo dell'applicazione.

```python
if __name__ == "__main__":
    app = ScoponeApp()
    app.mainloop()
```

---

## 🔄 Flusso di Dati

```
main.py (Entry)
    ↓
ui.app.ScoponeApp (GUI)
    ↓
engine.game_engine.GameEngine (Game Logic)
    ├─ models.player.Player (State)
    ├─ models.card.Card (State)
    ├─ engine.scoring.ScoringEngine (Calculation)
    └─ ai.strategies.AIStrategy (Decision)
```

---

## 📦 Dipendenze Interne

```
ui/app.py imports from:
  ├─ config/constants.py      (Settings)
  ├─ engine/game_engine.py    (Logic)
  ├─ engine/scoring.py        (Scoring)
  ├─ models/player.py         (Data)
  ├─ models/card.py           (Data)
  ├─ ai/strategies.py         (AI)
  └─ utils/image_loader.py    (Utilities)

engine/game_engine.py imports from:
  ├─ config/constants.py      (Settings)
  ├─ models/player.py         (Data)
  └─ engine/scoring.py        (Scoring)

engine/scoring.py imports from:
  └─ config/constants.py      (Settings)

ai/strategies.py imports from:
  └─ engine/scoring.py        (Logic)
```

**Nessuna dipendenza circolare!** ✅

---

## 🏛️ Principi Applicati

### 1. **Single Responsibility Principle (SRP)**
Ogni classe ha una sola ragione per cambiare:
- `Player` → per cambiamenti allo stato del giocatore
- `GameEngine` → per cambiamenti alle regole di gioco
- `ScoponeApp` → per cambiamenti all'UI
- `ScoringEngine` → per cambiamenti al calcolo punteggi

### 2. **Open/Closed Principle (OCP)**
Aperto all'estensione, chiuso alla modifica:
- Nuove strategie AI → aggiungi classe, non modificare le vecchie
- Nuovi colori → modifica constants.py
- Nuove regole → estendi ScoringEngine

### 3. **Dependency Inversion (DIP)**
Dipende da astrazioni, non da implementazioni:
- `ui/app.py` dipende da `engine.GameEngine` (astratto)
- `ai/` usa `AIStrategy` (interface)

### 4. **Composition over Inheritance**
- `GameEngine` compone `Player`, `Card`, `ScoringEngine`
- Non usa ereditarietà inutile

---

## 🧪 Testabilità

Grazie all'architettura modulare, puoi testare facilmente:

```python
# Testare GameEngine senza UI
engine = GameEngine(4, ["Player1", "AI1", "AI2", "AI3"])
engine.reset()
engine.deal_cards()
assert len(engine.players) == 4

# Testare ScoringEngine in isolamento
cards = [(7, 'Denari'), (6, 'Denari')]
score = ScoringEngine.calculate_primiera(cards)
assert score == 39

# Testare AI Strategy
ai = NormalAI()
card = ai.choose_card(hand, table)
assert card in hand
```

---

## 🚀 Scalabilità

### Aggiungere Variante di Gioco
1. Crea `models/variant.py` per nuove regole
2. Crea `engine/variant_engine.py` che estende `GameEngine`
3. Crea `ui/variant_app.py` che usa il nuovo engine

### Aggiungere Statistiche Avanzate
1. Crea `utils/statistics.py`
2. Registra dati in `GameEngine`
3. Visualizza in `ui/app.py`

### Aggiungere Network Play
1. Crea `network/client.py` e `network/server.py`
2. UI invia comandi a `network/client.py`
3. Client comunica con server
4. Server orchestrazione condivisa su `GameEngine`

---

## 📊 Metriche di Qualità

### Coesione: **Alta** ✅
- Ogni modulo è focato
- Funzioni correlate insieme

### Accoppiamento: **Basso** ✅
- Pochi import tra moduli
- Interfacce ben definite
- Facilmente testabile

### Manutenibilità: **Alta** ✅
- Codice autodocumentato
- Commenti abbondanti
- Nomi chiari e descrittivi

### Estendibilità: **Alta** ✅
- Pattern di design usati
- Punti di estensione evidenti
- Facile aggiungere nuovo codice

---

## 📚 Convenzioni

### Naming
- `classes`: `CamelCase` (e.g., `GameEngine`, `ScoponeApp`)
- `functions`: `snake_case` (e.g., `check_turn()`, `play_card()`)
- `constants`: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PLAYERS`)
- `private`: `_leading_underscore` (e.g., `_verify_directory()`)

### Module Organization
- Imports: Standard → Third-party → Local
- Docstrings: Google style
- Type hints: Dove utile (in docstrings se Python < 3.5)

### Comments
- Commenti soprattutto per **perché**, non **cosa**
- Docstrings per tutte le public classes/methods
- TODO comments per future improvements

---

## 🔐 Best Practices Implementate

✅ **Separation of Concerns** - Ogni modulo ha responsabilità distinct
✅ **DRY** (Don't Repeat Yourself) - Utilità centralizzate
✅ **KISS** (Keep It Simple) - Codice leggibile prima di tutto
✅ **Error Handling** - Try-catch dove necessario
✅ **Logging** - Log system per debugging
✅ **Configuration** - Settings centralizzati
✅ **Type Safety** - Validation input
✅ **Documentation** - Docstrings completi

---

## 🎓 Conclusione

Questa struttura è:
- **Professionale**: Follow industry standards
- **Scalabile**: Facile aggiungere features
- **Mantenibile**: Chiarezza e organizzazione
- **Testabile**: Componenti isolabili
- **Estensibile**: Punti di estensione evidenti

Perfetta per un **portfolio professionale** o **applicazione enterprise**! 🚀
