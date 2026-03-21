# 🎨 Customization Guide - Modern Scopone Interface

## Make It Your Own!

This guide shows you how to customize the modern interface to match your preferences or brand.

---

## 🎯 Quick Customizations

### Change Theme (Dark/Light)

**Location**: `ui/modern_app.py`, line ~11

```python
# Current (Dark):
ctk.set_appearance_mode("dark")

# Change to Light:
ctk.set_appearance_mode("light")

# Or System default:
ctk.set_appearance_mode("system")  # Follows OS setting
```

### Change Accent Color

**Location**: `ui/modern_app.py`, line ~12

```python
# Current (Blue):
ctk.set_default_color_theme("blue")

# Available options:
ctk.set_default_color_theme("green")
ctk.set_default_color_theme("dark-blue")
```

### Window Size

**Location**: `ui/modern_app.py`, line ~34

```python
# Current:
self.geometry("1920x1080")

# Make it smaller:
self.geometry("1280x720")

# Make it larger:
self.geometry("2560x1440")

# Or fullscreen:
self.attributes('-fullscreen', True)
```

---

## 🎨 Color Scheme Customization

### Player Colors

**Location**: `ui/modern_app.py`, lines ~350-360

```python
# Current colors:
colors = [
    ("#e74c3c", "#c0392b"),  # Red - Player 1
    ("#3498db", "#2980b9"),  # Blue - Player 2
    ("#2ecc71", "#27ae60"),  # Green - Player 3
    ("#f39c12", "#e67e22"),  # Orange - Player 4
    ("#9b59b6", "#8e44ad"),  # Purple - Player 5
    ("#1abc9c", "#16a085"),  # Teal - Player 6
]

# Customize (hex colors):
colors = [
    ("#FF6B6B", "#CC5555"),  # Coral Red
    ("#4ECDC4", "#3DA8A0"),  # Turquoise
    ("#95E1D3", "#76B4AA"),  # Mint
    ("#FFD93D", "#CCAE31"),  # Golden Yellow
    ("#A8DADC", "#86AEB0"),  # Powder Blue
    ("#F38181", "#C26767"),  # Pink
]
```

### Button Colors

#### Start Button

**Location**: `ui/modern_app.py`, lines ~180-188

```python
# Current (Green):
start_button = ctk.CTkButton(
    buttons_frame,
    text="▶  INIZIA PARTITA",
    fg_color=("#2ecc71", "#27ae60"),      # Normal state
    hover_color=("#27ae60", "#229954"),   # Hover state
    ...
)

# Change to Blue:
fg_color=("#3498db", "#2980b9"),
hover_color=("#2980b9", "#21618c"),

# Or Orange:
fg_color=("#f39c12", "#e67e22"),
hover_color=("#e67e22", "#d35400"),
```

#### Control Buttons

**Location**: `ui/modern_app.py`, lines ~270-305

Find these buttons and change their colors:
- 🔄 **New Game**: Green
- 👁 **Toggle**: Blue
- 📊 **Stats**: Purple
- 🏠 **Menu**: Gray

```python
# Example: Change Stats button to cyan
ctk.CTkButton(
    controls_frame,
    text="📊 Statistiche",
    fg_color=("#17a2b8", "#138496"),      # Cyan
    hover_color=("#138496", "#0f6674"),
    ...
)
```

### Table Border Color

**Location**: `ui/modern_app.py`, line ~324

```python
# Current (Blue):
self.table_frame = ctk.CTkFrame(
    center_area,
    border_color=("#3498db", "#2980b9")
)

# Change to Green:
border_color=("#2ecc71", "#27ae60")

# Or Purple:
border_color=("#9b59b6", "#8e44ad")
```

---

## 📝 Text Customization

### Application Title

**Location**: `ui/modern_app.py`, line ~33

```python
# Current:
self.title("SCOPONE • Gioco di Carte Italiano")

# Customize:
self.title("My Scopone Game")
self.title("🎴 Scopa Pro Edition")
self.title("Italian Cards")
```

### Main Title (Setup Screen)

**Location**: `ui/modern_app.py`, lines ~80-86

```python
# Current:
title_label = ctk.CTkLabel(
    title_frame,
    text="🎴 SCOPONE",
    font=ctk.CTkFont(family="Segoe UI", size=72, weight="bold"),
    ...
)

# Change text:
text="♠️♥️ SCOPA ♦️♣️"

# Change size:
font=ctk.CTkFont(family="Segoe UI", size=96, weight="bold")

# Change font:
font=ctk.CTkFont(family="Arial", size=72, weight="bold")
```

### Subtitle

**Location**: `ui/modern_app.py`, lines ~88-93

```python
# Current:
subtitle_label = ctk.CTkLabel(
    title_frame,
    text="Traditional Italian Card Game",
    ...
)

# Change:
text="Il Gioco delle Carte Italiane"
text="Professional Edition"
text="Your Custom Subtitle"
```

### Button Labels

**Location**: Throughout `ui/modern_app.py`

Change any button text:
```python
# Examples:
text="▶  INIZIA PARTITA"  →  text="▶ START GAME"
text="Esci"              →  text="Exit"
text="🔄 Nuova Partita"  →  text="🔄 New Game"
text="👁 Mostra/Nascondi" →  text="👁 Toggle Cards"
```

For full English translation, search for all Italian strings.

---

## 🖼️ Card Customization

### Card Size

**Location**: `config/constants.py`, lines ~30-35

```python
# Current:
CARD_SIZE_HAND = (80, 120)    # Hand cards
CARD_SIZE_TABLE = (100, 150)  # Table cards

# Make larger:
CARD_SIZE_HAND = (100, 150)
CARD_SIZE_TABLE = (120, 180)

# Make smaller:
CARD_SIZE_HAND = (60, 90)
CARD_SIZE_TABLE = (80, 120)
```

### Card Styling

**Location**: `ui/modern_app.py`, lines ~520-550

```python
# Current card button:
card_btn = ctk.CTkButton(
    parent,
    corner_radius=8,                          # Rounded corners
    fg_color=("white", "gray25"),            # Background
    border_width=2,                           # Border thickness
    border_color=("gray70", "gray40"),       # Border color
    ...
)

# Customize:
corner_radius=15,                              # More rounded
border_width=3,                                # Thicker border
border_color=("#3498db", "#2980b9"),          # Blue border
```

### Back of Card (Hidden)

**Location**: `ui/modern_app.py`, lines ~553-566

```python
# Current (Dark red):
card_btn = ctk.CTkButton(
    parent,
    text="?",
    fg_color=("#8b0000", "#660000"),         # Dark red
    border_color=("#660000", "#440000"),
    ...
)

# Change to Blue back:
fg_color=("#1e3a8a", "#1e40af"),
border_color=("#1e40af", "#1d4ed8"),

# Or Pattern/Image:
text="🂠",  # Unicode card back
font=ctk.CTkFont(size=48)
```

---

## 🎭 Layout Customization

### Top Bar Height

**Location**: `ui/modern_app.py`, line ~212

```python
# Current:
top_bar = ctk.CTkFrame(
    main_container,
    height=80,
    ...
)

# Make taller:
height=100,

# Make shorter:
height=60,
```

### Sidebar Width

**Location**: `ui/modern_app.py`, line ~312

```python
# Current:
log_sidebar = ctk.CTkFrame(
    game_container,
    width=350,
    ...
)

# Make wider:
width=450,

# Make narrower:
width=300,
```

### Corner Radius (Roundness)

**Location**: Throughout `ui/modern_app.py`

```python
# Current (various):
corner_radius=10   # Slight rounding
corner_radius=15   # Medium rounding
corner_radius=20   # More rounded

# More extreme:
corner_radius=30   # Very rounded
corner_radius=5    # Barely rounded
corner_radius=0    # Square (no rounding)
```

Change all `corner_radius` values for consistent look.

---

## 🔤 Font Customization

### System-Wide Font

**Location**: `ui/modern_app.py`, multiple locations

Find and replace:
```python
# Current:
font=ctk.CTkFont(family="Segoe UI", ...)

# Change to:
font=ctk.CTkFont(family="Arial", ...)
font=ctk.CTkFont(family="Helvetica", ...)
font=ctk.CTkFont(family="Calibri", ...)
font=ctk.CTkFont(family="Roboto", ...)  # If installed
```

### Font Sizes

**Location**: Throughout `ui/modern_app.py`

```python
# Current sizes:
size=72  # Main title
size=20  # Subtitles, headers
size=18  # Section titles
size=16  # Body text
size=15  # Buttons
size=13  # Small text
size=11  # Log text

# Scale up (10% larger):
size=79  # Main title
size=22  # Subtitles
...

# Scale down (10% smaller):
size=65  # Main title
size=18  # Subtitles
...
```

### Monospace Log Font

**Location**: `ui/modern_app.py`, line ~332

```python
# Current (Consolas):
self.log_widget = ctk.CTkTextbox(
    log_sidebar,
    font=ctk.CTkFont(family="Consolas", size=11),
    ...
)

# Change to:
font=ctk.CTkFont(family="Courier New", size=11),
font=ctk.CTkFont(family="Monaco", size=11),
font=ctk.CTkFont(family="Lucida Console", size=11),
```

---

## 🎪 Animation & Timing

### AI Thinking Delay

**Location**: `config/constants.py`, line ~85

```python
# Current (1.5 seconds):
AI_THINKING_DELAY = 1500  # milliseconds

# Make faster:
AI_THINKING_DELAY = 500   # Half second

# Make slower (more dramatic):
AI_THINKING_DELAY = 3000  # 3 seconds
```

### Button Hover Speed

CustomTkinter has built-in smooth transitions. To adjust globally:

**Location**: After `import customtkinter as ctk` in `ui/modern_app.py`

```python
# Set animation speed (not in current code, but can add):
ctk.deactivate_automatic_dpi_awareness()  # If having scaling issues
```

*Note: Hover animations are built into CustomTkinter and very smooth by default.*

---

## 🎯 Advanced Customizations

### Custom Color Scheme (Complete)

Create a color dictionary:

```python
# Add to top of ModernScoponeApp class:
COLORS = {
    'primary': '#2ecc71',      # Green
    'secondary': '#3498db',    # Blue
    'accent': '#f39c12',       # Orange
    'danger': '#e74c3c',       # Red
    'dark': '#2c3e50',         # Dark gray
    'light': '#ecf0f1',        # Light gray
}

# Then use throughout:
fg_color=self.COLORS['primary']
```

### Custom Theme Class

Create a separate theme file:

**New File**: `ui/themes.py`

```python
class Theme:
    # Colors
    PRIMARY = "#2ecc71"
    SECONDARY = "#3498db"
    ACCENT = "#f39c12"
    
    # Fonts
    TITLE_FONT = ("Segoe UI", 72, "bold")
    HEADER_FONT = ("Segoe UI", 20, "bold")
    BODY_FONT = ("Segoe UI", 16)
    
    # Sizes
    BUTTON_HEIGHT = 60
    CORNER_RADIUS = 15
    BORDER_WIDTH = 2

# In modern_app.py:
from ui.themes import Theme

# Use:
fg_color=Theme.PRIMARY
font=ctk.CTkFont(*Theme.TITLE_FONT)
```

### Dynamic Theme Switching

Add a button to switch themes on-the-fly:

```python
def switch_theme(self):
    """Toggle between dark and light themes."""
    current = ctk.get_appearance_mode()
    if current == "Dark":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")

# Add button in top bar:
ctk.CTkButton(
    controls_frame,
    text="🌓 Theme",
    command=self.switch_theme,
    ...
)
```

---

## 🎨 Pre-made Color Schemes

### Ocean Theme
```python
colors = [
    ("#006994", "#004d6f"),  # Deep Blue
    ("#00a8cc", "#0086a3"),  # Cyan
    ("#0abdc6", "#0897a0"),  # Turquoise
    ("#00e0c6", "#00b39f"),  # Aqua
    ("#4dd0e1", "#3aa7b5"),  # Light Blue
    ("#80deea", "#66b2bc"),  # Sky
]
```

### Sunset Theme
```python
colors = [
    ("#ff6b6b", "#cc5555"),  # Coral
    ("#ff8c42", "#cc7035"),  # Orange
    ("#ffb347", "#cc8f39"),  # Peach
    ("#ffd93d", "#ccae31"),  # Yellow
    ("#f9ca24", "#c7a11d"),  # Gold
    ("#f39c12", "#c27d0e"),  # Dark Orange
]
```

### Forest Theme
```python
colors = [
    ("#2d5016", "#234012"),  # Dark Green
    ("#40770f", "#335f0c"),  # Forest
    ("#5e9c2e", "#4b7d25"),  # Leaf
    ("#80b918", "#669413"),  # Lime
    ("#a4c639", "#839e2e"),  # Yellow-Green
    ("#b8e986", "#93ba6b"),  # Light Green
]
```

### Neon Theme
```python
colors = [
    ("#ff006e", "#cc0058"),  # Hot Pink
    ("#8338ec", "#6929bd"),  # Purple
    ("#3a86ff", "#2e6bcc"),  # Blue
    ("#06ffa5", "#05cc84"),  # Mint
    ("#ffbe0b", "#cc9809"),  # Yellow
    ("#fb5607", "#c94506"),  # Orange
]
```

### Monochrome Theme
```python
colors = [
    ("#2c3e50", "#1a2530"),  # Very Dark
    ("#34495e", "#283747"),  # Dark
    ("#546e7a", "#435861"),  # Medium Dark
    ("#78909c", "#60737d"),  # Medium
    ("#90a4ae", "#73838b"),  # Medium Light
    ("#b0bec5", "#8d989d"),  # Light
]
```

---

## 🖼️ Background Customization

### Setup Screen Background

**Location**: `ui/modern_app.py`, line ~58

```python
# Current (transparent):
main_container = ctk.CTkFrame(self, fg_color=("gray95", "gray10"))

# Solid color:
main_container = ctk.CTkFrame(self, fg_color="#1a1a1a")

# Or use an image (requires additional code):
# Add to __init__:
bg_image = Image.open("background.jpg")
self.bg_image = ctk.CTkImage(bg_image, size=(1920, 1080))
bg_label = ctk.CTkLabel(main_container, image=self.bg_image, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
```

### Game Board Background

**Location**: `ui/modern_app.py`, line ~206

```python
# Current:
main_container = ctk.CTkFrame(self, fg_color=("gray95", "gray10"))

# Customize:
main_container = ctk.CTkFrame(self, fg_color="#0d1117")  # GitHub dark
main_container = ctk.CTkFrame(self, fg_color="#1e1e1e")  # VS Code dark
```

---

## 🔧 Configuration File

For easy customization, create a config file:

**New File**: `config/theme_config.py`

```python
"""
Theme Configuration
Centralized customization for modern UI
"""

# ============== APPEARANCE ==============
APPEARANCE_MODE = "dark"  # "dark", "light", or "system"
COLOR_THEME = "blue"      # "blue", "green", or "dark-blue"

# ============== WINDOW ==============
WINDOW_SIZE = "1920x1080"
WINDOW_TITLE = "SCOPONE • Gioco di Carte Italiano"
FULLSCREEN = False

# ============== COLORS ==============
PLAYER_COLORS = [
    ("#e74c3c", "#c0392b"),  # Red
    ("#3498db", "#2980b9"),  # Blue
    ("#2ecc71", "#27ae60"),  # Green
    ("#f39c12", "#e67e22"),  # Orange
    ("#9b59b6", "#8e44ad"),  # Purple
    ("#1abc9c", "#16a085"),  # Teal
]

BUTTON_COLORS = {
    'start': ("#2ecc71", "#27ae60"),
    'new_game': ("#27ae60", "#229954"),
    'toggle': ("#3498db", "#2980b9"),
    'stats': ("#9b59b6", "#8e44ad"),
    'menu': ("gray70", "gray30"),
}

# ============== FONTS ==============
FONT_FAMILY = "Segoe UI"
FONT_SIZES = {
    'title': 72,
    'subtitle': 20,
    'header': 18,
    'body': 16,
    'button': 15,
    'small': 13,
    'log': 11,
}

# ============== LAYOUT ==============
CORNER_RADIUS = 15
BORDER_WIDTH = 2
TOP_BAR_HEIGHT = 80
SIDEBAR_WIDTH = 350

# ============== CARDS ==============
CARD_CORNER_RADIUS = 8
CARD_BORDER_WIDTH = 2

# ============== TIMING ==============
AI_DELAY = 1500  # milliseconds
```

**Then in `ui/modern_app.py`**:

```python
from config.theme_config import *

# Use throughout:
self.geometry(WINDOW_SIZE)
self.title(WINDOW_TITLE)
ctk.set_appearance_mode(APPEARANCE_MODE)
font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SIZES['title'])
```

---

## 🎮 Icon/Emoji Customization

### Change Emojis

**Location**: Throughout `ui/modern_app.py`

```python
# Current:
text="🎴 SCOPONE"       # Cards emoji
text="▶  INIZIA"        # Play button
text="🔄 Nuova"         # Refresh
text="👁 Mostra"        # Eye
text="📊 Statistiche"   # Chart
text="🏠 Menu"          # Home
text="👤 Marco"         # Person
text="🤖 AI"            # Robot

# Alternatives:
text="♠️ SCOPONE"       # Spade
text="🃏 SCOPONE"       # Joker
text="🎯 INIZIA"        # Target
text="♻️ Nuova"         # Recycle
text="👀 Mostra"        # Eyes
text="📈 Stats"         # Trending
text="🏡 Menu"          # House with garden
text="😀 Marco"         # Smiley
text="🧠 AI"            # Brain
```

---

## 🎨 Save Your Custom Theme

After customizing, save your changes:

### 1. Document Your Theme

Create `MY_THEME.md`:

```markdown
# My Custom Theme

## Colors
- Primary: #your_color
- Player 1: #your_color
...

## Fonts
- Main: Your Font, 72pt
...

## Notes
- Changed ocean theme
- Larger cards
- Custom button colors
```

### 2. Backup Original

```bash
cp ui/modern_app.py ui/modern_app_original.py
```

### 3. Version Control

```bash
git add ui/modern_app.py
git commit -m "Custom ocean theme with larger cards"
```

---

## 🌟 Share Your Theme

Created an amazing theme? Share it!

### Package Theme

1. Export your color scheme
2. Document all changes
3. Take screenshots
4. Create theme guide

### Theme Template

```python
"""
THEME NAME: Ocean Breeze
AUTHOR: Your Name
DATE: 2024

DESCRIPTION:
Calm ocean colors with large cards and smooth animations.

CHANGES:
- Player colors: Ocean blue palette
- Card size: 120x180 (larger)
- Fonts: Roboto family
- Corner radius: 20px (more rounded)
"""
```

---

## 🏁 Quick Start Checklist

Ready to customize? Follow this checklist:

- [ ] **Backup original files**
- [ ] **Choose color scheme** (ocean, sunset, forest, etc.)
- [ ] **Update player colors** (6 colors)
- [ ] **Change button colors** (5 buttons)
- [ ] **Adjust fonts** (family and sizes)
- [ ] **Modify layout** (spacing, sizes)
- [ ] **Test changes** (run application)
- [ ] **Document theme** (save settings)
- [ ] **Take screenshots**
- [ ] **Commit changes** (version control)

---

## 🐛 Troubleshooting

### Colors Don't Apply
- **Issue**: Wrong format
- **Fix**: Use hex: `"#RRGGBB"` or name: `"red"`
- **Example**: `"#2ecc71"` not `"2ecc71"`

### Font Not Found
- **Issue**: Font not installed on system
- **Fix**: Use common fonts (Arial, Helvetica)
- **Check**: Print available fonts:
```python
from tkinter import font
print(font.families())
```

### Layout Breaks
- **Issue**: Changed too many sizes
- **Fix**: Adjust proportionally
- **Restore**: Use backup file

---

## 🎉 Have Fun Customizing!

The modern interface is designed to be easily customizable. Experiment, create, and make it your own!

**Tips**:
- Start small (change one color at a time)
- Test frequently (run app after each change)
- Use color picker tools (Google "color picker")
- Browse design inspiration (Dribbble, Behance)
- Keep backups (save original files)

**Buona Personalizzazione!** 🎨✨

---

**Need Help?** Check README_MODERN.md for documentation or create an issue.
