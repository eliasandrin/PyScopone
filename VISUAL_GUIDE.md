# 🎮 Quick Guide - Modern Scopone Interface

## Welcome to Modern Scopone!

This guide will help you navigate the beautiful new interface and start playing immediately.

---

## 🚀 First Launch

### 1. Start the Application
```bash
python main.py
```

You'll see the modern setup screen with a dark theme and large, centered layout.

### 2. Setup Screen Overview

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                  🎴 SCOPONE                         │
│          Traditional Italian Card Game              │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Modalità Principianti (Show All Cards)     │  │
│  │  ○────●  (Toggle switch)                    │  │
│  │                                              │  │
│  │  Difficoltà AI                               │  │
│  │  ○ 🟢 Facile  - Perfect for beginners       │  │
│  │  ● 🔵 Normale - Balanced and fun            │  │
│  │  ○ 🟠 Esperto - Challenging                 │  │
│  │  ○ 🔴 Adattivo - Intelligent AI             │  │
│  │                                              │  │
│  │  Numero Giocatori                            │  │
│  │  ○ 2  ● 3  ○ 4  ○ 5  ○ 6                   │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│           ┌────────────────────────┐                │
│           │  ▶ INIZIA PARTITA      │  (Large green) │
│           └────────────────────────┘                │
│           ┌────────────────────────┐                │
│           │       Esci             │  (Gray)        │
│           └────────────────────────┘                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 3. Configuration Options

#### Beginner Mode (Switch)
- **ON** (Green): Shows all players' cards - great for learning!
- **OFF** (Gray): Hides opponent cards - traditional play

#### AI Difficulty (Radio Buttons)
- **🟢 Facile**: AI makes random moves
  - *Perfect for learning the rules*
  - *No strategy, just random plays*

- **🔵 Normale** (Default): AI uses basic strategy
  - *Captures when possible*
  - *Balanced and fun*

- **🟠 Esperto**: AI uses advanced tactics
  - *Prioritizes coins*
  - *Multi-card captures*
  - *Strategic thinking*

- **🔴 Adattivo**: AI adapts to game state
  - *Context-aware decisions*
  - *Hardest challenge*

#### Number of Players (Radio Buttons)
- **2-6 players**: Choose your preferred game size
- You are always "Tu" (You) - Player 1
- Other players are AI opponents

---

## 🎮 Game Board Interface

### Layout Overview

```
┌──────────────────────────────────────────────────────────────────┐
│ Status: Turno di: Tu        🔄 Nuova  👁 Toggle  📊 Stats  🏠 Menu│ TOP BAR
├────────┬─────────────────────────────────────────────┬───────────┤
│ LOG    │              PLAYER 2 (AI)                  │           │
│ ═══    │  👤 Marco  ▶  Mano: 4  Catturate: 6  Scope: 1│           │
│        │  [Card] [Card] [Card] [Card]                │           │
│ Player │                                              │           │
│ Tu     │         ┌─────────────────────┐             │  PLAYER 3 │
│ gioca  │         │  🎴 TAVOLO          │             │  (AI)     │
│ 7♦     │         │  [7♣] [3♠] [10♥]   │             │  Sidebar  │
│        │         └─────────────────────┘             │           │
│ Marco  │                                              │           │
│ gioca  │              PLAYER 1 (YOU)                 │           │
│ 3♠     │  👤 Tu  ▶  Mano: 5  Catturate: 8  Scope: 2 │           │
│        │  [Card] [Card] [Card] [Card] [Card]        │           │
└────────┴─────────────────────────────────────────────┴───────────┘
```

### Interface Components

#### Top Bar (Always Visible)
Left side:
- **Status**: "Turno di: [Player Name]" in blue
- **Mode**: Green/Red indicator for beginner/normal mode

Right side (Buttons):
- **🔄 Nuova Partita** (Green): Start new game with same settings
- **👁 Mostra/Nascondi** (Blue): Toggle card visibility
- **📊 Statistiche** (Purple): View game statistics
- **🏠 Menu** (Gray): Return to setup screen

#### Left Sidebar (Game Log)
- Real-time scrolling log
- All moves displayed
- Format: "[Player] gioca [Card]"
- Monospace font (Consolas)
- Auto-scrolls to latest move

#### Center Area (Game Board)
**Table (Center)**:
- Blue-bordered rounded rectangle
- Title: "🎴 TAVOLO"
- Shows all cards currently on table
- Empty: displays "Tavolo Vuoto"

**Players** (Arranged dynamically):
- 2 players: Bottom (You), Top (AI)
- 3 players: Bottom (You), Left (AI), Right (AI)
- 4+ players: Complex arrangement around table

#### Player Display Frame
Each player has:
```
┌────────────────────────────────────────┐
│ 👤 Marco  ▶                            │ ← Name & Turn indicator
│ Mano: 4 • Catturate: 6 • Scope: 1     │ ← Statistics
│ ┌──────────────────────────────────┐   │
│ │ [Card] [Card] [Card] [Card]     │   │ ← Cards (scrollable)
│ └──────────────────────────────────┘   │
└────────────────────────────────────────┘
```

**Border colors** (by player):
- Player 1 (You): Red
- Player 2: Blue
- Player 3: Green
- Player 4: Orange
- Player 5: Purple
- Player 6: Teal

**Active player**: Border glows brighter + Arrow ▶ appears

---

## 🃏 Playing Cards

### Your Turn
1. **Look for the arrow**: ▶ next to your name
2. **Your frame border glows** in your color
3. **Hover over your cards**: They'll highlight
4. **Click a card** to play it
5. **Card appears on table** immediately
6. **Game processes** the move:
   - Captures if possible
   - Scopa detection
   - Table updates
   - Turn passes

### AI Turn
1. Status shows AI player name
2. Brief pause (1.5 seconds) - AI "thinking"
3. AI's move logged in sidebar
4. Card appears on table
5. Turn automatically passes

### Card Display
**With Images**:
- Full card image loaded from `scopa/carte/`
- Crisp rendering at optimal size
- Hover effect for playable cards

**Without Images** (Fallback):
- Large text: "7 ♦"
- Value and suit symbol
- Still fully playable

---

## 📊 Reading the Interface

### Status Messages
- **Initial**: "Turno di: [Player]"
- **Playing**: Shows whose turn
- **End**: Final scores appear

### Game Log Entries
- `✓ Giocata 7♦` - Card played successfully
- `❌ Non è il tuo turno!` - Error: not your turn
- `❌ Mossa non valida!` - Error: invalid move
- `🤖 Marco gioca 3♠` - AI move
- `🏁 PARTITA TERMINATA!` - Game over

### Player Stats
- **Mano**: Cards currently in hand
- **Catturate**: Cards captured so far
- **Scope**: Number of scopes (table clearing)

---

## 🏆 Game End & Results

### Final Scores Window
When game ends, a modal window appears:

```
┌────────────────────────────────────────┐
│      🏆 CLASSIFICA FINALE              │
├────────────────────────────────────────┤
│ ┌────────────────────────────────────┐ │
│ │ 🥇 Marco           18 punti        │ │ Gold border
│ │ Carte: 25 • Denari: 7 • Scope: 3   │ │
│ └────────────────────────────────────┘ │
│ ┌────────────────────────────────────┐ │
│ │ 🥈 Tu              15 punti        │ │
│ │ Carte: 22 • Denari: 6 • Scope: 2   │ │
│ └────────────────────────────────────┘ │
│ ┌────────────────────────────────────┐ │
│ │ 🥉 Anna            12 punti        │ │
│ │ Carte: 18 • Denari: 5 • Scope: 1   │ │
│ └────────────────────────────────────┘ │
│                                          │
│           [Chiudi] button                │
└──────────────────────────────────────────┘
```

**Medals**:
- 🥇 Gold: 1st place
- 🥈 Silver: 2nd place
- 🥉 Bronze: 3rd place
- 4th-6th: Just the position number

**Score Details**:
- Total points (large, green)
- Cards captured
- Coins (Denari) collected
- Scopes achieved

---

## 🎯 Tips for Best Experience

### Visual Tips
1. **Watch the arrow** (▶) to know whose turn it is
2. **Frame borders glow** for active player
3. **Game log** shows all moves - scroll to review
4. **Hover over cards** to see highlights
5. **Check stats** to track progress

### Gameplay Tips
1. **Start with Beginner Mode** to see all cards
2. **Learn by watching AI** moves in the log
3. **Focus on capturing coins** (Denari)
4. **Try to clear the table** for scopes
5. **Calculate primiera** (7s are worth most)

### Interface Tips
1. **Use 👁 Toggle** to switch viewing mode mid-game
2. **Check 📊 Stats** for game history
3. **Click 🔄 New Game** to retry quickly
4. **Return to 🏠 Menu** to change settings

---

## ⌨️ Quick Actions

| Action | Button | Location |
|--------|--------|----------|
| Play Card | Left-click card | Your hand |
| Toggle Visibility | 👁 Button | Top bar |
| New Game | 🔄 Button | Top bar |
| View Stats | 📊 Button | Top bar |
| Return to Menu | 🏠 Button | Top bar |
| Close Results | Chiudi | Results window |

---

## 🎨 Visual Indicators

### Color Meanings
- **Green**: Positive actions (Start, New Game)
- **Blue**: Information (Toggle, Player themes)
- **Purple**: Analytics (Statistics)
- **Gray**: Neutral (Exit, Close)
- **Yellow**: Current turn indicator (arrow)
- **Gold**: Winner border

### Border Styles
- **Thin border**: Normal state
- **Thick/bright border**: Active player
- **Gold border**: Winner in results
- **Blue border**: Table area

### Text Colors
- **Bright white**: Primary text (dark mode)
- **Gray**: Secondary information
- **Blue**: Status and headers
- **Green**: Scores and success
- **Red**: Errors (if any)

---

## 🐛 Troubleshooting

### Cards Appear as Text
- **Cause**: Images not found
- **Solution**: Place card images in `scopa/carte/`
- **Format**: `7_denari.jpg`, `3_coppe.jpg`, etc.
- **Note**: Game is still playable with text

### Can't Click Cards
- **Cause**: Not your turn
- **Check**: Arrow (▶) should be by your name
- **Wait**: For AI to complete their turn

### Interface Looks Wrong
- **Restart**: Close and reopen application
- **Check**: CustomTkinter installed (`pip install customtkinter`)
- **Update**: Upgrade to latest version

### Game Freezes
- **Wait**: AI is "thinking" (1.5 seconds)
- **Check**: Console for error messages
- **Restart**: If issue persists

---

## 📱 Responsive Design

The interface adapts to different screen sizes:

**Small**: 1280x720 - Compact layout
**Medium**: 1920x1080 - Optimal (default)
**Large**: 2560x1440+ - Spacious

Adjust window size as needed - elements will reflow.

---

## 🎓 Learning Path

### Complete Beginner
1. Enable **Beginner Mode** (show all cards)
2. Choose **Easy AI** (random moves)
3. Select **2 players** (you vs 1 AI)
4. Watch the game log to learn
5. Focus on understanding captures

### Intermediate
1. Try **Normal AI**
2. Add **3 players**
3. Toggle between show/hide cards
4. Start calculating primiera
5. Look for scope opportunities

### Advanced
1. Use **Expert AI** or **Adaptive AI**
2. Play **4-6 players** for complexity
3. Disable beginner mode (hide cards)
4. Try to predict AI moves
5. Optimize for maximum points

---

## 🌟 Enjoy the Game!

You're now ready to enjoy Scopone with the beautiful modern interface!

**Quick Start Checklist**:
- ✅ Launch application
- ✅ Configure settings
- ✅ Click "INIZIA PARTITA"
- ✅ Play cards by clicking
- ✅ Watch game log
- ✅ Check final results

**Buon Divertimento!** 🎴

---

**Need Help?** Check the README_MODERN.md for detailed documentation.

**Found a Problem?** Look at the CHANGELOG.md for known issues and fixes.

**Want to Customize?** See the developer section in README_MODERN.md.
