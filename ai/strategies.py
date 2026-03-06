# ============================================================================
# SCOPONE - AI Strategies
# ============================================================================
# Strategie di gioco per giocatori AI
# ============================================================================

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
    
    def choose_card(self, hand, table_cards):
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
    
    def choose_card(self, hand, table_cards):
        """
        Easy AI strategy: Play a random card.
        
        Args:
            hand (list): Cards in AI's hand
            table_cards (list): Cards currently on table
            
        Returns:
            tuple: Random card from hand
        """
        import random
        return random.choice(hand)


class NormalAI(AIStrategy):
    """
    Normal AI - Tries to capture when possible, otherwise plays low cards.
    
    Strategy:
    1. Play first card that can capture
    2. If no capture possible, play lowest card
    """
    
    def choose_card(self, hand, table_cards):
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
                return card
        
        # If no capture possible, play lowest card
        if hand:
            return min(hand, key=lambda x: x[0])
        
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
    
    def choose_card(self, hand, table_cards):
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
            return best_card
        
        # Priority 2: Try single captures
        for card in hand:
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            if possible_captures and possible_captures[0]:
                return card
        
        # Priority 3: Play card that won't leave dangerous cards on table
        # Try to play high cards first if can't capture
        if hand:
            # Sort by value, descending (play high cards first)
            return max(hand, key=lambda x: x[0])
        
        return None


class AdaptiveAI(AIStrategy):
    """
    Adaptive AI - Learns and adjusts strategy based on game situation.
    
    More sophisticated strategy that considers multiple factors.
    """
    
    def choose_card(self, hand, table_cards, player_scores=None):
        """
        Adaptive AI strategy.
        
        Args:
            hand (list): Cards in AI's hand
            table_cards (list): Cards currently on table
            player_scores (list): Current player scores (for context)
            
        Returns:
            tuple: Card to play
        """
        # If no table cards, just play lowest
        if not table_cards:
            return min(hand, key=lambda x: x[0])
        
        # Try to capture
        captures_available = []
        for card in hand:
            possible_captures = ScoringEngine.find_captures(card, table_cards)
            if possible_captures and possible_captures[0]:
                captures_available.append((card, possible_captures[0]))
        
        if captures_available:
            # Rank captures by quality
            best_capture = max(
                captures_available,
                key=lambda x: (
                    len(x[1]),  # Prefer multi-card captures
                    sum(1 for c in x[1] if c[1] == 'Denari'),  # Coins
                    sum(1 for c in x[1] if c[0] == 7 and c[1] == 'Denari')  # Settebello
                )
            )
            return best_capture[0]
        
        # No capture: play strategically
        # Avoid leaving Denari on table if possible
        denari_on_table = [c for c in table_cards if c[1] == 'Denari']
        hands_without_denari = [c for c in hand if c[1] != 'Denari']
        
        if hands_without_denari and denari_on_table:
            # If there are Denari on table, try not to play those
            return min(hands_without_denari, key=lambda x: x[0])
        
        # Otherwise play the lowest card
        if hand:
            return min(hand, key=lambda x: x[0])
        
        return None


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
