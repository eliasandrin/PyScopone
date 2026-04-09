"""AI strategies for Scopone."""

from collections import OrderedDict
import random
from typing import Any, Dict, List, Optional, Tuple

from scopone.config.game import FULL_DECK, VALORI_PRIMIERA
from scopone.engine.scoring import ScoringEngine
from scopone.types import Card


class AIStrategy:
    """Base class for AI strategies in Scopone."""

    STRATEGY_LOG_NAME = "base"

    def __init__(self, difficulty: str = "normale") -> None:
        self.difficulty = difficulty
        self.last_decision_reason = ""
        self.last_decision_log = {
            "strategy": self.STRATEGY_LOG_NAME,
            "candidates_evaluated": 0,
            "chosen_card": None,
            "chosen_combo": [],
            "reasoning": "",
        }

    def get_last_decision_reason(self) -> str:
        return self.last_decision_reason or "Nessuna motivazione disponibile"

    def get_last_decision_log(self) -> Dict[str, Any]:
        return dict(self.last_decision_log)

    def _set_reason(self, reason: str) -> None:
        self.last_decision_reason = reason

    def _set_decision(
        self,
        reason: str,
        chosen_card: Optional[Card],
        chosen_combo: Optional[List[Card]],
        candidates_evaluated: int,
        **extras: Any,
    ) -> None:
        self.last_decision_reason = reason
        decision_log = {
            "strategy": self.STRATEGY_LOG_NAME,
            "candidates_evaluated": max(0, int(candidates_evaluated)),
            "chosen_card": chosen_card,
            "chosen_combo": list(chosen_combo or []),
            "reasoning": reason,
        }
        for key, value in extras.items():
            if value is not None:
                decision_log[key] = value
        self.last_decision_log = decision_log

    def choose_card(self, hand, table_cards, **kwargs):
        raise NotImplementedError

    def choose_move(self, hand, table_cards, **kwargs) -> Tuple[Optional[Card], List[Card]]:
        chosen_card = self.choose_card(hand, table_cards, **kwargs)
        if chosen_card is None:
            self._set_decision("mano vuota", None, [], 0)
            return None, []
        captures = ScoringEngine.filter_min_card_captures(ScoringEngine.find_captures(chosen_card, table_cards))
        chosen_combo = list(captures[0]) if captures else []
        self._set_decision("scelta base strategia", chosen_card, chosen_combo, len(hand))
        return chosen_card, chosen_combo


class EasyAI(AIStrategy):
    STRATEGY_LOG_NAME = "easy"

    def choose_move(self, hand, table_cards, **kwargs) -> Tuple[Optional[Card], List[Card]]:
        del kwargs

        if not hand:
            self._set_decision("mano vuota", None, [], 0)
            return None, []

        capture_candidates = []
        for card in hand:
            possible_captures = ScoringEngine.filter_min_card_captures(ScoringEngine.find_captures(card, table_cards))
            if possible_captures:
                capture_candidates.append((card, possible_captures))

        if capture_candidates:
            chosen_card, capture_options = random.choice(capture_candidates)
            chosen_combo = list(random.choice(capture_options))
            self._set_decision(
                "presa casuale disponibile (livello divertimento)",
                chosen_card,
                chosen_combo,
                len(capture_candidates),
            )
            return chosen_card, chosen_combo

        chosen = random.choice(hand)
        self._set_decision(
            "nessuna presa disponibile: scarto casuale (livello divertimento)",
            chosen,
            [],
            len(hand),
        )
        return chosen, []

    def choose_card(self, hand, table_cards, **kwargs):
        chosen_card, _ = self.choose_move(hand, table_cards, **kwargs)
        return chosen_card


class NormalAI(AIStrategy):
    STRATEGY_LOG_NAME = "normal"

    def choose_move(self, hand, table_cards, **kwargs) -> Tuple[Optional[Card], List[Card]]:
        del kwargs

        if not hand:
            self._set_decision("mano vuota", None, [], 0)
            return None, []

        best_card = None
        best_combo = []
        best_move_key = None
        capture_candidates = 0
        for card in hand:
            possible_captures = ScoringEngine.filter_min_card_captures(ScoringEngine.find_captures(card, table_cards))
            for combo in possible_captures:
                capture_candidates += 1
                remaining_table = list(table_cards)
                for captured_card in combo:
                    remaining_table.remove(captured_card)
                move_key = (
                    1 if not remaining_table else 0,
                    1 if (7, "Denari") in combo else 0,
                    len(combo),
                    sum(1 for captured in combo if captured[1] == "Denari"),
                    ScoringEngine.calculate_primiera(combo),
                )
                if best_move_key is None or move_key > best_move_key:
                    best_move_key = move_key
                    best_card = card
                    best_combo = list(combo)

        if best_card is not None:
            self._set_decision(
                "cattura: scelgo la presa con combinazione piu vantaggiosa",
                best_card,
                best_combo,
                capture_candidates,
            )
            return best_card, best_combo

        # Livello normale: mantiene valore immediato preservando i semi/carte piu pesanti.
        chosen = min(
            hand,
            key=lambda item: (
                1 if item == (7, "Denari") else 0,
                1 if item[1] == "Denari" else 0,
                1 if item[0] in (7, 6, 1) else 0,
                item[0],
            ),
        )
        self._set_decision(
            "nessuna presa: scarto carta di minor valore strategico",
            chosen,
            [],
            len(hand),
        )
        return chosen, []

    def choose_card(self, hand, table_cards, **kwargs):
        chosen_card, _ = self.choose_move(hand, table_cards, **kwargs)
        return chosen_card


class ExpertAI(AIStrategy):
    STRATEGY_LOG_NAME = "expert"
    PRIMIERA_VALUES = VALORI_PRIMIERA

    def __init__(self, difficulty: str = "esperto", enable_scopa_cache: bool = True, scopa_cache_size: int = 256) -> None:
        super().__init__(difficulty)
        self.enable_scopa_cache = enable_scopa_cache
        self.scopa_cache_size = max(32, scopa_cache_size)
        self._scopa_cache = OrderedDict()

    def choose_move(
        self,
        hand,
        table_cards,
        player_scores=None,
        seen_cards=None,
        deck_size=None,
    ) -> Tuple[Optional[Card], List[Card]]:
        del deck_size

        if not hand:
            self._set_reason("mano vuota")
            return None, []

        seen = set(seen_cards or set())
        if not table_cards:
            best_move = self._choose_safe_card_empty_table(hand, seen)
        else:
            best_move = self._choose_strategic_card_with_table(hand, table_cards, seen, player_scores)

        self._set_decision(
            best_move["reason"],
            best_move["card"],
            list(best_move.get("capture_combo", [])),
            best_move.get("candidates_evaluated", 0),
            scopa_probability=best_move.get("scopa_prob"),
            primiera_gain=best_move.get("primiera_gain"),
            denari_count=best_move.get("denari_gain"),
        )
        return best_move["card"], list(best_move.get("capture_combo", []))

    def choose_card(
        self,
        hand,
        table_cards,
        player_scores=None,
        seen_cards=None,
        deck_size=None,
    ):
        chosen_card, _ = self.choose_move(hand, table_cards, player_scores=player_scores, seen_cards=seen_cards, deck_size=deck_size)
        return chosen_card

    def _choose_safe_card_empty_table(self, hand, seen_cards):
        candidates = []
        for card in hand:
            value, suit = card
            scopa_prob = self._opponent_scopa_probability([card], seen_cards, hand, card)
            candidates.append(
                {
                    "card": card,
                    "scopa_prob": scopa_prob,
                    "is_settebello": value == 7 and suit == "Denari",
                    "is_high_primiera": value in (7, 6),
                    "is_denari": suit == "Denari",
                    "primiera": self.PRIMIERA_VALUES.get(value, 0),
                }
            )

        best = min(
            candidates,
            key=lambda move: (
                move["scopa_prob"],
                1 if move["is_settebello"] else 0,
                1 if move["is_high_primiera"] else 0,
                1 if move["is_denari"] else 0,
                move["primiera"],
                move["card"][0],
            ),
        )
        best["reason"] = (
            "tavolo vuoto: minimizzo rischio scopa avversaria "
            f"({best['scopa_prob']:.1%}), evitando carte di valore"
        )
        best["capture_combo"] = []
        best["primiera_gain"] = 0
        best["denari_gain"] = 0
        best["candidates_evaluated"] = len(candidates)
        return best

    def _calculate_real_primiera_gain(self, capture_combo: List[Card], player_scores: dict) -> int:
        if not player_scores:
            return sum(self.PRIMIERA_VALUES.get(card[0], 0) for card in capture_combo)

        current_captured = player_scores.get("team_captured", [])

        def get_best_per_suit(cards: List[Card]) -> Dict[str, int]:
            best = {"Denari": 0, "Coppe": 0, "Spade": 0, "Bastoni": 0}
            for value, suit in cards:
                points = self.PRIMIERA_VALUES.get(value, 0)
                if points > best[suit]:
                    best[suit] = points
            return best

        current_best = get_best_per_suit(current_captured)
        current_total = sum(current_best.values())

        hypothetical_captured = current_captured + capture_combo
        hypothetical_best = get_best_per_suit(hypothetical_captured)
        hypothetical_total = sum(hypothetical_best.values())

        return hypothetical_total - current_total

    def _choose_strategic_card_with_table(self, hand, table_cards, seen_cards, player_scores=None):
        moves = []
        for card in hand:
            legal_captures = ScoringEngine.filter_min_card_captures(ScoringEngine.find_captures(card, table_cards))
            if legal_captures:
                for capture_combo in legal_captures:
                    remaining_table = list(table_cards)
                    for captured_card in capture_combo:
                        remaining_table.remove(captured_card)

                    moves.append(
                        {
                            "card": card,
                            "capture_combo": list(capture_combo),
                            "is_capture": True,
                            "makes_scopa": not remaining_table,
                            "captures_settebello": (7, "Denari") in capture_combo,
                            "primiera_gain": self._calculate_real_primiera_gain(capture_combo, player_scores),
                            "denari_gain": sum(1 for captured in capture_combo if captured[1] == "Denari"),
                            "capture_count": len(capture_combo),
                            "scopa_prob": self._opponent_scopa_probability(remaining_table, seen_cards, hand, card),
                        }
                    )
                continue

            remaining_table = table_cards + [card]
            moves.append(
                {
                    "card": card,
                    "capture_combo": [],
                    "is_capture": False,
                    "makes_scopa": False,
                    "captures_settebello": False,
                    "primiera_gain": 0,
                    "denari_gain": 0,
                    "capture_count": 0,
                    "scopa_prob": self._opponent_scopa_probability(remaining_table, seen_cards, hand, card),
                }
            )

        candidates_evaluated = len(moves)

        scopa_now = [move for move in moves if move["makes_scopa"]]
        if scopa_now:
            best = max(
                scopa_now,
                key=lambda move: (
                    move["captures_settebello"],
                    move["primiera_gain"],
                    move["denari_gain"],
                    move["capture_count"],
                ),
            )
            best["reason"] = "faccio scopa immediata (priorita massima)"
            best["candidates_evaluated"] = candidates_evaluated
            return best

        safe_captures = [move for move in moves if move["is_capture"] and move["scopa_prob"] <= 1e-9]
        if safe_captures:
            best = max(
                safe_captures,
                key=lambda move: (
                    1 if move["captures_settebello"] else 0,
                    move["primiera_gain"],
                    move["denari_gain"],
                    move["capture_count"],
                    -move["card"][0],
                ),
            )
            if best["captures_settebello"]:
                best["reason"] = "presa sicura (0% scopa concessa) e catturo il 7 di Denari"
            elif best["primiera_gain"] > 0:
                best["reason"] = "presa sicura (0% scopa concessa) e massimizzo primiera"
            elif best["denari_gain"] > 0:
                best["reason"] = "presa sicura (0% scopa concessa) con priorita Denari"
            elif best["capture_count"] > 1:
                best["reason"] = "presa sicura (0% scopa concessa) e prendo piu carte"
            else:
                best["reason"] = "presa singola sicura (0% scopa concessa)"
            best["candidates_evaluated"] = candidates_evaluated
            return best

        discard_moves = [move for move in moves if not move["is_capture"]]
        if discard_moves:
            best = min(
                discard_moves,
                key=lambda move: (
                    move["scopa_prob"],
                    1 if (move["card"][0] == 7 and move["card"][1] == "Denari") else 0,
                    1 if move["card"][0] in (7, 6) else 0,
                    1 if move["card"][1] == "Denari" else 0,
                    move["card"][0],
                ),
            )
            best["reason"] = (
                "nessuna presa sicura: scarto la carta con rischio scopa minimo "
                f"({best['scopa_prob']:.1%})"
            )
            best["candidates_evaluated"] = candidates_evaluated
            return best

        best = min(
            moves,
            key=lambda move: (
                move["scopa_prob"],
                -move["captures_settebello"],
                -move["primiera_gain"],
                -move["denari_gain"],
                -move["capture_count"],
            ),
        )
        best["reason"] = (
            "solo prese rischiose disponibili: scelgo quella con rischio scopa minore "
            f"({best['scopa_prob']:.1%})"
        )
        best["candidates_evaluated"] = candidates_evaluated
        return best

    def _opponent_scopa_probability(
        self,
        table_after_move,
        seen_cards,
        hand_cards,
        played_card,
    ) -> float:
        if not table_after_move:
            return 0.0

        cache_key = self._build_scopa_cache_key(table_after_move, seen_cards, hand_cards, played_card)
        if self.enable_scopa_cache and cache_key in self._scopa_cache:
            self._scopa_cache.move_to_end(cache_key)
            return self._scopa_cache[cache_key]

        unavailable = set(seen_cards)
        unavailable.update(hand_cards)
        unavailable.update(table_after_move)
        unavailable.add(played_card)

        opponent_candidates = [card for card in FULL_DECK if card not in unavailable]
        if not opponent_candidates:
            return 0.0

        scopa_cards = 0
        for opponent_card in opponent_candidates:
            captures = ScoringEngine.find_captures(opponent_card, table_after_move)
            if captures and captures[0] and len(captures[0]) == len(table_after_move):
                scopa_cards += 1

        probability = scopa_cards / len(opponent_candidates)
        if self.enable_scopa_cache:
            self._scopa_cache[cache_key] = probability
            if len(self._scopa_cache) > self.scopa_cache_size:
                self._scopa_cache.popitem(last=False)

        return probability

    def _build_scopa_cache_key(self, table_after_move, seen_cards, hand_cards, played_card) -> Tuple[Any, ...]:
        return (
            tuple(sorted(table_after_move)),
            tuple(sorted(hand_cards)),
            tuple(sorted(seen_cards)),
            played_card,
        )

def get_ai_strategy(difficulty: str = "normale") -> AIStrategy:
    strategies = {
        "divertimento": EasyAI,
        "normale": NormalAI,
        "esperto": ExpertAI,
    }
    selected_difficulty = difficulty if difficulty in strategies else "normale"
    return strategies[selected_difficulty](selected_difficulty)
