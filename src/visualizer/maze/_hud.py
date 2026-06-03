from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from .._visualizer import Visualizer


class HudRenderer:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 20
        )

    def draw(self, score: int, lives: int, time: int) -> None:
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
            screen_w // 2 - container_w // 2, -2, container_w, 68
        )
        pygame.draw.rect(
            screen, (50, 50, 50), rect,
            border_bottom_left_radius=10, border_bottom_right_radius=10
        )
        pygame.draw.rect(
            screen, (255, 255, 255), rect, 2,
            border_bottom_left_radius=10, border_bottom_right_radius=10
        )

        left_x = rect.x + 20
        mid_x_text = rect.centerx
        right_x = rect.right - 20

        screen.blit(lives_surf, (left_x, 8))
        screen.blit(high_surf, (mid_x_text - high_surf.get_width() // 2, 8))
        screen.blit(level_surf, (mid_x_text - level_surf.get_width() // 2, 30))
        screen.blit(time_surf, (right_x - time_surf.get_width(), 8))
