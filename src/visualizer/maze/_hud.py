from typing import TYPE_CHECKING
from src.utils import RoundRect
import pygame

if TYPE_CHECKING:
    from .._visualizer import Visualizer


class HudRenderer:
    """HUD (Heads-Up Display) renderer for score, lives, and time.

    Displays game statistics including current score, remaining lives,
    and time remaining in the level.
    """

    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 20
        )

    def draw(self, score: int, lives: int, time: int) -> None:
        """
        Draw a rounded rectangle on the surface.

        Args:
            surface: Target Pygame surface.
            rect: Rectangle defining position and size.
            color: RGB color tuple.
            radius: Corner radius in pixels.
            b_size: Border size.
            b_color: Border color tuple.
        """
        screen = self.vis.screen

        level_surf = self.font.render(
            f"Level: {self.vis.gameplay.map_idx}", True, (255, 255, 255)
        )
        high_surf = self.font.render(
            f"High Score: {score}", True, (255, 255, 255)
        )
        lives_surf = self.font.render(
            f"Lives: {lives}", True, (255, 255, 255)
        )
        time_surf = self.font.render(
            f"Time: {time}", True, (255, 255, 255)
        )

        screen_w, _ = screen.get_size()

        container_w = 370
        rect = pygame.Rect(
            screen_w // 2 - container_w // 2, -15, container_w, 80
        )

        RoundRect().draw(screen, rect, color=(50, 50, 50), b_size=2)

        left_x = rect.x + 20
        mid_x_text = rect.centerx
        right_x = rect.right - 20

        screen.blit(lives_surf, (left_x, 6))
        screen.blit(high_surf, (mid_x_text - high_surf.get_width() // 2, 6))
        screen.blit(level_surf, (mid_x_text - level_surf.get_width() // 2, 35))
        screen.blit(time_surf, (right_x - time_surf.get_width(), 6))
