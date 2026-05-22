from ._protocol import VisualizerProtocol as VProtocol
import pygame


class Window:
    def __init__(self) -> None:
        pass

    def setup_main_menu_win(self: VProtocol) -> None:
        self.width = 200
        self.height = 200
        self.screen = pygame.display.set_mode((self.width, self.height))
