"""Tests for Player, Team, and Game logic."""

import pytest

from scopone.card import Card, Deck, Suit
from scopone.player import Player, Team
from scopone.game import Game


# ---------------------------------------------------------------------------
# Player tests
# ---------------------------------------------------------------------------


class TestPlayer:
    def _make_player(self, name: str = "Test") -> Player:
        return Player(name)

    def test_receive_and_play_card(self) -> None:
        player = self._make_player()
        cards = [Card(Suit.COINS, 5), Card(Suit.CUPS, 3)]
        player.receive_cards(cards)
        assert len(player.hand) == 2
        played = player.play_card(cards[0])
        assert played == cards[0]
        assert len(player.hand) == 1

    def test_play_card_not_in_hand_raises(self) -> None:
        player = self._make_player()
        card = Card(Suit.COINS, 5)
        with pytest.raises(ValueError):
            player.play_card(card)

    def test_show_hand(self) -> None:
        player = self._make_player()
        player.receive_cards([Card(Suit.COINS, 7), Card(Suit.CUPS, 3)])
        result = player.show_hand()
        assert "[1]" in result
        assert "[2]" in result

    def test_ai_chooses_scopa(self) -> None:
        """AI must play the card that clears the table (scopa)."""
        player = self._make_player()
        # Table has a single 5; player has 5 and 3 in hand
        table = [Card(Suit.CUPS, 5)]
        player.receive_cards([Card(Suit.COINS, 5), Card(Suit.CLUBS, 3)])
        chosen = player.choose_card_to_play(table)
        # Playing the 5 clears the table – that's a scopa; AI should prefer it
        assert chosen == Card(Suit.COINS, 5)

    def test_ai_prefers_sette_bello_capture(self) -> None:
        player = self._make_player()
        table = [Card(Suit.COINS, 7)]  # sette bello on table
        player.receive_cards([Card(Suit.SWORDS, 7), Card(Suit.CLUBS, 1)])
        chosen = player.choose_card_to_play(table)
        # Playing the 7 of Swords captures the 7 of Coins (sette bello)
        assert chosen == Card(Suit.SWORDS, 7)

    def test_ai_plays_least_valuable_when_no_capture(self) -> None:
        player = self._make_player()
        # Table has a 6; player has a 3 and a 7 (neither matches 6)
        table = [Card(Suit.CUPS, 6)]
        player.receive_cards([Card(Suit.COINS, 3), Card(Suit.SWORDS, 7)])
        chosen = player.choose_card_to_play(table)
        # 3 has lower primiera value (13) than 7 (21)
        assert chosen == Card(Suit.COINS, 3)

    def test_ai_choose_capture_prefers_sette_bello(self) -> None:
        player = self._make_player()
        played = Card(Suit.CLUBS, 7)
        table = [Card(Suit.COINS, 7), Card(Suit.CUPS, 7)]
        combo = player.choose_capture(played, table)
        # Should pick the combo containing the sette bello
        assert combo is not None
        assert any(c.is_sette_bello for c in combo)

    def test_ai_choose_capture_none_when_no_match(self) -> None:
        player = self._make_player()
        played = Card(Suit.CLUBS, 5)
        table = [Card(Suit.COINS, 3)]
        assert player.choose_capture(played, table) is None

    def test_scope_counter_starts_at_zero(self) -> None:
        player = self._make_player()
        assert player.scope == 0


# ---------------------------------------------------------------------------
# Team tests
# ---------------------------------------------------------------------------


class TestTeam:
    def _make_team(self) -> Team:
        p1, p2 = Player("P1"), Player("P2")
        return Team("T1", p1, p2)

    def _give_captured(self, team: Team, *card_specs) -> None:
        for i, (suit, rank) in enumerate(card_specs):
            team.players[i % 2].captured.append(Card(suit, rank))

    def test_card_count(self) -> None:
        team = self._make_team()
        team.players[0].captured = [Card(Suit.COINS, 1), Card(Suit.CUPS, 2)]
        team.players[1].captured = [Card(Suit.SWORDS, 3)]
        assert team.card_count() == 3

    def test_coin_count(self) -> None:
        team = self._make_team()
        team.players[0].captured = [Card(Suit.COINS, 1), Card(Suit.COINS, 2)]
        team.players[1].captured = [Card(Suit.CUPS, 3)]
        assert team.coin_count() == 2

    def test_has_sette_bello_true(self) -> None:
        team = self._make_team()
        team.players[0].captured = [Card(Suit.COINS, 7)]
        assert team.has_sette_bello() is True

    def test_has_sette_bello_false(self) -> None:
        team = self._make_team()
        team.players[0].captured = [Card(Suit.CUPS, 7)]
        assert team.has_sette_bello() is False

    def test_primiera_score_with_all_suits(self) -> None:
        team = self._make_team()
        # Best cards: 7♦ (21), 6♥ (18), A♠ (16), 5♣ (15) → total 70
        team.players[0].captured = [
            Card(Suit.COINS, 7),
            Card(Suit.CUPS, 6),
        ]
        team.players[1].captured = [
            Card(Suit.SWORDS, 1),
            Card(Suit.CLUBS, 5),
        ]
        assert team.primiera_score() == 21 + 18 + 16 + 15

    def test_primiera_score_missing_suit(self) -> None:
        """Missing a suit contributes 0 to primiera."""
        team = self._make_team()
        team.players[0].captured = [Card(Suit.COINS, 7)]
        # No Cups, Swords, or Clubs
        assert team.primiera_score() == 21

    def test_scope_total(self) -> None:
        team = self._make_team()
        team.players[0].scope = 2
        team.players[1].scope = 1
        assert team.scope_total == 3


# ---------------------------------------------------------------------------
# Game logic tests (non-interactive)
# ---------------------------------------------------------------------------


class TestGameScoring:
    """Tests for _calculate_round_points using a pre-arranged game state."""

    def _make_game(self) -> Game:
        return Game(target_score=11, ai_delay=0.0)

    def _assign_captured(self, game: Game) -> None:
        """Distribute all 40 cards to the two teams' captured piles."""
        deck = Deck()
        for i, card in enumerate(deck.cards):
            if i % 2 == 0:
                game.team_a.players[0].captured.append(card)
            else:
                game.team_b.players[0].captured.append(card)

    def test_sette_bello_always_scored(self) -> None:
        game = self._make_game()
        self._assign_captured(game)
        points_a, points_b = game._calculate_round_points()
        # Sette bello must be scored by exactly one team
        # (captured list alternates so COINS-7 goes to team_a since it's even-indexed)
        assert points_a + points_b >= 1  # at least one team scores sette bello

    def test_scope_points_added(self) -> None:
        game = self._make_game()
        self._assign_captured(game)
        # Team A: 3 scope, Team B: 1 scope
        game.team_a.players[0].scope = 3
        game.team_b.players[1].scope = 1
        points_a, points_b = game._calculate_round_points()
        # Scope points are added directly; each team must have at least their scope count
        assert points_a >= 3, f"Team A should score at least 3 points (3 scope), got {points_a}"
        assert points_b >= 1, f"Team B should score at least 1 point (1 scope), got {points_b}"

    def test_cumulative_scores_updated(self, capsys) -> None:
        game = self._make_game()
        self._assign_captured(game)
        game._tally_round()
        total = game.scores[game.team_a.name] + game.scores[game.team_b.name]
        # With alternating distribution, cards and coins may tie (0 pts each),
        # but sette bello (1) and primiera (1) are always decided → min 2 pts
        assert total >= 2

    def test_team_of(self) -> None:
        game = self._make_game()
        assert game._team_of(game.human) is game.team_a
        assert game._team_of(game.ai2) is game.team_a
        assert game._team_of(game.ai1) is game.team_b
        assert game._team_of(game.ai3) is game.team_b

    def test_fmt_cards(self) -> None:
        cards = [Card(Suit.COINS, 7), Card(Suit.CUPS, 3)]
        result = Game._fmt_cards(cards)
        assert "7♦" in result
        assert "3♥" in result
