"""Game rules and gameplay constants."""

from typing import List

from scopone.types import Card

SEMI = ["Denari", "Coppe", "Bastoni", "Spade"]
SIMBOLI = {
    "Denari": "\u2666",
    "Coppe": "\u2665",
    "Bastoni": "\u2663",
    "Spade": "\u2660",
}

VALORI_PRIMIERA = {
    7: 21,
    6: 18,
    1: 16,
    5: 15,
    4: 14,
    3: 13,
    2: 12,
    8: 10,
    9: 10,
    10: 10,
}

TOTAL_DECK_SIZE = 40
INITIAL_TABLE_CARDS = 4

MIN_PLAYERS = 2
MAX_PLAYERS = 4
DEFAULT_PLAYERS = 4

INITIAL_HAND_CARDS = {
    2: 10,
    4: 9,
}

INITIAL_TABLE_CARDS_BY_MODE = {
    2: 0,
    4: 4,
}

TEAM_A_PLAYERS = {0, 2}
TEAM_B_PLAYERS = {1, 3}

POINTS_FOR_MOST_CARDS = 1
POINTS_FOR_MOST_COINS = 1
POINTS_FOR_SETTEBELLO = 1
POINTS_FOR_PRIMIERA = 1
POINTS_PER_SWEEP = 1

THRESHOLD_CARDS = 20
THRESHOLD_COINS = 5

DEFAULT_PLAYER_NAMES = ["Tu", "AI 1", "AI 2", "AI 3", "AI 4", "AI 5"]

FULL_DECK = [
    (value, suit)
    for suit in SEMI
    for value in range(1, 11)
]  # type: List[Card]
