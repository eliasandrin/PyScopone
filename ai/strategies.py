# ============================================================================
# SCOPONE - AI Strategies
# ============================================================================
# Strategie di gioco per giocatori AI
# ============================================================================

import random

from engine.scoring import ScoringEngine


class AIStrategy:
    """
    Base class for AI strategies in Scopone.
    
    Different strategies can be implemented for various difficulty levels.
    """
    
    def __init__(self, difficulty='normal'):
        """
        Initialize AI strategy.
        
        Args:
            difficulty (str): 'easy', 'normal', or 'expert'
        """
        self.difficulty = difficulty
        self.last_decision_reason = ""

    def get_last_decision_reason(self):
        """Return a human-readable reason for the latest AI choice."""
        return self.last_decision_reason or "Nessuna motivazione disponibile"

    def _set_reason(self, reason):
        """Store the latest decision reason."""
        self.last_decision_reason = reason
    
    def choose_card(self, hand, table_cards, **kwargs):
        """
        Choose which card to play.
        
        Args:
            hand (list): Cards in AI's hand
            table_cards (list): Cards currently on table
            
        Returns:
            tuple: Card to play (value, suit)
        """
        raise NotImplementedError


class EasyAI(AIStrategy):
    """
    Easy AI - Plays randomly.
    """
    
    def choose_card(self, hand, table_cards, **kwargs):
        """
        Easy AI strategy: Play a random card.
        
        Args:
            hand (list): Cards in AI's hand
            table_cards (list): Cards currently on table
            
        Returns:
            tuple: Random card from hand
        """
        chosen = random.choice(hand)
        self._set_reason("scelta casuale (livello facile)")
        return chosen


class NormalAI(AIStrategy):
    """
    Normal AI - Tries to capture when possible, otherwise plays low cards.
    
    Strategy:
    1. Play first card that can capture
    2. If no capture possible, play lowest card
    """
    
    def choose_card(self, hand, table_cards, **kwargs):
        """
        Normal AI strategy.
        
        Args:
            hand (list): Cards in AI's hand
            table_cards (list): Cards currently on table
            
        Returns:
            tuple: Card to play
        """
        # Try to find a card that can capture
        for card in hand:
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            if possible_captures and possible_captures[0]:
                self._set_reason("cattura disponibile: priorita alla presa")
                return card
        
        # If no capture possible, play lowest card
        if hand:
            chosen = min(hand, key=lambda x: x[0])
            self._set_reason("nessuna presa disponibile: gioco la carta piu bassa")
            return chosen
        
        self._set_reason("mano vuota")
        return None


class ExpertAI(AIStrategy):
    """
    Expert AI - Uses advanced strategies.
    
    Strategy:
    1. Prioritize capturing Denari (coins)
    2. Try to capture multiple cards
    3. Avoid leaving good cards on table for opponents
    4. Plan ahead for sweeps (scope)
    """
    
    def choose_card(self, hand, table_cards, **kwargs):
        """
        Expert AI strategy with lookahead.
        
        Args:
            hand (list): Cards in AI's hand
            table_cards (list): Cards currently on table
            
        Returns:
            tuple: Card to play
        """
        # Priority 1: Capture multiple cards (better combinations)
        best_card = None
        best_combo_size = 0
        
        for card in hand:
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            if possible_captures:
                for combo in possible_captures:
                    if len(combo) > best_combo_size:
                        best_combo_size = len(combo)
                        best_card = card
                    
                    # Extra points for capturing Denari
                    if best_combo_size >= 2:
                        coins_captured = len([c for c in combo if c[1] == 'Denari'])
                        if coins_captured > 0:
                            best_card = card
                            break
        
        if best_card:
            self._set_reason("scelgo la presa con combinazione piu vantaggiosa")
            return best_card
        
        # Priority 2: Try single captures
        for card in hand:
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            if possible_captures and possible_captures[0]:
                self._set_reason("faccio una presa singola utile")
                return card
        
        # Priority 3: Play card that won't leave dangerous cards on table
        # Try to play high cards first if can't capture
        if hand:
            # Sort by value, descending (play high cards first)
            chosen = max(hand, key=lambda x: x[0])
            self._set_reason("nessuna presa: scarico carta alta")
            return chosen
        
        self._set_reason("mano vuota")
        return None


class AdaptiveAI(AIStrategy):
    """
    Adaptive AI with explicit scopa-risk analysis.

    The strategy estimates the probability that the next opponent can make
    scopa after each candidate move, then applies your requested priorities.
    """
    
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
    ALL_CARDS = [(value, suit) for suit in ('Denari', 'Coppe', 'Bastoni', 'Spade') for value in range(1, 11)]
    
    def __init__(self, difficulty='adaptive'):
        """Initialize Adaptive AI strategy."""
        super().__init__(difficulty)
    
    def choose_card(self, hand, table_cards, player_scores=None, seen_cards=None, deck_size=None):
        """
        Adaptive AI strategy with sophisticated decision making.
        
        Args:
            hand (list): Cards in AI's hand
            table_cards (list): Cards currently on table
            player_scores (list): Current player scores (for context)
            seen_cards (set): Cards already played/seen in the game
            deck_size (int): Total remaining cards in deck
            
        Returns:
            tuple: Card to play
        """
        del player_scores, deck_size

        if not hand:
            self._set_reason("mano vuota")
            return None

        seen = set(seen_cards or set())

        if not table_cards:
            best_move = self._choose_safe_card_empty_table(hand, seen)
        else:
            best_move = self._choose_strategic_card_with_table(hand, table_cards, seen)

        self._set_reason(best_move['reason'])
        return best_move['card']

    def _choose_safe_card_empty_table(self, hand, seen_cards):
        """
        CASE 1: no cards on table.

        Priorities:
        1) minimize scopa probability for next opponent move
        2) avoid 7 of Denari
        3) avoid high primiera cards (7, 6)
        4) avoid Denari
        """
        candidates = []
        for card in hand:
            value, suit = card
            table_after = [card]
            scopa_prob = self._opponent_scopa_probability(table_after, seen_cards, hand, card)
            candidates.append({
                'card': card,
                'scopa_prob': scopa_prob,
                'is_settebello': value == 7 and suit == 'Denari',
                'is_high_primiera': value in (7, 6),
                'is_denari': suit == 'Denari',
                'primiera': self.PRIMIERA_VALUES.get(value, 0),
            })

        best = min(
            candidates,
            key=lambda m: (
                m['scopa_prob'],
                1 if m['is_settebello'] else 0,
                1 if m['is_high_primiera'] else 0,
                1 if m['is_denari'] else 0,
                m['primiera'],
                m['card'][0],
            ),
        )

        reason = (
            f"tavolo vuoto: minimizzo rischio scopa avversaria "
            f"({best['scopa_prob']:.1%}), evitando carte di valore"
        )
        best['reason'] = reason
        return best

    def _choose_strategic_card_with_table(self, hand, table_cards, seen_cards):
        """
        CASE 2: cards on table with strict priority order.
        """
        moves = []
        for card in hand:
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            capture_combo = possible_captures[0] if (possible_captures and possible_captures[0]) else []

            if capture_combo:
                remaining_table = [c for c in table_cards if c not in capture_combo]
            else:
                remaining_table = table_cards + [card]

            scopa_prob = self._opponent_scopa_probability(remaining_table, seen_cards, hand, card)
            primiera_gain = sum(self.PRIMIERA_VALUES.get(c[0], 0) for c in capture_combo)
            denari_gain = sum(1 for c in capture_combo if c[1] == 'Denari')

            moves.append({
                'card': card,
                'capture_combo': capture_combo,
                'is_capture': bool(capture_combo),
                'makes_scopa': bool(capture_combo) and not remaining_table,
                'captures_settebello': (7, 'Denari') in capture_combo,
                'primiera_gain': primiera_gain,
                'denari_gain': denari_gain,
                'capture_count': len(capture_combo),
                'scopa_prob': scopa_prob,
                'remaining_table': remaining_table,
            })

        # Priority: if we can make scopa now, do it.
        scopa_now = [m for m in moves if m['makes_scopa']]
        if scopa_now:
            best = max(
                scopa_now,
                key=lambda m: (m['captures_settebello'], m['primiera_gain'], m['denari_gain'], m['capture_count']),
            )
            best['reason'] = "faccio scopa immediata (priorita massima)"
            return best

        # Safe captures: opponent scopa probability exactly 0.
        safe_captures = [m for m in moves if m['is_capture'] and m['scopa_prob'] <= 1e-9]
        if safe_captures:
            best = max(
                safe_captures,
                key=lambda m: (
                    1 if m['captures_settebello'] else 0,
                    m['primiera_gain'],
                    m['denari_gain'],
                    m['capture_count'],
                    -m['card'][0],
                ),
            )
            if best['captures_settebello']:
                reason = "presa sicura (0% scopa concessa) e catturo il 7 di Denari"
            elif best['primiera_gain'] > 0:
                reason = "presa sicura (0% scopa concessa) e massimizzo primiera"
            elif best['denari_gain'] > 0:
                reason = "presa sicura (0% scopa concessa) con priorita Denari"
            elif best['capture_count'] > 1:
                reason = "presa sicura (0% scopa concessa) e prendo piu carte"
            else:
                reason = "presa singola sicura (0% scopa concessa)"
            best['reason'] = reason
            return best

        # If no safe capture exists, prefer discarding card that minimizes scopa chance.
        discard_moves = [m for m in moves if not m['is_capture']]
        if discard_moves:
            best = min(
                discard_moves,
                key=lambda m: (
                    m['scopa_prob'],
                    1 if (m['card'][0] == 7 and m['card'][1] == 'Denari') else 0,
                    1 if m['card'][0] in (7, 6) else 0,
                    1 if m['card'][1] == 'Denari' else 0,
                    m['card'][0],
                ),
            )
            best['reason'] = (
                f"nessuna presa sicura: scarto la carta con rischio scopa minimo "
                f"({best['scopa_prob']:.1%})"
            )
            return best

        # Fallback: all moves are captures with non-zero risk. Pick the least risky one.
        best = min(
            moves,
            key=lambda m: (
                m['scopa_prob'],
                -m['captures_settebello'],
                -m['primiera_gain'],
                -m['denari_gain'],
                -m['capture_count'],
            ),
        )
        best['reason'] = (
            f"solo prese rischiose disponibili: scelgo quella con rischio scopa minore "
            f"({best['scopa_prob']:.1%})"
        )
        return best

    def _opponent_scopa_probability(self, table_after_move, seen_cards, hand_cards, played_card):
        """Estimate probability of opponent making scopa on their next turn."""
        if not table_after_move:
            return 0.0

        unavailable = set(seen_cards)
        unavailable.update(hand_cards)
        unavailable.update(table_after_move)
        unavailable.add(played_card)

        opponent_candidates = [card for card in self.ALL_CARDS if card not in unavailable]
        if not opponent_candidates:
            return 0.0

        scopa_cards = 0
        for opponent_card in opponent_candidates:
            captures = ScoringEngine.find_captures(opponent_card, table_after_move)
            if captures and captures[0] and len(captures[0]) == len(table_after_move):
                scopa_cards += 1

        return scopa_cards / len(opponent_candidates)


def get_ai_strategy(difficulty='normal'):
    """
    Factory function to get AI strategy by difficulty.
    
    Args:
        difficulty (str): 'easy', 'normal', 'expert', or 'adaptive'
        
    Returns:
        AIStrategy: Strategy instance
    """
    strategies = {
        'easy': EasyAI,
        'normal': NormalAI,
        'expert': ExpertAI,
        'adaptive': AdaptiveAI
    }
    
    strategy_class = strategies.get(difficulty, NormalAI)
    return strategy_class(difficulty)
