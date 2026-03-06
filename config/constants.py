# ============================================================================
# SCOPONE - Constants Configuration
# ============================================================================
# Centralizza tutte le costanti di gioco per una facile manutenzione
# ============================================================================

# --- Card Game Constants ---
SEMI = ["Denari", "Coppe", "Bastoni", "Spade"]
SIMBOLI = {
    "Denari": "♦",
    "Coppe": "♥",
    "Bastoni": "♣",
    "Spade": "♠"
}

# Primiera values for each card
VALORI_PRIMIERA = {
    7: 21,   # Seven is worth 21 points
    6: 18,   # Six is worth 18 points
    1: 16,   # Ace is worth 16 points
    5: 15,   # Five is worth 15 points
    4: 14,   # Four is worth 14 points
    3: 13,   # Three is worth 13 points
    2: 12,   # Two is worth 12 points
    8: 10,   # Eight through Ten are worth 10 points
    9: 10,
    10: 10
}

# Total cards in a deck
TOTAL_DECK_SIZE = 40  # 10 cards per suit × 4 suits

# Cards to deal to table at start
INITIAL_TABLE_CARDS = 4

# --- Game Configuration ---
# Only 2 or 4 players allowed
MIN_PLAYERS = 2
MAX_PLAYERS = 4
DEFAULT_PLAYERS = 4

# Distribution rules per player count
# 2 players: 10 cards each, 0 on table (then restock with remaining 20)
# 4 players: 9 cards each, 4 on table (current rules)
INITIAL_HAND_CARDS = {
    2: 10,  # 2-player: 10 cards per hand
    4: 9    # 4-player: 9 cards per hand
}

INITIAL_TABLE_CARDS_BY_MODE = {
    2: 0,   # 2-player: 0 cards on table initially
    4: 4    # 4-player: 4 cards on table initially
}

# Team configuration (4-player mode only)
# Team A: players 0 and 2 (opposite sides)
# Team B: players 1 and 3 (opposite sides)
TEAM_A_PLAYERS = {0, 2}
TEAM_B_PLAYERS = {1, 3}

# --- Scoring Rules ---
# Points for each category
POINTS_FOR_MOST_CARDS = 1       # More than 20 captured cards
POINTS_FOR_MOST_COINS = 1       # More than 5 Denari coins
POINTS_FOR_SETTEBELLO = 1       # Having the 7♦
POINTS_FOR_PRIMIERA = 1         # Highest primiera score
POINTS_PER_SWEEP = 1            # Each scopa/sweep

THRESHOLD_CARDS = 20            # Need more than this for points
THRESHOLD_COINS = 5             # Need more than this for points

# --- UI Configuration ---
DEFAULT_WINDOW_WIDTH = 1800
DEFAULT_WINDOW_HEIGHT = 1000

# Colors for UI
COLOR_BG_PRIMARY = "#0e0e0e"
COLOR_BG_SECONDARY = "#1a1a1a"
COLOR_BG_TERTIARY = "#181818"
COLOR_TEXT_PRIMARY = "white"
COLOR_TEXT_SECONDARY = "#0f0"
COLOR_TEXT_HIGHLIGHT = "cyan"
COLOR_TEXT_GOLD = "gold"
COLOR_ACCENT_GREEN = "#2ecc71"
COLOR_ACCENT_BLUE = "#3498db"
COLOR_ACCENT_RED = "#e74c3c"
COLOR_ACCENT_ORANGE = "#f39c12"
COLOR_ACCENT_PURPLE = "#9b59b6"
COLOR_ACCENT_TEAL = "#1abc9c"
COLOR_ACCENT_YELLOW = "#f1c40f"

# --- Fonts ---
FONT_TITLE = ("Arial", 48, "bold")
FONT_SUBTITLE = ("Arial", 20, "normal")
FONT_HEADING = ("Arial", 16, "bold")
FONT_SUBHEADING = ("Arial", 14, "bold")
FONT_BODY = ("Arial", 12, "normal")
FONT_SMALL = ("Arial", 10, "normal")
FONT_TINY = ("Arial", 8, "normal")
FONT_MONOSPACE = ("Consolas", 10, "normal")

# --- Card Sizes (for images) ---
CARD_SIZE_HAND = (50, 75)           # Smaller cards in hand
CARD_SIZE_TABLE = (90, 135)         # Larger cards on table
CARD_SIZE_CAPTURED = (60, 90)       # Medium cards in captured display

# --- Game Delays (ms) ---
AI_THINKING_DELAY = 1500            # Time before AI plays a card
AI_TURN_DELAY = 500                 # Additional delay after AI plays

# --- Player Types ---
PLAYER_TYPE_HUMAN = "human"
PLAYER_TYPE_AI = "ai"

# --- Game States ---
GAME_STATE_SETUP = "setup"
GAME_STATE_PLAYING = "playing"
GAME_STATE_FINISHED = "finished"

# Default player names
DEFAULT_PLAYER_NAMES = ["Tu", "AI 1", "AI 2", "AI 3", "AI 4", "AI 5"]

# --- Logger Configuration ---
LOG_PREFIX = ">"
LOG_SUCCESS = "✓"
LOG_ERROR = "❌"
LOG_WARNING = "⚠️"
LOG_INFO = "💡"
LOG_AI = "🤖"
LOG_CELEBRATION = "🎉"
LOG_TROPHY = "🏆"
LOG_MATCH_END = "🏁"
