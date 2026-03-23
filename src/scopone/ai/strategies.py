"""AI strategies for Scopone."""

import random
from typing import Dict, List

from scopone.config.game import FULL_DECK
from scopone.engine.scoring import ScoringEngine
from scopone.types import Card


class AIStrategy:
    """Base class for AI strategies in Scopone."""

    def __init__(self, difficulty: str = "normale") -> None:
        self.difficulty = difficulty
        self.last_decision_reason = ""

    def get_last_decision_reason(self) -> str:
        return self.last_decision_reason or "Nessuna motivazione disponibile"

    def _set_reason(self, reason: str) -> None:
        self.last_decision_reason = reason

    def choose_card(self, hand, table_cards, **kwargs):
        raise NotImplementedError


class EasyAI(AIStrategy):
    def choose_card(self, hand, table_cards, **kwargs):
        del kwargs

        if not hand:
            self._set_reason("mano vuota")
            return None

        capture_candidates = []
        for card in hand:
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            if possible_captures and possible_captures[0]:
                capture_candidates.append(card)

        if capture_candidates:
            chosen = random.choice(capture_candidates)
            self._set_reason("presa casuale disponibile (livello divertimento)")
            return chosen

        chosen = random.choice(hand)
        self._set_reason("nessuna presa disponibile: scarto casuale (livello divertimento)")
        return chosen


class NormalAI(AIStrategy):
    def choose_card(self, hand, table_cards, **kwargs):
        del kwargs

        if not hand:
            self._set_reason("mano vuota")
            return None

        best_card = None
        best_move_key = None
        for card in hand:
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            for combo in possible_captures:
                if not combo:
                    continue
                move_key = (
                    len(combo),
                    sum(1 for captured in combo if captured[1] == "Denari"),
                )
                if best_move_key is None or move_key > best_move_key:
                    best_move_key = move_key
                    best_card = card

        if best_card is not None:
            self._set_reason("scelgo la presa con combinazione piu vantaggiosa")
            return best_card

        chosen = max(hand, key=lambda item: item[0])
        self._set_reason("nessuna presa: scarico carta alta")
        return chosen


class ExpertAI(AIStrategy):
    PRIMIERA_VALUES = {
        7: 21,
        6: 18,
        1: 16,
        5: 15,
        4: 14,
        3: 13,
        2: 12,
        8: 10,
        9: 10,
        10: 10,
    }

    def choose_card(
        self,
        hand,
        table_cards,
        player_scores=None,
        seen_cards=None,
        deck_size=None,
    ):
        del deck_size

        if not hand:
            self._set_reason("mano vuota")
            return None

        seen = set(seen_cards or set())
        if not table_cards:
            best_move = self._choose_safe_card_empty_table(hand, seen)
        else:
            best_move = self._choose_strategic_card_with_table(hand, table_cards, seen, player_scores)

        self._set_reason(best_move["reason"])
        return best_move["card"]

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
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            capture_combo = possible_captures[0] if (possible_captures and possible_captures[0]) else []
            remaining_table = [table_card for table_card in table_cards if table_card not in capture_combo]
            if not capture_combo:
                remaining_table = table_cards + [card]

            moves.append(
                {
                    "card": card,
                    "capture_combo": capture_combo,
                    "is_capture": bool(capture_combo),
                    "makes_scopa": bool(capture_combo) and not remaining_table,
                    "captures_settebello": (7, "Denari") in capture_combo,
                    "primiera_gain": self._calculate_real_primiera_gain(capture_combo, player_scores),
                    "denari_gain": sum(1 for captured in capture_combo if captured[1] == "Denari"),
                    "capture_count": len(capture_combo),
                    "scopa_prob": self._opponent_scopa_probability(remaining_table, seen_cards, hand, card),
                }
            )

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

        return scopa_cards / len(opponent_candidates)


def get_ai_strategy(difficulty: str = "normale") -> AIStrategy:
    strategies = {
        "divertimento": EasyAI,
        "normale": NormalAI,
        "esperto": ExpertAI,
    }
    selected_difficulty = difficulty if difficulty in strategies else "normale"
    return strategies[selected_difficulty](selected_difficulty)
