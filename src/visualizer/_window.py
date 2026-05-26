from ._protocol import VisualizerProtocol as VProtocol
from ._constants import MENU_SIZE
import pygame
import os


class Window:
    def __init__(self) -> None:
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def stetup_window(self: VProtocol) -> None:
        self.screen: pygame.Surface = pygame.display.set_mode(MENU_SIZE)
        pygame.display.set_caption("Pac-Man")

    def update_display_mode(self: VProtocol, width: int, height: int) -> None:
        self.screen = pygame.display.set_mode((width, height))
        pygame.event.post(
            pygame.event.Event(pygame.ACTIVEEVENT, gain=1, state=1)
        )
