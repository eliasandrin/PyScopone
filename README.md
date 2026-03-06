# SCOPONE - Traditional Italian Card Game

Implementazione completa e professionale del gioco di carte italiano "Scopone" con AI giocatori, interfaccia GUI moderna e sistema di punteggio secondo le regole tradizionali.

## 📋 Descrizione Progetto

SCOPONE è un gioco di carte italiano classico per 2-6 giocatori. Questo progetto fornisce:

- ✅ Implementazione completa delle regole del gioco
- ✅ Giocatori AI con multiple difficoltà (Facile, Normale, Esperto, Adattivo)
- ✅ Interfaccia GUI intuitiva e moderna
- ✅ Sistema di punteggio completo (Primiera, Carte, Denari, Settebello, Scope)
- ✅ Modalità principianti (tutte le carte visibili)
- ✅ Architettura professionale e modulare

## 🏗️ Struttura Progetto

```
scopa_refactored/
├── config/
│   ├── __init__.py
│   └── constants.py              # Costanti e configurazioni globali
├── models/
│   ├── __init__.py
│   ├── card.py                   # Modello Carta
│   └── player.py                 # Modello Giocatore
├── engine/
│   ├── __init__.py
│   ├── game_engine.py            # Motore del gioco
│   └── scoring.py                # Sistema di punteggio
├── ai/
│   ├── __init__.py
│   └── strategies.py             # Strategie AI (Easy, Normal, Expert, Adaptive)
├── ui/
│   ├── __init__.py
│   └── app.py                    # Interfaccia GUI principale
├── utils/
│   ├── __init__.py
│   └── image_loader.py           # Gestione caricamento immagini
├── main.py                       # Entry point dell'applicazione
├── requirements.txt              # Dipendenze Python
└── README.md                     # Questo file
```

## 🎯 Principi Architetturali

### Separation of Concerns
- **config**: Centralizza tutte le costanti e configurazioni
- **models**: Definisce le entità di gioco (Player, Card)
- **engine**: Logica di gioco pura (indipendente dalla GUI)
- **ai**: Strategie AI facilmente estensibili
- **ui**: Interfaccia utente disaccoppiata dalla logica
- **utils**: Funzioni utility riutilizzabili

### Modularità
Ogni modulo ha una responsabilità ben definita e può essere:
- Testato indipendentemente
- Modificato senza impattare altri moduli
- Esteso e migliorato facilmente

### Scalabilità
- Facile aggiungere nuove strategie AI
- Facile aggiungere nuove varianti di gioco
- Facile estendere il sistema di punteggio

## 🎮 Regole del Gioco

### Obiettivo
Ottenere più punti dell'avversario catturando le carte giuste.

### Sistema di Punteggio
- **1 punto**: Per avere più di 20 carte catturate
- **1 punto**: Per avere più di 5 Denari (carte di Denari)
- **1 punto**: Per avere il 7 di Denari (Settebello)
- **1 punto**: Per avere la miglior Primiera (combinazione di valori)
- **1 punto per scopa**: Svuotare il tavolo (catturare tutte le carte)

### Primiera
Il valore della carta più alta di ogni seme:
- 7 = 21 punti
- 6 = 18 punti
- 1 (Asso) = 16 punti
- 5 = 15 punti
- 4 = 14 punti
- 3 = 13 punti
- 2 = 12 punti
- 8, 9, 10 = 10 punti

## 🚀 Come Iniziare

### Prerequisiti
- Python 3.7+
- Pillow (per gestire le immagini)

### Installazione

1. **Installa le dipendenze**:
```bash
pip install -r requirements.txt
```

2. **Configura le immagini delle carte**:
   
   Le immagini delle carte devono essere in una cartella `carte/`. Il gioco cerca automaticamente in:
   - `scopa_refactored/carte/` (locale al progetto)
   - `../scopa/carte/` (cartella fratella, default se già esiste)
   - `../scopone/carte/` (alternativa)
   
   **Nomenclatura immagini**: `{valore}_{seme}.jpg` (es: `7_denari.jpg`, `1_coppe.jpg`)

3. **Avvia l'applicazione**:
```bash
python main.py
```

### Primo Avvio

1. Seleziona "MODO PER PRINCIPIANTI" per vedere tutte le carte
2. Scegli la difficoltà AI (consigliato: Normale)
3. Seleziona il numero di giocatori (default: 4)
4. Clicca "INIZIA PARTITA"
5. Clicca sulle tue carte nel basso della schermata per giocarle

## 📖 Guida Utente

### Interfaccia Principale

- **Barra Superiore**: Mostra il giocatore corrente e controlli rapidi
- **Tavolo Centrale**: Mostra le carte sul tavolo
- **Riquadri Giocatori**: Mostrano mano e carte catturate di ogni giocatore
- **Log di Gioco**: A destra, mostra gli eventi della partita in tempo reale

### Modalità Gioco

- **Modo Principianti**: Tutte le carte sono visibili (ideale per imparare)
- **Modo Normale**: Le carte dei giocatori IA sono nascoste (sfida reale)

### Difficoltà AI

- **Facile**: IA gioca carte casuali
- **Normale**: IA prova a catturare, altrimenti gioca la carta più bassa
- **Esperto**: IA usa strategie avanzate (catture multiple, pianificazione)
- **Adattivo**: IA si adatta alla situazione di gioco in tempo reale

## 💻 Architettura Tecnica

### Flusso di Gioco

```
main.py
  ↓
ui/app.py (Interfaccia GUI)
  ↓
engine/game_engine.py (Logica di gioco)
  ├─ models/player.py (Giocatori)
  ├─ models/card.py (Carte)
  ├─ engine/scoring.py (Punteggio)
  └─ ai/strategies.py (Strategie AI)
```

### Moduli Principali

#### `engine.game_engine.GameEngine`
Il cuore del gioco. Gestisce:
- Inizializzazione gioco
- Distribuzione carte
- Turni giocatori
- Cattura carte
- Calcolo score finale

#### `engine.scoring.ScoringEngine`
Calcola i punteggi secondo le regole:
- Primiera per ogni seme
- Conteggio carte e Denari
- Assegnazione punti categoria
- Ranking finale giocatori

#### `ai.strategies.*AI`
Diverse strategie di intelligenza artificiale:
- `EasyAI`: Casuale
- `NormalAI`: Cattura quando possibile
- `ExpertAI`: Strategia avanzata
- `AdaptiveAI`: Adattivo e complesso

#### `ui.app.ScoponeApp`
Interfaccia grafica Tkinter:
- Setup gioco
- Rendering tavolo e mano
- Input umano
- Log messaggi
- Statistiche

## 🔧 Sviluppo e Estensione

### Aggiungere una Nuova Strategia AI

```python
# In ai/strategies.py
class MyAI(AIStrategy):
    def choose_card(self, hand, table_cards):
        # Logica personalizzata
        return selected_card
```

### Personalizzare la Grafica

Modifica i colori in `config/constants.py`:
```python
COLOR_BG_PRIMARY = "#0e0e0e"  # Sfondo principale
COLOR_ACCENT_GREEN = "#2ecc71"  # Colore accento
```

### Aggiungere Nuove Regole

Modifica `engine/scoring.py` per aggiungere nuove logiche di punteggio.

## 📊 Struttura Dati

### Card (tuple)
```python
card = (value, suit)  # Es: (7, 'Denari')
# value: 1-10 (Asso è 1)
# suit: 'Denari', 'Coppe', 'Bastoni', 'Spade'
```

### Player Object
```python
player.hand          # [card, card, ...]
player.captured      # [card, card, ...]
player.sweeps        # int (numero di scope)
player.total_points  # int
```

## 🐛 Troubleshooting

### Errore: "Card directory not found"
La cartella `carte/` non è trovata. Posizionala nella radice del progetto oppure nella cartella `scopa/`.

### Immagini non si caricano
- Verifica che le immagini siano in formato JPG/PNG
- Verifica la nomenclatura: `1_denari.jpg` (valore_seme.jpg)
- Fallback automatico a visualizzazione testuale

## 👨‍💻 Contributi

Questo progetto è progettato per essere facile da estendere:

1. **Nuove strategie AI**: Aggiungi una classe in `ai/strategies.py`
2. **Miglioramenti GUI**: Modifica `ui/app.py`
3. **Varianti di gioco**: Estendi `engine/game_engine.py`

## 📝 Licenza

Questo progetto è fornito come è, per scopi educativi e di intrattenimento.

## 🎓 Apprendimento

Questo progetto dimostra:
- ✅ Design patterns e architettura clean code
- ✅ Separazione delle responsabilità (SoC)
- ✅ Object-oriented programming
- ✅ Game logic implementation
- ✅ GUI development con Tkinter
- ✅ AI e decision making
- ✅ Modularità e riutilizzabilità

## 📞 Supporto

Per domande o problemi, consulta la struttura del codice e i commenti forniti (sono abbondanti e chiari!).

---

Buon divertimento con SCOPONE! 🎴

Versione: 2.0 (Refactored - Professional Architecture)
