from ._constants import MENU_SIZE
from typing import TYPE_CHECKING
import pygame
import os

if TYPE_CHECKING:
    from ._visualizer import Visualizer


class Window:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def stetup_window(self) -> None:
        self.vis.screen = pygame.display.set_mode(MENU_SIZE)
        pygame.display.set_caption("Pac-Man")

    def update_display_mode(self, width: int, height: int) -> None:
        self.vis.screen = pygame.display.set_mode((width, height))
        pygame.event.post(
            pygame.event.Event(pygame.ACTIVEEVENT, gain=1, state=1)
        )
