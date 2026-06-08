from src.gameplay import PacManGameplay
from .maze import MazeRenderer, Maze
from src.parser import PacManConfig, PacManCLI
from ._gameover import GameOver
from ._menu import Menu
from ._window import Window
from pygame import Surface
import json
import pygame


class Visualizer():
    """Main visualizer coordinating all visual and gameplay components.

    Integrates configuration parsing, gameplay logic, window management,
    rendering, and UI menus into a cohesive visual framework.
    """

    def __init__(self) -> None:
        self.maze_size: tuple[int, int]

        pacman_cli = PacManCLI()
        self.config = PacManConfig(pacman_cli.args.config)
        self.gameplay = PacManGameplay(self.config)

        self.window = Window(self)

        self.maze = Maze(self)
        self.maze_surface = self.maze.maze_surface

        self.renderer = MazeRenderer(self)

        self.menu = Menu(self)
        self.game_over = GameOver(self)

        self.screen: Surface
        self.game_play_size: tuple[int, int] = (500, 500)
        self.state: str = "MAIN_MENU"

        self.user_name: str = ""
        try:
            with open(self.config.settings.highscore_filename, "r") as fd:
                self.leaderboard: list[dict[str, int]] = json.load(fd)
        except FileNotFoundError:
            self.leaderboard = []

        self.title_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 130
        )

        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 40
        )

        self.error_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 30
        )

        self.text_box_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 30
        )

        self.sub_title_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 60
        )

        self.ins_font = pygame.font.Font("assets/fonts/Rajdhani-Bold.ttf", 30)

        self.arrows_font = pygame.font.SysFont("dejavusans", 30)
