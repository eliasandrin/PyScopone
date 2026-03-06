# ============================================================================
# SCOPONE - Main Application GUI
# ============================================================================
# Interfaccia grafica principale dell'applicazione
# ============================================================================

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

from engine.game_engine import GameEngine
from engine.scoring import ScoringEngine
from config.constants import *
from ai.strategies import get_ai_strategy
from utils.image_loader import ImageLoader


class ScoponeApp(tk.Tk):
    """
    Main GUI application for Scopone game.
    
    Handles:
    - Game initialization and setup
    - Player management and AI control
    - Game display and updates
    - Card interaction and game flow
    - Game history and statistics
    """
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        
        self.title("SCOPONE - Gioco di Carte Italiano")
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.configure(bg=COLOR_BG_PRIMARY)
        
        # Game state
        self.engine = None
        self.num_players = DEFAULT_PLAYERS
        self.show_all_cards = True
        self.ai_difficulty = 'normal'
        
        # UI state
        self.player_frames = {}
        self.image_loader = ImageLoader()
        self.image_cache = {}
        self.log_widget = None
        
        # Show initial screen
        self.show_setup_screen()
    
    def show_setup_screen(self):
        """Display the game setup/menu screen."""
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        setup_frame = tk.Frame(self, bg=COLOR_BG_PRIMARY)
        setup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(setup_frame, text="SCOPONE", fg=COLOR_TEXT_GOLD, bg=COLOR_BG_PRIMARY,
                font=FONT_TITLE).pack(pady=50)
        
        tk.Label(setup_frame, text="Gioco di Carte Italiano", fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_BG_PRIMARY, font=FONT_SUBTITLE).pack(pady=10)
        
        # Beginner mode toggle
        beginner_frame = tk.Frame(setup_frame, bg=COLOR_BG_PRIMARY)
        beginner_frame.pack(pady=20)
        
        self.beginner_var = tk.BooleanVar(value=True)
        tk.Checkbutton(beginner_frame, text="MODO PER PRINCIPIANTI (Mostra tutte le carte)",
                      variable=self.beginner_var, bg=COLOR_BG_PRIMARY, fg=COLOR_TEXT_PRIMARY,
                      selectcolor=COLOR_BG_PRIMARY, font=FONT_BODY).pack()
        
        # AI difficulty selection
        difficulty_frame = tk.LabelFrame(setup_frame, text=" DIFFICOLTÀ AI ",
                                        fg=COLOR_ACCENT_BLUE, bg=COLOR_BG_PRIMARY,
                                        font=FONT_SUBHEADING)
        difficulty_frame.pack(pady=20)
        
        self.difficulty_var = tk.StringVar(value='normal')
        
        for difficulty in [('Facile', 'easy'), ('Normale', 'normal'), 
                          ('Esperto', 'expert'), ('Adattivo', 'adaptive')]:
            tk.Radiobutton(difficulty_frame, text=difficulty[0], variable=self.difficulty_var,
                          value=difficulty[1], bg=COLOR_BG_PRIMARY, fg=COLOR_TEXT_PRIMARY,
                          selectcolor=COLOR_BG_PRIMARY, font=FONT_BODY).pack(anchor=tk.W, padx=20)
        
        # Player count selection
        tk.Label(setup_frame, text="NUMERO DI GIOCATORI (2-6):", fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_BG_PRIMARY, font=FONT_HEADING).pack(pady=20)
        
        player_frame = tk.Frame(setup_frame, bg=COLOR_BG_PRIMARY)
        player_frame.pack(pady=10)
        
        self.player_var = tk.IntVar(value=DEFAULT_PLAYERS)
        
        for i in range(MIN_PLAYERS, MAX_PLAYERS + 1):
            tk.Radiobutton(player_frame, text=str(i), variable=self.player_var, value=i,
                          bg=COLOR_BG_PRIMARY, fg=COLOR_TEXT_PRIMARY, selectcolor=COLOR_BG_PRIMARY,
                          font=FONT_BODY).pack(side=tk.LEFT, padx=15)
        
        # Control buttons
        button_frame = tk.Frame(setup_frame, bg=COLOR_BG_PRIMARY)
        button_frame.pack(pady=40)
        
        tk.Button(button_frame, text="INIZIA PARTITA", bg=COLOR_ACCENT_GREEN, fg=COLOR_TEXT_PRIMARY,
                 font=FONT_HEADING, command=self.start_game, width=25, height=2).pack()
        
        tk.Button(button_frame, text="ESCI", bg=COLOR_ACCENT_RED, fg=COLOR_TEXT_PRIMARY,
                 font=FONT_BODY, command=self.quit, width=25).pack(pady=10)
    
    def start_game(self):
        """Initialize and start a new game."""
        self.num_players = self.player_var.get()
        self.ai_difficulty = self.difficulty_var.get()
        self.show_all_cards = self.beginner_var.get()
        
        # Create game engine
        player_names = [DEFAULT_PLAYER_NAMES[i] if i > 0 else "Tu" 
                       for i in range(self.num_players)]
        
        self.engine = GameEngine(self.num_players, player_names)
        self.engine.reset()
        self.engine.deal_cards()
        
        # Setup game UI
        self.setup_game_ui()
    
    def setup_game_ui(self):
        """Setup the main game interface."""
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header frame
        header = tk.Frame(self, bg=COLOR_BG_SECONDARY, height=100)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        # Game mode indicator
        mode_text = "MODO PER PRINCIPIANTI" if self.show_all_cards else "MODO NORMALE"
        mode_color = COLOR_ACCENT_GREEN if self.show_all_cards else COLOR_ACCENT_RED
        tk.Label(header, text=mode_text, fg=mode_color, bg=COLOR_BG_SECONDARY,
                font=FONT_BODY).pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(header, text="Caricamento...", fg=COLOR_TEXT_HIGHLIGHT,
                                    bg=COLOR_BG_SECONDARY, font=FONT_HEADING)
        self.status_label.pack(pady=5)
        
        # Controls
        control_frame = tk.Frame(header, bg=COLOR_BG_SECONDARY)
        control_frame.pack(pady=5)
        
        tk.Button(control_frame, text="NUOVA PARTITA", bg=COLOR_ACCENT_GREEN,
                 fg=COLOR_TEXT_PRIMARY, font=FONT_SMALL, command=self.new_game).pack(
                 side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="MOSTRA/NASCONDI", bg=COLOR_ACCENT_BLUE,
                 fg=COLOR_TEXT_PRIMARY, font=FONT_SMALL,
                 command=self.toggle_cards).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="STATISTICHE", bg=COLOR_ACCENT_PURPLE,
                 fg=COLOR_TEXT_PRIMARY, font=FONT_SMALL,
                 command=self.show_statistics).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="MENU", bg=COLOR_ACCENT_ORANGE, fg=COLOR_TEXT_PRIMARY,
                 font=FONT_SMALL, command=self.show_setup_screen).pack(side=tk.LEFT, padx=10)
        
        # Main game area
        main = tk.Frame(self, bg=COLOR_BG_PRIMARY)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Setup player displays
        self.setup_player_displays(main)
        
        # Table display
        table_container = tk.Frame(main, bg=COLOR_BG_PRIMARY)
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.table_frame = tk.LabelFrame(table_container, text=" TAVOLO ", fg=COLOR_ACCENT_BLUE,
                                        bg=COLOR_BG_TERTIARY, font=FONT_SUBHEADING)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log box
        log_container = tk.Frame(main, bg=COLOR_BG_PRIMARY)
        log_container.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(log_container, text="LOG GIOCO", fg=COLOR_ACCENT_GREEN, bg=COLOR_BG_PRIMARY,
                font=FONT_BODY).pack()
        
        self.log_widget = tk.Text(log_container, width=40, height=30, bg=COLOR_BG_TERTIARY,
                                 fg=COLOR_TEXT_SECONDARY, font=FONT_MONOSPACE)
        self.log_widget.pack(fill=tk.BOTH, expand=True)
        
        # Initial display
        self.update_display()
        self.check_turn()
    
    def setup_player_displays(self, parent):
        """Setup player frame displays around the table."""
        self.player_frames = {}
        colors = [COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, COLOR_ACCENT_GREEN,
                 COLOR_ACCENT_ORANGE, COLOR_ACCENT_PURPLE, COLOR_ACCENT_TEAL]
        
        for i, player in enumerate(self.engine.players):
            color = colors[i % len(colors)]
            
            player_frame = tk.LabelFrame(parent, text=f" {player.name} ", fg=color,
                                        bg=COLOR_BG_SECONDARY, font=FONT_SUBHEADING)
            
            # Position frames
            self._position_player_frame(player_frame, i)
            
            # Player info labels
            info_frame = tk.Frame(player_frame, bg=COLOR_BG_SECONDARY)
            info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            hand_label = tk.Label(info_frame, text="Mano: 0", fg=COLOR_TEXT_PRIMARY,
                                 bg=COLOR_BG_SECONDARY, font=FONT_SMALL)
            hand_label.pack(side=tk.LEFT, padx=10)
            
            # Hand display
            hand_display = tk.Frame(player_frame, bg=COLOR_BG_SECONDARY)
            hand_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Captured info
            captured_frame = tk.Frame(player_frame, bg=COLOR_BG_SECONDARY)
            captured_frame.pack(fill=tk.X, padx=5, pady=5)
            
            cards_label = tk.Label(captured_frame, text="Catturate: 0", fg=COLOR_TEXT_PRIMARY,
                                  bg=COLOR_BG_SECONDARY, font=FONT_SMALL)
            cards_label.pack(side=tk.LEFT, padx=5)
            
            sweeps_label = tk.Label(captured_frame, text="Scope: 0", fg=COLOR_TEXT_PRIMARY,
                                   bg=COLOR_BG_SECONDARY, font=FONT_SMALL)
            sweeps_label.pack(side=tk.LEFT, padx=5)
            
            self.player_frames[player.id] = {
                'frame': player_frame,
                'hand_display': hand_display,
                'hand_label': hand_label,
                'cards_label': cards_label,
                'sweeps_label': sweeps_label,
                'color': color
            }
    
    def _position_player_frame(self, frame, idx):
        """Position player frame based on player index."""
        if self.num_players == 2:
            frame.pack(side=tk.BOTTOM if idx == 0 else tk.TOP, fill=tk.X, padx=20, pady=10)
        elif self.num_players == 3:
            if idx == 0:
                frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
            elif idx == 1:
                frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)
            else:
                frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=20)
        else:
            if idx == 0:
                frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
            elif idx == 1:
                frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)
            elif idx == 2:
                frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
            else:
                frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=20)
    
    def update_display(self):
        """Update all game display elements."""
        if not self.engine:
            return
        
        current_player = self.engine.get_current_player()
        
        # Update status
        self.status_label.config(text=f"TURNO: {current_player.name}")
        
        # Update player displays
        for player in self.engine.players:
            if player.id in self.player_frames:
                self._update_player_display(player)
        
        # Update table display
        self._update_table_display()
    
    def _update_player_display(self, player):
        """Update display for a single player."""
        frame_data = self.player_frames[player.id]
        
        # Update labels
        frame_data['hand_label'].config(text=f"Mano: {len(player.hand)}")
        frame_data['cards_label'].config(text=f"Catturate: {len(player.captured)}")
        frame_data['sweeps_label'].config(text=f"Scope: {player.sweeps}")
        
        # Update hand display
        hand_display = frame_data['hand_display']
        for widget in hand_display.winfo_children():
            widget.destroy()
        
        # Show cards
        for card in player.hand:
            show_card = (player.is_human or self.show_all_cards)
            
            if show_card:
                self._display_card_widget(hand_display, card, player)
            else:
                card_frame = tk.Frame(hand_display, bg="darkred", relief=tk.SUNKEN, bd=2)
                card_frame.pack(side=tk.LEFT, padx=2, pady=2)
                tk.Label(card_frame, text="?", bg="darkred", fg="white",
                        font=("Arial", 10)).pack()
    
    def _display_card_widget(self, parent, card, player):
        """Display a card widget in the given parent."""
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=2)
        card_frame.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Try to load image
        img = self.image_loader.load_image(card[0], card[1], CARD_SIZE_HAND)
        
        if img:
            try:
                cache_key = f"card_{card[0]}_{card[1]}"
                if cache_key not in self.image_cache:
                    self.image_cache[cache_key] = ImageTk.PhotoImage(img)
                
                label = tk.Label(card_frame, image=self.image_cache[cache_key], bg="white")
                label.pack()
                
                if player.is_human:
                    label.bind("<Button-1>", lambda e: self.play_card(card))
                    label.config(cursor="hand2")
            except:
                self._display_card_text(card_frame, card, player)
        else:
            self._display_card_text(card_frame, card, player)
    
    def _display_card_text(self, parent, card, player):
        """Display card as text (fallback)."""
        label = tk.Label(parent, text=f"{card[0]}\\n{SIMBOLI[card[1]]}", bg="white",
                        fg="black", font=("Arial", 9), width=4, height=2)
        label.pack()
        
        if player.is_human:
            label.bind("<Button-1>", lambda e: self.play_card(card))
            label.config(cursor="hand2")
    
    def _update_table_display(self):
        """Update the table card display."""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        table_inner = tk.Frame(self.table_frame, bg=COLOR_BG_TERTIARY)
        table_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if self.engine.table:
            for card in self.engine.table:
                card_frame = tk.Frame(table_inner, bg="white", relief=tk.RAISED, bd=3)
                card_frame.pack(side=tk.LEFT, padx=8, pady=8)
                
                img = self.image_loader.load_image(card[0], card[1], CARD_SIZE_TABLE)
                
                if img:
                    try:
                        cache_key = f"table_{card[0]}_{card[1]}"
                        if cache_key not in self.image_cache:
                            self.image_cache[cache_key] = ImageTk.PhotoImage(img)
                        
                        tk.Label(card_frame, image=self.image_cache[cache_key],
                                bg="white").pack()
                    except:
                        tk.Label(card_frame, text=f"{card[0]}\\n{SIMBOLI[card[1]]}",
                                bg="white", fg="black", font=("Arial", 14, "bold"),
                                width=6, height=3).pack()
                else:
                    tk.Label(card_frame, text=f"{card[0]}\\n{SIMBOLI[card[1]]}", bg="white",
                            fg="black", font=("Arial", 14, "bold"), width=6, height=3).pack()
        else:
            tk.Label(table_inner, text="TAVOLO VUOTO", fg="gray", bg=COLOR_BG_TERTIARY,
                    font=FONT_HEADING).pack(expand=True)
    
    def play_card(self, card):
        """Handle human player card play."""
        if not self.engine or not self.engine.game_active:
            return
        
        current_player = self.engine.get_current_player()
        if not current_player.is_human:
            self.log("❌ Non è il tuo turno!")
            return
        
        if not self.engine.play_card(current_player.id, card):
            self.log("❌ Mossa non valida!")
            return
        
        self.log(f"✓ Gioacata {card[0]}{SIMBOLI[card[1]]}")
        self.engine.next_player()
        self.update_display()
        self.check_turn()
    
    def check_turn(self):
        """Check if it's AI's turn and execute AI move."""
        if not self.engine or not self.engine.game_active:
            if self.engine and not self.engine.game_active:
                self.show_final_results()
            return
        
        current_player = self.engine.get_current_player()
        
        if current_player.is_ai and current_player.hand:
            self.after(AI_THINKING_DELAY, self.ai_turn)
    
    def ai_turn(self):
        """Execute AI player's turn."""
        if not self.engine or not self.engine.game_active:
            return
        
        current_player = self.engine.get_current_player()
        if not current_player.is_ai or not current_player.hand:
            return
        
        self.log(f"🤖 {current_player.name} sta pensando...")
        self.update()
        
        # Get AI strategy
        ai_strategy = get_ai_strategy(self.ai_difficulty)
        card_to_play = ai_strategy.choose_card(
            current_player.hand, 
            self.engine.table,
            seen_cards=self.engine.seen_cards
        )
        
        if card_to_play:
            self.engine.play_card(current_player.id, card_to_play)
            self.log(f"🤖 {current_player.name} gioca {card_to_play[0]}{SIMBOLI[card_to_play[1]]}")
            self.log(f"   Motivo AI: {ai_strategy.get_last_decision_reason()}")
        
        self.engine.next_player()
        self.update_display()
        self.check_turn()
    
    def toggle_cards(self):
        """Toggle display mode for cards."""
        self.show_all_cards = not self.show_all_cards
        self.update_display()
    
    def new_game(self):
        """Start a new game with same settings."""
        if self.engine:
            player_names = [p.name for p in self.engine.players]
            self.engine = GameEngine(self.num_players, player_names)
            self.engine.reset()
            self.engine.deal_cards()
            self.update_display()
            self.check_turn()
            self.log("=== NUOVA PARTITA INIZIATA ===")
    
    def show_final_results(self):
        """Display final game results."""
        if not self.engine.final_scores:
            return
        
        self.log("\\n" + "="*50)
        self.log("🏁 PARTITA TERMINATA!")
        self.log("="*50)
        
        result_window = tk.Toplevel(self)
        result_window.title("RISULTATI FINALI")
        result_window.geometry("600x500")
        result_window.configure(bg=COLOR_BG_PRIMARY)
        
        tk.Label(result_window, text="🏆 CLASSIFICA FINALE", fg=COLOR_TEXT_GOLD,
                bg=COLOR_BG_PRIMARY, font=FONT_HEADING).pack(pady=20)
        
        for i, score in enumerate(self.engine.final_scores):
            medals = ["🥇", "🥈", "🥉"]
            medal = medals[i] if i < 3 else f"{i+1}."
            
            frame = tk.Frame(result_window, bg=COLOR_BG_SECONDARY, relief=tk.RAISED, bd=2)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(frame, text=f"{medal} {score['player']} - {score['total']} punti",
                    fg=COLOR_TEXT_PRIMARY, bg=COLOR_BG_SECONDARY,
                    font=FONT_BODY).pack(anchor="w", padx=10, pady=5)
    
    def show_statistics(self):
        """Show game statistics."""
        if not self.engine:
            messagebox.showinfo("Statistiche", "Nessuna partita in corso")
            return
        
        msg = f"Partite: {len(self.engine.game_history)}\\n"
        if self.engine.final_scores:
            msg += f"Ultima: {self.engine.num_players} giocatori"
        
        messagebox.showinfo("Statistiche", msg)
    
    def log(self, msg):
        """Add a message to the game log."""
        if self.log_widget:
            self.log_widget.insert(tk.END, f"  {msg}\\n")
            self.log_widget.see(tk.END)


def main():
    """Main entry point for the application."""
    try:
        app = ScoponeApp()
        app.mainloop()
    except ImportError as e:
        print(f"Errore di importazione: {e}")
        print("Installa: pip install pillow")
    except Exception as e:
        print(f"Errore: {e}")
        raise


if __name__ == "__main__":
    main()
