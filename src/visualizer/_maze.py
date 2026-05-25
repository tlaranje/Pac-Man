from mazegenerator import MazeGenerator
from typing import TYPE_CHECKING
import pygame
import random

if TYPE_CHECKING:
    from pygame.typing import ColorLike
    from .protocol import VisualizerProtocol as VProtocol

TILE_SIZE = 32


class Maze:
    def __init__(
            self,
            screen: pygame.Surface,
            maze_size: tuple[int, int] = (20, 20),
            entry_cell: tuple[int, int] = (0, 0),
            exit_cell: tuple[int, int] = (19, 19),
            perfect: bool = True,
            seed: int = -1
    ) -> None:
        self.maze = MazeGenerator(
            size=(maze_size[0], maze_size[1]), perfect=perfect,
            entry_cell=entry_cell, exit_cell=exit_cell, seed=seed
        )
        self.screen = screen
        self.maze_size = maze_size
        self.perfect = perfect
        self.entry_cell = entry_cell
        self.exit_cell = exit_cell
        self.seed = seed
        self.player_frames: list[pygame.Surface] = self.init_player_frames()

    """ def init_player_frames(self) -> list[pygame.Surface]:
        tileset = pygame.image.load("assets/img/PacMan.png").convert_alpha()
        p_frames = []

        frame = pygame.Rect(0, 0, 32, 32)
        p_frames.append(tileset.subsurface(frame))

        return p_frames """

    def handle_game_play_events(
        self: VProtocol, event: pygame.event.Event
    ) -> None:
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                self.state = "MAIN_MENU"
                x, y = self.menu_size
                self.update_display_mode(x, y)
            if event.key == pygame.K_r:
                if self.seed == -1:
                    seed = random.randint(0, 100000)
                else:
                    seed = self.seed

                self.maze = MazeGenerator(
                    size=(self.maze_size[0], self.maze_size[1]),
                    perfect=self.perfect,
                    entry_cell=self.entry_cell,
                    exit_cell=self.exit_cell,
                    seed=seed
                )

    def draw_maze(self) -> None:
        border_color = (0, 0, 0)
        inner_color = (25, 25, 166)

        border_size = 9
        inner_thickness = 3
        margin = 16

        def draw_square(color: ColorLike, pos: tuple[int, int]) -> None:
            padding = border_size // 2

            inner_tile_size = TILE_SIZE - (padding * 2)

            start_rect = pygame.Rect(
                pos[0] + padding,
                pos[1] + padding,
                inner_tile_size,
                inner_tile_size
            )

            pygame.draw.rect(self.screen, color, start_rect)

        def draw_square_cap(color: tuple, pos: tuple, thickness: int) -> None:
            color = (0, 0, 0)
            rect = pygame.Rect(0, 0, thickness, thickness)
            rect.center = (pos[0], pos[1])
            pygame.draw.rect(self.screen, color, rect)

        for y, row in enumerate(self.maze.maze):
            for x, cell in enumerate(row):

                pos_x = (x * TILE_SIZE) + margin
                pos_y = (y * TILE_SIZE) + margin

                top_left = (pos_x, pos_y)
                top_right = (pos_x + TILE_SIZE, pos_y)
                bottom_left = (pos_x, pos_y + TILE_SIZE)
                bottom_right = (pos_x + TILE_SIZE, pos_y + TILE_SIZE)

                if x == self.entry_cell[0] and y == self.entry_cell[1]:
                    draw_square(pygame.Color("green"), (pos_x, pos_y))

                if x == self.exit_cell[0] and y == self.exit_cell[1]:
                    draw_square(pygame.Color("red"), (pos_x, pos_y))

                if cell & 1:  # Norte
                    pygame.draw.line(
                        self.screen, border_color,
                        (top_left[0] - 1, top_left[1]),
                        (top_right[0] + 1, top_right[1]),
                        border_size
                    )
                    draw_square_cap(border_color, top_left, border_size)
                    draw_square_cap(border_color, top_right, border_size)

                if cell & 2:  # Leste
                    pygame.draw.line(
                        self.screen, border_color,
                        (top_right[0], top_right[1] - 1),
                        (bottom_right[0], bottom_right[1] + 1),
                        border_size
                    )
                    draw_square_cap(border_color, top_right, border_size)
                    draw_square_cap(border_color, bottom_right, border_size)

                if cell & 4:  # Sul
                    pygame.draw.line(
                        self.screen, border_color,
                        (bottom_left[0] - 1, bottom_left[1]),
                        (bottom_right[0] + 1, bottom_right[1]),
                        border_size
                    )
                    draw_square_cap(border_color, bottom_left, border_size)
                    draw_square_cap(border_color, bottom_right, border_size)

                if cell & 8:  # Oeste
                    pygame.draw.line(
                        self.screen, border_color,
                        (top_left[0], top_left[1] - 1),
                        (bottom_left[0], bottom_left[1] + 1),
                        border_size
                    )
                    draw_square_cap(border_color, top_left, border_size)
                    draw_square_cap(border_color, bottom_left, border_size)

        for y, row in enumerate(self.maze.maze):
            for x, cell in enumerate(row):
                pos_x = (x * TILE_SIZE) + margin
                pos_y = (y * TILE_SIZE) + margin

                top_left = (pos_x, pos_y)
                top_right = (pos_x + TILE_SIZE, pos_y)
                bottom_left = (pos_x, pos_y + TILE_SIZE)
                bottom_right = (pos_x + TILE_SIZE, pos_y + TILE_SIZE)

                if cell & 1:  # Norte
                    pygame.draw.line(
                        self.screen, inner_color,
                        (top_left[0] - 1, top_left[1]),
                        (top_right[0] + 1, top_right[1]),
                        inner_thickness
                    )

                if cell & 2:  # Leste
                    pygame.draw.line(
                        self.screen, inner_color,
                        (top_right[0], top_right[1] - 1),
                        (bottom_right[0], bottom_right[1] + 1),
                        inner_thickness
                    )

                if cell & 4:  # Sul
                    pygame.draw.line(
                        self.screen, inner_color,
                        (bottom_left[0] - 1, bottom_left[1]),
                        (bottom_right[0] + 1, bottom_right[1]),
                        inner_thickness
                    )

                if cell & 8:  # Oeste
                    pygame.draw.line(
                        self.screen, inner_color,
                        (top_left[0], top_left[1] - 1),
                        (bottom_left[0], bottom_left[1] + 1),
                        inner_thickness
                    )
