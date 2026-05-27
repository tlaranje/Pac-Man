from ._constants import TILE_SIZE, MARGIN, MAZE_OFFSET
from .maze import MazeRenderer, Maze, GameOver, SpriteLoader
from src.gameplay import PacManGameplay
from src.parser import PacManConfig
from ._menu import Menu
from ._window import Window
from pygame import Surface
import pygame


class Visualizer():
    def __init__(self) -> None:
        self.config = PacManConfig("./config.json")
        self.gameplay = PacManGameplay(self.config)

        self.window = Window(self)
        self.sprite_loader = SpriteLoader(self)

        self.maze = Maze(self)
        maze_width = self.maze.size[0] * TILE_SIZE + MARGIN
        maze_height = self.maze.size[1] * TILE_SIZE + MARGIN + MAZE_OFFSET
        self.maze_surface = pygame.Surface((maze_width, maze_height))
        self.maze_surface.fill((50, 50, 50))

        self.renderer = MazeRenderer(self)

        self.menu = Menu(self)
        self.game_over = GameOver(self)

        self.maze.init_sprites(self.renderer)

        self.screen: Surface
        self.game_play_size: tuple[int, int] = (500, 500)
        self.state: str = "MAIN_MENU"
