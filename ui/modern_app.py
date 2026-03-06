# ============================================================================
# SCOPONE - Modern Professional UI
# ============================================================================
# Interfaccia grafica moderna con CustomTkinter
# Design professionale, pulito e intuitivo
# ============================================================================

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import os
from typing import Optional
import threading
import time

from engine.game_engine import GameEngine
from engine.scoring import ScoringEngine
from config.constants import *
from ai.strategies import get_ai_strategy
from utils.image_loader import ImageLoader

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Modern color palette
ACCENT_COLOR = "#3498db"      # Bright blue
ACCENT_DARK = "#2980b9"       # Dark blue
SUCCESS_COLOR = "#2ecc71"      # Green
SUCCESS_DARK = "#27ae60"       # Dark green
WARNING_COLOR = "#f39c12"      # Orange
DANGER_COLOR = "#e74c3c"       # Red
BG_DARK = "#0f0f0f"            # Very dark background
CARD_BG = "#1a1a2e"            # Card background
TEXT_PRIMARY = "#ffffff"       # White text
TEXT_SECONDARY = "#b0b0b0"     # Gray text


class ModernScoponeApp(ctk.CTk):
    """
    Modern professional GUI for Scopone game using CustomTkinter.
    
    Features:
    - Clean, modern dark theme
    - Smooth animations
    - Professional card display
    - Intuitive controls
    - Responsive layout
    """
    
    def __init__(self):
        """Initialize the modern application window."""
        super().__init__()
        
        self.title("SCOPONE • Gioco di Carte Italiano")
        
        # Get screen dimensions
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        
        # Calculate default window size (85% of screen)
        default_width = int(self.screen_width * 0.85)
        default_height = int(self.screen_height * 0.85)
        
        # Set geometry with calculated dimensions
        self.geometry(f"{default_width}x{default_height}")
        
        # Make window resizable
        self.resizable(True, True)
        
        # Game state
        self.engine: Optional[GameEngine] = None
        self.num_players = DEFAULT_PLAYERS
        self.show_all_cards = True
        self.ai_difficulty = 'normal'
        self.is_fullscreen = False
        
        # UI state
        self.player_frames = {}
        self.image_loader = ImageLoader()
        self.image_cache = {}
        self.card_widgets = {}
        self.animation_jobs = []
        
        # Bind fullscreen toggle
        self.bind("<F11>", self._toggle_fullscreen)
        
        # Show initial screen
        self.show_setup_screen()
    
    def _toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes('-fullscreen', self.is_fullscreen)
        return "break"
    
    def animate_widget_in(self, widget, duration=500):
        """Animate widget fade-in effect."""
        widget.pack_propagate(False)
        start_alpha = 0.0
        end_alpha = 1.0
        steps = 20
        step_duration = duration // steps
        
        def animate_step(current_step):
            if current_step <= steps:
                alpha = start_alpha + (end_alpha - start_alpha) * (current_step / steps)
                # For CustomTkinter, we can't directly set opacity, but we can simulate with color transitions
                current_step += 1
                job = self.after(step_duration, animate_step, current_step)
                self.animation_jobs.append(job)
            else:
                widget.pack_propagate(True)
        
        animate_step(0)
    
    def animate_button_hover(self, button, enter=True):
        """Add hover animation effects to buttons."""
        if enter:
            button.configure(corner_radius=15)
        else:
            button.configure(corner_radius=10)
    
    def bounce_animation(self, widget, iterations=3):
        """Add bounce animation to widget."""
        original_y = widget.winfo_y()
        bounce_height = 15
        step_duration = 30
        
        def animate_bounce(step):
            if step < iterations * 2:
                # Oscillate up and down
                offset = int(bounce_height * abs(((step % (iterations * 2)) - iterations) / iterations))
                widget.place(y=original_y - offset)
                job = self.after(step_duration, animate_bounce, step + 1)
                self.animation_jobs.append(job)
            else:
                widget.place(y=original_y)
        
        animate_bounce(0)
    
    def scale_animation(self, widget, target_scale=1.05, duration=300):
        """Add scale animation to widget."""
        steps = 15
        step_duration = duration // steps
        
        def animate_scale(current_step):
            if current_step <= steps:
                # This is a placeholder - CustomTkinter doesn't support direct scaling
                # But we can use it as a base for future enhancements
                current_step += 1
                job = self.after(step_duration, animate_scale, current_step)
                self.animation_jobs.append(job)
        
        animate_scale(0)
    
    def _animate_turn_pulse(self, frame, color_pair, cycles=3):
        """Animate pulsing border effect for current player's turn."""
        color_main, color_hover = color_pair
        colors = [color_hover, color_main]
        color_index = [0]
        
        def pulse():
            if color_index[0] < len(colors) * cycles:
                current_color = colors[color_index[0] % len(colors)]
                frame.configure(border_color=current_color)
                color_index[0] += 1
                job = self.after(300, pulse)
                self.animation_jobs.append(job)
            else:
                frame.configure(border_color=color_hover)
        
        pulse()
    
    def show_setup_screen(self):
        """Display the modern game setup screen with enhanced graphics and proper distribution."""
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Main container with modern dark background
        main_container = ctk.CTkFrame(self, fg_color=BG_DARK)
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Configure grid for main container (3 rows: header, content, footer)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # ==================== HEADER ====================
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎴 SCOPONE",
            font=ctk.CTkFont(family="Segoe UI", size=72, weight="bold"),
            text_color="#00d4ff"
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="✨ Traditional Italian Card Game ✨",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#5dade2"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # ==================== CONTENT AREA ====================
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        
        # Settings panel
        settings_frame = ctk.CTkFrame(
            content_frame,
            fg_color=CARD_BG,
            corner_radius=25,
            border_width=3,
            border_color=ACCENT_COLOR
        )
        settings_frame.pack(fill="both", expand=True)
        
        # Inner frame for settings
        inner_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Configure sub-grid (2 columns + 1 row separator)
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(1, weight=1)
        inner_frame.grid_rowconfigure(1, weight=1)
        
        # ========== TOP SECTION: Beginner Mode ==========
        beginner_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        beginner_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        beginner_label = ctk.CTkLabel(
            beginner_frame,
            text="🎓 Modalità Principianti",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=(TEXT_PRIMARY, TEXT_PRIMARY)
        )
        beginner_label.pack(anchor="w", pady=(0, 10))
        
        self.beginner_var = ctk.BooleanVar(value=True)
        beginner_switch = ctk.CTkSwitch(
            beginner_frame,
            text="Mostra tutte le carte durante il gioco",
            variable=self.beginner_var,
            font=ctk.CTkFont(size=13, weight="bold"),
            progress_color=(SUCCESS_COLOR, SUCCESS_DARK),
            button_color=("#555555", "#444444"),
            button_hover_color=(ACCENT_COLOR, ACCENT_DARK),
            text_color=(TEXT_PRIMARY, TEXT_PRIMARY)
        )
        beginner_switch.pack(anchor="w")
        
        # ========== MIDDLE SECTION: Three Columns ==========
        
        # LEFT COLUMN: Difficulty
        left_col = ctk.CTkFrame(inner_frame, fg_color="transparent")
        left_col.grid(row=1, column=0, sticky="nsew", padx=(0, 15))
        
        diff_title = ctk.CTkLabel(
            left_col,
            text="⚔️  Difficoltà AI",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT_COLOR
        )
        diff_title.pack(anchor="w", pady=(0, 15))
        
        self.difficulty_var = ctk.StringVar(value="normal")
        
        difficulties = [
            ("🟢 Facile", "easy", "Per principianti"),
            ("🔵 Normale", "normal", "Equilibrato"),
            ("🟠 Esperto", "expert", "Difficile"),
            ("🔴 Adattivo", "adaptive", "Intelligente")
        ]
        
        for label, value, desc in difficulties:
            btn_frame = ctk.CTkFrame(left_col, fg_color="transparent")
            btn_frame.pack(anchor="w", pady=6, padx=0)
            
            btn = ctk.CTkRadioButton(
                btn_frame,
                text=label,
                variable=self.difficulty_var,
                value=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                radiobutton_width=18,
                radiobutton_height=18,
                text_color=(TEXT_PRIMARY, TEXT_PRIMARY),
                border_color=ACCENT_COLOR,
                hover_color=(ACCENT_COLOR, ACCENT_DARK)
            )
            btn.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                btn_frame,
                text=desc,
                font=ctk.CTkFont(size=10),
                text_color=(TEXT_SECONDARY, "#999999")
            )
            desc_label.pack(anchor="w", padx=(35, 0), pady=(2, 0))
        
        # CENTER COLUMN: Game Mode
        center_col = ctk.CTkFrame(inner_frame, fg_color="transparent")
        center_col.grid(row=1, column=1, sticky="nsew", padx=15)
        
        mode_title = ctk.CTkLabel(
            center_col,
            text="🎮 Modalità di Gioco",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT_COLOR
        )
        mode_title.pack(anchor="w", pady=(0, 15))
        
        self.player_var = ctk.IntVar(value=DEFAULT_PLAYERS)
        
        player_modes = [
            (2, "👥 Due Giocatori", "10 carte a testa\nDistribuzione sequenziale"),
            (4, "👥👥 Quattro (Squadre)", "4 carte in tavola\nPunteggio per coppia")
        ]
        
        for num_players, mode_name, mode_desc in player_modes:
            btn_frame = ctk.CTkFrame(center_col, fg_color="transparent")
            btn_frame.pack(anchor="w", pady=8, padx=0, fill="x")
            
            btn = ctk.CTkRadioButton(
                btn_frame,
                text=mode_name,
                variable=self.player_var,
                value=num_players,
                font=ctk.CTkFont(size=13, weight="bold"),
                radiobutton_width=18,
                radiobutton_height=18,
                text_color=(TEXT_PRIMARY, TEXT_PRIMARY),
                border_color=ACCENT_COLOR,
                hover_color=(ACCENT_COLOR, ACCENT_DARK)
            )
            btn.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                btn_frame,
                text=mode_desc,
                font=ctk.CTkFont(size=10),
                text_color=(TEXT_SECONDARY, "#999999"),
                justify="left"
            )
            desc_label.pack(anchor="w", padx=(35, 0), pady=(2, 0))
        
        # ==================== FOOTER ====================
        footer_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(10, 20))
        
        # Buttons
        buttons_row = ctk.CTkFrame(footer_frame, fg_color="transparent")
        buttons_row.pack(fill="x", pady=10)
        
        start_button = ctk.CTkButton(
            buttons_row,
            text="▶  INIZIA PARTITA",
            command=self.start_game,
            width=300,
            height=60,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color=(SUCCESS_COLOR, "#27ae60"),
            hover_color=(SUCCESS_DARK, "#1e8c52"),
            corner_radius=15,
            border_width=0
        )
        start_button.pack(side="left", padx=10)
        
        exit_button = ctk.CTkButton(
            buttons_row,
            text="🚪 Esci",
            command=self.quit,
            width=140,
            height=60,
            font=ctk.CTkFont(size=16),
            fg_color=("#2c2c2c", "#3c3c3c"),
            hover_color=("#1f1f1f", "#4c4c4c"),
            text_color=(TEXT_PRIMARY, TEXT_PRIMARY),
            corner_radius=15,
            border_width=1,
            border_color=("#555555", "#666666")
        )
        exit_button.pack(side="left", padx=5)
        
        fullscreen_button = ctk.CTkButton(
            buttons_row,
            text="⛶ Fullscreen",
            command=self._toggle_fullscreen,
            width=140,
            height=60,
            font=ctk.CTkFont(size=16),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_DARK,
            text_color=(TEXT_PRIMARY, TEXT_PRIMARY),
            corner_radius=15,
            border_width=0
        )
        fullscreen_button.pack(side="left", padx=5)
    
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
        """Setup the modern game interface."""
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color=BG_DARK)
        main_container.pack(fill="both", expand=True)
        
        # Top bar with controls - responsive height
        top_bar = ctk.CTkFrame(
            main_container,
            height=85,
            fg_color=("white", "gray20"),
            corner_radius=0
        )
        top_bar.pack(fill="x", padx=0, pady=0)
        # Don't use pack_propagate(False) to allow responsive sizing
        
        # Top bar content
        top_content = ctk.CTkFrame(top_bar, fg_color="transparent")
        top_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        # Left side: Status
        status_frame = ctk.CTkFrame(top_content, fg_color="transparent")
        status_frame.pack(side="left", fill="y")
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Caricamento...",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1f538d", "#3a7ebf")
        )
        self.status_label.pack(anchor="w")
        
        mode_text = "🟢 Modo Principianti" if self.show_all_cards else "🔴 Modo Normale"
        self.mode_label = ctk.CTkLabel(
            status_frame,
            text=mode_text,
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60")
        )
        self.mode_label.pack(anchor="w")
        
        # Right side: Controls
        controls_frame = ctk.CTkFrame(top_content, fg_color="transparent")
        controls_frame.pack(side="right", fill="y")
        
        button_config = {
            "height": 40,
            "corner_radius": 10,
            "font": ctk.CTkFont(size=13, weight="bold")
        }
        
        ctk.CTkButton(
            controls_frame,
            text="🔄 Nuova Partita",
            command=self.new_game,
            fg_color=("#27ae60", "#229954"),
            hover_color=("#229954", "#1e8449"),
            width=130,
            **button_config
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="👁 Mostra/Nascondi",
            command=self.toggle_cards,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#21618c"),
            width=150,
            **button_config
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="📊 Statistiche",
            command=self.show_statistics,
            fg_color=("#9b59b6", "#8e44ad"),
            hover_color=("#8e44ad", "#7d3c98"),
            width=120,
            **button_config
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="🏠 Menu",
            command=self.show_setup_screen,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            text_color=("gray20", "gray80"),
            width=90,
            **button_config
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="⛶ Fullscreen",
            command=self._toggle_fullscreen,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_DARK,
            width=110,
            **button_config
        ).pack(side="left", padx=5)
        
        # Game area
        game_container = ctk.CTkFrame(main_container, fg_color="transparent")
        game_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Calculate responsive dimensions
        window_width = self.winfo_width()
        if window_width < 1:
            window_width = 1600  # Default estimate
        log_width = int(window_width * 0.2)  # 20% of window width
        log_width = max(250, min(400, log_width))  # Clamp between 250-400
        
        # Left sidebar: Log
        log_sidebar = ctk.CTkFrame(
            game_container,
            width=log_width,
            fg_color=("white", "gray20"),
            corner_radius=15
        )
        log_sidebar.pack(side="left", fill="y", padx=(0, 15))
        log_sidebar.pack_propagate(False)
        
        log_title = ctk.CTkLabel(
            log_sidebar,
            text="📋 Log di Gioco",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        log_title.pack(padx=15, pady=(15, 8), anchor="w")
        
        self.log_widget = ctk.CTkTextbox(
            log_sidebar,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=("gray95", "gray15"),
            corner_radius=10,
            wrap="word"
        )
        self.log_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Center: Game board
        center_area = ctk.CTkFrame(game_container, fg_color="transparent")
        center_area.pack(side="left", fill="both", expand=True)
        
        # Players arrangement
        self.setup_player_displays(center_area)
        
        # Table in center
        self.table_frame = ctk.CTkFrame(
            center_area,
            fg_color=("white", "gray20"),
            corner_radius=20,
            border_width=3,
            border_color=ACCENT_COLOR
        )
        self.table_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.55, relheight=0.35)
        
        table_title = ctk.CTkLabel(
            self.table_frame,
            text="🎴 TAVOLO",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#3498db", "#5dade2")
        )
        table_title.pack(pady=(15, 5))
        
        self.table_cards_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        self.table_cards_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        # Initial display
        self.update_display()
        self.check_turn()
    
    def setup_player_displays(self, parent):
        """Setup modern player frame displays."""
        self.player_frames = {}
        
        colors = [
            ("#e74c3c", "#c0392b"),  # Red
            ("#3498db", "#2980b9"),  # Blue
            ("#2ecc71", "#27ae60"),  # Green
            ("#f39c12", "#e67e22"),  # Orange
            ("#9b59b6", "#8e44ad"),  # Purple
            ("#1abc9c", "#16a085"),  # Teal
        ]
        
        for i, player in enumerate(self.engine.players):
            color_main, color_hover = colors[i % len(colors)]
            
            player_frame = ctk.CTkFrame(
                parent,
                fg_color=("white", "gray20"),
                corner_radius=15,
                border_width=2,
                border_color=(color_main, color_hover)
            )
            
            # Position frames
            self._position_player_frame(player_frame, i)
            
            # Player header with team info for 4-player mode
            header = ctk.CTkFrame(player_frame, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=12)
            
            # Build player name with team info if applicable
            player_name = f"👤 {player.name}"
            if self.num_players == 4 and hasattr(player, 'team') and player.team is not None:
                team_label = "Squadra 1" if player.team == 0 else "Squadra 2"
                player_name += f" ({team_label})"
            
            name_label = ctk.CTkLabel(
                header,
                text=player_name,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=(color_main, color_hover),
                anchor="w"
            )
            name_label.pack(side="left")
            
            self.turn_indicator = ctk.CTkLabel(
                header,
                text="",
                font=ctk.CTkFont(size=18),
                text_color=("#f39c12", "#f1c40f")
            )
            self.turn_indicator.pack(side="right")
            
            # Stats row
            stats_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
            stats_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            hand_label = ctk.CTkLabel(
                stats_frame,
                text="Mano: 0",
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray70")
            )
            hand_label.pack(side="left", padx=(0, 15))
            
            captured_label = ctk.CTkLabel(
                stats_frame,
                text="Catturate: 0",
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray70")
            )
            captured_label.pack(side="left", padx=(0, 15))
            
            sweeps_label = ctk.CTkLabel(
                stats_frame,
                text="Scope: 0",
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray70")
            )
            sweeps_label.pack(side="left")
            
            # Hand display
            hand_display = ctk.CTkScrollableFrame(
                player_frame,
                fg_color=("gray95", "gray15"),
                corner_radius=10,
                orientation="horizontal",
                height=110
            )
            hand_display.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
            self.player_frames[player.id] = {
                'frame': player_frame,
                'header': header,
                'name_label': name_label,
                'turn_indicator': self.turn_indicator,
                'hand_label': hand_label,
                'captured_label': captured_label,
                'sweeps_label': sweeps_label,
                'hand_display': hand_display,
                'color': (color_main, color_hover)
            }
    
    def _position_player_frame(self, frame, idx):
        """
        Position player frame based on index and game mode.
        
        2-player mode: Bottom (player 0), Top (player 1)
        4-player mode (teams): Arranged with teams opposite
            - Player 0 (Team A): Bottom
            - Player 1 (Team B): Left
            - Player 2 (Team A): Top
            - Player 3 (Team B): Right
        """
        if self.num_players == 2:
            # 2-player simple layout
            if idx == 0:
                frame.pack(side="bottom", fill="x", pady=(15, 0))
            else:
                frame.pack(side="top", fill="x", pady=(0, 15))
        elif self.num_players == 4:
            # 4-player team layout (opposite seating)
            if idx == 0:
                # Team A player 1: Bottom
                frame.pack(side="bottom", fill="x", pady=(15, 0))
            elif idx == 1:
                # Team B player 1: Left
                frame.place(relx=0, rely=0.3, relwidth=0.18, relheight=0.4)
            elif idx == 2:
                # Team A player 2: Top
                frame.pack(side="top", fill="x", pady=(0, 15))
            else:
                # Team B player 2: Right
                frame.place(relx=0.82, rely=0.3, relwidth=0.18, relheight=0.4)
    
    def update_display(self):
        """Update all game display elements."""
        if not self.engine:
            return
        
        current_player = self.engine.get_current_player()
        
        # Update status
        self.status_label.configure(text=f"Turno di: {current_player.name}")
        
        # Update player displays
        for player in self.engine.players:
            if player.id in self.player_frames:
                self._update_player_display(player)
        
        # Update table
        self._update_table_display()
    
    def _update_player_display(self, player):
        """Update display for a single player."""
        frame_data = self.player_frames[player.id]
        current = (player == self.engine.get_current_player())
        
        # Update turn indicator with animation
        if current:
            frame_data['turn_indicator'].configure(text="⭐ TURNO ⭐")
            # Start pulsing animation for current player
            self._animate_turn_pulse(frame_data['frame'], frame_data['color'])
        else:
            frame_data['turn_indicator'].configure(text="")
        
        # Highlight current player frame
        color_main, color_hover = frame_data['color']
        border_color = color_hover if current else color_main
        frame_data['frame'].configure(
            border_color=border_color,
            border_width=3 if current else 2
        )
        
        # Update stats
        frame_data['hand_label'].configure(text=f"Mano: {len(player.hand)}")
        frame_data['captured_label'].configure(text=f"Catturate: {len(player.captured)}")
        frame_data['sweeps_label'].configure(text=f"Scope: {player.sweeps}")
        
        # Update hand display
        hand_display = frame_data['hand_display']
        for widget in hand_display.winfo_children():
            widget.destroy()
        
        # Show cards
        for card in player.hand:
            show_card = (player.is_human or self.show_all_cards)
            self._create_card_widget(hand_display, card, player, show_card, size="small")
    
    def _create_card_widget(self, parent, card, player, show_card=True, size="small"):
        """Create a modern card widget."""
        card_size = CARD_SIZE_HAND if size == "small" else CARD_SIZE_TABLE
        
        if show_card:
            # Try to load image
            img = self.image_loader.load_image(card[0], card[1], card_size)
            
            card_btn = ctk.CTkButton(
                parent,
                text="" if img else f"{card[0]}\n{SIMBOLI[card[1]]}",
                width=card_size[0] + 10,
                height=card_size[1] + 10,
                corner_radius=8,
                fg_color=("white", "gray25"),
                hover_color=("gray90", "gray30") if player.is_human else ("white", "gray25"),
                border_width=2,
                border_color=("gray70", "gray40"),
                font=ctk.CTkFont(size=18, weight="bold")
            )
            
            if img:
                cache_key = f"card_{card[0]}_{card[1]}"
                if cache_key not in self.image_cache:
                    self.image_cache[cache_key] = ctk.CTkImage(
                        light_image=img,
                        dark_image=img,
                        size=card_size
                    )
                card_btn.configure(image=self.image_cache[cache_key], text="")
            
            if player.is_human:
                card_btn.configure(
                    command=lambda c=card: self.play_card(c),
                    cursor="hand2"
                )
            else:
                card_btn.configure(state="disabled")
        else:
            # Hidden card (back)
            card_btn = ctk.CTkButton(
                parent,
                text="?",
                width=card_size[0] + 10,
                height=card_size[1] + 10,
                corner_radius=8,
                fg_color=("#8b0000", "#660000"),
                hover_color=("#8b0000", "#660000"),
                border_width=2,
                border_color=("#660000", "#440000"),
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=("white", "white"),
                state="disabled"
            )
        
        card_btn.pack(side="left", padx=5, pady=5)
    
    def _update_table_display(self):
        """Update the table card display."""
        for widget in self.table_cards_frame.winfo_children():
            widget.destroy()
        
        if self.engine.table:
            cards_container = ctk.CTkFrame(self.table_cards_frame, fg_color="transparent")
            cards_container.pack(expand=True)
            
            for card in self.engine.table:
                img = self.image_loader.load_image(card[0], card[1], CARD_SIZE_TABLE)
                
                card_frame = ctk.CTkFrame(
                    cards_container,
                    fg_color=("white", "gray25"),
                    corner_radius=10,
                    border_width=2,
                    border_color=("gray70", "gray40")
                )
                card_frame.pack(side="left", padx=10)
                
                if img:
                    cache_key = f"table_{card[0]}_{card[1]}"
                    if cache_key not in self.image_cache:
                        self.image_cache[cache_key] = ctk.CTkImage(
                            light_image=img,
                            dark_image=img,
                            size=CARD_SIZE_TABLE
                        )
                    
                    label = ctk.CTkLabel(
                        card_frame,
                        image=self.image_cache[cache_key],
                        text=""
                    )
                    label.pack(padx=5, pady=5)
                else:
                    label = ctk.CTkLabel(
                        card_frame,
                        text=f"{card[0]}\n{SIMBOLI[card[1]]}",
                        font=ctk.CTkFont(size=28, weight="bold"),
                        width=CARD_SIZE_TABLE[0],
                        height=CARD_SIZE_TABLE[1]
                    )
                    label.pack(padx=5, pady=5)
        else:
            empty_label = ctk.CTkLabel(
                self.table_cards_frame,
                text="Tavolo Vuoto",
                font=ctk.CTkFont(size=24),
                text_color=("gray60", "gray50")
            )
            empty_label.pack(expand=True)
    
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
        
        self.log(f"✓ Giocata {card[0]}{SIMBOLI[card[1]]}")
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
        mode_text = "🟢 Modo Principianti" if self.show_all_cards else "🔴 Modo Normale"
        self.mode_label.configure(text=mode_text)
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
            self.log("🔄 === NUOVA PARTITA INIZIATA ===")
    
    def show_final_results(self):
        """Display final game results in modern style."""
        if not self.engine.final_scores:
            return
        
        self.log("\n" + "="*50)
        self.log("🏁 PARTITA TERMINATA!")
        
        # Determine if team mode or individual mode
        is_team_mode = (self.num_players == 4 and 
                        any('team' in str(score).lower() for score in self.engine.final_scores))
        
        # Create modern results window
        results_window = ctk.CTkToplevel(self)
        results_window.title("Risultati Finali")
        results_window.geometry("700x700")
        results_window.transient(self)
        results_window.grab_set()
        
        # Header
        header = ctk.CTkFrame(results_window, fg_color=("#3498db", "#2980b9"), corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        
        title_text = "🏆 CLASSIFICA FINALE (Squadre)" if is_team_mode else "🏆 CLASSIFICA FINALE"
        ctk.CTkLabel(
            header,
            text=title_text,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        ).pack(pady=25)
        
        # Scrollable results
        scroll_frame = ctk.CTkScrollableFrame(results_window, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        medals = ["🥇", "🥈", "🥉"]
        
        # Color palette for ranking positions
        rank_colors = [
            ("#FFD700", "#FFA500"),  # Gold (1st)
            ("#C0C0C0", "#A9A9A9"),  # Silver (2nd)
            ("#CD7F32", "#8B4513"),  # Bronze (3rd)
        ]
        
        for i, score in enumerate(self.engine.final_scores):
            medal = medals[i] if i < 3 else f"{i+1}°"
            
            # Get color for this position
            if i < 3:
                border_color = rank_colors[i][0]
                card_bg = rank_colors[i][1]
            else:
                border_color = "gray70"
                card_bg = "gray40"
            
            result_card = ctk.CTkFrame(
                scroll_frame,
                fg_color=("white", "gray20"),
                corner_radius=15,
                border_width=3,
                border_color=(border_color, card_bg)
            )
            result_card.pack(fill="x", pady=10)
            
            # Header with name and points
            header_frame = ctk.CTkFrame(result_card, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=15)
            
            ctk.CTkLabel(
                header_frame,
                text=f"{medal} {score['player']}",
                font=ctk.CTkFont(size=24, weight="bold"),
                anchor="w",
                text_color=(border_color if i < 3 else "white", border_color if i < 3 else "white")
            ).pack(side="left")
            
            ctk.CTkLabel(
                header_frame,
                text=f"{score['total']} punti",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("#2ecc71", "#27ae60"),
                anchor="e"
            ).pack(side="right")
            
            # Details
            details = ctk.CTkFrame(result_card, fg_color=("gray95", "gray15"), corner_radius=10)
            details.pack(fill="x", padx=20, pady=(0, 15))
            
            # Build details text based on game mode
            if is_team_mode:
                # Team mode: show team members and combined stats
                members_text = ", ".join(score.get('members', []))
                stats_text = f"Giocatori: {members_text}\nCarte: {score['captured_cards']} • Denari: {score['coins']} • Scope: {score['sweeps']}"
            else:
                # Individual mode
                stats_text = f"Carte: {score['captured_cards']} • Denari: {score['coins']} • Scope: {score['sweeps']}"
            
            ctk.CTkLabel(
                details,
                text=stats_text,
                font=ctk.CTkFont(size=13),
                text_color=("gray40", "gray70")
            ).pack(pady=(10, 5))
            
            # Points breakdown
            points_dict = score.get('points', {})
            points_breakdown = []
            
            if points_dict.get('cards', 0) > 0:
                points_breakdown.append(f"📇 Carte: +{points_dict['cards']}")
            if points_dict.get('coins', 0) > 0:
                points_breakdown.append(f"💰 Denari: +{points_dict['coins']}")
            if points_dict.get('settebello', 0) > 0:
                points_breakdown.append(f"✨ Settebello: +{points_dict['settebello']}")
            if points_dict.get('primiera', 0) > 0:
                primiera_value = score.get('primiera_value', 0)
                points_breakdown.append(f"👑 Primiera ({primiera_value}): +{points_dict['primiera']}")
            if points_dict.get('sweeps', 0) > 0:
                points_breakdown.append(f"🎯 Scope: +{points_dict['sweeps']}")
            
            if points_breakdown:
                breakdown_text = " • ".join(points_breakdown)
                ctk.CTkLabel(
                    details,
                    text=breakdown_text,
                    font=ctk.CTkFont(size=11),
                    text_color=("#3498db", "#5dade2")
                ).pack(pady=(0, 10))
        
        # Close button
        ctk.CTkButton(
            results_window,
            text="Chiudi",
            command=results_window.destroy,
            width=200,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            corner_radius=10
        ).pack(pady=(0, 20))
    
    def show_statistics(self):
        """Show game statistics."""
        if not self.engine:
            return
        
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Statistiche")
        stats_window.geometry("500x400")
        stats_window.transient(self)
        
        ctk.CTkLabel(
            stats_window,
            text="📊 Statistiche di Gioco",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=30)
        
        info_frame = ctk.CTkFrame(stats_window, fg_color=("white", "gray20"), corner_radius=15)
        info_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        stats_text = f"""
        Partite giocate: {len(self.engine.game_history)}
        Giocatori: {self.engine.num_players}
        Mosse effettuate: {len(self.engine.moves_played)}
        Difficoltà AI: {self.ai_difficulty.title()}
        """
        
        ctk.CTkLabel(
            info_frame,
            text=stats_text,
            font=ctk.CTkFont(size=16),
            justify="left"
        ).pack(pady=40)
        
        ctk.CTkButton(
            stats_window,
            text="Chiudi",
            command=stats_window.destroy,
            width=150,
            height=40,
            corner_radius=10
        ).pack(pady=(0, 20))
    
    def log(self, msg):
        """Add a message to the game log."""
        if self.log_widget:
            self.log_widget.insert("end", f"{msg}\n")
            self.log_widget.see("end")


def main():
    """Main entry point for the modern application."""
    try:
        app = ModernScoponeApp()
        app.mainloop()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nInstalla le dipendenze:")
        print("  pip install customtkinter pillow")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
