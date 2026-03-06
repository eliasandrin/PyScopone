"""Tests for Card and Deck classes."""

import pytest

from scopone.card import (
    Card,
    Deck,
    Suit,
    find_capture_combinations,
    PRIMIERA_VALUES,
)


class TestCard:
    def test_str_representation(self) -> None:
        assert str(Card(Suit.COINS, 7)) == "7♦"
        assert str(Card(Suit.CUPS, 1)) == "A♥"
        assert str(Card(Suit.SWORDS, 8)) == "J♠"
        assert str(Card(Suit.CLUBS, 10)) == "K♣"

    def test_value_equals_rank(self) -> None:
        for rank in range(1, 11):
            card = Card(Suit.COINS, rank)
            assert card.value == rank

    def test_primiera_values(self) -> None:
        assert Card(Suit.COINS, 7).primiera_value == 21
        assert Card(Suit.CUPS, 6).primiera_value == 18
        assert Card(Suit.SWORDS, 1).primiera_value == 16
        assert Card(Suit.CLUBS, 10).primiera_value == 10

    def test_sette_bello(self) -> None:
        assert Card(Suit.COINS, 7).is_sette_bello is True
        assert Card(Suit.CUPS, 7).is_sette_bello is False
        assert Card(Suit.COINS, 6).is_sette_bello is False

    def test_equality(self) -> None:
        c1 = Card(Suit.COINS, 5)
        c2 = Card(Suit.COINS, 5)
        c3 = Card(Suit.CUPS, 5)
        assert c1 == c2
        assert c1 != c3

    def test_hash_consistency(self) -> None:
        c1 = Card(Suit.COINS, 3)
        c2 = Card(Suit.COINS, 3)
        assert hash(c1) == hash(c2)

    def test_invalid_rank_raises(self) -> None:
        with pytest.raises(ValueError):
            Card(Suit.COINS, 0)
        with pytest.raises(ValueError):
            Card(Suit.COINS, 11)

    def test_all_primiera_values_covered(self) -> None:
        for rank in range(1, 11):
            card = Card(Suit.COINS, rank)
            assert card.primiera_value == PRIMIERA_VALUES[rank]


class TestDeck:
    def test_deck_has_40_cards(self) -> None:
        deck = Deck()
        assert len(deck) == 40

    def test_deck_has_all_suits_and_ranks(self) -> None:
        deck = Deck()
        for suit in Suit:
            for rank in range(1, 11):
                assert Card(suit, rank) in deck.cards

    def test_deal_removes_cards(self) -> None:
        deck = Deck()
        hand = deck.deal(10)
        assert len(hand) == 10
        assert len(deck) == 30

    def test_deal_four_hands(self) -> None:
        deck = Deck()
        hands = [deck.deal(10) for _ in range(4)]
        assert len(deck) == 0
        total = sum(len(h) for h in hands)
        assert total == 40

    def test_deal_too_many_raises(self) -> None:
        deck = Deck()
        with pytest.raises(ValueError):
            deck.deal(41)

    def test_shuffle_does_not_lose_cards(self) -> None:
        deck = Deck()
        deck.shuffle()
        assert len(deck) == 40
        for suit in Suit:
            for rank in range(1, 11):
                assert Card(suit, rank) in deck.cards


class TestFindCaptureCombinations:
    """Tests for find_capture_combinations helper."""

    def _table(self, *pairs):
        """Build a list of cards from (suit_enum, rank) pairs."""
        return [Card(suit, rank) for suit, rank in pairs]

    def test_no_match(self) -> None:
        table = self._table((Suit.COINS, 3), (Suit.CUPS, 4))
        assert find_capture_combinations(10, table) == []

    def test_single_card_match(self) -> None:
        table = self._table((Suit.COINS, 5), (Suit.CUPS, 3))
        combos = find_capture_combinations(5, table)
        assert len(combos) == 1
        assert combos[0][0] == Card(Suit.COINS, 5)

    def test_multi_card_match(self) -> None:
        table = self._table((Suit.COINS, 3), (Suit.CUPS, 4))
        combos = find_capture_combinations(7, table)
        assert len(combos) == 1
        assert len(combos[0]) == 2

    def test_single_takes_priority_over_multi(self) -> None:
        """When a single-card match exists, only singles should be returned."""
        # Table: 5, 3, 2  — playing a 5 could match the single 5 or the pair 3+2
        table = self._table(
            (Suit.COINS, 5), (Suit.CUPS, 3), (Suit.SWORDS, 2)
        )
        combos = find_capture_combinations(5, table)
        # Only the single-card match should be returned
        assert all(len(c) == 1 for c in combos)
        assert any(c[0] == Card(Suit.COINS, 5) for c in combos)

    def test_multiple_singles(self) -> None:
        """Multiple single-card matches all returned (player's choice)."""
        table = self._table(
            (Suit.COINS, 7), (Suit.CUPS, 7)
        )
        combos = find_capture_combinations(7, table)
        assert len(combos) == 2
        assert all(len(c) == 1 for c in combos)

    def test_empty_table(self) -> None:
        assert find_capture_combinations(5, []) == []

    def test_king_match(self) -> None:
        table = self._table((Suit.CLUBS, 10))
        combos = find_capture_combinations(10, table)
        assert len(combos) == 1

    def test_ace_match_with_combo(self) -> None:
        """Ace (value 1) can only match a single ace on the table."""
        table = self._table((Suit.CUPS, 1))
        combos = find_capture_combinations(1, table)
        assert len(combos) == 1
        assert combos[0][0] == Card(Suit.CUPS, 1)
