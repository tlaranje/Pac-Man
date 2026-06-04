from .._constants import TILE_SIZE, SCREEN_MIDPOINT
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from .._visualizer import Visualizer


class PacgumController:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer

    def try_eat(self, maze_surface: pygame.Surface, score: int) -> int:
        vis = self.vis
        gameplay = vis.gameplay
        px = gameplay.player.x
        py = gameplay.player.y
        pacgums_map = gameplay.pacgums_maps[gameplay.map_idx]

        if not pacgums_map[py][px][0]:
            return score

        cell_type = pacgums_map[py][px][1]

        if cell_type == "normal":
            score += gameplay.config.settings.points_per_pacgum
        elif cell_type == "super":
            gameplay.player.turn_on_super()
            score += gameplay.config.settings.points_per_super_pacgum

        gameplay.player.eat(pacgums_map)

        pos_x = (
            (px * TILE_SIZE) + SCREEN_MIDPOINT[0]
            - vis.maze_size[0] // 2 + 5
        )
        pos_y = (
            (py * TILE_SIZE) + SCREEN_MIDPOINT[1]
            - vis.maze_size[1] // 2 + 5
        )
        pygame.draw.rect(maze_surface, (0, 0, 0), (pos_x, pos_y, 18, 18))

        return score
