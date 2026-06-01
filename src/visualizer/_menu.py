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

    def draw_user_selection(self) -> None:
        vis = self.vis

        vis.screen.fill((50, 50, 50))

    def draw_main_menu(self) -> None:
        vis = self.vis

        if vis.screen.get_size() != MENU_SIZE and vis.state == "MAIN_MENU":
            x, y = MENU_SIZE
            self.vis.window.update_display_mode(x, y)

        vis.screen.fill((50, 50, 50))
        text_surf = self.title_font.render("Pac-Man", True, TILE_COLOR)
        text_rect = text_surf.get_rect(
            centerx=vis.screen.get_rect().centerx, y=10
        )
        vis.screen.blit(text_surf, text_rect)
        for btn in self.menu_buttons:
            btn.draw()

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis

        for btn in self.menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    width = vis.maze.size[0] * TILE_SIZE + MARGIN
                    height = (
                        vis.maze.size[1] * TILE_SIZE + MARGIN + MAZE_OFFSET
                    )
                    vis.window.update_display_mode(width, height)
                    vis.state = 'GAME_PLAY'
                    vis.renderer.draw_walls(vis.maze.maze_grid.maze)
                    vis.renderer.draw_pacgums(
                        vis.maze.gameplay.pacgums_maps[0],
                        vis.maze.fruit_sprites
                    )
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()
