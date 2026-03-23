"""Visual board state decoupled from the game engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import pygame

from scopone.config.game import INITIAL_HAND_CARDS
from scopone.config.ui import CARD_SIZE_HAND, CARD_SIZE_SMALL, CARD_SIZE_TABLE, FONT_NAME

from scopone.types import Card


@dataclass
class RenderBoard:
    """Single source of truth for the static cards currently visible in the UI."""

    render_table_cards: List[Card] = field(default_factory=list)
    render_hand_cards: Dict[int, List[Card]] = field(default_factory=dict)
    render_captures: Dict[int, List[Card]] = field(default_factory=lambda: {0: [], 1: []})
    render_sweeps: Dict[int, int] = field(default_factory=lambda: {0: 0, 1: 0})
    render_deck_count: int = 0

    @classmethod
    def from_engine(cls, engine) -> "RenderBoard":
        board = cls()
        board.sync_from_engine(engine)
        return board

    def sync_from_engine(self, engine) -> None:
        self.render_table_cards = list(engine.table)
        self.render_hand_cards = dict((player.id, list(player.hand)) for player in engine.players)
        self.render_captures = {0: [], 1: []}
        self.render_sweeps = {0: 0, 1: 0}

        if engine.num_players == 4:
            for player in engine.players:
                if player.team is None:
                    continue
                self.render_captures.setdefault(player.team, []).extend(player.captured)
                self.render_sweeps[player.team] = self.render_sweeps.get(player.team, 0) + player.sweeps
        else:
            for player in engine.players[:2]:
                self.render_captures[player.id] = list(player.captured)
                self.render_sweeps[player.id] = player.sweeps

        self.render_deck_count = len(engine.deck_remaining)

    def ensure_player(self, player_id: int) -> List[Card]:
        return self.render_hand_cards.setdefault(player_id, [])

    def ensure_team(self, team_id: int) -> List[Card]:
        return self.render_captures.setdefault(team_id, [])

    def ensure_sweeps(self, team_id: int) -> int:
        return self.render_sweeps.setdefault(team_id, 0)


class BoardView:
    """Computes board layout and orchestrates board rendering calls for MatchScene."""

    def __init__(self, scene) -> None:
        self.scene = scene

    def calculate_layout(self, width: int, height: int):
        ui_scale = self._clamp_float(min(width / 1920.0, height / 1080.0), 0.85, 1.4)
        card_presence_scale = self._clamp_float(ui_scale * 1.14, 0.95, 1.6)
        hand_card_size = self._scale_card_size(CARD_SIZE_HAND, card_presence_scale, minimum=(100, 150))
        table_card_size = self._scale_card_size(CARD_SIZE_TABLE, card_presence_scale, minimum=(116, 174))
        small_card_size = self._scale_card_size(CARD_SIZE_SMALL, card_presence_scale, minimum=(78, 117))

        min_gap = self._clamp(int(min(width, height) * 0.015), 10, 24)

        bottom_label_rect = self._estimate_player_label_rect(0, hand_card_size)
        top_player_id = 1 if self.scene.engine.num_players == 2 else 2
        top_label_rect_est = self._estimate_player_label_rect(top_player_id, hand_card_size)
        left_label_rect_est = self._estimate_player_label_rect(1, hand_card_size)
        right_label_rect_est = (
            self._estimate_player_label_rect(3, hand_card_size)
            if self.scene.engine.num_players == 4
            else left_label_rect_est
        )

        bottom_cards_block_h = hand_card_size[1] + 8
        top_cards_block_h = small_card_size[1] + 2
        left_cards_block_w = small_card_size[1]
        right_cards_block_w = small_card_size[1]
        left_label_block_w = left_label_rect_est.height
        right_label_block_w = right_label_rect_est.height

        reserve_top = top_cards_block_h + top_label_rect_est.height + (min_gap * 3)
        reserve_bottom = bottom_cards_block_h + bottom_label_rect.height + (min_gap * 3)
        reserve_left = left_cards_block_w + left_label_block_w + (min_gap * 3)
        reserve_right = (
            reserve_left
            if self.scene.engine.num_players == 2
            else right_cards_block_w + right_label_block_w + (min_gap * 3)
        )

        min_table_width = self._clamp(int(width * 0.38), 520, 980)
        min_table_height = self._clamp(int(height * 0.30), 220, 540)

        overflow_x = max(0, (reserve_left + reserve_right + min_table_width) - width)
        overflow_y = max(0, (reserve_top + reserve_bottom + min_table_height) - height)

        if overflow_x:
            reduce_each = int((overflow_x + 1) / 2)
            reserve_left = max(min_gap * 2 + left_cards_block_w + left_label_block_w, reserve_left - reduce_each)
            reserve_right = max(min_gap * 2 + right_cards_block_w + right_label_block_w, reserve_right - reduce_each)

        if overflow_y:
            reduce_each = int((overflow_y + 1) / 2)
            reserve_top = max(min_gap * 2 + top_cards_block_h + top_label_rect_est.height, reserve_top - reduce_each)
            reserve_bottom = max(min_gap * 2 + bottom_cards_block_h + bottom_label_rect.height, reserve_bottom - reduce_each)

        table_rect = pygame.Rect(
            reserve_left,
            reserve_top,
            max(min_table_width, width - reserve_left - reserve_right),
            max(min_table_height, height - reserve_top - reserve_bottom),
        )

        score_panel = pygame.Rect(
            min_gap,
            min_gap,
            self._clamp(int(322 * ui_scale), 312, 428),
            self._clamp(int(132 * ui_scale), 126, 176),
        )
        menu_button = pygame.Rect(
            width - min_gap - self._clamp(int(92 * ui_scale), 90, 124),
            min_gap,
            self._clamp(int(92 * ui_scale), 90, 124),
            self._clamp(int(38 * ui_scale), 36, 50),
        )
        audio_button = pygame.Rect(menu_button.left - 44, min_gap + 1, 36, 36)

        available_top_y = table_rect.top
        gap_top = self._equidistant_gap(available_top_y, top_label_rect_est.height, top_cards_block_h, min_gap)
        top_player_rect = pygame.Rect(table_rect.left, gap_top, table_rect.width, top_cards_block_h)
        top_label_rect = pygame.Rect(
            table_rect.centerx - (top_label_rect_est.width // 2),
            top_player_rect.bottom + gap_top,
            top_label_rect_est.width,
            top_label_rect_est.height,
        )

        available_bottom_y = height - table_rect.bottom
        gap_bottom = self._equidistant_gap(available_bottom_y, bottom_label_rect.height, bottom_cards_block_h, min_gap)
        bottom_label_rect = pygame.Rect(
            table_rect.centerx - (bottom_label_rect.width // 2),
            table_rect.bottom + gap_bottom,
            bottom_label_rect.width,
            bottom_label_rect.height,
        )
        bottom_player_rect = pygame.Rect(
            table_rect.left,
            bottom_label_rect.bottom + gap_bottom,
            table_rect.width,
            bottom_cards_block_h,
        )

        available_left_x = table_rect.left
        gap_left = self._equidistant_gap(available_left_x, left_label_block_w, left_cards_block_w, min_gap)
        left_player_rect = pygame.Rect(gap_left, table_rect.centery - (table_rect.height // 2), left_cards_block_w, table_rect.height)
        left_label_rect = pygame.Rect(
            left_player_rect.right + gap_left,
            table_rect.centery - (left_label_rect_est.width // 2),
            left_label_block_w,
            left_label_rect_est.width,
        )

        available_right_x = width - table_rect.right
        gap_right = self._equidistant_gap(available_right_x, right_label_block_w, right_cards_block_w, min_gap)
        right_label_rect = pygame.Rect(
            table_rect.right + gap_right,
            table_rect.centery - (right_label_rect_est.width // 2),
            right_label_block_w,
            right_label_rect_est.width,
        )
        right_player_rect = pygame.Rect(
            right_label_rect.right + gap_right,
            table_rect.centery - (table_rect.height // 2),
            right_cards_block_w,
            table_rect.height,
        )

        deck_rect = pygame.Rect(
            table_rect.right - small_card_size[0] - 22,
            table_rect.centery - (small_card_size[1] // 2),
            small_card_size[0],
            small_card_size[1],
        )
        capture_piles = self._build_capture_pile_layout(
            width,
            height,
            bottom_player_rect,
            top_player_rect,
            right_player_rect,
            hand_card_size,
            small_card_size,
        )
        capture_targets = dict((team_id, pile_rect.center) for team_id, pile_rect in capture_piles.items())
        overlay_rect = pygame.Rect(width // 2 - 340, height // 2 - 180, 680, 360)

        return {
            "table_rect": table_rect,
            "deck_rect": deck_rect,
            "capture_piles": capture_piles,
            "capture_targets": capture_targets,
            "top_player_rect": top_player_rect,
            "bottom_player_rect": bottom_player_rect,
            "left_player_rect": left_player_rect,
            "right_player_rect": right_player_rect,
            "top_label_rect": top_label_rect,
            "bottom_label_rect": bottom_label_rect,
            "left_label_rect": left_label_rect,
            "right_label_rect": right_label_rect,
            "score_panel": score_panel,
            "menu_button": menu_button,
            "audio_button": audio_button,
            "overlay_rect": overlay_rect,
            "hand_card_size": hand_card_size,
            "table_card_size": table_card_size,
            "small_card_size": small_card_size,
        }

    def render_table_and_players(self, renderer, layout, mouse_pos) -> None:
        self.scene._draw_table(renderer, layout["table_rect"])
        self.scene._draw_deck_anchor(renderer, layout["deck_rect"])
        self.scene._draw_table_cards(renderer, layout["table_rect"])
        self.scene._draw_live_score_panel(renderer, layout["score_panel"])
        self.scene._draw_menu_button(renderer, layout["menu_button"], mouse_pos)
        renderer.draw_audio_toggle(
            layout["audio_button"],
            muted=self.scene.app.is_muted,
            hovered=layout["audio_button"].collidepoint(mouse_pos),
        )
        self.scene._draw_players(renderer, layout)
        self.scene.draw_captured_piles(renderer.surface)

    def _build_capture_pile_layout(
        self,
        screen_width: int,
        screen_height: int,
        bottom_player_rect: pygame.Rect,
        top_player_rect: pygame.Rect,
        right_player_rect: pygame.Rect,
        hand_card_size,
        small_card_size,
    ):
        hand_slots = INITIAL_HAND_CARDS.get(self.scene.engine.num_players, 9)
        pile_w, pile_h = small_card_size
        piles = {}

        tu_fixed_centery = bottom_player_rect.centery
        tu_hand_fixed_left = self._get_fixed_horizontal_hand_left(
            bottom_player_rect,
            hand_card_size,
            hand_slots,
            spacing_min=40,
            spacing_max=96,
        )
        team1_rect = pygame.Rect(0, 0, pile_w, pile_h)
        team1_rect.centery = tu_fixed_centery
        team1_rect.right = tu_hand_fixed_left - 40
        team1_rect = self._clamp_rect_inside_screen(team1_rect, screen_width, screen_height)
        piles[0] = team1_rect

        if self.scene.engine.num_players == 4:
            ai3_fixed_centerx = right_player_rect.centerx
            ai3_hand_fixed_top = self._get_fixed_vertical_hand_top(right_player_rect, small_card_size, hand_slots)
            team2_rect = pygame.Rect(0, 0, pile_h, pile_w)
            team2_rect.centerx = ai3_fixed_centerx
            team2_rect.bottom = ai3_hand_fixed_top - 40
            team2_rect = self._clamp_rect_inside_screen(team2_rect, screen_width, screen_height)
        else:
            ai1_fixed_centery = top_player_rect.centery
            ai1_hand_fixed_right = self._get_fixed_horizontal_hand_right(
                top_player_rect,
                small_card_size,
                hand_slots,
                spacing_min=22,
                spacing_max=54,
            )
            team2_rect = pygame.Rect(0, 0, pile_w, pile_h)
            team2_rect.centery = ai1_fixed_centery
            team2_rect.left = ai1_hand_fixed_right + 40
            team2_rect = self._clamp_rect_inside_screen(team2_rect, screen_width, screen_height)
        piles[1] = team2_rect

        return piles

    def _estimate_player_label_rect(self, player_id: int, hand_card_size) -> pygame.Rect:
        player = None
        for current in self.scene.engine.players:
            if current.id == player_id:
                player = current
                break

        if player is None:
            label_text = "Giocatore"
            team_text = "Squadra"
        else:
            label_text = player.name
            if self.scene.engine.num_players == 4 and player.team is not None:
                team_text = "Squadra {0}".format(player.team + 1)
            else:
                team_text = "Squadra {0}".format((player.id if player.id in (0, 1) else 0) + 1)

        label_scale = self._clamp_float(hand_card_size[0] / float(CARD_SIZE_HAND[0]), 0.95, 1.3)
        name_size = self._clamp(int(22 * label_scale), 20, 28)
        team_size = self._clamp(int(16 * label_scale), 15, 21)
        line_gap = self._clamp(int(5 * label_scale), 4, 8)
        padding_x = self._clamp(int(20 * label_scale), 18, 28)
        padding_y = self._clamp(int(13 * label_scale), 12, 20)

        name_font = pygame.font.SysFont(FONT_NAME, name_size, bold=True)
        team_font = pygame.font.SysFont(FONT_NAME, team_size, bold=False)
        name_width, name_height = name_font.size(label_text)
        team_width, team_height = team_font.size(team_text)

        width = max(name_width, team_width) + (padding_x * 2)
        height = name_height + line_gap + team_height + (padding_y * 2)
        return pygame.Rect(0, 0, width, height)

    def _get_fixed_horizontal_hand_left(self, rect: pygame.Rect, card_size, slot_count: int, spacing_min: int, spacing_max: int) -> int:
        card_width = card_size[0]
        slots = max(1, slot_count)
        spacing = max(spacing_min, min(spacing_max, (rect.width - card_width) // slots))
        total_width = card_width + (spacing * (slots - 1))
        return rect.centerx - (total_width // 2)

    def _get_fixed_horizontal_hand_right(self, rect: pygame.Rect, card_size, slot_count: int, spacing_min: int, spacing_max: int) -> int:
        card_width = card_size[0]
        slots = max(1, slot_count)
        spacing = max(spacing_min, min(spacing_max, (rect.width - card_width) // slots))
        total_width = card_width + (spacing * (slots - 1))
        return rect.centerx + (total_width // 2)

    def _get_fixed_vertical_hand_top(self, rect: pygame.Rect, card_size, slot_count: int) -> int:
        rotated_height = card_size[0]
        slots = max(1, slot_count)
        spacing = max(50, min(92, (rect.height - rotated_height) // slots))
        total_height = rotated_height + (spacing * (slots - 1))
        return rect.centery - (total_height // 2)

    def _clamp_rect_inside_screen(self, rect: pygame.Rect, width: int, height: int, padding: int = 8) -> pygame.Rect:
        clamped = rect.copy()
        clamped.x = max(padding, min(clamped.x, width - clamped.width - padding))
        clamped.y = max(padding, min(clamped.y, height - clamped.height - padding))
        return clamped

    def _clamp(self, value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))

    def _clamp_float(self, value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    def _scale_card_size(self, base_size, scale: float, minimum) -> tuple:
        return (
            self._clamp(int(base_size[0] * scale), minimum[0], int(base_size[0] * 1.6)),
            self._clamp(int(base_size[1] * scale), minimum[1], int(base_size[1] * 1.6)),
        )

    def _equidistant_gap(self, available_space: int, text_extent: int, cards_extent: int, minimum_gap: int) -> int:
        gap = int((available_space - text_extent - cards_extent) / 3)
        return max(minimum_gap, gap)
