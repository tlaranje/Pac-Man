from ._constants import TILE_COLOR, TEXT_COLOR, TILE_SIZE
from typing import TYPE_CHECKING
from ._button import Button
from pygame import Event
import pygame
import sys

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
        b1_text = "Restart" if self.title == "GAME_OVER" else "Play again"
        self.gameover_buttons = [
            Button(
                screen=vis.screen, pos=(None, 110), text="Next Level",
                action="NEXT_LEVEL"
            ),
            Button(
                screen=vis.screen, pos=(None, 170), text=b1_text,
                action="PLAY"
            ),
            Button(
                screen=vis.screen, pos=(None, 230), text="Exit",
                action="QUIT_APP"
            )
        ]

    def handle_game_over_events(self, event: Event) -> None:
        vis = self.vis
        gameplay = vis.gameplay

        levels = gameplay.config.settings.levels
        if gameplay.map_idx >= len(levels) or self.title == "Game Over":
            buttons = self.gameover_buttons[1:]
        else:
            buttons = self.gameover_buttons

        for btn in buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    gameplay.level_start = None
                    gameplay.scores.pop()
                    vis.maze.score = sum(vis.gameplay.scores)
                    vis.maze.lives = 3
                    gameplay.reset()
                    vis.maze.player_ctrl.reset_state()
                    vis.maze.ghost_renderer.reset_visual_positions()
                    vis.maze.maze_surface.fill((0, 0, 0))
                    vis.state = "GAME_PLAY"
                    vis.maze.reset_maze()
                    return
                elif btn.action_value == "NEXT_LEVEL":
                    vis.maze_surface.fill((0, 0, 0))
                    gameplay.next_level()
                    vis.maze.init_level()
                    maze_grid = vis.maze.maze_grid[gameplay.map_idx].maze
                    vis.maze_size = (
                        len(maze_grid) * TILE_SIZE, len(maze_grid) * TILE_SIZE
                    )
                    vis.maze.reset_maze()
                    vis.state = "GAME_PLAY"
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()

    def draw_game_over(self) -> None:
        vis = self.vis
        gameplay = vis.gameplay

        vis.screen.fill((50, 50, 50))
        title_surface = self.title_font.render(
            self.title, True, TILE_COLOR
        )
        high_score_surface = self.font.render(
            f"Score: {str(gameplay.scores[-1])}", True, TEXT_COLOR
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
        levels = gameplay.config.settings.levels
        if gameplay.map_idx + 1 >= len(levels) or self.title == "Game Over":
            buttons = self.gameover_buttons[1:]
        else:
            buttons = self.gameover_buttons

        btn_width = 160
        popup_x = screen_w // 2 - btn_width // 2
        popup_rect = pygame.Rect(popup_x, 0, btn_width, screen_h)

        for i, btn in enumerate(buttons):
            btn.rect.x = popup_rect.x
            btn.rect.y = 110 + i * 60

        for button in buttons:
            button.draw()

        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.update(mouse_pos)
