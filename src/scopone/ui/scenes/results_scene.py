import pygame

from scopone.config.game import DEFAULT_PLAYER_NAMES, MODE_QUICK, MODE_TOURNAMENT, TARGET_SCORE_TOURNAMENT
from scopone.config.ui import TEXT_COLOR, TEXT_DIM_COLOR
from scopone.ui.backgrounds import draw_prismatic_background
from scopone.ui.scene_manager import Scene


TEAM_COLORS = {
    0: (117, 185, 255),
    1: (255, 176, 96),
}

WINNER_COLOR = (246, 216, 112)
TIE_COLOR = (144, 231, 184)


class ResultsScene(Scene):
    """Shows the final scores in a text-driven two-column layout."""

    def __init__(self, app, final_scores, settings, log_messages):
        super().__init__(app)
        self.final_scores = list(final_scores)
        self.settings = dict(settings)
        self.settings.setdefault("game_mode", MODE_QUICK)
        self.log_messages = list(log_messages)
        self.buttons = {}
        self.audio_button_rect = pygame.Rect(0, 0, 0, 0)

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.show_setup()
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self.audio_button_rect.collidepoint(event.pos):
            self.app.toggle_mute()
            return

        for action, rect in self.buttons.items():
            if not rect.collidepoint(event.pos):
                continue
            if action == "play_again":
                self.app.start_match(
                    self.settings["num_players"],
                    self.settings["difficulty"],
                    self.settings["show_all_cards"],
                    self.settings.get("game_mode", MODE_QUICK),
                )
            elif action == "menu":
                self.app.show_setup()
            elif action == "quit":
                self.app.request_quit()
            return

    def render(self, renderer) -> None:
        width, height = renderer.surface.get_size()
        mouse_pos = pygame.mouse.get_pos()
        layout = self._calculate_layout(width, height)
        self.audio_button_rect = layout["audio_button"]
        columns = self._build_columns()

        draw_prismatic_background(renderer.surface, variant="game")

        # Dim the shared background so the final comparison stays readable
        # without reintroducing rigid boxed containers.
        dimmer = pygame.Surface((width, height), pygame.SRCALPHA)
        dimmer.fill((4, 10, 20, 150))
        renderer.surface.blit(dimmer, (0, 0))

        renderer.draw_text(
            self._build_title(),
            layout["title_center"],
            size=layout["title_size"],
            color=TEXT_COLOR,
            bold=True,
            align="center",
            font_role="title",
        )
        renderer.draw_text(
            self._build_subtitle(),
            layout["subtitle_center"],
            size=layout["subtitle_size"],
            color=TEXT_DIM_COLOR,
            align="center",
        )

        left_metrics = self._draw_column(renderer, columns[0], layout["left_center_x"], layout["columns_top"], layout)
        right_metrics = self._draw_column(renderer, columns[1], layout["right_center_x"], layout["columns_top"], layout)
        self._draw_winner(renderer, columns, left_metrics, right_metrics, layout)
        self._draw_actions(renderer, layout, mouse_pos)
        renderer.draw_audio_toggle(
            layout["audio_button"],
            muted=self.app.is_muted,
            hovered=layout["audio_button"].collidepoint(mouse_pos),
        )

    def _build_subtitle(self) -> str:
        difficulty_labels = {
            "divertimento": "Divertimento",
            "normale": "Normale",
            "esperto": "Esperto",
        }
        mode_label = "Partita Rapida" if self.settings.get("game_mode") == MODE_QUICK else "Torneo a {0} punti".format(TARGET_SCORE_TOURNAMENT)
        match_type = "Partita a {0} giocatori".format(self.settings["num_players"])
        difficulty = "Difficolta: {0}".format(
            difficulty_labels.get(self.settings["difficulty"], self.settings["difficulty"])
        )
        visibility = "Carte IA: {0}".format("Visibili" if self.settings["show_all_cards"] else "Nascoste")
        return "{0} | {1} | {2} | {3}".format(match_type, mode_label, difficulty, visibility)

    def _build_title(self) -> str:
        if self.settings.get("game_mode") == MODE_TOURNAMENT:
            return "HA VINTO IL TORNEO A 21 PUNTI!"
        return "RISULTATI PARTITA"

    def _build_columns(self):
        if self.settings["num_players"] == 4 and all("team" in score for score in self.final_scores):
            score_lookup = {score["team"]: score for score in self.final_scores}
            return [
                self._build_team_column(0, score_lookup.get(0, {})),
                self._build_team_column(1, score_lookup.get(1, {})),
            ]

        expected_names = ["Tu", DEFAULT_PLAYER_NAMES[1]]
        score_lookup = {score.get("player"): score for score in self.final_scores}
        ordered_scores = []
        used_scores = set()
        for expected_name in expected_names:
            score = score_lookup.get(expected_name)
            if score is not None:
                ordered_scores.append(score)
                used_scores.add(id(score))

        for score in self.final_scores:
            if id(score) not in used_scores and len(ordered_scores) < 2:
                ordered_scores.append(score)

        while len(ordered_scores) < 2:
            ordered_scores.append({})

        return [
            self._build_player_column(0, ordered_scores[0], "Tu"),
            self._build_player_column(1, ordered_scores[1], DEFAULT_PLAYER_NAMES[1]),
        ]

    def _build_team_column(self, team_id: int, score: dict):
        total_label = "Punti Torneo" if self.settings.get("game_mode") == MODE_TOURNAMENT else "Punti Totali"
        members = score.get("members") or []
        return {
            "team_id": team_id,
            "team_name": "Squadra {0}".format(team_id + 1),
            "members": ", ".join(members) if members else "Nessun giocatore",
            "color": TEAM_COLORS[team_id],
            "stats": [
                ("Carte", score.get("captured_cards", 0)),
                ("Denari", score.get("coins", 0)),
                ("Settebello", "Si" if score.get("has_settebello") else "No"),
                ("Primiera", score.get("primiera_value", 0)),
                ("Scope", score.get("sweeps", 0)),
                (total_label, score.get("total", 0)),
            ],
            "total": score.get("total", 0),
        }

    def _build_player_column(self, team_id: int, score: dict, fallback_name: str):
        total_label = "Punti Torneo" if self.settings.get("game_mode") == MODE_TOURNAMENT else "Punti Totali"
        player_name = score.get("player", fallback_name)
        return {
            "team_id": team_id,
            "team_name": "Squadra {0}".format(team_id + 1),
            "members": player_name,
            "color": TEAM_COLORS[team_id],
            "stats": [
                ("Carte", score.get("captured_cards", 0)),
                ("Denari", score.get("coins", 0)),
                ("Settebello", "Si" if score.get("has_settebello") else "No"),
                ("Primiera", score.get("primiera_value", 0)),
                ("Scope", score.get("sweeps", 0)),
                (total_label, score.get("total", 0)),
            ],
            "total": score.get("total", 0),
        }

    def _draw_column(self, renderer, column: dict, center_x: int, top_y: int, layout: dict) -> None:
        renderer.draw_text(
            column["team_name"],
            (center_x, top_y),
            size=layout["team_name_size"],
            color=column["color"],
            bold=True,
            align="midtop",
        )
        renderer.draw_text(
            column["members"],
            (center_x, top_y + layout["members_offset"]),
            size=layout["members_size"],
            color=TEXT_DIM_COLOR,
            align="midtop",
        )

        stats_y = top_y + layout["stats_start_offset"]
        total_rect = None
        for label, value in column["stats"]:
            is_total = label in ("Punti Totali", "Punti Torneo")
            row_rect = renderer.draw_text(
                "{0}: {1}".format(label, value),
                (center_x, stats_y),
                size=layout["total_stat_size"] if is_total else layout["stat_size"],
                color=TEXT_COLOR if is_total else TEXT_DIM_COLOR,
                bold=is_total,
                align="midtop",
            )
            if is_total:
                total_rect = row_rect
            stats_y += layout["stat_gap"]

        return {
            "total_rect": total_rect,
        }

    def _draw_winner(self, renderer, columns, left_metrics: dict, right_metrics: dict, layout: dict) -> None:
        left_total = columns[0]["total"]
        right_total = columns[1]["total"]
        left_total_rect = left_metrics.get("total_rect")
        right_total_rect = right_metrics.get("total_rect")
        fallback_y = layout["columns_top"] + layout["stats_start_offset"] + ((len(columns[0]["stats"]) + 1) * layout["stat_gap"])

        if left_total == right_total:
            renderer.draw_text(
                "PAREGGIO",
                (layout["screen_center_x"], max(
                    left_total_rect.bottom if left_total_rect is not None else fallback_y,
                    right_total_rect.bottom if right_total_rect is not None else fallback_y,
                ) + layout["winner_offset"]),
                size=layout["winner_size"],
                color=TIE_COLOR,
                bold=True,
                align="center",
                font_role="title",
            )
            return

        winner_x = layout["left_center_x"] if left_total > right_total else layout["right_center_x"]
        winner_total_rect = left_total_rect if left_total > right_total else right_total_rect
        winner_y = (winner_total_rect.bottom if winner_total_rect is not None else fallback_y) + layout["winner_offset"]
        renderer.draw_text(
            "VINCITORE",
            (winner_x, winner_y),
            size=layout["winner_size"],
            color=WINNER_COLOR,
            bold=True,
            align="center",
            font_role="title",
        )

    def _draw_actions(self, renderer, layout: dict, mouse_pos) -> None:
        self.buttons = {}
        button_specs = [
            ("play_again", "Gioca ancora", "success", layout["buttons"][0]),
            ("menu", "Menu", "neutral", layout["buttons"][1]),
            ("quit", "Esci", "danger", layout["buttons"][2]),
        ]

        for action, label, tone, rect in button_specs:
            self.buttons[action] = renderer.draw_button(
                label,
                rect,
                hovered=rect.collidepoint(mouse_pos),
                tone=tone,
                font_size=layout["button_font_size"],
            )

    def _calculate_layout(self, width: int, height: int):
        title_size = self._clamp(int(width * 0.05), 54, 76)
        subtitle_size = self._clamp(int(width * 0.0135), 18, 22)
        team_name_size = self._clamp(int(width * 0.025), 30, 40)
        members_size = self._clamp(int(width * 0.0135), 17, 21)
        stat_size = self._clamp(int(width * 0.018), 23, 31)
        total_stat_size = self._clamp(int(width * 0.021), 27, 35)
        winner_size = self._clamp(int(width * 0.03), 34, 46)
        button_font_size = self._clamp(int(width * 0.0155), 19, 25)

        button_width = self._clamp(int(width * 0.18), 180, 260)
        button_height = self._clamp(int(height * 0.075), 52, 68)
        button_gap = self._clamp(int(width * 0.02), 18, 30)
        total_buttons_width = (button_width * 3) + (button_gap * 2)
        buttons_left = (width - total_buttons_width) // 2
        buttons_y = height - 100 - (button_height // 2)

        return {
            "screen_center_x": width // 2,
            "left_center_x": width // 4,
            "right_center_x": (width * 3) // 4,
            "title_center": (width // 2, 56),
            "subtitle_center": (width // 2, 120),
            "title_size": title_size,
            "subtitle_size": subtitle_size,
            "columns_top": self._clamp(int(height * 0.22), 178, 232),
            "members_offset": self._clamp(int(height * 0.05), 34, 44),
            "stats_start_offset": self._clamp(int(height * 0.12), 92, 112),
            "stat_gap": self._clamp(int(height * 0.062), 42, 54),
            "winner_offset": self._clamp(int(height * 0.03), 22, 32),
            "team_name_size": team_name_size,
            "members_size": members_size,
            "stat_size": stat_size,
            "total_stat_size": total_stat_size,
            "winner_size": winner_size,
            "button_font_size": button_font_size,
            "audio_button": pygame.Rect(width - 54, height - 54, 36, 36),
            "buttons": [
                pygame.Rect(buttons_left, buttons_y, button_width, button_height),
                pygame.Rect(buttons_left + button_width + button_gap, buttons_y, button_width, button_height),
                pygame.Rect(buttons_left + (button_width + button_gap) * 2, buttons_y, button_width, button_height),
            ],
        }

    def _clamp(self, value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))
