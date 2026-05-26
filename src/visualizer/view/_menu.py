from .._constants import MENU_SIZE, BUTTON_SIZE, TILE_COLOR, TILE_SIZE, MARGIN
from typing import TYPE_CHECKING
from ..ui._button import Button
import pygame
import sys

if TYPE_CHECKING:
    from ._protocol import VisualizerProtocol as VProtocol


class Menu:
    def __init__(self) -> None:
        self.menu_buttons: list[Button] = []
        self.title_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 50
        )

    def init_menu_buttons(self: "VProtocol") -> None:
        self.menu_buttons = [
            Button(
                screen=self.screen, win_size=MENU_SIZE,
                size=BUTTON_SIZE, pos=(None, 100), text="Play", action="PLAY"
            ),
            Button(
                screen=self.screen, win_size=MENU_SIZE,
                size=BUTTON_SIZE, pos=(None, 170), text="Exit",
                action="QUIT_APP"
            )
        ]

    def draw_main_menu(self: "VProtocol") -> None:
        text_surf = self.title_font.render("Pac-Man", True, TILE_COLOR)
        text_rect = text_surf.get_rect(
            centerx=self.screen.get_rect().centerx, y=10
        )
        self.screen.blit(text_surf, text_rect)
        for btn in self.menu_buttons:
            btn.draw()

    def handle_menu_events(
        self: "VProtocol", event: pygame.event.Event
    ) -> None:
        for btn in self.menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    self.state = 'GAME_PLAY'
                    width = self.maze_size[0] * TILE_SIZE + MARGIN
                    height = self.maze_size[1] * TILE_SIZE + MARGIN
                    self.update_display_mode(width, height)
                    pygame.event.clear()
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()
