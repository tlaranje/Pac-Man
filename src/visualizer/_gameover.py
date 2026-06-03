from ._constants import TILE_COLOR, TEXT_COLOR, TILE_SIZE
from typing import TYPE_CHECKING
from ._button import Button
from pygame import Event
import pygame
import json
import sys

if TYPE_CHECKING:
    from .._visualizer import Visualizer

BUTTON_SIZE = (300, 100)


class GameOver():
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.gameover_buttons: list[Button] = []
        self.title: str = "Game Over"
        self.show_error: bool = False
        self.text: str = "Hi"
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
        gameplay = vis.gameplay
        settings = gameplay.config.settings

        if gameplay.map_idx + 1 >= len(settings.levels) or vis.maze.lives <= 0:
            vis.leaderboard.append({vis.user_name: vis.maze.score})
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
                    username = self.text.strip()

                    if username == "":
                        self.show_error = True
                        return

                    vis.user_name = username
                    gameplay.level_start = None
                    self.save_score()
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

        self.handle_text_box_events(event)

    def handle_text_box_events(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.vis.user_name = self.text
                self.save_score()
                self.text = ""
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
        popup_rect = pygame.Rect(wx // 2 - pw // 2, wy // 2 - ph // 2, pw, ph)
        pygame.draw.rect(
            vis.screen, (40, 40, 40), popup_rect, border_radius=8
        )
        pygame.draw.rect(
            vis.screen, (220, 50, 50), popup_rect, 2, border_radius=8
        )

        txt = vis.font.render(error_message, True, (255, 255, 255))
        vis.screen.blit(txt, (
            popup_rect.centerx - txt.get_width() // 2,
            popup_rect.centery - txt.get_height() // 2
        ))

    def draw_user_selection(self) -> None:
        vis = self.vis
        wx, wy = vis.screen.get_size()
        centerx = wx // 2

        text = vis.font.render("Enter username", True, TILE_COLOR)
        text_rect = text.get_rect(centerx=centerx, y=250)
        vis.screen.blit(text, text_rect)

        text_box_size = (150, 40)
        tx, ty = text_box_size
        self.rect = pygame.Rect(centerx - tx // 2, 300, tx, ty)

        pygame.draw.rect(vis.screen, (60, 60, 60), self.rect)
        color = (255, 255, 255) if self.active else (100, 100, 100)
        pygame.draw.rect(vis.screen, color, self.rect, 2)

        txt_surface = vis.text_box_font.render(
            self.text, True, (255, 255, 255)
        )
        vis.screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 7))

    def draw_game_over(self) -> None:
        vis = self.vis
        gameplay = vis.gameplay
        vis.screen.fill((50, 50, 50))

        self.draw_user_selection()

        title_surface = vis.title_font.render(
            self.title, True, TILE_COLOR
        )
        high_score_surface = vis.font.render(
            f"Score: {str(vis.maze.score)}", True, TEXT_COLOR
        )
        screen_w, screen_h = self.vis.screen.get_size()
        center_y = screen_h // 2

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
            btn_start_y = center_y - 105
        else:
            buttons = self.gameover_buttons
            btn_start_y = center_y - 160

        btn_width = BUTTON_SIZE[0]
        popup_x = screen_w // 2 - btn_width // 2

        for i, btn in enumerate(buttons):
            btn.rect.x = popup_x
            btn.rect.y = btn_start_y + i * 110

        for button in buttons:
            button.draw()

        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.update(mouse_pos)

        pygame.draw.aaline(
            vis.screen, pygame.Color("red"), (screen_w // 2, 0),
            (screen_w // 2, screen_h)
        )
        pygame.draw.aaline(
            vis.screen, pygame.Color("red"), (0, screen_h // 2),
            (screen_w, screen_h // 2)
        )

        if self.show_error:
            self.draw_error_popup("Empty username!")
