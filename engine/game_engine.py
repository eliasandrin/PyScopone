# ============================================================================
# SCOPONE - Game Engine
# ============================================================================
# Motore principale del gioco di Scopone
# ============================================================================

import random
from models.player import Player
from config.constants import (
    SEMI, TOTAL_DECK_SIZE, INITIAL_TABLE_CARDS,
    INITIAL_HAND_CARDS, INITIAL_TABLE_CARDS_BY_MODE,
    TEAM_A_PLAYERS, TEAM_B_PLAYERS
)
from engine.scoring import ScoringEngine


class GameEngine:
    """
    Main game engine for Scopone card game.
    
    Manages:
    - Game state and flow
    - Player turns and card plays
    - Card distribution and table management
    - Final score calculation and history
    """
    
    def __init__(self, num_players=4, player_names=None):
        """
        Initialize a new game.
        
        Args:
            num_players (int): Number of players (2-6)
            player_names (list): Names for each player
        """
        # Validate player count
        from config.constants import MIN_PLAYERS, MAX_PLAYERS
        self.num_players = min(max(num_players, MIN_PLAYERS), MAX_PLAYERS)
        
        # Initialize deck
        self.deck = self._create_deck()
        
        # Game state
        self.players = []
        self.table = []
        self.seen_cards = set()
        self.current_player_idx = 0
        self.last_capturer_idx = 0
        self.game_active = False
        
        # Game history
        self.moves_played = []
        self.final_scores = []
        self.game_history = []
        
        # Create players
        self._initialize_players(player_names)
    
    def _create_deck(self):
        """
        Create a standard 40-card Italian deck.
        
        Returns:
            list: Deck of cards as (value, suit) tuples
        """
        deck = [(value, suit) for suit in SEMI for value in range(1, 11)]
        return deck
    
    def _initialize_players(self, player_names):
        """
        Initialize players for the game.
        
        Args:
            player_names (list): Names for each player, or None for defaults
        """
        self.players = []
        for i in range(self.num_players):
            if player_names and i < len(player_names):
                name = player_names[i]
            else:
                name = f"Giocatore {i+1}"
            
            is_human = (i == 0)  # First player is always human
            is_ai = not is_human
            
            # Assign team for 4-player games
            team = None
            if self.num_players == 4:
                if i in TEAM_A_PLAYERS:
                    team = 0
                else:
                    team = 1
            
            self.players.append(Player(name, i, is_ai, is_human, team=team))
    
    def reset(self):
        """Reset the game for a new round."""
        self.deck = self._create_deck()
        self.table = []
        self.seen_cards = set()
        # Randomly select starting player
        self.current_player_idx = random.randint(0, self.num_players - 1)
        self.game_active = True
        self.moves_played = []
        self.final_scores = []
        
        for player in self.players:
            player.reset()
    
    def deal_cards(self):
        """
        Deal initial cards to all players and table.
        
        Two-player mode:
        - 10 cards per player, 0 on table
        - After all cards played, restock with remaining 20 cards
        
        Four-player mode:
        - 9 cards per player, 4 on table
        - Standard Scopone distribution
        """
        random.shuffle(self.deck)
        
        # Get initial distribution based on player count
        initial_table_cards = INITIAL_TABLE_CARDS_BY_MODE.get(self.num_players, 4)
        initial_hand_cards = INITIAL_HAND_CARDS.get(self.num_players, 9)
        
        if self.num_players == 2:
            # 2-player mode: 10 cards per player, 0 on table
            # Deal all 20 cards to players, keep rest for later restocking
            cards_to_use = 20  # 10 per player
            self.table = []
            
            # Deal 10 cards per player
            for i in range(self.num_players):
                cards = self.deck[i*10:(i+1)*10]
                self.players[i].add_to_hand(cards)
                
            # Save remaining 20 cards for restocking
            self.deck_remaining = self.deck[20:]
            
        else:
            # 4-player mode (standard): 4 cards on table, 9 per player
            # Deal 4 cards to table
            self.table = self.deck[:initial_table_cards]
            self.seen_cards.update(self.table)
            
            # Divide remaining 36 cards among players (9 each)
            remaining_cards = self.deck[initial_table_cards:]
            cards_per_player = 9
            
            for i in range(self.num_players):
                start = i * cards_per_player
                end = start + cards_per_player
                cards = remaining_cards[start:end]
                self.players[i].add_to_hand(cards)
            
            # No remaining cards to track in 4-player mode
            self.deck_remaining = []
    
    def restock_cards(self):
        """
        Restock cards for 2-player mode after first 10 cards are depleted.
        
        Only used in 2-player mode.
        """
        if self.num_players != 2 or not hasattr(self, 'deck_remaining'):
            return
            
        if len(self.deck_remaining) < 2 * self.num_players:
            return  # Not enough cards to restock (less than 4 cards)
        
        # Deal 10 more cards to each player
        for i in range(self.num_players):
            if i < len(self.deck_remaining) // self.num_players:
                start = i * 10
                end = start + 10
                if end <= len(self.deck_remaining):
                    cards = self.deck_remaining[start:end]
                    self.players[i].add_to_hand(cards)
        
        # Remove used cards from remaining deck
        self.deck_remaining = self.deck_remaining[self.num_players * 10:]
    
    def get_current_player(self):
        """
        Get the player whose turn it is.
        
        Returns:
            Player: Current player
        """
        return self.players[self.current_player_idx]
    
    def get_human_player(self):
        """
        Get the human player.
        
        Returns:
            Player: First human player found
        """
        for player in self.players:
            if player.is_human:
                return player
        return self.players[0]
    
    def play_card(self, player_idx, card):
        """
        Play a card from a player's hand.
        
        Args:
            player_idx (int): Index of player
            card (tuple): Card to play (value, suit)
            
        Returns:
            bool: True if move was successful
        """
        player = self.players[player_idx]
        
        # Validate card is in hand
        if not player.has_card(card):
            return False
        
        # Remove from hand and record move
        player.remove_from_hand(card)
        self.seen_cards.add(card)
        self.moves_played.append((player.name, card))
        
        # Check for possible captures
        possible_captures = ScoringEngine.find_captures(card, self.table)
        
        if possible_captures and possible_captures[0]:
            # Card captures something
            captured_combo = possible_captures[0]
            for captured_card in captured_combo:
                self.table.remove(captured_card)
            
            # Add captured cards and playing card to player's pile
            player.capture_cards(captured_combo + [card])
            
            # Check for scopa (cleared table)
            # CRITICAL: According to Scopone rules, the last card of the game 
            # that empties the table does NOT count as scopa
            if not self.table:
                is_last_card_of_game = all(len(p.hand) == 0 for p in self.players)
                if not is_last_card_of_game:
                    player.add_sweep()
            
            self.last_capturer_idx = player_idx
        else:
            # Card doesn't capture anything, goes to table
            self.table.append(card)
        
        # Check if game should end
        if all(len(p.hand) == 0 for p in self.players):
            # Check if we need to restock (2-player mode)
            if self.num_players == 2 and hasattr(self, 'deck_remaining') and self.deck_remaining:
                self.restock_cards()
            else:
                self.end_game()
        
        return True
    
    def next_player(self):
        """Advance to the next player's turn."""
        self.current_player_idx = (self.current_player_idx - 1) % self.num_players
    
    def end_game(self):
        """
        End the current game and calculate final scores.
        
        Remaining cards on table go to the last player who captured.
        """
        # Give remaining table cards to last capturer
        if self.table:
            last_player = self.players[self.last_capturer_idx]
            last_player.capture_cards(self.table)
            self.table = []
        
        # Calculate final scores
        self._calculate_final_scores()
        self.game_active = False
    
    def _calculate_final_scores(self):
        """Calculate final scores for all players."""
        self.final_scores = ScoringEngine.calculate_final_scores(self.players)
        
        # Add to game history
        winners = ScoringEngine.get_game_winners(self.final_scores)
        self.game_history.append({
            'winners': winners,
            'scores': self.final_scores.copy(),
            'num_players': self.num_players,
            'moves': self.moves_played.copy()
        })
    
    def get_game_state(self):
        """
        Get a snapshot of the current game state.
        
        Returns:
            dict: Game state information
        """
        return {
            'current_player': self.get_current_player().name,
            'current_player_idx': self.current_player_idx,
            'table_cards': self.table.copy(),
            'game_active': self.game_active,
            'players': [
                {
                    'name': p.name,
                    'hand_size': len(p.hand),
                    'captured_count': len(p.captured),
                    'sweeps': p.sweeps,
                    'is_human': p.is_human,
                    'is_ai': p.is_ai
                }
                for p in self.players
            ]
        }
    
    def get_game_stats(self):
        """
        Get game statistics.
        
        Returns:
            dict: Game statistics
        """
        return {
            'total_games': len(self.game_history),
            'current_game_moves': len(self.moves_played),
            'num_players': self.num_players,
            'final_scores': self.final_scores
        }
