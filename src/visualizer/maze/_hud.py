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
        high_score_surf = self.font.render(
            f"High Score: {score}", True, (255, 255, 255)
        )
        lives_surf = self.font.render(
            f"Lives: {lives}", True, (255, 255, 255)
        )
        time_surf = self.font.render(
            f"Time: {time}", True, (255, 255, 255)
        )

        screen_w, _ = screen.get_size()
        mid_x = screen_w // 2

        container_w = 600
        slice_w = container_w // 3
        start_x = mid_x - (container_w // 2)

        center_1 = start_x + (slice_w // 2)
        center_2 = start_x + slice_w + (slice_w // 2)
        center_3 = start_x + (slice_w * 2) + (slice_w // 2)

        live_x = center_1 - lives_surf.get_width() // 2
        high_x = center_2 - high_score_surf.get_width() // 2
        time_x = center_3 - time_surf.get_width() // 2

        screen.blit(lives_surf, (live_x, 10))
        screen.blit(high_score_surf, (high_x, 10))
        screen.blit(level_surf, (high_x, 30))
        screen.blit(time_surf, (time_x, 10))
