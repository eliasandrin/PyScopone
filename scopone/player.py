"""Player and Team classes for Scopone."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, List, Optional

from .card import Card, Suit, find_capture_combinations

if TYPE_CHECKING:
    pass


class Player:
    """Represents one of the four Scopone players.

    Parameters
    ----------
    name:
        Display name for the player.
    is_human:
        If *True*, the game will prompt this player for input.
        If *False*, the AI strategy is used.
    """

    def __init__(self, name: str, is_human: bool = False) -> None:
        self.name = name
        self.is_human = is_human
        self.hand: List[Card] = []
        self.captured: List[Card] = []   # all cards this player has captured
        self.scope: int = 0              # number of scope (sweeps) made

    # ------------------------------------------------------------------
    # Hand management
    # ------------------------------------------------------------------

    def receive_cards(self, cards: List[Card]) -> None:
        """Add *cards* to this player's hand."""
        self.hand.extend(cards)

    def play_card(self, card: Card) -> Card:
        """Remove *card* from hand and return it."""
        self.hand.remove(card)
        return card

    # ------------------------------------------------------------------
    # AI card-selection logic
    # ------------------------------------------------------------------

    def choose_card_to_play(self, table: List[Card]) -> Card:
        """Choose which card to play (AI strategy).

        Priority order:
        1. Play a card that makes a *scopa* (clears the table).
        2. Capture the *sette bello* (7 of Coins) if possible.
        3. Capture the most table cards in a single move.
        4. Play the card with the lowest primiera value (keep good cards).
        """
        # --- 1. Look for a scopa ---
        for card in self.hand:
            combos = find_capture_combinations(card.value, table)
            for combo in combos:
                if set(combo) == set(table):
                    return card  # this play will sweep the table

        # --- 2. Capture the sette bello ---
        for card in self.hand:
            combos = find_capture_combinations(card.value, table)
            for combo in combos:
                if any(c.is_sette_bello for c in combo):
                    return card

        # --- 3. Capture the most table cards (greedy) ---
        best_card: Optional[Card] = None
        best_count = 0
        for card in self.hand:
            combos = find_capture_combinations(card.value, table)
            for combo in combos:
                if len(combo) > best_count:
                    best_count = len(combo)
                    best_card = card
        if best_card is not None:
            return best_card

        # --- 4. No capture possible – play the least-valuable card ---
        return min(self.hand, key=lambda c: c.primiera_value)

    def choose_capture(
        self, played_card: Card, table: List[Card]
    ) -> Optional[List[Card]]:
        """Choose which capture combination to take (AI strategy).

        Returns the chosen combination, or *None* if no capture is possible.
        """
        combos = find_capture_combinations(played_card.value, table)
        if not combos:
            return None

        # Prefer combos that contain the sette bello
        for combo in combos:
            if any(c.is_sette_bello for c in combo):
                return combo

        # Prefer combos that clear the table (scopa)
        for combo in combos:
            if set(combo) == set(table):
                return combo

        # Prefer the combo that captures the most cards
        return max(combos, key=len)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def show_hand(self) -> str:
        """Return a numbered list of cards in hand for display."""
        return "  ".join(
            f"[{i + 1}] {card}" for i, card in enumerate(sorted(self.hand))
        )

    def __repr__(self) -> str:
        return f"Player({self.name!r}, hand={len(self.hand)}, captured={len(self.captured)})"


class Team:
    """Two players that play together as a team."""

    def __init__(self, name: str, player1: Player, player2: Player) -> None:
        self.name = name
        self.players = [player1, player2]

    @property
    def all_captured(self) -> List[Card]:
        """Combined captured pile from both team members."""
        return self.players[0].captured + self.players[1].captured

    @property
    def scope_total(self) -> int:
        """Total scope (sweeps) for the team."""
        return self.players[0].scope + self.players[1].scope

    def card_count(self) -> int:
        return len(self.all_captured)

    def coin_count(self) -> int:
        return sum(1 for c in self.all_captured if c.suit == Suit.COINS)

    def has_sette_bello(self) -> bool:
        return any(c.is_sette_bello for c in self.all_captured)

    def primiera_score(self) -> int:
        """Calculate the primiera score.

        For each suit, take the card with the highest primiera value from
        the team's captured pile.  Sum the four best-of-suit primiera values.
        A suit contributes 0 if the team captured no card in that suit.
        """
        score = 0
        for suit in Suit:
            suit_cards = [c for c in self.all_captured if c.suit == suit]
            if suit_cards:
                score += max(c.primiera_value for c in suit_cards)
        return score

    def __repr__(self) -> str:
        return f"Team({self.name!r})"
