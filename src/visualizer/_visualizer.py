from ._window import Window
from .view._menu import Menu
from .maze._maze import Maze

from pygame import Surface


class Visualizer(Window, Menu, Maze):
    def __init__(self) -> None:
        Window.__init__(self)
        Menu.__init__(self)

        self.screen: Surface
        self.maze: "Maze"

        self.game_play_size: tuple[int, int] = (500, 500)
        self.state: str = "MAIN_MENU"
