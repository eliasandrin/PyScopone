"""Core game logic for Scopone."""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

from .card import Card, Deck, Suit, find_capture_combinations
from .player import Player, Team


class Game:
    """Manages a full game of Scopone.

    Scopone rules summary
    ---------------------
    * 4 players, 2 teams of 2 (sitting opposite each other).
    * All 40 cards of an Italian deck are dealt (10 per player).
    * The table starts empty.
    * Players take turns playing one card:
        - If a table card matches the played card's value, capture it
          (single-card match is mandatory and takes precedence).
        - If a combination of table cards sums to the played card, capture it.
        - Otherwise, leave the played card on the table.
    * A *scopa* is scored whenever all table cards are captured in one move.
    * After all cards are played, remaining table cards go to the last capturer.
    * Score one point each for: most cards, most Coins, Sette Bello, Primiera,
      plus one point per scopa.
    * The first team to reach a target score (default 11) wins the game.

    Parameters
    ----------
    target_score:
        Points needed to win the game (default 11).
    ai_delay:
        Seconds to pause after each AI move so the player can follow along.
    """

    def __init__(
        self,
        target_score: int = 11,
        ai_delay: float = 0.8,
    ) -> None:
        self.target_score = target_score
        self.ai_delay = ai_delay

        # Create players
        self.human = Player("You", is_human=True)
        self.ai1 = Player("CPU-1")
        self.ai2 = Player("CPU-2")
        self.ai3 = Player("CPU-3")

        # Teams: human + ai2 vs ai1 + ai3
        self.team_a = Team("Team A", self.human, self.ai2)
        self.team_b = Team("Team B", self.ai1, self.ai3)

        # Turn order: human, ai1, ai2, ai3
        self.players: List[Player] = [self.human, self.ai1, self.ai2, self.ai3]

        # Game-level state
        self.table: List[Card] = []
        self.last_capturer: Optional[Team] = None
        self.round_number: int = 0
        self.scores: Dict[str, int] = {
            self.team_a.name: 0,
            self.team_b.name: 0,
        }

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def play(self) -> None:
        """Run the full game loop until one team reaches the target score."""
        self._print_welcome()
        while max(self.scores.values()) < self.target_score:
            self.round_number += 1
            self._play_round()
            self._print_round_scores()
            input("\nPress Enter to continue to the next round…")
        self._print_final_result()

    # ------------------------------------------------------------------
    # Round logic
    # ------------------------------------------------------------------

    def _play_round(self) -> None:
        """Deal and play a single round (10 tricks × 4 players)."""
        # Reset per-round state
        for player in self.players:
            player.hand.clear()
            player.captured.clear()
            player.scope = 0
        self.table.clear()
        self.last_capturer = None

        # Deal
        deck = Deck()
        deck.shuffle()
        for player in self.players:
            player.receive_cards(deck.deal(10))

        print(f"\n{'=' * 60}")
        print(f"  ROUND {self.round_number}")
        print(f"  Score → {self.team_a.name}: {self.scores[self.team_a.name]}  |  "
              f"{self.team_b.name}: {self.scores[self.team_b.name]}")
        print(f"{'=' * 60}\n")

        # Play 10 tricks (each player plays all 10 cards, one at a time)
        for _trick in range(10):
            for player in self.players:
                self._take_turn(player)

        # Remaining table cards go to the last capturing team
        if self.table and self.last_capturer is not None:
            # Find which player on the team last captured (use first player
            # as recipient – doesn't matter for team scoring)
            recipient = self.last_capturer.players[0]
            recipient.captured.extend(self.table)
            self.table.clear()

        # Tally round scores
        self._tally_round()

    def _take_turn(self, player: Player) -> None:
        """Execute one player's turn."""
        self._print_table()

        if player.is_human:
            card = self._human_choose_card()
            capture = self._human_choose_capture(card)
        else:
            card = player.choose_card_to_play(self.table)
            capture = player.choose_capture(card, self.table)
            print(f"\n  {player.name} plays {card}", end="")
            if capture:
                print(f"  →  captures {self._fmt_cards(capture)}")
            else:
                print("  (no capture)")
            time.sleep(self.ai_delay)

        player.play_card(card)

        if capture:
            self._apply_capture(player, card, capture)
        else:
            self.table.append(card)

    # ------------------------------------------------------------------
    # Human interaction helpers
    # ------------------------------------------------------------------

    def _human_choose_card(self) -> Card:
        """Prompt the human player to pick a card from their hand."""
        while True:
            print(f"\n  Your hand: {self.human.show_hand()}")
            raw = input("  Pick a card (number): ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(self.human.hand):
                    return sorted(self.human.hand)[idx]
            print("  ⚠  Invalid choice, try again.")

    def _human_choose_capture(self, card: Card) -> Optional[List[Card]]:
        """Prompt the human player to choose a capture combination."""
        combos = find_capture_combinations(card.value, self.table)
        if not combos:
            return None
        if len(combos) == 1:
            print(f"  Auto-capturing: {self._fmt_cards(combos[0])}")
            return combos[0]

        print(f"\n  Available captures for {card}:")
        for i, combo in enumerate(combos):
            print(f"    [{i + 1}] {self._fmt_cards(combo)}")
        while True:
            raw = input("  Choose a capture (number): ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(combos):
                    return combos[idx]
            print("  ⚠  Invalid choice, try again.")

    # ------------------------------------------------------------------
    # Capture application
    # ------------------------------------------------------------------

    def _apply_capture(
        self, player: Player, played: Card, combo: List[Card]
    ) -> None:
        """Apply a capture: add played card + combo to player's pile."""
        for c in combo:
            self.table.remove(c)

        player.captured.append(played)
        player.captured.extend(combo)

        team = self._team_of(player)
        self.last_capturer = team

        # Check for scopa (table now empty)
        if not self.table:
            player.scope += 1
            print(f"  🎉  SCOPA! {player.name} sweeps the table!")

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _tally_round(self) -> None:
        """Calculate round points and update cumulative scores."""
        points_a, points_b = self._calculate_round_points()
        self.scores[self.team_a.name] += points_a
        self.scores[self.team_b.name] += points_b

    def _calculate_round_points(self) -> Tuple[int, int]:
        """Return (team_a_points, team_b_points) for the current round."""
        pa, pb = 0, 0

        # --- Cards (most captured) ---
        ca, cb = self.team_a.card_count(), self.team_b.card_count()
        if ca > cb:
            pa += 1
            _cards_msg = f"Cards: {self.team_a.name} wins ({ca} vs {cb})"
        elif cb > ca:
            pb += 1
            _cards_msg = f"Cards: {self.team_b.name} wins ({cb} vs {ca})"
        else:
            _cards_msg = f"Cards: tie ({ca} each)"

        # --- Coins (most Coins suit cards) ---
        oa, ob = self.team_a.coin_count(), self.team_b.coin_count()
        if oa > ob:
            pa += 1
            _coins_msg = f"Coins: {self.team_a.name} wins ({oa} vs {ob})"
        elif ob > oa:
            pb += 1
            _coins_msg = f"Coins: {self.team_b.name} wins ({ob} vs {oa})"
        else:
            _coins_msg = f"Coins: tie ({oa} each)"

        # --- Sette Bello ---
        if self.team_a.has_sette_bello():
            pa += 1
            _sb_msg = f"Sette Bello: {self.team_a.name}"
        else:
            pb += 1
            _sb_msg = f"Sette Bello: {self.team_b.name}"

        # --- Primiera ---
        pra, prb = self.team_a.primiera_score(), self.team_b.primiera_score()
        if pra > prb:
            pa += 1
            _prim_msg = f"Primiera: {self.team_a.name} wins ({pra} vs {prb})"
        elif prb > pra:
            pb += 1
            _prim_msg = f"Primiera: {self.team_b.name} wins ({prb} vs {pra})"
        else:
            _prim_msg = f"Primiera: tie ({pra} each)"

        # --- Scope ---
        sa, sb = self.team_a.scope_total, self.team_b.scope_total
        pa += sa
        pb += sb
        _scope_msg = f"Scope: {self.team_a.name} {sa}  |  {self.team_b.name} {sb}"

        # Print breakdown
        print(f"\n{'─' * 50}")
        print("  Round scoring breakdown:")
        print(f"    {_cards_msg}")
        print(f"    {_coins_msg}")
        print(f"    {_sb_msg}")
        print(f"    {_prim_msg}")
        print(f"    {_scope_msg}")
        print(f"  Round points → {self.team_a.name}: {pa}  |  {self.team_b.name}: {pb}")
        print(f"{'─' * 50}")

        return pa, pb

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _print_welcome(self) -> None:
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 20 + "SCOPONE" + " " * 31 + "║")
        print("╠" + "═" * 58 + "╣")
        print("║  Rules summary:                                          ║")
        print("║  • 4 players – You + CPU-2 (Team A) vs CPU-1 + CPU-3    ║")
        print("║    (Team B)                                              ║")
        print("║  • Play a card that matches or sums cards on the table   ║")
        print("║    to capture them.                                      ║")
        print("║  • A scopa earns a bonus point.                          ║")
        print("║  • Score for: most cards, most Coins, Sette Bello,      ║")
        print("║    Primiera, and each scopa.                             ║")
        print(f"║  • First team to {self.target_score} points wins.                     ║")
        print("╚" + "═" * 58 + "╝")
        input("\nPress Enter to start…")

    def _print_table(self) -> None:
        cards_str = "  ".join(str(c) for c in self.table) if self.table else "(empty)"
        print(f"\n  Table: {cards_str}")

    def _print_round_scores(self) -> None:
        print(
            f"\n  Cumulative score → "
            f"{self.team_a.name}: {self.scores[self.team_a.name]}  |  "
            f"{self.team_b.name}: {self.scores[self.team_b.name]}"
        )

    def _print_final_result(self) -> None:
        print(f"\n{'=' * 60}")
        if self.scores[self.team_a.name] >= self.target_score:
            winner = self.team_a.name
        else:
            winner = self.team_b.name
        print(f"  🏆  {winner} wins the game!")
        print(f"  Final score → "
              f"{self.team_a.name}: {self.scores[self.team_a.name]}  |  "
              f"{self.team_b.name}: {self.scores[self.team_b.name]}")
        print(f"{'=' * 60}\n")

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _team_of(self, player: Player) -> Team:
        """Return the team that *player* belongs to."""
        if player in self.team_a.players:
            return self.team_a
        return self.team_b

    @staticmethod
    def _fmt_cards(cards: List[Card]) -> str:
        return "  ".join(str(c) for c in cards)
