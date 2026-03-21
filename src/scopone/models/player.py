"""Player domain model."""

from typing import Iterable, List, Optional, Union

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
        self.id = player_id
        self.name = name
        self.hand = []  # type: List[Card]
        self.captured = []  # type: List[Card]
        self.sweeps = 0
        self.total_points = 0
        self.primiera_point = 0
        self.is_ai = is_ai
        self.is_human = is_human
        self.team = team

    def reset(self) -> None:
        self.hand = []
        self.captured = []
        self.sweeps = 0
        self.total_points = 0
        self.primiera_point = 0

    def add_to_hand(self, cards: Union[Card, Iterable[Card]]) -> None:
        if isinstance(cards, tuple):
            self.hand.append(cards)
        else:
            self.hand.extend(cards)
        self.hand.sort(key=lambda card: (card[0], card[1]))

    def remove_from_hand(self, card: Card) -> bool:
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False

    def capture_cards(self, cards: Union[Card, Iterable[Card]]) -> None:
        if isinstance(cards, tuple):
            self.captured.append(cards)
        else:
            self.captured.extend(cards)

    def add_sweep(self) -> None:
        self.sweeps += 1

    def has_card(self, card: Card) -> bool:
        return card in self.hand

    def get_hand_size(self) -> int:
        return len(self.hand)

    def get_captured_count(self) -> int:
        return len(self.captured)

    def count_coins(self) -> int:
        return len([card for card in self.captured if card[1] == "Denari"])

    def has_settebello(self) -> bool:
        return (7, "Denari") in self.captured

    def __repr__(self) -> str:
        player_type = "AI" if self.is_ai else "Human"
        return (
            f"Player({self.name}, {player_type}, hand={len(self.hand)}, "
            f"captured={len(self.captured)})"
        )
