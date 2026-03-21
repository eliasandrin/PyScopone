"""Core Scopone game engine."""

import random
from typing import Dict, List, Optional, Set, Tuple

from scopone.config.game import (
    INITIAL_HAND_CARDS,
    INITIAL_TABLE_CARDS_BY_MODE,
    MAX_PLAYERS,
    MIN_PLAYERS,
    SEMI,
    TEAM_A_PLAYERS,
)
from scopone.engine.scoring import ScoringEngine
from scopone.models.player import Player
from scopone.types import Card


class GameEngine:
    """Main game engine for Scopone card game."""

    def __init__(self, num_players=4, player_names=None):
        self.num_players = min(max(num_players, MIN_PLAYERS), MAX_PLAYERS)
        self.deck = self._create_deck()  # type: List[Card]
        self.deck_remaining = []  # type: List[Card]

        self.players = []  # type: List[Player]
        self.table = []  # type: List[Card]
        self.seen_cards = set()  # type: Set[Card]
        self.current_player_idx = 0
        self.last_capturer_idx = 0
        self.game_active = False

        self.moves_played = []  # type: List[Tuple[str, Card]]
        self.final_scores = []  # type: List[Dict]
        self.game_history = []  # type: List[Dict]
        self.last_move_result = None  # type: Optional[Dict]

        self._initialize_players(player_names)

    def _create_deck(self):
        return [(value, suit) for suit in SEMI for value in range(1, 11)]

    def _initialize_players(self, player_names):
        self.players = []
        for index in range(self.num_players):
            name = player_names[index] if player_names and index < len(player_names) else f"Giocatore {index + 1}"
            is_human = index == 0
            team = None
            if self.num_players == 4:
                team = 0 if index in TEAM_A_PLAYERS else 1
            self.players.append(Player(name, index, is_ai=not is_human, is_human=is_human, team=team))

    def reset(self) -> None:
        self.deck = self._create_deck()
        self.deck_remaining = []
        self.table = []
        self.seen_cards = set()
        self.current_player_idx = random.randint(0, self.num_players - 1)
        self.last_capturer_idx = 0
        self.game_active = True
        self.moves_played = []
        self.final_scores = []
        self.last_move_result = None

        for player in self.players:
            player.reset()

    def deal_cards(self) -> None:
        random.shuffle(self.deck)

        initial_table_cards = INITIAL_TABLE_CARDS_BY_MODE.get(self.num_players, 4)
        initial_hand_cards = INITIAL_HAND_CARDS.get(self.num_players, 9)

        if self.num_players == 2:
            self.table = []
            for index in range(self.num_players):
                cards = self.deck[index * initial_hand_cards : (index + 1) * initial_hand_cards]
                self.players[index].add_to_hand(cards)
            self.deck_remaining = self.deck[self.num_players * initial_hand_cards :]
            return

        self.table = self.deck[:initial_table_cards]
        self.seen_cards.update(self.table)

        remaining_cards = self.deck[initial_table_cards:]
        cards_per_player = initial_hand_cards
        for index in range(self.num_players):
            start = index * cards_per_player
            end = start + cards_per_player
            self.players[index].add_to_hand(remaining_cards[start:end])

        self.deck_remaining = []

    def restock_cards(self) -> None:
        if self.num_players != 2 or not self.deck_remaining:
            return

        cards_per_player = INITIAL_HAND_CARDS[2]
        required_cards = self.num_players * cards_per_player
        if len(self.deck_remaining) < required_cards:
            return

        for index in range(self.num_players):
            start = index * cards_per_player
            end = start + cards_per_player
            self.players[index].add_to_hand(self.deck_remaining[start:end])

        self.deck_remaining = self.deck_remaining[required_cards:]

    def get_current_player(self) -> Player:
        return self.players[self.current_player_idx]

    def get_human_player(self) -> Player:
        for player in self.players:
            if player.is_human:
                return player
        return self.players[0]

    def play_card(self, player_idx: int, card: Card) -> bool:
        player = self.players[player_idx]
        if not player.has_card(card):
            return False

        captured_combo = []  # type: List[Card]
        sweep_scored = False
        restocked = False

        player.remove_from_hand(card)
        self.seen_cards.add(card)
        self.moves_played.append((player.name, card))

        possible_captures = ScoringEngine.find_captures(card, self.table)
        if possible_captures and possible_captures[0]:
            captured_combo = possible_captures[0]
            for captured_card in captured_combo:
                self.table.remove(captured_card)

            player.capture_cards(captured_combo + [card])

            if not self.table:
                is_last_card_of_game = all(len(current.hand) == 0 for current in self.players)
                if not is_last_card_of_game:
                    player.add_sweep()
                    sweep_scored = True

            self.last_capturer_idx = player_idx
        else:
            self.table.append(card)

        if all(len(current.hand) == 0 for current in self.players):
            if self.num_players == 2 and self.deck_remaining:
                self.restock_cards()
                restocked = True
            else:
                self.end_game()

        self.last_move_result = {
            "player_idx": player_idx,
            "player_name": player.name,
            "played_card": card,
            "captured_cards": captured_combo.copy(),
            "sweep_scored": sweep_scored,
            "restocked": restocked,
            "game_ended": not self.game_active,
            "table_cards_after": self.table.copy(),
        }

        return True

    def next_player(self) -> None:
        self.current_player_idx = (self.current_player_idx - 1) % self.num_players

    def end_game(self) -> None:
        if self.table:
            last_player = self.players[self.last_capturer_idx]
            last_player.capture_cards(self.table)
            self.table = []

        self._calculate_final_scores()
        self.game_active = False

    def _calculate_final_scores(self) -> None:
        self.final_scores = ScoringEngine.calculate_final_scores(self.players)
        winners = ScoringEngine.get_game_winners(self.final_scores)
        self.game_history.append(
            {
                "winners": winners,
                "scores": self.final_scores.copy(),
                "num_players": self.num_players,
                "moves": self.moves_played.copy(),
            }
        )

    def get_game_state(self) -> dict:
        return {
            "current_player": self.get_current_player().name,
            "current_player_idx": self.current_player_idx,
            "table_cards": self.table.copy(),
            "game_active": self.game_active,
            "players": [
                {
                    "name": player.name,
                    "hand_size": len(player.hand),
                    "captured_count": len(player.captured),
                    "sweeps": player.sweeps,
                    "is_human": player.is_human,
                    "is_ai": player.is_ai,
                }
                for player in self.players
            ],
        }

    def get_game_stats(self) -> dict:
        return {
            "total_games": len(self.game_history),
            "current_game_moves": len(self.moves_played),
            "num_players": self.num_players,
            "final_scores": self.final_scores,
        }
