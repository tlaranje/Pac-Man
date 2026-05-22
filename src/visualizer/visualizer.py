from typing import TYPE_CHECKING
from ._window import Window
import pygame

if TYPE_CHECKING:
    from pygame import Surface


class Visualizer(Window):
    def __init__(self) -> None:
        pygame.init()

        self.scale: int = 80
        self.margin: int = 64

        self.width: int = 0
        self.height: int = 0

        # Assigned in setup_window()
        self.screen: "Surface"
