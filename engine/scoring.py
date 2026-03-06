# ============================================================================
# SCOPONE - Scoring Engine
# ============================================================================
# Logica per il calcolo dei punti e delle statistiche di gioco
# ============================================================================

from config.constants import (
    VALORI_PRIMIERA,
    POINTS_FOR_MOST_CARDS,
    POINTS_FOR_MOST_COINS,
    POINTS_FOR_SETTEBELLO,
    POINTS_FOR_PRIMIERA,
    THRESHOLD_CARDS,
    THRESHOLD_COINS
)


class ScoringEngine:
    """
    Manages all scoring calculations for the Scopone game.
    """
    
    @staticmethod
    def calculate_primiera(cards_list):
        """
        Calculate primiera (best scoring combination) for a list of cards.
        
        Primiera is calculated by taking the highest-scoring card of each suit.
        The highest-scoring card of each suit is worth its primiera value.
        The total primiera is the sum of these values.
        
        Args:
            cards_list (list): List of cards to score, each as (value, suit) tuple
            
        Returns:
            int: Total primiera score
        """
        suit_scores = {"Denari": 0, "Coppe": 0, "Bastoni": 0, "Spade": 0}
        
        for value, suit in cards_list:
            primiera_value = VALORI_PRIMIERA.get(value, 0)
            if primiera_value > suit_scores[suit]:
                suit_scores[suit] = primiera_value
        
        return sum(suit_scores.values())
    
    @staticmethod
    def find_captures(card, table_cards):
        """
        Find all possible capture combinations for a given card.
        
        A card can capture:
        1. A single card with the same value
        2. A combination of cards that sum to the card's value
        
        Args:
            card (tuple): Card to play (value, suit)
            table_cards (list): Cards currently on the table
            
        Returns:
            list: List of possible capture combinations
        """
        from itertools import combinations
        
        card_value = card[0]
        
        # Check for single card capture
        single_captures = [c for c in table_cards if c[0] == card_value]
        if single_captures:
            return [[single_captures[0]]]
        
        # Check for combination captures
        combination_captures = []
        for combo_size in range(2, len(table_cards) + 1):
            for combo in combinations(table_cards, combo_size):
                if sum(c[0] for c in combo) == card_value:
                    combination_captures.append(list(combo))
        
        # Return combinations if found, otherwise return empty combination (card goes to table)
        return combination_captures if combination_captures else [[]]
    
    @staticmethod
    def calculate_player_score(player):
        """
        Calculate total score for a player based on captured cards.
        
        Scoring rules:
        - 1 point for having most cards (>20)
        - 1 point for having most Denari coins (>5)
        - 1 point for having the 7 of Denari
        - 1 point for having best primiera
        - 1 point per scopa (sweep)
        
        Args:
            player: Player object
            
        Returns:
            dict: Scoring breakdown with totals
        """
        captured_count = len(player.captured)
        coins_count = player.count_coins()
        has_settebello = player.has_settebello()
        primiera_value = ScoringEngine.calculate_primiera(player.captured)
        
        points = {
            'cards': POINTS_FOR_MOST_CARDS if captured_count > THRESHOLD_CARDS else 0,
            'coins': POINTS_FOR_MOST_COINS if coins_count > THRESHOLD_COINS else 0,
            'settebello': POINTS_FOR_SETTEBELLO if has_settebello else 0,
            'primiera': 0,  # Will be assigned later based on comparison
            'sweeps': player.sweeps
        }
        
        total = sum(points.values())
        
        return {
            'player': player.name,
            'points': points,
            'primiera_value': primiera_value,
            'total': total,
            'captured_cards': captured_count,
            'sweeps': player.sweeps,
            'coins': coins_count,
            'has_settebello': has_settebello
        }
    
    @staticmethod
    def calculate_final_scores(players):
        """
        Calculate final scores for all players in the game.
        
        For 4-player team games, scores are calculated per team.
        For 2-player games, scores are calculated per player.
        
        Args:
            players (list): List of Player objects
            
        Returns:
            list: Sorted list of final scores (highest first)
        """
        # Check if this is a team game (4-player mode)
        if len(players) == 4 and all(hasattr(p, 'team') and p.team is not None for p in players):
            return ScoringEngine._calculate_team_scores(players)
        else:
            return ScoringEngine._calculate_individual_scores(players)
    
    @staticmethod
    def _calculate_individual_scores(players):
        """
        Calculate scores for individual players (2-player mode).
        
        Args:
            players (list): List of Player objects
            
        Returns:
            list: Sorted list of final scores
        """
        # Calculate individual scores
        final_scores = []
        for player in players:
            score_data = ScoringEngine.calculate_player_score(player)
            final_scores.append(score_data)
        
        # Award primiera point to player(s) with highest primiera value
        primiera_scores = [(i, score['primiera_value']) for i, score in enumerate(final_scores)]
        if primiera_scores:
            highest_primiera = max(primiera_scores, key=lambda x: x[1])[1]
            for i, score in enumerate(final_scores):
                if score['primiera_value'] == highest_primiera:
                    final_scores[i]['points']['primiera'] = POINTS_FOR_PRIMIERA
                    final_scores[i]['total'] += POINTS_FOR_PRIMIERA
        
        # Sort by total points
        final_scores.sort(key=lambda x: x['total'], reverse=True)
        
        return final_scores
    
    @staticmethod
    def _calculate_team_scores(players):
        """
        Calculate scores for team-based play (4-player mode).
        
        Teams are determined by player.team attribute:
        - Team 0: players 0 and 2
        - Team 1: players 1 and 3
        
        Args:
            players (list): List of Player objects
            
        Returns:
            list: Sorted list of team final scores
        """
        # Calculate individual scores first
        individual_scores = []
        for player in players:
            score_data = ScoringEngine.calculate_player_score(player)
            individual_scores.append(score_data)
        
        # Combine scores by team
        team_scores = {0: {'players': [], 'points': 0, 'primiera': 0, 'cards': 0, 
                           'coins': 0, 'sweeps': 0, 'settebello': False},
                       1: {'players': [], 'points': 0, 'primiera': 0, 'cards': 0, 
                           'coins': 0, 'sweeps': 0, 'settebello': False}}
        
        for player in players:
            team = player.team
            team_scores[team]['players'].append(player.name)
            # Sum up team cards and sweeps
            team_scores[team]['cards'] += len(player.captured)
            team_scores[team]['sweeps'] += player.sweeps
            # Check for settebello
            if player.has_settebello():
                team_scores[team]['settebello'] = True
        
        # Calculate team primiera (combine cards from team members)
        for team in [0, 1]:
            team_cards = []
            for player in players:
                if player.team == team:
                    team_cards.extend(player.captured)
            team_scores[team]['primiera'] = ScoringEngine.calculate_primiera(team_cards)
        
        # Award points to teams
        final_team_scores = []
        for team_id in [0, 1]:
            team_data = team_scores[team_id]
            points = 0
            
            # Most cards point
            if team_data['cards'] > THRESHOLD_CARDS:
                points += POINTS_FOR_MOST_CARDS
            
            # Most coins point
            coins_in_team = sum(player.count_coins() for player in players if player.team == team_id)
            if coins_in_team > THRESHOLD_COINS:
                points += POINTS_FOR_MOST_COINS
            
            # Settebello point
            if team_data['settebello']:
                points += POINTS_FOR_SETTEBELLO
            
            # Sweeps points
            points += team_data['sweeps']
            
            final_team_scores.append({
                'team': team_id,
                'player': f"Team {team_id + 1}",  # "Team 1" or "Team 2"
                'members': team_data['players'],
                'captured_cards': team_data['cards'],
                'coins': coins_in_team,
                'sweeps': team_data['sweeps'],
                'primiera_value': team_data['primiera'],
                'total': points,
                'points': {
                    'cards': POINTS_FOR_MOST_CARDS if team_data['cards'] > THRESHOLD_CARDS else 0,
                    'coins': POINTS_FOR_MOST_COINS if coins_in_team > THRESHOLD_COINS else 0,
                    'settebello': POINTS_FOR_SETTEBELLO if team_data['settebello'] else 0,
                    'primiera': 0,  # Will be assigned next
                    'sweeps': team_data['sweeps']
                }
            })
        
        # Award primiera to team with highest primiera value
        if final_team_scores:
            highest_primiera = max(final_team_scores, key=lambda x: x['primiera_value'])['primiera_value']
            for score in final_team_scores:
                if score['primiera_value'] == highest_primiera:
                    score['points']['primiera'] = POINTS_FOR_PRIMIERA
                    score['total'] += POINTS_FOR_PRIMIERA
        
        # Sort by total points
        final_team_scores.sort(key=lambda x: x['total'], reverse=True)
        
        return final_team_scores
    
    @staticmethod
    def get_game_winners(final_scores):
        """
        Get the winner(s) of the game.
        
        Args:
            final_scores (list): Sorted list of final scores
            
        Returns:
            list: List of winner names
        """
        if not final_scores:
            return []
        
        highest_score = final_scores[0]['total']
        winners = [score['player'] for score in final_scores if score['total'] == highest_score]
        
        return winners
