# SCOPONE - Quick Start Guide

## 🚀 Avvio Rapido

### 1. Installa le Dipendenze
```bash
cd scopa_refactored
pip install -r requirements.txt
```

### 2. Configura le Carte (se necessario)

Le immagini delle carte vengono caricate automaticamente dalla cartella `../scopa/carte/`.

Se le carte non vengono trovate, puoi:
- Copiare la cartella `scopa/carte/` in `scopa_refactored/carte/`
- Oppure creare un link simbolico: `mklink /D carte ..\scopa\carte`

**Formato immagini**: `{valore}_{seme}.jpg` (es: `7_denari.jpg`, `10_Bastoni.jpg`)

### 3. Avvia l'Applicazione
```bash
python main.py
```

### 4. Gioca!
- Seleziona il numero di giocatori
- Scegli la difficoltà AI
- Clicca "INIZIA PARTITA"
- Clicca sulle tue carte per giocarle

---

## 📁 Cartella `carte/`

Le immagini delle carte devono trovarsi in:
```
scopa/carte/
├── 1_denari.jpg
├── 1_coppe.jpg
├── ...
└── 10_spade.jpg
```

Il file system cerca automaticamente nella cartella `carte/` padre.

---

## 🎮 Come Giocare

### Fase di Setup
1. Scegli **Modo Principianti** (recommended per imparare)
2. Scegli **Difficoltà AI**: Normal per cominciare
3. Scegli **Numero Giocatori**: 4 è il standard
4. Clicca **INIZIA PARTITA**

### Durante la Partita
- Le carte sono **ordinate per valore** da sinistra a destra
- **Clicca** su una carta per giocarla
- Il tavolo mostra le carte disponibili
- Log a destra fornisce feedback in tempo reale

### Catturare Carte
Puoi catturare:
- Una singola carta con lo **stesso valore**
- Una **combinazione** di carte che somma al valore della tua carta

Esempio: Giochi il 9, puoi catturare:
- Un'altra carta 9, OPPURE
- Un 5 + un 4, OPPURE
- Un 3 + un 2 + un 4, etc.

### Scopa (Sweep)
Se catturi **tutte** le carte sul tavolo → Hai fatto una SCOPA!
- Valore: 1 punto
- Tavolo si svuota

---

## 🤖 Strategie AI

### Easy (Facile)
- IA gioca carte **casuali**
- Perfetto per principianti
- Permette di vincere facilmente

### Normal (Normale) ⭐ CONSIGLIATO
- IA cerca di **catturare** quando possibile
- Altrimenti gioca la **carta più bassa**
- Simile a un giocatore vero

### Expert (Esperto)
- IA cerca **catture multiple**
- Priorità a **Denari** e **combinazioni**
- Molto difficile da battere

### Adaptive (Adattivo)
- IA si **adatta** al contesto
- Strategia più complessa
- Più impegnativa

---

## 📊 Calcolo Punteggi

Alla fine della partita vinci punti per:

| Categoria | Condizione | Punti |
|-----------|-----------|-------|
| **Carte** | >20 carte catturate | 1 |
| **Denari** | >5 Denari catturati | 1 |
| **Settebello** | Hai il 7♦ | 1 |
| **Primiera** | Miglior primiera | 1 |
| **Scope** | Per ogni scopa | 1 |

### Primiera (Best Hand)
Somma della carta più alta per ogni seme:
- 7 = 21 punti, 6 = 18, 1 = 16, 5 = 15, 4 = 14, 3 = 13, 2 = 12, 8-10 = 10

Chi ha la **somma più alta** vince il punto!

---

## ⚙️ Configurazione

Per personalizzare il gioco, modifica `config/constants.py`:

```python
# Numero di giocatori
MIN_PLAYERS = 2
MAX_PLAYERS = 6
DEFAULT_PLAYERS = 4

# Ritardo AI (millisecondi)
AI_THINKING_DELAY = 1500  # Tempo di "thinking" dell'IA

# Colori UI
COLOR_ACCENT_GREEN = "#2ecc71"
COLOR_TEXT_PRIMARY = "white"
```

---

## 🐛 Troubleshooting

### "Card directory not found"
La cartella `carte/` non è trovata. Soluzioni:
1. Crea una cartella `carte/` nella radice del progetto
2. Oppure nella cartella `scopa/`
3. Colloca le immagini PNG/JPG al suo interno

### Il gioco è lento
- Diminuisci `AI_THINKING_DELAY` in constants.py
- Usa difficoltà AI "Normal" invece di "Expert"

### Le immagini non si caricano
1. Verifica che le immagini siano in `carte/`
2. Verifica la nomenclatura: `1_denari.jpg` (numero_seme.jpg)
3. Il gioco mostrerà valori testuali come fallback

---

## 💡 Tips per Vincere

1. **Prioritari i Denari**: Valgono 1 punto se hai >5
2. **Scope**: Ogni scopa = 1 punto, molto importante!
3. **Primiera**: Tieni le carte alte di ogni seme
4. **Settebello**: Il 7♦ è un bonus garantito
5. **Bloccare Avversari**: Non lasciare carte facili da catturare

---

## 📖 Regole Ufficiali

Per le regole complete del Scopone tradizionale, consulta:
- GUIDA_SCOPA.txt (accompagna il progetto)
- Wikipedia: Scopone (Italian Card Game)

---

## 🔧 Per Sviluppatori

Per modificare il codice, consulta:
- **STRUCTURE.md** - Architettura tecnica
- **Code Comments** - Ogni file è ben documentato
- **Docstrings** - Ogni classe/funzione è spiegata

### Aggiungere Nuova Funzione
1. Identifica il modulo appropriato
2. Aggiungi la funzione con docstring
3. Testa in isolamento
4. Usa dal modulo UI se necessario

### Aggiungere Nuova Strategia AI
```python
# In ai/strategies.py

class MyAI(AIStrategy):
    """Descrizione strategia."""
    
    def choose_card(self, hand, table_cards):
        """Scegli una carta da giocare."""
        # Logica qui
        return card_to_play
```

---

## 📞 Support

Leggi i commenti nel codice - sono esempi!

Buon gioco! 🎴

---

**Versione**: 2.0 (Professional Refactored)
**Data**: 2025-03-05
