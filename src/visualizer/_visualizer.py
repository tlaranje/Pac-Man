from .maze import MazeRenderer, Maze, GameOver
from src.gameplay import PacManGameplay
from src.parser import PacManConfig
from ._menu import Menu
from ._window import Window
from pygame import Surface


class Visualizer():
    def __init__(self) -> None:
        self.config = PacManConfig("./config.json")
        self.gameplay = PacManGameplay(self.config)

        self.window = Window(self)

        self.maze = Maze(self)
        self.maze_surface = self.maze.maze_surface
        self.maze_surface.fill((50, 50, 50))

        self.renderer = MazeRenderer(self)

        self.menu = Menu(self)
        self.game_over = GameOver(self)

        self.screen: Surface
        self.game_play_size: tuple[int, int] = (500, 500)
        self.state: str = "MAIN_MENU"
