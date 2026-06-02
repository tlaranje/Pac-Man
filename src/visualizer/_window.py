from ._constants import SCREEN_SIZE
from typing import TYPE_CHECKING
import pygame
import os

if TYPE_CHECKING:
    from ._visualizer import Visualizer


class Window:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

    def stetup_window(self) -> None:
        flags = pygame.NOFRAME | pygame.SCALED

        self.vis.screen = pygame.display.set_mode(SCREEN_SIZE, flags)
        pygame.display.set_caption("Pac-Man")

        pygame.display.iconify()
        pygame.event.pump()

        self.vis.screen = pygame.display.set_mode(SCREEN_SIZE, flags)
        pygame.event.pump()

    def update_display_mode(self, width: int, height: int) -> None:
        self.vis.screen = pygame.display.set_mode((width, height))
        pygame.event.post(
            pygame.event.Event(pygame.ACTIVEEVENT, gain=1, state=1)
        )
