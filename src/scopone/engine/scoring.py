"""Scopone scoring and capture utilities."""

from itertools import combinations
from typing import List, Protocol, TypedDict

from scopone.config.game import (
    DENARI_SUIT,
    POINTS_FOR_MOST_CARDS,
    POINTS_FOR_MOST_COINS,
    POINTS_FOR_PRIMIERA,
    POINTS_FOR_SETTEBELLO,
    POINTS_PER_SWEEP,
    SETTEBELLO_CARD,
    SEMI,
    VALORI_PRIMIERA,
)
from scopone.types import Card


PRIMIERA_SUITS = tuple(SEMI)


class ScorePoints(TypedDict):
    cards: int
    coins: int
    settebello: int
    primiera: int
    sweeps: int


class PointsBreakdown(TypedDict):
    settebello: int
    sweeps: int


class Bonuses(TypedDict):
    cards: int
    coins: int
    primiera: int


class RawStats(TypedDict):
    entity_id: int
    team_id: int
    player: str
    members: List[str]
    captured_cards: int
    coins: int
    sweeps: int
    has_settebello: bool
    primiera_value: int
    captured_cards_list: List[Card]
    team: int


class ScoreEntry(TypedDict):
    entity_id: int
    team_id: int
    player: str
    members: List[str]
    captured_cards: int
    coins: int
    sweeps: int
    has_settebello: bool
    primiera_value: int
    points_breakdown: PointsBreakdown
    bonuses: Bonuses
    total_score: int
    team: int
    points: ScorePoints
    total: int


class SupportsScoringPlayer(Protocol):
    id: int
    name: str
    captured: List[Card]
    sweeps: int
    team: int | None


class ScoringEngine:
    """Manages scoring calculations and capture discovery."""

    @staticmethod
    def calculate_primiera(cards_list: List[Card]) -> int:
        """Calculate the primiera value for a captured card collection.

        Args:
            cards_list: Captured cards to evaluate.

        Returns:
            The total primiera value obtained from the best card of each suit.
        """
        best_by_suit = dict((suit, 0) for suit in PRIMIERA_SUITS)
        primiera_values = VALORI_PRIMIERA

        for value, suit in cards_list:
            primiera_value = primiera_values.get(value, 0)
            if primiera_value > best_by_suit[suit]:
                best_by_suit[suit] = primiera_value

        return sum(best_by_suit.values())

    @staticmethod
    def find_captures(card: Card, table_cards: List[Card]) -> List[List[Card]]:
        """Return all legal captures for a played card.

        Args:
            card: Card being played.
            table_cards: Cards currently on the table.

        Returns:
            A list of capture combinations. If no capture is available, returns
            a single empty combination.
        """
        card_value = card[0]

        legal_captures = []  # type: List[List[Card]]
        for combo_size in range(1, len(table_cards) + 1):
            for combo in combinations(table_cards, combo_size):
                if sum(table_card[0] for table_card in combo) == card_value:
                    legal_captures.append(list(combo))

        return legal_captures if legal_captures else [[]]

    @staticmethod
    def calculate_player_score(player: SupportsScoringPlayer) -> ScoreEntry:
        """Build the standardized score payload for a single player.

        Args:
            player: Player whose captured cards and sweeps must be evaluated.

        Returns:
            A standardized score dictionary with legacy compatibility aliases.
        """
        raw_stats = ScoringEngine._aggregate_player_stats(player)
        return ScoringEngine._build_score_entry(raw_stats)

    @staticmethod
    def calculate_final_scores(players: List[SupportsScoringPlayer]) -> List[ScoreEntry]:
        """Calculate final scores for either solo or team matches.

        Args:
            players: Players taking part in the current match.

        Returns:
            A list of score payloads sorted by total score descending.
        """
        if len(players) == 4 and all(hasattr(player, "team") and player.team is not None for player in players):
            return ScoringEngine._calculate_team_scores(players)
        return ScoringEngine._calculate_individual_scores(players)

    @staticmethod
    def _aggregate_player_stats(player: SupportsScoringPlayer) -> RawStats:
        """Aggregate raw captured statistics for a player.

        Args:
            player: Player to summarize.

        Returns:
            A raw stats dictionary independent from bonus assignment.
        """
        captured_cards = list(player.captured)
        team_id = player.team if getattr(player, "team", None) is not None else player.id
        return {
            "entity_id": player.id,
            "team_id": team_id,
            "player": player.name,
            "members": [player.name],
            "captured_cards": len(captured_cards),
            "coins": sum(1 for card in captured_cards if card[1] == DENARI_SUIT),
            "sweeps": player.sweeps,
            "has_settebello": SETTEBELLO_CARD in captured_cards,
            "primiera_value": ScoringEngine.calculate_primiera(captured_cards),
            "captured_cards_list": captured_cards,
            "team": team_id,
        }

    @staticmethod
    def _calculate_individual_scores(players: List[SupportsScoringPlayer]) -> List[ScoreEntry]:
        """Calculate scores for solo entities.

        Args:
            players: Players to evaluate independently.

        Returns:
            Standardized score entries sorted by total score.
        """
        final_scores = [ScoringEngine._build_score_entry(ScoringEngine._aggregate_player_stats(player)) for player in players]
        ScoringEngine._apply_standard_bonuses(final_scores)
        return ScoringEngine._sort_scores(final_scores)

    @staticmethod
    def _calculate_team_scores(players: List[SupportsScoringPlayer]) -> List[ScoreEntry]:
        """Calculate scores for team entities by merging player raw stats.

        Args:
            players: Players participating in a team match.

        Returns:
            Standardized team score entries sorted by total score.
        """
        player_stats = [ScoringEngine._aggregate_player_stats(player) for player in players]
        team_stats: dict[int, RawStats] = {}

        for raw_stats in player_stats:
            team_id = raw_stats["team_id"]
            existing = team_stats.get(team_id)
            if existing is None:
                team_stats[team_id] = {
                    "entity_id": team_id,
                    "team_id": team_id,
                    "team": team_id,
                    "player": "Team {0}".format(team_id + 1),
                    "members": list(raw_stats["members"]),
                    "captured_cards": raw_stats["captured_cards"],
                    "coins": raw_stats["coins"],
                    "sweeps": raw_stats["sweeps"],
                    "has_settebello": raw_stats["has_settebello"],
                    "captured_cards_list": list(raw_stats["captured_cards_list"]),
                }
                continue

            existing["members"].extend(raw_stats["members"])
            existing["captured_cards"] += raw_stats["captured_cards"]
            existing["coins"] += raw_stats["coins"]
            existing["sweeps"] += raw_stats["sweeps"]
            existing["has_settebello"] = existing["has_settebello"] or raw_stats["has_settebello"]
            existing["captured_cards_list"].extend(raw_stats["captured_cards_list"])

        final_scores = []
        for team_id in sorted(team_stats.keys()):
            raw_stats = team_stats[team_id]
            raw_stats["primiera_value"] = ScoringEngine.calculate_primiera(raw_stats["captured_cards_list"])
            final_scores.append(ScoringEngine._build_score_entry(raw_stats))

        ScoringEngine._apply_standard_bonuses(final_scores)
        return ScoringEngine._sort_scores(final_scores)

    @staticmethod
    def get_game_winners(final_scores: List[ScoreEntry]) -> List[str]:
        """Return the names of the winners for the supplied scoreboard.

        Args:
            final_scores: Final score entries sorted descending.

        Returns:
            The list of winners. Multiple entries indicate a tie.
        """
        if not final_scores:
            return []

        highest_score = final_scores[0]["total_score"]
        return [score["player"] for score in final_scores if score["total_score"] == highest_score]

    @staticmethod
    def _build_score_entry(raw_stats: RawStats) -> ScoreEntry:
        """Convert raw stats into the standardized score payload.

        Args:
            raw_stats: Raw aggregated statistics for one scoring entity.

        Returns:
            A standardized score dictionary plus legacy aliases.
        """
        points_breakdown: PointsBreakdown = {
            "settebello": POINTS_FOR_SETTEBELLO if raw_stats["has_settebello"] else 0,
            "sweeps": raw_stats["sweeps"] * POINTS_PER_SWEEP,
        }
        bonuses: Bonuses = {
            "cards": 0,
            "coins": 0,
            "primiera": 0,
        }
        legacy_points: ScorePoints = {
            "cards": 0,
            "coins": 0,
            "settebello": points_breakdown["settebello"],
            "primiera": 0,
            "sweeps": points_breakdown["sweeps"],
        }
        total_score = sum(points_breakdown.values()) + sum(bonuses.values())

        return {
            "entity_id": raw_stats["entity_id"],
            "team_id": raw_stats["team_id"],
            "player": raw_stats["player"],
            "members": list(raw_stats["members"]),
            "captured_cards": raw_stats["captured_cards"],
            "coins": raw_stats["coins"],
            "sweeps": raw_stats["sweeps"],
            "has_settebello": raw_stats["has_settebello"],
            "primiera_value": raw_stats["primiera_value"],
            "points_breakdown": points_breakdown,
            "bonuses": bonuses,
            "total_score": total_score,
            "team": raw_stats["team"],
            "points": legacy_points,
            "total": total_score,
        }

    @staticmethod
    def _apply_standard_bonuses(scores: List[ScoreEntry]) -> None:
        """Apply the unique-highest bonuses defined by the base ruleset.

        Args:
            scores: Score entries to mutate in-place.
        """
        ScoringEngine._apply_unique_highest_bonus(scores, "captured_cards", "cards", POINTS_FOR_MOST_CARDS)
        ScoringEngine._apply_unique_highest_bonus(scores, "coins", "coins", POINTS_FOR_MOST_COINS)
        ScoringEngine._apply_unique_highest_bonus(scores, "primiera_value", "primiera", POINTS_FOR_PRIMIERA)

    @staticmethod
    def _apply_unique_highest_bonus(scores: List[ScoreEntry], value_key: str, bonus_key: str, points_award: int) -> None:
        """Award a bonus if exactly one entity owns the highest raw value.

        Args:
            scores: Score entries to update.
            value_key: Raw metric used for comparison.
            bonus_key: Bonus bucket to mutate when awarded.
            points_award: Points to assign to the unique winner.
        """
        if not scores:
            return

        values = [score.get(value_key, 0) for score in scores]
        highest_value = max(values)
        if values.count(highest_value) != 1:
            return

        winner_index = values.index(highest_value)
        winner = scores[winner_index]
        winner["bonuses"][bonus_key] = points_award
        winner["points"][bonus_key] = points_award
        winner["total_score"] += points_award
        winner["total"] = winner["total_score"]

    @staticmethod
    def _sort_scores(scores: List[ScoreEntry]) -> List[ScoreEntry]:
        """Sort scores descending by total score.

        Args:
            scores: Score entries to sort.

        Returns:
            The sorted score list.
        """
        scores.sort(key=lambda score: score["total_score"], reverse=True)
        return scores
