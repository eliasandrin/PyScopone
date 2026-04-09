"""Core Scopone game engine."""

import random
from typing import Any, Dict, List, Optional, Set, Tuple

from scopone.config.game import (
    CARD_VALUE_MAX,
    CARD_VALUE_MIN,
    DENARI_SUIT,
    INITIAL_HAND_CARDS,
    INITIAL_TABLE_CARDS_BY_MODE,
    MAX_PLAYERS,
    MIN_PLAYERS,
    MODE_QUICK,
    MODE_TOURNAMENT,
    SEMI,
    SETTEBELLO_CARD,
    TEAM_IDS,
    TARGET_SCORE_TOURNAMENT,
    TEAM_A_PLAYERS,
)
from scopone.engine.scoring import ScoringEngine
from scopone.models.player import Player
from scopone.types import Card


class GameEngine:
    """Main game engine for Scopone card game."""

    def __init__(self, num_players: int = 4, player_names: Optional[List[str]] = None, game_mode: str = MODE_QUICK) -> None:
        """Inizializza stato partita, giocatori e punteggi di sessione."""
        self.num_players = min(max(num_players, MIN_PLAYERS), MAX_PLAYERS)
        self.game_mode = game_mode if game_mode in (MODE_QUICK, MODE_TOURNAMENT) else MODE_QUICK
        self.target_score = TARGET_SCORE_TOURNAMENT
        self.deck = self._create_deck()  # type: List[Card]
        self.deck_remaining = []  # type: List[Card]

        self.players = []  # type: List[Player]
        self.table = []  # type: List[Card]
        self.seen_cards = set()  # type: Set[Card]
        self.current_player_idx = 0
        self.dealer_idx = 0
        self.last_capturer_idx = 0
        self.game_active = False

        self.moves_played = []  # type: List[Dict[str, Any]]
        self.final_scores = []  # type: List[Dict]
        self.round_scores = []  # type: List[Dict]
        self.tournament_scores = {}  # type: Dict[int, Dict]
        self.round_history = []  # type: List[Dict]
        self.last_move_result = None  # type: Optional[Dict]
        self.round_number = 0

        self._initialize_players(player_names)
        self.dealer_idx = random.randint(0, self.num_players - 1)
        self.tournament_scores = self._build_empty_session_scores()

    def _create_deck(self) -> List[Card]:
        """Costruisce il mazzo italiano completo da 40 carte."""
        return [(value, suit) for suit in SEMI for value in range(CARD_VALUE_MIN, CARD_VALUE_MAX + 1)]

    def _initialize_players(self, player_names: Optional[List[str]]) -> None:
        """Crea i giocatori e assegna team quando la modalita e a 4 player."""
        self.players = []
        for index in range(self.num_players):
            name = player_names[index] if player_names and index < len(player_names) else f"Giocatore {index + 1}"
            is_human = index == 0
            team = None
            if self.num_players == 4:
                team = 0 if index in TEAM_A_PLAYERS else 1
            self.players.append(Player(name, index, is_ai=not is_human, is_human=is_human, team=team))

    def reset(self, preserve_session: bool = False) -> None:
        """Resetta mano corrente; opzionalmente mantiene storico torneo."""
        self.deck = self._create_deck()
        self.deck_remaining = []
        self.table = []
        self.seen_cards = set()
        if preserve_session:
            self.current_player_idx = self.dealer_idx
        else:
            self.dealer_idx = random.randint(0, self.num_players - 1)
            self.current_player_idx = self.dealer_idx
            self.round_number = 1
            self.tournament_scores = self._build_empty_session_scores()
        self.last_capturer_idx = 0
        self.game_active = True
        self.moves_played = []
        if not preserve_session:
            self.final_scores = []
            self.round_scores = []
        elif self.game_mode == MODE_TOURNAMENT:
            self.final_scores = self._clone_scores(self._get_sorted_tournament_scores())
        self.last_move_result = None

        for player in self.players:
            player.reset()

    def deal_cards(self) -> None:
        """Distribuisce carte iniziali in base al formato 2 o 4 giocatori."""
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
        """Esegue il restock nel formato a 2 giocatori quando il deck residuo lo consente."""
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
        """Restituisce il giocatore di turno corrente."""
        return self.players[self.current_player_idx]

    def get_human_player(self) -> Player:
        """Restituisce il player umano, con fallback al primo indice."""
        for player in self.players:
            if player.is_human:
                return player
        return self.players[0]

    def play_card(
        self,
        player_idx: int,
        card: Card,
        capture_combo: Optional[List[Card]] = None,
        decision_log: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Esegue una giocata completa e aggiorna stato, log e transizioni round."""
        player = self.players[player_idx]
        if not player.has_card(card):
            return False

        captured_combo = []  # type: List[Card]
        sweep_scored = False
        restocked = False
        round_end_summary = {}
        hand_snapshot = list(player.hand)
        table_snapshot = list(self.table)

        player.remove_from_hand(card)
        self.seen_cards.add(card)

        possible_captures = ScoringEngine.find_captures(card, self.table)
        captured_combo = self._choose_capture_combo(card, possible_captures, capture_combo)
        if captured_combo:
            for captured_card in captured_combo:
                self.table.remove(captured_card)

            player.capture_cards(captured_combo + [card])

            if not self.table:
                # Regola Scopa: svuotare il Tavolo vale punto solo se non e
                # l'ultima carta assoluta della mano/smazzata.
                is_last_card_of_game = all(len(current.hand) == 0 for current in self.players)
                if not is_last_card_of_game:
                    player.add_sweep()
                    sweep_scored = True

            self.last_capturer_idx = player_idx
        else:
            self.table.append(card)

        normalized_decision_log = self._normalize_decision_log(
            player=player,
            played_card=card,
            captured_combo=captured_combo,
            decision_log=decision_log,
        )
        self.moves_played.append(
            {
                "player_name": player.name,
                "played_card": card,
                "captured_cards": list(captured_combo),
                "hand": hand_snapshot,
                "table": table_snapshot,
                "decision_log": normalized_decision_log,
            }
        )

        if all(len(current.hand) == 0 for current in self.players):
            if self.num_players == 2 and self.deck_remaining:
                self.restock_cards()
                restocked = True
            else:
                round_end_summary = self.end_game()

        self.last_move_result = {
            "player_idx": player_idx,
            "player_name": player.name,
            "played_card": card,
            "captured_cards": captured_combo.copy(),
            "sweep_scored": sweep_scored,
            "restocked": restocked,
            "game_ended": round_end_summary.get("session_complete", not self.game_active),
            "round_ended": round_end_summary.get("round_complete", False),
            "next_round_started": round_end_summary.get("next_round_started", False),
            "round_scores": round_end_summary.get("round_scores", []),
            "tournament_scores": round_end_summary.get("tournament_scores", []),
            "table_cards_after": round_end_summary.get("table_cards_after", self.table.copy()),
        }

        return True

    def select_capture_combo(self, card: Card, preferred_capture: Optional[List[Card]] = None) -> List[Card]:
        """Resolve capture choice for the played card using optional preferred combo."""
        possible_captures = ScoringEngine.find_captures(card, self.table)
        return self._choose_capture_combo(card, possible_captures, preferred_capture)

    def next_player(self) -> None:
        """Avanza il turno secondo l'ordine di gioco impostato nel progetto."""
        self.current_player_idx = (self.current_player_idx - 1) % self.num_players

    def get_live_tournament_scores(self) -> Dict[int, int]:
        """Returns cumulative tournament totals for each team/player before the current hand."""
        if not self.tournament_scores:
            return {}
        return dict((team_id, score.get("total", 0)) for team_id, score in self.tournament_scores.items())

    def end_game(self) -> dict:
        """Chiude round corrente e, se necessario, anche l'intera sessione."""
        round_summary = {
            "round_complete": True,
            "session_complete": False,
            "next_round_started": False,
            "table_cards_after": [],
            "round_scores": [],
            "tournament_scores": [],
        }

        if self.table:
            last_player = self.players[self.last_capturer_idx]
            last_player.capture_cards(self.table)
            self.table = []

        self.round_scores = ScoringEngine.calculate_final_scores(self.players)
        round_summary["round_scores"] = self._clone_scores(self.round_scores)
        round_summary["table_cards_after"] = self.table.copy()

        if self.game_mode == MODE_QUICK:
            # In partita rapida il punteggio del round coincide con il finale.
            self.final_scores = self._clone_scores(self.round_scores)
            self._record_round_history(self.final_scores, session_complete=True)
            self.game_active = False
            round_summary["session_complete"] = True
            round_summary["tournament_scores"] = self._clone_scores(self.final_scores)
            return round_summary

        self._accumulate_tournament_scores(self.round_scores)
        tournament_score_list = self._get_sorted_tournament_scores()
        self.final_scores = self._clone_scores(tournament_score_list)
        round_summary["tournament_scores"] = self._clone_scores(tournament_score_list)

        if self._has_tournament_winner():
            # In torneo la sessione termina solo quando una squadra/player
            # supera il target cumulativo.
            self._record_round_history(self.final_scores, session_complete=True)
            self.game_active = False
            round_summary["session_complete"] = True
            return round_summary

        self._record_round_history(self.round_scores, session_complete=False)
        # Tournament continues, but the next hand is started by the UI after
        # showing the round-end summary overlay.
        self.game_active = False
        return round_summary

    def start_next_round(self) -> None:
        """Prepara la smazzata successiva mantenendo i punteggi cumulativi."""
        # Rotate dealer and keep cumulative session data while resetting hands/table.
        self.dealer_idx = self._previous_turn_index(self.dealer_idx)
        self.round_number += 1
        self.reset(preserve_session=True)
        self.deal_cards()

    def _build_empty_session_scores(self) -> Dict[int, Dict[str, Any]]:
        """Costruisce lo scheletro punteggi per sessione (team o singoli)."""
        entries: List[Dict[str, Any]] = []
        if self.num_players == 4 and all(player.team is not None for player in self.players):
            entries = [
                self._create_session_entry(
                    entity_id=team_id,
                    player_name="Team {0}".format(team_id + 1),
                    members=[player.name for player in self.players if player.team == team_id],
                    team_id=team_id,
                )
                for team_id in TEAM_IDS
            ]
        else:
            entries = [
                self._create_session_entry(
                    entity_id=player.id,
                    player_name=player.name,
                    members=[player.name],
                    team_id=player.id,
                )
                for player in self.players
            ]

        return dict((entry["team_id"], entry) for entry in entries)

    def _create_session_entry(self, entity_id: int, player_name: str, members: List[str], team_id: int) -> Dict[str, Any]:
        """Crea un record punteggio iniziale con tutti i campi attesi dalla UI."""
        return {
            "entity_id": entity_id,
            "team_id": team_id,
            "team": team_id,
            "player": player_name,
            "members": list(members),
            "captured_cards": 0,
            "coins": 0,
            "sweeps": 0,
            "has_settebello": False,
            "primiera_value": 0,
            "points_breakdown": {"settebello": 0, "sweeps": 0},
            "bonuses": {"cards": 0, "coins": 0, "primiera": 0},
            "points": {"cards": 0, "coins": 0, "settebello": 0, "primiera": 0, "sweeps": 0},
            "total": 0,
        }

    def _accumulate_tournament_scores(self, round_scores: List[Dict[str, Any]]) -> None:
        """Somma i risultati del round nel totale cumulativo di torneo."""
        score_lookup = self.tournament_scores
        for round_score in round_scores:
            team_id = round_score["team_id"]
            cumulative_score = score_lookup.get(team_id)
            if cumulative_score is None:
                cumulative_score = self._create_session_entry(
                    entity_id=round_score["entity_id"],
                    player_name=round_score["player"],
                    members=round_score.get("members", []),
                    team_id=team_id,
                )
                score_lookup[team_id] = cumulative_score

            cumulative_score["captured_cards"] += round_score.get("captured_cards", 0)
            cumulative_score["coins"] += round_score.get("coins", 0)
            cumulative_score["sweeps"] += round_score.get("sweeps", 0)
            cumulative_score["primiera_value"] += round_score.get("primiera_value", 0)
            cumulative_score["has_settebello"] = cumulative_score["has_settebello"] or round_score.get("has_settebello", False)

            for key, value in round_score.get("points_breakdown", {}).items():
                cumulative_score["points_breakdown"][key] = cumulative_score["points_breakdown"].get(key, 0) + value
                cumulative_score["points"][key] = cumulative_score["points"].get(key, 0) + value

            for key, value in round_score.get("bonuses", {}).items():
                cumulative_score["bonuses"][key] = cumulative_score["bonuses"].get(key, 0) + value
                cumulative_score["points"][key] = cumulative_score["points"].get(key, 0) + value

            cumulative_score["total"] += round_score.get("total", 0)

    def _get_sorted_tournament_scores(self) -> List[Dict[str, Any]]:
        """Restituisce classifica torneo ordinata per totale decrescente."""
        return sorted(
            [self._clone_score_entry(score) for score in self.tournament_scores.values()],
            key=lambda score: score.get("total", 0),
            reverse=True,
        )

    def _has_tournament_winner(self) -> bool:
        """Verifica se almeno un totale ha raggiunto il target di torneo."""
        if not self.tournament_scores:
            return False
        return max(score.get("total", 0) for score in self.tournament_scores.values()) >= self.target_score

    def _record_round_history(self, scores: List[Dict[str, Any]], session_complete: bool) -> None:
        """Persistenza storica del round per risultati, replay e debug decisionale."""
        winners = ScoringEngine.get_game_winners(scores)
        self.round_history.append(
            {
                "winners": winners,
                "scores": self._clone_scores(scores),
                "round_scores": self._clone_scores(self.round_scores),
                "num_players": self.num_players,
                "turns": self._clone_moves(self.moves_played),
                "moves": self._clone_moves(self.moves_played),
                "game_mode": self.game_mode,
                "dealer_idx": self.dealer_idx,
                "round_number": self.round_number,
                "session_complete": session_complete,
            }
        )

    def _previous_turn_index(self, index: int) -> int:
        """Calcola l'indice precedente nel giro turni circolare."""
        return (index - 1) % self.num_players

    def _choose_capture_combo(
        self,
        played_card: Card,
        possible_captures: List[List[Card]],
        preferred_capture: Optional[List[Card]] = None,
    ) -> List[Card]:
        """Seleziona la presa valida rispettando vincoli min-card e priorita."""
        legal_captures = ScoringEngine.filter_min_card_captures(possible_captures)
        if not legal_captures:
            return []

        if preferred_capture:
            preferred_key = self._normalize_capture_combo(preferred_capture)
            for combo in legal_captures:
                if self._normalize_capture_combo(combo) == preferred_key:
                    return combo

        return max(legal_captures, key=self._capture_priority_key)

    def _capture_priority_key(self, combo: List[Card]) -> Tuple[int, int, int, int, Tuple[Card, ...]]:
        """Chiave ordinamento prese: 7b, Denari, numero carte, Primiera, tie-break."""
        denari_count = sum(1 for card in combo if card[1] == DENARI_SUIT)
        contains_settebello = 1 if SETTEBELLO_CARD in combo else 0
        primiera_value = ScoringEngine.calculate_primiera(combo)
        # Ordine lessicografico voluto dal dominio: prima obiettivi ad alto
        # valore (Settebello/Denari), poi volume presa e infine tie-break stabile.
        return (
            contains_settebello,
            denari_count,
            len(combo),
            primiera_value,
            self._normalize_capture_combo(combo),
        )

    def _normalize_capture_combo(self, combo: List[Card]) -> Tuple[Card, ...]:
        """Normalizza una combo per confronti deterministici indipendenti dall'ordine."""
        return tuple(sorted(combo))

    def _normalize_decision_log(
        self,
        player: Player,
        played_card: Card,
        captured_combo: List[Card],
        decision_log: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Uniforma il decision log per garantire schema stabile a UI e test."""
        base_log = {
            "strategy": "human" if player.is_human else "normal",
            "candidates_evaluated": 0,
            "chosen_card": played_card,
            "chosen_combo": list(captured_combo),
            "reasoning": "mossa eseguita",
        }
        if not decision_log:
            return base_log

        normalized = dict(base_log)
        normalized.update(decision_log)
        normalized["chosen_card"] = normalized.get("chosen_card") or played_card
        normalized["chosen_combo"] = list(captured_combo)
        normalized["candidates_evaluated"] = max(0, int(normalized.get("candidates_evaluated", 0)))
        normalized["reasoning"] = normalized.get("reasoning") or base_log["reasoning"]
        return normalized

    def _clone_score_entry(self, score: Dict[str, Any]) -> Dict[str, Any]:
        """Copia difensiva di una score entry con sotto-strutture annidate."""
        cloned = dict(score)
        if "members" in cloned:
            cloned["members"] = list(cloned["members"])
        if "points_breakdown" in cloned:
            cloned["points_breakdown"] = dict(cloned["points_breakdown"])
        if "bonuses" in cloned:
            cloned["bonuses"] = dict(cloned["bonuses"])
        if "points" in cloned:
            cloned["points"] = dict(cloned["points"])
        return cloned

    def _clone_scores(self, scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Copia profonda leggera dell'elenco punteggi."""
        return [self._clone_score_entry(score) for score in scores]

    def _clone_moves(self, moves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Copia i log mossa per evitare mutazioni retroattive nello storico."""
        cloned_moves = []
        for move in moves:
            cloned_moves.append(
                {
                    "player_name": move.get("player_name"),
                    "played_card": move.get("played_card"),
                    "captured_cards": list(move.get("captured_cards", [])),
                    "hand": list(move.get("hand", [])),
                    "table": list(move.get("table", [])),
                    "decision_log": dict(move.get("decision_log", {})),
                }
            )
        return cloned_moves

    def get_game_state(self) -> dict:
        """Snapshot serializzabile dello stato runtime per UI/debug."""
        return {
            "game_mode": self.game_mode,
            "dealer_idx": self.dealer_idx,
            "round_number": self.round_number,
            "current_player": self.get_current_player().name,
            "current_player_idx": self.current_player_idx,
            "table_cards": self.table.copy(),
            "game_active": self.game_active,
            "tournament_scores": self._clone_scores(self._get_sorted_tournament_scores()),
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
        """Raccoglie statistiche aggregate di partita/sessione per report UI."""
        return {
            "total_games": len(self.round_history),
            "current_game_moves": len(self.moves_played),
            "num_players": self.num_players,
            "game_mode": self.game_mode,
            "round_number": self.round_number,
            "final_scores": self._clone_scores(self.final_scores),
            "round_scores": self._clone_scores(self.round_scores),
            "tournament_scores": self._clone_scores(self._get_sorted_tournament_scores()),
        }
