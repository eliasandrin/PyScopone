# ============================================================================
# SCOPONE - Card Model
# ============================================================================
# Definizione della classe Card per rappresentare le carte
# ============================================================================

from config.constants import SEMI, SIMBOLI, VALORI_PRIMIERA


class Card:
    """
    Represents a single playing card in Scopone.
    
    Attributes:
        value (int): Card value from 1 (Ace) to 10
        suit (str): Card suit (Denari, Coppe, Bastoni, Spade)
    """
    
    def __init__(self, value, suit):
        """
        Initialize a card.
        
        Args:
            value (int): Card value (1-10)
            suit (str): Card suit
            
        Raises:
            ValueError: If value or suit is invalid
        """
        if not isinstance(value, int) or value < 1 or value > 10:
            raise ValueError(f"Invalid card value: {value}. Must be 1-10.")
        
        if suit not in SEMI:
            raise ValueError(f"Invalid suit: {suit}. Must be one of {SEMI}.")
        
        self.value = value
        self.suit = suit
    
    def get_primiera_value(self):
        """
        Get the primiera (scoring value) for this card.
        
        Returns:
            int: Primiera value for scoring calculations
        """
        return VALORI_PRIMIERA.get(self.value, 0)
    
    def get_display_name(self):
        """
        Get a display name for the card.
        
        Returns:
            str: Card name with symbol (e.g., "7♦")
        """
        return f"{self.value}{SIMBOLI[self.suit]}"
    
    def is_coin(self):
        """Check if this is a Denari (coin)."""
        return self.suit == 'Denari'
    
    def is_settebello(self):
        """Check if this is the 7 of Denari."""
        return self.value == 7 and self.suit == 'Denari'
    
    def to_tuple(self):
        """
        Convert to tuple representation (for compatibility).
        
        Returns:
            tuple: (value, suit)
        """
        return (self.value, self.suit)
    
    @staticmethod
    def from_tuple(card_tuple):
        """
        Create a Card from a tuple representation.
        
        Args:
            card_tuple (tuple): (value, suit)
            
        Returns:
            Card: Card instance
        """
        return Card(card_tuple[0], card_tuple[1])
    
    def __eq__(self, other):
        """Check equality with another card or tuple."""
        if isinstance(other, Card):
            return self.value == other.value and self.suit == other.suit
        elif isinstance(other, tuple):
            return self.value == other[0] and self.suit == other[1]
        return False
    
    def __hash__(self):
        """Make card hashable for use in sets and dicts."""
        return hash((self.value, self.suit))
    
    def __repr__(self):
        """String representation of card."""
        return f"Card({self.value}, {self.suit})"
    
    def __str__(self):
        """User-friendly string representation."""
        return self.get_display_name()
