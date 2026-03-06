"""Card and Deck classes for Scopone."""

from __future__ import annotations

import random
from enum import Enum
from typing import List, Optional


class Suit(Enum):
    """The four suits of an Italian 40-card deck."""

    COINS = "Coins"       # Denari
    CUPS = "Cups"         # Coppe
    SWORDS = "Swords"     # Spade
    CLUBS = "Clubs"       # Bastoni


# Human-readable short names for display
SUIT_SYMBOLS = {
    Suit.COINS: "♦",
    Suit.CUPS: "♥",
    Suit.SWORDS: "♠",
    Suit.CLUBS: "♣",
}

# Rank display names (1-7 are numeric; 8=Fante/J, 9=Cavallo/Q, 10=Re/K)
RANK_NAMES = {
    1: "A",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "J",
    9: "Q",
    10: "K",
}

# Primiera values used in scoring
PRIMIERA_VALUES = {
    7: 21,
    6: 18,
    1: 16,  # Ace
    5: 15,
    4: 14,
    3: 13,
    2: 12,
    8: 10,  # Fante
    9: 10,  # Cavallo
    10: 10,  # Re
}


class Card:
    """A single playing card with a suit and a rank (1–10).

    Rank meanings
    -------------
    1 : Ace (Asso)
    2–7 : numeric cards
    8 : Knave (Fante)
    9 : Knight (Cavallo)
    10 : King (Re)

    The *value* property is used for capture arithmetic (Ace=1 … King=10).
    """

    def __init__(self, suit: Suit, rank: int) -> None:
        if rank < 1 or rank > 10:
            raise ValueError(f"Rank must be between 1 and 10, got {rank}")
        self.suit = suit
        self.rank = rank

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def value(self) -> int:
        """Numeric capture value (same as rank for this deck)."""
        return self.rank

    @property
    def primiera_value(self) -> int:
        """Primiera scoring value for end-game calculation."""
        return PRIMIERA_VALUES[self.rank]

    @property
    def is_sette_bello(self) -> bool:
        """True if this card is the 7 of Coins (the most prized card)."""
        return self.suit == Suit.COINS and self.rank == 7

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"{RANK_NAMES[self.rank]}{SUIT_SYMBOLS[self.suit]}"

    def __repr__(self) -> str:
        return f"Card({self.suit.value}, {self.rank})"

    # ------------------------------------------------------------------
    # Comparison (useful for sorting)
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))

    def __lt__(self, other: "Card") -> bool:
        return (self.suit.value, self.rank) < (other.suit.value, other.rank)


class Deck:
    """A full 40-card Italian deck (4 suits × 10 ranks)."""

    def __init__(self) -> None:
        self.cards: List[Card] = [
            Card(suit, rank) for suit in Suit for rank in range(1, 11)
        ]

    def shuffle(self) -> None:
        """Shuffle the deck in place."""
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> List[Card]:
        """Remove and return *num_cards* from the top of the deck."""
        if num_cards > len(self.cards):
            raise ValueError(
                f"Cannot deal {num_cards} cards; only {len(self.cards)} remain"
            )
        hand, self.cards = self.cards[:num_cards], self.cards[num_cards:]
        return hand

    def __len__(self) -> int:
        return len(self.cards)

    def __repr__(self) -> str:
        return f"Deck({len(self.cards)} cards)"


def find_capture_combinations(
    played_value: int, table_cards: List[Card]
) -> List[List[Card]]:
    """Return all subsets of *table_cards* whose values sum to *played_value*.

    The result includes both single-card matches and multi-card combinations.
    The list is sorted so that single-card matches come first (they are
    mandatory in Scopone when they exist).

    Parameters
    ----------
    played_value:
        The capture value of the card just played.
    table_cards:
        The cards currently on the table.

    Returns
    -------
    A list of combinations (each combination is a list of Card objects).
    An empty list means no capture is possible.
    """
    singles: List[List[Card]] = []
    multiples: List[List[Card]] = []

    n = len(table_cards)
    # Iterate over all non-empty subsets using bitmask
    for mask in range(1, 1 << n):
        subset = [table_cards[i] for i in range(n) if mask & (1 << i)]
        if sum(c.value for c in subset) == played_value:
            if len(subset) == 1:
                singles.append(subset)
            else:
                multiples.append(subset)

    # In Scopone, if any single-card match exists the player MUST capture
    # a single card (they choose which one if there are multiple singles).
    if singles:
        return singles  # only single-card captures are legal
    return multiples
