from ._constants import (
    BUTTON_SIZE, TILE_SIZE, MARGIN, MAZE_OFFSET, TILE_COLOR, TEXT_COLOR
)
from typing import TYPE_CHECKING
from ._button import Button
from pygame import Event
import pygame

if TYPE_CHECKING:
    from .._visualizer import Visualizer


class GameOver():
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.gameover_buttons: list[Button] = []
        self.title: str = "Game Over"
        self.title_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 40
        )
        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 30
        )

    def init_game_over_buttons(self) -> None:
        vis = self.vis
        win_size = self.vis.screen.get_size()
        b1_text = "Restart" if self.title == "GAME_OVER" else "Play again"
        self.gameover_buttons = [
            Button(
                screen=vis.screen, win_size=win_size,
                size=BUTTON_SIZE, pos=(None, 110), text=b1_text, action="PLAY"
            ),
            Button(
                screen=vis.screen, win_size=win_size,
                size=BUTTON_SIZE, pos=(None, 180), text="Exit",
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
        title_surface = self.title_font.render(
            self.title, True, TILE_COLOR
        )
        high_score_surface = self.font.render(
            f"Score: {str(vis.gameplay.scores[-1])}", True, TEXT_COLOR
        )
        screen_w, screen_h = self.vis.screen.get_size()

        self.vis.screen.blit(
            title_surface,
            (screen_w // 2 - title_surface.get_width() // 2, 10)
        )
        self.vis.screen.blit(
            high_score_surface,
            (screen_w // 2 - high_score_surface.get_width() // 2, 60)
        )

        for button in self.gameover_buttons:
            button.setup_button()
            button.draw()

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.gameover_buttons:
            btn.update(mouse_pos)
