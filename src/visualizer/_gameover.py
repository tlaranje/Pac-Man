from ._constants import TILE_COLOR, TEXT_COLOR, TILE_SIZE
from typing import TYPE_CHECKING
from src.utils import RoundRect
from ._button import Button
from pygame import Event
import pygame
import re
import json
import sys

if TYPE_CHECKING:
    from ._visualizer import Visualizer

BUTTON_SIZE = (250, 80)


class GameOver():
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.gameover_buttons: list[Button] = []
        self.title: str = "Game Over"
        self.show_error: bool = False
        self.text: str = ""
        self.active: bool = False

    def init_game_over_buttons(self) -> None:
        vis = self.vis
        b1_text = "Restart" if self.title == "GAME_OVER" else "Play again"
        self.gameover_buttons = [
            Button(
                size=BUTTON_SIZE, screen=vis.screen, text="Next Level",
                action="NEXT_LEVEL", text_size=40
            ),
            Button(
                size=BUTTON_SIZE, screen=vis.screen, text=b1_text,
                action="PLAY", text_size=40
            ),
            Button(
                size=BUTTON_SIZE, screen=vis.screen, text="Exit",
                action="QUIT_APP", text_size=40
            )
        ]

    def save_score(self) -> None:
        vis = self.vis
        file_name = vis.gameplay.config.settings.highscore_filename

        vis.leaderboard.append({vis.user_name: vis.maze.score})
        vis.leaderboard.sort(
            key=lambda entry: list(entry.values())[0],
            reverse=True
        )
        if len(vis.leaderboard) > 10:
            vis.leaderboard.pop()

        with open(file_name, "w") as fd:
            fd.write(json.dumps(vis.leaderboard, indent=4))

    def handle_game_over_events(self, event: Event) -> None:
        vis = self.vis
        gameplay = vis.gameplay

        if self.show_error:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.show_error = False
            return

        levels = gameplay.config.settings.levels
        if gameplay.map_idx >= len(levels) or self.title == "Game Over":
            buttons = self.gameover_buttons[1:]
        else:
            buttons = self.gameover_buttons

        for btn in buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    gameplay.level_start = None
                    gameplay.gameplay_init(0)
                    vis.maze.init_level()
                    maze_grid = vis.maze.maze_grid[gameplay.map_idx].maze
                    vis.maze_size = (
                        len(maze_grid) * TILE_SIZE, len(maze_grid) * TILE_SIZE
                    )
                    vis.maze.score = 0
                    vis.maze.lives = vis.gameplay.config.settings.lives
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

        if gameplay.map_idx + 1 >= len(levels) and self.title == "Win" or \
           self.title == "Game Over":
            self.handle_text_box_events(event)

    @staticmethod
    def is_valid_username(username: str) -> bool:
        if not isinstance(username, str):
            return False

        username = username.strip()

        if len(username) == 0:
            return False

        if len(username) > 10:
            return False

        return bool(re.fullmatch(r"[A-Za-z0-9 ]+", username))

    def handle_text_box_events(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                username = self.text.strip()

                if not self.is_valid_username(username):
                    self.show_error = True
                    return

                self.vis.user_name = self.text
                self.save_score()
                self.text = ""
                return
            else:
                test = self.vis.text_box_font.render(
                    self.text + event.unicode, True, (255, 255, 255)
                )
                if test.get_width() < self.rect.width - 10:
                    self.text += event.unicode

    def draw_error_popup(self, error_message: str = "") -> None:
        vis = self.vis
        wx, wy = vis.screen.get_size()

        overlay = pygame.Surface((wx, wy), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))
        vis.screen.blit(overlay, (0, 0))

        pw, ph = 250, 60
        popup_rect = pygame.Rect(wx // 2 - pw // 2, 20, pw, ph)

        RoundRect().draw(
            vis.screen, popup_rect, color=(40, 40, 40), b_size=2,
            b_color=pygame.Color("red")
        )

        txt = vis.error_font.render(error_message, True, (255, 255, 255))
        vis.screen.blit(txt, (popup_rect.centerx - txt.get_width() // 2, 30))

    def draw_user_selection(self) -> None:
        vis = self.vis
        sw, _ = vis.screen.get_size()
        centerx = sw // 2

        container_w = 350
        rect = pygame.Rect(
            sw // 2 - container_w // 2, 180, container_w, 200
        )
        RoundRect().draw(vis.screen, rect, b_size=2)

        text = vis.font.render("Enter username", True, TEXT_COLOR)
        text_rect = text.get_rect(centerx=centerx, y=240)
        vis.screen.blit(text, text_rect)

        text_box_size = (300, 50)
        tx, ty = text_box_size
        self.rect = pygame.Rect(centerx - tx // 2, 300, tx, ty)

        RoundRect().draw(vis.screen, self.rect, color=(60, 60, 60), b_size=0)

        border_color = (80, 80, 80) if self.active else (100, 100, 100)
        RoundRect().draw(vis.screen, self.rect, color=border_color, b_size=2)

        txt_surface = vis.text_box_font.render(
            self.text, True, TEXT_COLOR
        )
        vis.screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 7))

    def draw_game_over(self) -> None:
        vis = self.vis
        gameplay = vis.gameplay
        vis.screen.fill((50, 50, 50))

        sw, sh = vis.screen.get_size()
        container_w = 300
        levels = gameplay.config.settings.levels
        if gameplay.map_idx + 1 >= len(levels) and self.title == "Win" or \
           self.title == "Game Over":
            self.draw_user_selection()
        else:
            rect = pygame.Rect(
                sw // 2 - container_w // 2, 190, container_w, 50
            )
            RoundRect().draw(vis.screen, rect, b_size=2)

        title_surf = vis.title_font.render(
            self.title, True, TILE_COLOR
        )
        score_surf = vis.font.render(
            f"Score: {str(vis.maze.score)}", True, TEXT_COLOR
        )
        screen_w, screen_h = self.vis.screen.get_size()
        center_y = screen_h // 2

        self.vis.screen.blit(
            title_surf, (screen_w // 2 - title_surf.get_width() // 2, 0)
        )
        self.vis.screen.blit(
            score_surf, (screen_w // 2 - score_surf.get_width() // 2, 190)
        )
        levels = gameplay.config.settings.levels
        if gameplay.map_idx + 1 >= len(levels) or self.title == "Game Over":
            buttons = self.gameover_buttons[1:]
            btn_start_y = center_y - 85
        else:
            buttons = self.gameover_buttons
            btn_start_y = center_y - 125

        btn_width = BUTTON_SIZE[0]
        popup_x = screen_w // 2 - btn_width // 2

        for i, btn in enumerate(buttons):
            btn.rect.x = popup_x
            btn.rect.y = btn_start_y + i * 90

        for button in buttons:
            button.draw()

        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.update(mouse_pos)

        if self.show_error:
            self.draw_error_popup("Invalid username!")
