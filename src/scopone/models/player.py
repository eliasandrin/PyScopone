"""Player domain model."""

from __future__ import annotations

from typing import Iterable, Optional, Union

from scopone.config.game import DENARI_SUIT, SETTEBELLO_CARD
from scopone.types import Card


class Player:
    """Represents a player in the Scopone match."""

    def __init__(
        self,
        name: str,
        player_id: int,
        is_ai: bool = False,
        is_human: bool = False,
        team: Optional[int] = None,
    ) -> None:
        """Inizializza identita player e contenitori stato partita."""
        self.id: int = player_id
        self.name: str = name
        self.hand: list[Card] = []
        self.captured: list[Card] = []
        self.sweeps: int = 0
        self.total_points: int = 0
        self.primiera_point: int = 0
        self.is_ai: bool = is_ai
        self.is_human: bool = is_human
        self.team: Optional[int] = team

    def reset(self) -> None:
        """Azzera stato mano/prese/scope per avvio nuova partita o round."""
        self.hand = []
        self.captured = []
        self.sweeps = 0
        self.total_points = 0
        self.primiera_point = 0

    def add_to_hand(self, cards: Union[Card, Iterable[Card]]) -> None:
        """Aggiunge una o piu carte in Mano mantenendo ordinamento stabile."""
        if isinstance(cards, tuple):
            self.hand.append(cards)
        else:
            self.hand.extend(cards)
        self.hand.sort(key=lambda card: (card[0], card[1]))

    def remove_from_hand(self, card: Card) -> bool:
        """Rimuove una carta dalla Mano; ritorna False se non presente."""
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False

    def capture_cards(self, cards: Union[Card, Iterable[Card]]) -> None:
        """Aggiunge carte alle Prese del player."""
        if isinstance(cards, tuple):
            self.captured.append(cards)
        else:
            self.captured.extend(cards)

    def add_sweep(self) -> None:
        """Incrementa il contatore Scope del player."""
        self.sweeps += 1

    def has_card(self, card: Card) -> bool:
        """Verifica se una carta e attualmente in Mano."""
        return card in self.hand

    def get_hand_size(self) -> int:
        """Restituisce numero carte in Mano."""
        return len(self.hand)

    def get_captured_count(self) -> int:
        """Restituisce numero carte nelle Prese."""
        return len(self.captured)

    def count_coins(self) -> int:
        """Conta quante carte Denari sono presenti nelle Prese."""
        return sum(1 for card in self.captured if card[1] == DENARI_SUIT)

    def has_settebello(self) -> bool:
        """Indica se il player ha catturato il Settebello."""
        return SETTEBELLO_CARD in self.captured

    def __repr__(self) -> str:
        """Rappresentazione compatta utile in debug e log tecnici."""
        player_type = "AI" if self.is_ai else "Human"
        return (
            f"Player({self.name}, {player_type}, hand={len(self.hand)}, "
            f"captured={len(self.captured)})"
        )
