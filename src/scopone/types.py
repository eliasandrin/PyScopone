"""Shared domain types."""

from typing import Literal, Tuple

CardValue = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
Suit = Literal["Denari", "Coppe", "Bastoni", "Spade"]
TeamId = Literal[0, 1]

Card = Tuple[CardValue, Suit]

__all__ = ["Card", "CardValue", "Suit", "TeamId"]
