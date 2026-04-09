"""Shared futuristic blue background rendering."""

import pygame


def draw_prismatic_background(surface, variant="menu") -> None:
    """Disegna sfondo prismatico condiviso, variato per tipo scena."""
    width, height = surface.get_size()
    _draw_vertical_gradient(surface, (4, 8, 20), (14, 30, 58))

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    _draw_central_glow(overlay, width, height, variant)
    _draw_prismatic_planes(overlay, width, height, variant)
    _draw_star_field(overlay, width, height)
    surface.blit(overlay, (0, 0))


def _draw_vertical_gradient(surface, top_color, bottom_color) -> None:
    """Riempie la surface con gradiente verticale interpolato."""
    width, height = surface.get_size()
    for y in range(height):
        ratio = float(y) / max(height - 1, 1)
        color = (
            int(top_color[0] + ((bottom_color[0] - top_color[0]) * ratio)),
            int(top_color[1] + ((bottom_color[1] - top_color[1]) * ratio)),
            int(top_color[2] + ((bottom_color[2] - top_color[2]) * ratio)),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))


def _draw_central_glow(surface, width: int, height: int, variant: str) -> None:
    """Applica alone centrale multilayer per profondita visiva."""
    center = (int(width * 0.5), int(height * 0.54))
    radius = int(min(width, height) * (0.38 if variant == "menu" else 0.34))

    for index, color in enumerate(
        [
            (209, 240, 255, 38),
            (150, 205, 255, 32),
            (112, 170, 245, 26),
            (64, 108, 194, 16),
        ]
    ):
        pygame.draw.circle(surface, color, center, max(12, radius - (index * int(radius * 0.18))))


def _draw_prismatic_planes(surface, width: int, height: int, variant: str) -> None:
    """Disegna piani geometrici e streak di luce sullo sfondo."""
    plane_specs = [
        ((0.04, 0.88), (0.34, 0.52), (0.7, 0.92), (0.48, 1.02), (165, 210, 255, 34)),
        ((0.15, 0.24), (0.52, 0.06), (0.82, 0.54), (0.42, 0.78), (110, 160, 245, 22)),
        ((0.58, 0.18), (0.94, 0.02), (1.04, 0.62), (0.74, 0.8), (132, 184, 255, 18)),
        ((-0.06, 0.36), (0.18, 0.08), (0.56, 0.76), (0.28, 1.04), (86, 138, 225, 20)),
    ]
    if variant != "menu":
        plane_specs.append(((0.36, 0.3), (0.68, 0.16), (0.94, 0.62), (0.6, 0.82), (190, 228, 255, 12)))

    for p1, p2, p3, p4, color in plane_specs:
        points = [
            (int(width * p1[0]), int(height * p1[1])),
            (int(width * p2[0]), int(height * p2[1])),
            (int(width * p3[0]), int(height * p3[1])),
            (int(width * p4[0]), int(height * p4[1])),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.lines(surface, (180, 220, 255, max(12, color[3] + 22)), True, points, 2)

    streaks = [
        ((0.14, 0.5), (0.34, 0.2)),
        ((0.62, 0.76), (0.88, 0.42)),
        ((0.72, 0.18), (0.86, 0.06)),
        ((0.02, 0.86), (0.22, 0.56)),
    ]
    for start, end in streaks:
        pygame.draw.line(
            surface,
            (196, 231, 255, 68 if variant == "menu" else 52),
            (int(width * start[0]), int(height * start[1])),
            (int(width * end[0]), int(height * end[1])),
            2,
        )


def _draw_star_field(surface, width: int, height: int) -> None:
    """Aggiunge punti luce secondari per dettaglio atmosferico."""
    star_specs = [
        (0.12, 0.22, 2), (0.24, 0.6, 2), (0.44, 0.16, 2), (0.54, 0.1, 2),
        (0.61, 0.19, 2), (0.67, 0.26, 2), (0.82, 0.56, 2), (0.72, 0.72, 1),
        (0.18, 0.68, 1), (0.32, 0.82, 1), (0.88, 0.12, 1), (0.83, 0.3, 1),
    ]
    for x_ratio, y_ratio, radius in star_specs:
        center = (int(width * x_ratio), int(height * y_ratio))
        pygame.draw.circle(surface, (221, 243, 255, 190), center, radius)
        if radius > 1:
            pygame.draw.line(surface, (201, 235, 255, 90), (center[0] - 6, center[1]), (center[0] + 6, center[1]), 1)
            pygame.draw.line(surface, (201, 235, 255, 90), (center[0], center[1] - 6), (center[0], center[1] + 6), 1)
