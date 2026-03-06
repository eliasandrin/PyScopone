# ============================================================================
# SCOPONE - Config Package
# ============================================================================

from .constants import *

__all__ = [
    # Game Constants
    'SEMI', 'SIMBOLI', 'VALORI_PRIMIERA', 'TOTAL_DECK_SIZE', 'INITIAL_TABLE_CARDS',
    # Player Configuration
    'MIN_PLAYERS', 'MAX_PLAYERS', 'DEFAULT_PLAYERS',
    # Scoring Rules
    'POINTS_FOR_MOST_CARDS', 'POINTS_FOR_MOST_COINS', 'POINTS_FOR_SETTEBELLO',
    'POINTS_FOR_PRIMIERA', 'POINTS_PER_SWEEP', 'THRESHOLD_CARDS', 'THRESHOLD_COINS',
    # UI Configuration
    'DEFAULT_WINDOW_WIDTH', 'DEFAULT_WINDOW_HEIGHT',
    # Colors
    'COLOR_BG_PRIMARY', 'COLOR_BG_SECONDARY', 'COLOR_BG_TERTIARY',
    'COLOR_TEXT_PRIMARY', 'COLOR_TEXT_SECONDARY', 'COLOR_TEXT_HIGHLIGHT',
    'COLOR_TEXT_GOLD', 'COLOR_ACCENT_GREEN', 'COLOR_ACCENT_BLUE',
    'COLOR_ACCENT_RED', 'COLOR_ACCENT_ORANGE', 'COLOR_ACCENT_PURPLE',
    'COLOR_ACCENT_TEAL', 'COLOR_ACCENT_YELLOW',
    # Fonts
    'FONT_TITLE', 'FONT_SUBTITLE', 'FONT_HEADING', 'FONT_SUBHEADING',
    'FONT_BODY', 'FONT_SMALL', 'FONT_TINY', 'FONT_MONOSPACE',
    # Card Sizes
    'CARD_SIZE_HAND', 'CARD_SIZE_TABLE', 'CARD_SIZE_CAPTURED',
    # Game Delays
    'AI_THINKING_DELAY', 'AI_TURN_DELAY',
    # Player Types
    'PLAYER_TYPE_HUMAN', 'PLAYER_TYPE_AI',
    # Game States
    'GAME_STATE_SETUP', 'GAME_STATE_PLAYING', 'GAME_STATE_FINISHED',
    # Default Names
    'DEFAULT_PLAYER_NAMES',
    # Logger
    'LOG_PREFIX', 'LOG_SUCCESS', 'LOG_ERROR', 'LOG_WARNING', 'LOG_INFO',
    'LOG_AI', 'LOG_CELEBRATION', 'LOG_TROPHY', 'LOG_MATCH_END'
]
