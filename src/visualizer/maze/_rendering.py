from .._constants import (
    TILE_SIZE, MARGIN, BORDER_SIZE, MAZE_OFFSET,
    BORDER_COLOR, INNER_COLOR, INNER_THICKNESS
)
from typing import TYPE_CHECKING
from pygame import Event
import pygame

if TYPE_CHECKING:
    from .._visualizer import Visualizer


class MazeRenderer:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.maze_surface = self.vis.maze_surface

    def _draw_square(self, color, pos: tuple[int, int]) -> None:
        padding = BORDER_SIZE - 8 // 2
        start_rect = pygame.Rect(pos[0] + padding, pos[1] + padding, 16, 16)
        pygame.draw.rect(self.maze_surface, color, start_rect)

    def _draw_square_cap(self, pos: tuple) -> None:
        rect = pygame.Rect(0, 0, BORDER_SIZE, BORDER_SIZE)
        rect.center = (pos[0], pos[1])
        pygame.draw.rect(self.maze_surface, BORDER_COLOR, rect)

    def draw_walls(
        self, maze_grid: list, entry_cell: tuple, exit_cell: tuple
    ) -> None:
        for y, row in enumerate(maze_grid):
            for x, cell in enumerate(row):
                pos_x = (x * TILE_SIZE) + MARGIN // 2
                pos_y = (y * TILE_SIZE) + MARGIN + MAZE_OFFSET // 2

                top_left = (pos_x, pos_y)
                top_right = (pos_x + TILE_SIZE, pos_y)
                bottom_left = (pos_x, pos_y + TILE_SIZE)
                bottom_right = (pos_x + TILE_SIZE, pos_y + TILE_SIZE)

                if cell & 1:
                    pygame.draw.line(
                        self.maze_surface, BORDER_COLOR,
                        (top_left[0] - 1, top_left[1]),
                        (top_right[0] + 1, top_right[1]),
                        BORDER_SIZE
                    )
                    self._draw_square_cap(top_left)
                    self._draw_square_cap(top_right)
                if cell & 2:
                    pygame.draw.line(
                        self.maze_surface, BORDER_COLOR,
                        (top_right[0], top_right[1] - 1),
                        (bottom_right[0], bottom_right[1] + 1), BORDER_SIZE
                    )
                    self._draw_square_cap(top_right)
                    self._draw_square_cap(bottom_right)
                if cell & 4:
                    pygame.draw.line(
                        self.maze_surface, BORDER_COLOR,
                        (bottom_left[0] - 1, bottom_left[1]),
                        (bottom_right[0] + 1, bottom_right[1]),
                        BORDER_SIZE
                    )
                    self._draw_square_cap(bottom_left)
                    self._draw_square_cap(bottom_right)
                if cell & 8:
                    pygame.draw.line(
                        self.maze_surface, BORDER_COLOR,
                        (top_left[0], top_left[1] - 1),
                        (bottom_left[0], bottom_left[1] + 1),
                        BORDER_SIZE
                    )
                    self._draw_square_cap(top_left)
                    self._draw_square_cap(bottom_left)

        for y, row in enumerate(maze_grid):
            for x, cell in enumerate(row):
                pos_x = (x * TILE_SIZE) + MARGIN // 2
                pos_y = (y * TILE_SIZE) + MARGIN + MAZE_OFFSET // 2

                if cell & 1:
                    pygame.draw.line(
                        self.maze_surface, INNER_COLOR,
                        (pos_x - 1, pos_y),
                        (pos_x + TILE_SIZE + 1, pos_y),
                        INNER_THICKNESS
                    )
                if cell & 2:
                    pygame.draw.line(
                        self.maze_surface, INNER_COLOR,
                        (pos_x + TILE_SIZE, pos_y - 1),
                        (pos_x + TILE_SIZE, pos_y + TILE_SIZE + 1),
                        INNER_THICKNESS
                    )
                if cell & 4:
                    pygame.draw.line(
                        self.maze_surface, INNER_COLOR,
                        (pos_x - 1, pos_y + TILE_SIZE),
                        (pos_x + TILE_SIZE + 1, pos_y + TILE_SIZE),
                        INNER_THICKNESS
                    )
                if cell & 8:
                    pygame.draw.line(
                        self.maze_surface, INNER_COLOR, (pos_x, pos_y - 1),
                        (pos_x, pos_y + TILE_SIZE + 1),
                        INNER_THICKNESS
                    )

    def draw_pacgums(self, pacgums_map: list, fruit_frames: list) -> None:
        for y, row in enumerate(pacgums_map):
            for x, cell in enumerate(row):
                if (0, 0) == (x, y):
                    continue
                if cell[0]:
                    pacgums_size = 16
                    pos_x = (x * TILE_SIZE) + 14 + (
                        TILE_SIZE - pacgums_size) // 2 + 4
                    pos_y = (y * TILE_SIZE) + 15 + (
                        TILE_SIZE - pacgums_size) // 2 + 1 + MAZE_OFFSET
                    if cell[1] == "super":
                        self.maze_surface.blit(
                            fruit_frames[1]["0"][0],
                            (pos_x, pos_y, pacgums_size, pacgums_size)
                        )
                    else:
                        self.maze_surface.blit(
                            fruit_frames[0]["0"][0],
                            (pos_x, pos_y, pacgums_size, pacgums_size)
                        )


class GameOver():
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer

    def handle_game_over_events(self, event: Event) -> None:
        print("dead")

    def draw_game_over(self) -> None:
        pass
