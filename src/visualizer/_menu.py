from ._constants import (
    MENU_SIZE, BUTTON_SIZE, TILE_COLOR, TILE_SIZE, MARGIN, MAZE_OFFSET
)
from typing import TYPE_CHECKING
from ._button import Button
import pygame
import sys

if TYPE_CHECKING:
    from ._visualizer import Visualizer


class Menu:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.menu_buttons: list[Button] = []
        self.title_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 50
        )

    def init_menu_buttons(self) -> None:
        vis = self.vis

        self.menu_buttons = [
            Button(
                screen=vis.screen, win_size=MENU_SIZE,
                size=BUTTON_SIZE, pos=(None, 100), text="Play", action="PLAY"
            ),
            Button(
                screen=vis.screen, win_size=MENU_SIZE,
                size=BUTTON_SIZE, pos=(None, 170), text="Exit",
                action="QUIT_APP"
            )
        ]

    def draw_main_menu(self) -> None:
        text_surf = self.title_font.render("Pac-Man", True, TILE_COLOR)
        text_rect = text_surf.get_rect(
            centerx=self.vis.screen.get_rect().centerx, y=10
        )
        self.vis.screen.blit(text_surf, text_rect)
        for btn in self.menu_buttons:
            btn.draw()

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis

        for btn in self.menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    self.state = 'GAME_PLAY'
                    width = vis.maze.size[0] * TILE_SIZE + MARGIN
                    height = (
                        vis.maze.size[0] * TILE_SIZE + MARGIN + MAZE_OFFSET
                    )
                    vis.window.update_display_mode(width, height)
                    pygame.event.clear()
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()
