from ._constants import SCREEN_SIZE
from typing import TYPE_CHECKING
import pygame
import os

if TYPE_CHECKING:
    from ._visualizer import Visualizer


class Window:
    """Pygame window manager for display mode and sizing.

    Handles window setup, display mode configuration, and screen size updates.
    """

    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

    def stetup_window(self) -> None:
        """
        Set up the pygame window with display mode.
        """
        flags = pygame.NOFRAME | pygame.SCALED

        self.vis.screen = pygame.display.set_mode(SCREEN_SIZE, flags)
        pygame.display.set_caption("Pac-Man")

        pygame.event.pump()

    def update_display_mode(self, width: int, height: int) -> None:
        """
        Update window size and display mode.

        Args:
            width: New window width in pixels.
            height: New window height in pixels.
        """
        self.vis.screen = pygame.display.set_mode((width, height))
        pygame.event.post(
            pygame.event.Event(pygame.ACTIVEEVENT, gain=1, state=1)
        )
