"""Scopone scoring and capture utilities."""

from typing import Dict, List

from scopone.config.game import (
    POINTS_FOR_MOST_CARDS,
    POINTS_FOR_MOST_COINS,
    POINTS_FOR_PRIMIERA,
    POINTS_FOR_SETTEBELLO,
    POINTS_PER_SWEEP,
    VALORI_PRIMIERA,
)
from scopone.types import Card


class ScoringEngine:
    """Manages scoring calculations and capture discovery."""

    @staticmethod
    def calculate_primiera(cards_list):
        suit_scores = {"Denari": 0, "Coppe": 0, "Bastoni": 0, "Spade": 0}

        for value, suit in cards_list:
            primiera_value = VALORI_PRIMIERA.get(value, 0)
            if primiera_value > suit_scores[suit]:
                suit_scores[suit] = primiera_value

        return sum(suit_scores.values())

    @staticmethod
    def find_captures(card, table_cards):
        from itertools import combinations

        card_value = card[0]

        single_captures = [table_card for table_card in table_cards if table_card[0] == card_value]
        if single_captures:
            return [[single_captures[0]]]

        combination_captures = []  # type: List[List[Card]]
        for combo_size in range(2, len(table_cards) + 1):
            for combo in combinations(table_cards, combo_size):
                if sum(table_card[0] for table_card in combo) == card_value:
                    combination_captures.append(list(combo))

        return combination_captures if combination_captures else [[]]

    @staticmethod
    def calculate_player_score(player) -> dict:
        captured_count = len(player.captured)
        coins_count = player.count_coins()
        has_settebello = player.has_settebello()
        primiera_value = ScoringEngine.calculate_primiera(player.captured)

        sweeps_points = player.sweeps * POINTS_PER_SWEEP
        points = {
            "cards": 0,
            "coins": 0,
            "settebello": POINTS_FOR_SETTEBELLO if has_settebello else 0,
            "primiera": 0,
            "sweeps": sweeps_points,
        }

        return {
            "player": player.name,
            "points": points,
            "primiera_value": primiera_value,
            "total": sum(points.values()),
            "captured_cards": captured_count,
            "sweeps": player.sweeps,
            "coins": coins_count,
            "has_settebello": has_settebello,
        }

    @staticmethod
    def calculate_final_scores(players):
        if len(players) == 4 and all(hasattr(player, "team") and player.team is not None for player in players):
            return ScoringEngine._calculate_team_scores(players)
        return ScoringEngine._calculate_individual_scores(players)

    @staticmethod
    def _calculate_individual_scores(players):
        final_scores = [ScoringEngine.calculate_player_score(player) for player in players]

        ScoringEngine._apply_unique_highest_bonus(final_scores, "captured_cards", "cards", POINTS_FOR_MOST_CARDS)
        ScoringEngine._apply_unique_highest_bonus(final_scores, "coins", "coins", POINTS_FOR_MOST_COINS)
        ScoringEngine._apply_unique_highest_bonus(final_scores, "primiera_value", "primiera", POINTS_FOR_PRIMIERA)

        final_scores.sort(key=lambda score: score["total"], reverse=True)
        return final_scores

    @staticmethod
    def _calculate_team_scores(players):
        team_scores = {
            0: {"players": [], "primiera": 0, "cards": 0, "sweeps": 0, "settebello": False},
            1: {"players": [], "primiera": 0, "cards": 0, "sweeps": 0, "settebello": False},
        }

        for player in players:
            team_scores[player.team]["players"].append(player.name)
            team_scores[player.team]["cards"] += len(player.captured)
            team_scores[player.team]["sweeps"] += player.sweeps
            if player.has_settebello():
                team_scores[player.team]["settebello"] = True

        for team in [0, 1]:
            team_cards = []  # type: List[Card]
            for player in players:
                if player.team == team:
                    team_cards.extend(player.captured)
            team_scores[team]["primiera"] = ScoringEngine.calculate_primiera(team_cards)

        final_team_scores = []
        for team_id in [0, 1]:
            team_data = team_scores[team_id]
            coins_in_team = sum(player.count_coins() for player in players if player.team == team_id)
            sweeps_points = team_data["sweeps"] * POINTS_PER_SWEEP
            total = 0
            if team_data["settebello"]:
                total += POINTS_FOR_SETTEBELLO
            total += sweeps_points

            final_team_scores.append(
                {
                    "team": team_id,
                    "player": f"Team {team_id + 1}",
                    "members": team_data["players"],
                    "captured_cards": team_data["cards"],
                    "coins": coins_in_team,
                    "sweeps": team_data["sweeps"],
                    "primiera_value": team_data["primiera"],
                    "has_settebello": team_data["settebello"],
                    "total": total,
                    "points": {
                        "cards": 0,
                        "coins": 0,
                        "settebello": POINTS_FOR_SETTEBELLO if team_data["settebello"] else 0,
                        "primiera": 0,
                        "sweeps": sweeps_points,
                    },
                }
            )

        ScoringEngine._apply_unique_highest_bonus(final_team_scores, "captured_cards", "cards", POINTS_FOR_MOST_CARDS)
        ScoringEngine._apply_unique_highest_bonus(final_team_scores, "coins", "coins", POINTS_FOR_MOST_COINS)
        ScoringEngine._apply_unique_highest_bonus(final_team_scores, "primiera_value", "primiera", POINTS_FOR_PRIMIERA)

        final_team_scores.sort(key=lambda score: score["total"], reverse=True)
        return final_team_scores

    @staticmethod
    def get_game_winners(final_scores):
        if not final_scores:
            return []

        highest_score = final_scores[0]["total"]
        return [score["player"] for score in final_scores if score["total"] == highest_score]

    @staticmethod
    def _apply_unique_highest_bonus(scores, value_key: str, point_key: str, points_award: int) -> None:
        if not scores:
            return

        values = [score.get(value_key, 0) for score in scores]
        highest_value = max(values)
        if values.count(highest_value) != 1:
            return

        winner_index = values.index(highest_value)
        scores[winner_index]["points"][point_key] = points_award
        scores[winner_index]["total"] += points_award
