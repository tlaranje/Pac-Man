from ._constants import BUTTON_SIZE, TILE_SIZE, MARGIN, MAZE_OFFSET
from typing import TYPE_CHECKING
from ._button import Button
from pygame import Event
from pygame import Color
import pygame

if TYPE_CHECKING:
    from .._visualizer import Visualizer


class GameOver():
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.gameover_buttons: list[Button] = []
        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 40
        )

    def init_game_over_buttons(self) -> None:
        vis = self.vis
        win_size = self.vis.screen.get_size()

        self.gameover_buttons = [
            Button(
                screen=vis.screen, win_size=win_size,
                size=BUTTON_SIZE, pos=(None, 100), text="Play", action="PLAY"
            ),
            Button(
                screen=vis.screen, win_size=win_size,
                size=BUTTON_SIZE, pos=(None, 170), text="Exit",
                action="QUIT_APP"
            )
        ]

    def handle_game_over_events(self, event: Event) -> None:
        vis = self.vis

        for btn in self.gameover_buttons:
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
                    vis.state = "MAIN_MENU"

    def draw_game_over(self) -> None:
        vis = self.vis

        vis.screen.fill((50, 50, 50))
        high_score_surface = self.font.render(
            "Game Over", True, Color("white")
        )
        screen_w, screen_h = self.vis.screen.get_size()

        self.vis.screen.blit(
            high_score_surface,
            (screen_w // 2 - high_score_surface.get_width() // 2, 10)
        )

        for button in self.gameover_buttons:
            button.draw()
