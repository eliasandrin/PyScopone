"""Visual board state decoupled from the game engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from scopone.types import Card


@dataclass
class RenderBoard:
    """Single source of truth for the static cards currently visible in the UI."""

    render_table_cards: List[Card] = field(default_factory=list)
    render_hand_cards: Dict[int, List[Card]] = field(default_factory=dict)
    render_captures: Dict[int, List[Card]] = field(default_factory=lambda: {0: [], 1: []})
    render_sweeps: Dict[int, int] = field(default_factory=lambda: {0: 0, 1: 0})
    render_deck_count: int = 0

    @classmethod
    def from_engine(cls, engine) -> "RenderBoard":
        board = cls()
        board.sync_from_engine(engine)
        return board

    def sync_from_engine(self, engine) -> None:
        self.render_table_cards = list(engine.table)
        self.render_hand_cards = dict((player.id, list(player.hand)) for player in engine.players)
        self.render_captures = {0: [], 1: []}
        self.render_sweeps = {0: 0, 1: 0}

        if engine.num_players == 4:
            for player in engine.players:
                if player.team is None:
                    continue
                self.render_captures.setdefault(player.team, []).extend(player.captured)
                self.render_sweeps[player.team] = self.render_sweeps.get(player.team, 0) + player.sweeps
        else:
            for player in engine.players[:2]:
                self.render_captures[player.id] = list(player.captured)
                self.render_sweeps[player.id] = player.sweeps

        self.render_deck_count = len(engine.deck_remaining)

    def ensure_player(self, player_id: int) -> List[Card]:
        return self.render_hand_cards.setdefault(player_id, [])

    def ensure_team(self, team_id: int) -> List[Card]:
        return self.render_captures.setdefault(team_id, [])

    def ensure_sweeps(self, team_id: int) -> int:
        return self.render_sweeps.setdefault(team_id, 0)
