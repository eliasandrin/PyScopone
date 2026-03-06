# ============================================================================
# SCOPONE - Player Model
# ============================================================================
# Definizione della classe Player per rappresentare i giocatori
# ============================================================================


class Player:
    """
    Represents a player in the Scopone game.
    
    Attributes:
        id (int): Unique player identifier
        name (str): Player's name
        hand (list): Cards currently in hand
        captured (list): Cards captured during the game
        sweeps (int): Number of scopa (sweeps) made
        total_points (int): Total points scored
        primiera_point (int): Points from primiera (best scoring hand)
        is_ai (bool): Whether this is an AI player
        is_human (bool): Whether this is a human player
    """
    
    def __init__(self, name, player_id, is_ai=False, is_human=False, team=None):
        """
        Initialize a new player.
        
        Args:
            name (str): Player's name
            player_id (int): Unique identifier for the player
            is_ai (bool): Whether this is an AI player
            is_human (bool): Whether this is a human player
            team (int): Team number for team-based games (4-player mode)
        """
        self.id = player_id
        self.name = name
        self.hand = []
        self.captured = []
        self.sweeps = 0
        self.total_points = 0
        self.primiera_point = 0
        self.is_ai = is_ai
        self.is_human = is_human
        self.team = team  # 0 or 1 for team-based games
    
    def reset(self):
        """Reset player state for a new game."""
        self.hand = []
        self.captured = []
        self.sweeps = 0
        self.total_points = 0
        self.primiera_point = 0
    
    def add_to_hand(self, cards):
        """
        Add cards to player's hand.
        
        Args:
            cards (list): Cards to add to hand
        """
        if isinstance(cards, list):
            self.hand.extend(cards)
        else:
            self.hand.append(cards)
    
    def remove_from_hand(self, card):
        """
        Remove a card from player's hand.
        
        Args:
            card (tuple): Card to remove (value, suit)
            
        Returns:
            bool: True if card was removed, False otherwise
        """
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False
    
    def capture_cards(self, cards):
        """
        Capture cards and add them to captured pile.
        
        Args:
            cards (list): Cards to capture
        """
        if isinstance(cards, list):
            self.captured.extend(cards)
        else:
            self.captured.append(cards)
    
    def add_sweep(self):
        """Register a scopa (sweep) for this player."""
        self.sweeps += 1
    
    def has_card(self, card):
        """
        Check if player has a specific card.
        
        Args:
            card (tuple): Card to check (value, suit)
            
        Returns:
            bool: True if player has the card
        """
        return card in self.hand
    
    def get_hand_size(self):
        """Return the number of cards in hand."""
        return len(self.hand)
    
    def get_captured_count(self):
        """Return the number of captured cards."""
        return len(self.captured)
    
    def count_coins(self):
        """
        Count the number of Denari (coins) in captured cards.
        
        Returns:
            int: Number of Denari coins
        """
        return len([c for c in self.captured if c[1] == 'Denari'])
    
    def has_settebello(self):
        """
        Check if player has the 7 of Denari.
        
        Returns:
            bool: True if player has 7♦
        """
        return (7, 'Denari') in self.captured
    
    def __repr__(self):
        """String representation of player."""
        player_type = "AI" if self.is_ai else "Human"
        return f"Player({self.name}, {player_type}, hand={len(self.hand)}, captured={len(self.captured)})"
