# 🎴 SCOPONE - Modern Professional Edition

## Beautiful Italian Card Game with Modern UI

A complete, professional implementation of the traditional Italian card game **Scopone** featuring a stunning modern interface built with CustomTkinter.

---

## ✨ What's New in Modern Edition

### 🎨 **Beautiful Modern Interface**
- **Dark Theme**: Elegant dark mode interface with perfect contrast
- **Smooth Animations**: Fluid transitions and hover effects
- **Modern Widgets**: CustomTkinter components for a premium feel
- **Responsive Design**: Adapts beautifully to different screen sizes
- **Color-Coded Players**: Each player has unique color theme
- **Professional Cards**: High-quality card display with smooth rendering

### 🚀 **Enhanced Features**
- **Setup Screen**: Large, card-like design with modern switches
- **Game Board**: Dynamic layout with central table and player areas
- **Real-time Log**: Scrollable game log with all moves
- **Statistics Panel**: Track game history and performance
- **Results Screen**: Beautiful medal system and detailed scores
- **Quick Controls**: Top bar with all essential buttons

### 🎯 **User Experience**
- **Intuitive Controls**: Click cards to play, everything is clear
- **Hover Effects**: Cards respond to mouse movement
- **Status Updates**: Always know whose turn it is
- **Game Mode Toggle**: Switch between beginner/normal modes instantly
- **Responsive Feedback**: Visual confirmation of all actions

---

## 📸 Interface Screenshots

### Setup Screen
- Clean, centered layout with card-like panel
- Modern switches for game options
- Color-coded difficulty levels with descriptions
- Large, prominent "START GAME" button

### Game Board
- **Top Bar**: Status, controls, statistics access
- **Left Sidebar**: Real-time scrolling game log
- **Center**: Dynamic player arrangement around table
- **Table**: Central card display with blue highlight
- **Players**: Individual frames with stats and card displays

### Card Display
- Beautiful card images with smooth rendering
- Hover effects on playable cards
- Color-coded borders per player
- Clear stats: Cards in hand, captured, scopes

---

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `customtkinter >= 5.2.0` - Modern UI framework
- `Pillow >= 10.0.0` - Image processing

### Card Images
Place 40 card images in `scopa/carte/`:
- Format: `1_denari.jpg`, `2_coppe.jpg`, `3_bastoni.jpg`, `4_spade.jpg`, etc.
- The app will automatically find the card directory

### Run the Game
```bash
python main.py
```

---

## 🎮 How to Play

### Game Setup
1. Launch the application
2. **Toggle Beginner Mode**: Show/hide all cards
3. **Select AI Difficulty**:
   - 🟢 **Easy**: Random moves (perfect for learning)
   - 🔵 **Normal**: Basic strategy (balanced fun)
   - 🟠 **Expert**: Advanced tactics (challenging)
   - 🔴 **Adaptive**: Intelligent AI (hardest)
4. **Choose Players**: 2-6 players
5. Click **▶ INIZIA PARTITA**

### During the Game

**Human Turn**:
- Your cards will be clickable (with hover effect)
- Click a card to play it
- Watch it appear on the table

**AI Turn**:
- AI thinks for 1.5 seconds
- Plays automatically
- Move is logged in sidebar

**Following the Action**:
- Check the **game log** for all moves
- See **player stats** update in real-time
- Watch the **table** as cards are captured

### Controls (Top Bar)
- 🔄 **Nuova Partita**: Start new game with same settings
- 👁 **Mostra/Nascondi**: Toggle card visibility
- 📊 **Statistiche**: View game statistics
- 🏠 **Menu**: Return to setup screen

---

## 🏆 Scoring System

Traditional Scopone scoring rules:

| Achievement | Points |
|------------|--------|
| **Settebello** (7 of Coins) | 1 point |
| **Primiera** (Best card combo) | 1 point |
| **Most Cards** | 1 point |
| **Most Coins** (Denari) | 1 point |
| **Scopa** (Clear table) | 1 point each |

### Primiera Calculation
Each player's best card per suit contributes:
- **7**: 21 points
- **6**: 18 points
- **Ace**: 16 points
- **5**: 15 points
- **4**: 14 points
- **3**: 13 points
- **2**: 12 points
- **Face cards**: 10 points

---

## 🎨 Interface Design Details

### Color Scheme
- **Background**: Dark gray (#1a1a1a in dark mode)
- **Cards**: White/light gray with subtle shadows
- **Buttons**: Green (start), Blue (info), Gray (neutral)
- **Player Colors**: Red, Blue, Green, Orange, Purple, Teal
- **Highlights**: Yellow for current turn indicator

### Typography
- **Title**: Segoe UI, 72pt, Bold
- **Headers**: Segoe UI, 20pt, Bold
- **Body**: Segoe UI, 16pt
- **Monospace Log**: Consolas, 11pt

### Layout Philosophy
- **Centered Setup**: Single focus point for game start
- **Dynamic Game Board**: Players arranged based on count
- **Sidebar Information**: Non-intrusive but always accessible
- **Top Bar Controls**: Quick access without cluttering main view

---

## 📂 Project Structure

```
scopa_refactored/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── README_MODERN.md          # This file (modern UI docs)
├── README.md                 # Original documentation
│
├── config/
│   └── constants.py          # All game constants
│
├── models/
│   ├── player.py            # Player entity
│   └── card.py              # Card entity
│
├── engine/
│   ├── game_engine.py       # Core game logic
│   └── scoring.py           # Scoring calculations
│
├── ai/
│   └── strategies.py        # AI implementations
│
├── ui/
│   ├── app.py              # Classic Tkinter UI
│   └── modern_app.py       # Modern CustomTkinter UI ⭐ NEW
│
└── utils/
    └── image_loader.py      # Image loading with caching
```

---

## 🛠️ Technical Details

### Modern UI Framework
**CustomTkinter** provides:
- Native theme support (dark/light)
- Modern widget styling
- Smooth animations
- Better font rendering
- Professional appearance

### Architecture Patterns
- **MVC Pattern**: Clean separation (Model, View, Controller)
- **Strategy Pattern**: Pluggable AI strategies
- **Factory Pattern**: AI creation
- **Observer Pattern**: UI updates on state changes
- **Singleton Pattern**: Image cache

### Performance Optimizations
- **Image Caching**: Cards loaded once, reused everywhere
- **Lazy Loading**: Resources loaded when needed
- **Efficient Rendering**: Only update changed elements
- **Smart Path Finding**: Automatic card directory detection

---

## 🐛 Troubleshooting

### Application Won't Start
**Error**: `Import "customtkinter" could not be resolved`
```bash
pip install customtkinter
```

**Error**: `Module not found: PIL`
```bash
pip install Pillow
```

### Cards Not Loading
1. Check console for path messages
2. Verify cards are in `scopa/carte/`
3. Filename format: `7_denari.jpg` (lowercase)
4. App will show text fallback if images missing

### UI Looks Wrong
- Ensure CustomTkinter 5.2+ is installed
- Try restarting the application
- Check your Python version (3.7+ required)

### Performance Issues
- Close other applications
- Reduce number of players
- Check if card images are too large (recommended: 200x300px)

---

## 🎓 For Developers

### Customizing the Modern UI

**Change Colors**:
Edit `ui/modern_app.py`:
```python
# Player colors (line ~350)
colors = [
    ("#your_color", "#hover_color"),
    # Add more colors
]
```

**Adjust Layout**:
Modify `_position_player_frame()` method for different player arrangements.

**Add Animations**:
CustomTkinter supports smooth transitions - use `.configure()` with delays.

**Theme Switching**:
```python
ctk.set_appearance_mode("light")  # or "dark" or "system"
```

### Creating Custom AI
1. Extend base strategy in `ai/strategies.py`
2. Implement `choose_card(hand, table)` method
3. Add to `get_ai_strategy()` factory
4. Update UI difficulty selection

### Adding Features
**Example**: Add a "Help" button
```python
help_button = ctk.CTkButton(
    top_bar,
    text="❓ Aiuto",
    command=self.show_help,
    ...
)
```

---

## 🌟 Best Practices

### Playing the Game
- Start with **Beginner Mode** to see all cards
- Try **Easy AI** first to learn rules
- Progress to **Normal** and **Expert** as you improve
- Use **Adaptive AI** for ultimate challenge

### Learning Strategy
1. Watch AI moves in beginner mode
2. Focus on capturing coins (Denari)
3. Try to calculate primiera values
4. Look for scope opportunities (clearing table)

---

## 📊 Statistics & History

The app tracks:
- **Total Games Played**: Lifetime statistics
- **Current Game Moves**: Move counter
- **Player Performance**: Wins, captures, scopes
- **AI Decisions**: Logged for transparency

Access via the **📊 Statistiche** button.

---

## 🎉 Enjoy!

Experience the traditional Italian card game with modern, professional graphics that make learning and playing a joy!

**Buon Divertimento!** 🎴🇮🇹

---

## 📝 Version History

### v2.0 - Modern Edition (Current)
- ✨ New CustomTkinter interface
- 🎨 Dark theme with modern widgets
- 🚀 Smooth animations and hover effects
- 📊 Enhanced statistics panel
- 🏆 Beautiful results screen
- 🔄 Quick controls in top bar

### v1.0 - Professional Refactor
- 📂 Modular architecture
- 🤖 4 AI difficulty levels
- 🎮 Complete game rules
- 📚 Full documentation
- 🐛 Bug fixes and optimizations

---

**Made with ❤️ for card game enthusiasts**
