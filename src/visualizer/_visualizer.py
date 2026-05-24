from ._window import Window
from ._menu import Menu
from pygame import Surface


class Visualizer(Window, Menu):
    def __init__(self) -> None:
        self.screen: Surface
