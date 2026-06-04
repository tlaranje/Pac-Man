from ._constants import TILE_COLOR, TILE_SIZE, SCREEN_SIZE
from typing import TYPE_CHECKING
from src.utils import RoundRect
from ._button import Button
import pygame
import sys

if TYPE_CHECKING:
    from ._visualizer import Visualizer

BUTTON_SIZE = (250, 80)


class Menu:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer

        self.menu_buttons: list[Button] = []
        self.pause_menu_buttons: list[Button] = []
        self.cheat_menu_buttons: list[Button] = []
        self.cheat_button: Button

        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self.pause_surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.cheat_surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.cheat_menu_open: bool = False

    def init_buttons(self) -> None:
        vis = self.vis

        self.cheat_button = Button(
            screen=vis.screen, text="Cheat Menu", action="CHEAT",
            pos=(SCREEN_SIZE[0] - 170, SCREEN_SIZE[1] // 2 - 25)
        )

        self.close_cheat_button = Button(
            screen=self.cheat_surface, size=(40, 40), text="X",
            action="CLOSE_CHEAT", text_size=20
        )

        self.cheat_menu_buttons = [
            Button(
                screen=self.cheat_surface, text="Invincibility",
                action="CHEAT_INV"
            ),
            Button(
                screen=self.cheat_surface, text="Level skip",
                action="CHEAT_SKIP"
            ),
            Button(
                screen=self.cheat_surface, text="Ghost freeze",
                action="CHEAT_FREEZE"
            ),
            Button(
                screen=self.cheat_surface, text="Extra lives",
                action="CHEAT_LIVES"
            ),
            Button(
                screen=self.cheat_surface, text="Player speed",
                action="NONE", disabled=True
            ),
            Button(
                screen=self.cheat_surface, size=(50, 50), text="+",
                action="CHEAT_SPEED+"
            ),
            Button(
                screen=self.cheat_surface, size=(50, 50), text="-",
                action="CHEAT_SPEED-"
            ),
        ]

        self.pause_menu_buttons = [
            Button(
                screen=self.pause_surface, pos=(20, 20),
                text="Return", action="PLAY"
            ),
            Button(
                screen=self.pause_surface, pos=(20, 80),
                text="Restart", action="RESTART"
            ),
            Button(
                screen=self.pause_surface, pos=(20, 140),
                text="Main Menu", action="RMain"
            ),
            Button(
                screen=self.pause_surface, pos=(20, 200),
                text="Exit", action="QUIT_APP"
            ),
        ]

        self.menu_buttons = [
            Button(
                size=BUTTON_SIZE, screen=vis.screen, text="Play",
                action="PLAY", text_size=35

            ),
            Button(
                size=BUTTON_SIZE, screen=vis.screen, text_size=35,
                text="Leaderboard", action="LEADERBOARD"
            ),
            Button(
                size=BUTTON_SIZE, screen=vis.screen, text_size=35,
                text="Exit", action="QUIT_APP"
            )
        ]

    def handle_pause_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.vis.state = 'GAME_PLAY'
                return

        for btn in self.pause_menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    vis.state = 'GAME_PLAY'
                    return
                elif btn.action_value == "RESTART":
                    vis.maze.level_score = 0
                    vis.maze.score = 0
                    vis.maze.lives = vis.gameplay.config.settings.lives
                    vis.gameplay.reset()
                    vis.maze.player_ctrl.reset_state()
                    vis.maze.ghost_renderer.reset_visual_positions()
                    vis.maze.maze_surface.fill((0, 0, 0))
                    vis.state = "GAME_PLAY"
                    vis.maze.reset_maze()
                elif btn.action_value == "RMain":
                    vis.state = 'MAIN_MENU'
                    vis.maze.handle_player_death(0, True)
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()

    def handle_cheat_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis

        if self.cheat_button.is_clicked(event):
            self.cheat_menu_open = not self.cheat_menu_open
            return

        if not self.cheat_menu_open:
            return

        if self.close_cheat_button.is_clicked(event):
            self.cheat_menu_open = False
            return

        for btn in self.cheat_menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "CHEAT_INV":
                    vis.gameplay.player.toggle_invencibility()
                    return
                elif btn.action_value == "CHEAT_SKIP":
                    vis.maze.player_ctrl.game_started = False
                    vis.state = "GAME_PLAY"
                    vis.maze_surface.fill((0, 0, 0))
                    vis.gameplay.next_level()
                    vis.maze.init_level()
                    maze_grid = vis.maze.maze_grid[vis.gameplay.map_idx].maze
                    vis.maze_size = (
                        len(maze_grid) * TILE_SIZE, len(maze_grid) * TILE_SIZE
                    )
                    vis.maze.reset_maze()
                    return
                elif btn.action_value == "CHEAT_FREEZE":
                    vis.gameplay.toggle_freeze_ghosts()
                    return
                elif btn.action_value == "CHEAT_LIVES":
                    vis.maze.give_extra_lives()
                    return
                elif btn.action_value == "CHEAT_SPEED+":
                    vis.maze.increase_player_speed()
                elif btn.action_value == "CHEAT_SPEED-":
                    vis.maze.decrease_player_speed()
                    return

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis

        for btn in self.menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    vis.maze.reset_maze()
                    vis.state = 'GAME_PLAY'
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()

    def draw_main_menu(self) -> None:
        vis = self.vis
        vis.screen.fill((50, 50, 50))

        sw, sh = vis.screen.get_size()
        center_x = sw // 2
        center_y = sh // 2

        text_surf = vis.title_font.render("Pac-Man", True, TILE_COLOR)
        text_rect = text_surf.get_rect(centerx=center_x, y=50)
        vis.screen.blit(text_surf, text_rect)

        btn_width = BUTTON_SIZE[0]
        popup_x = center_x - btn_width // 2
        btn_start_y = center_y - 160

        for i, btn in enumerate(self.menu_buttons):
            btn.rect.x = popup_x
            btn.rect.y = btn_start_y + i * 90

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.menu_buttons:
            btn.update(mouse_pos)
            btn.draw()

    def draw_pause_menu(self) -> None:
        vis = self.vis
        current_size = vis.screen.get_size()

        self.pause_surface.fill((0, 0, 0, 0))

        sw, sh = current_size
        pw, ph = 250, 270
        rect = pygame.Rect(-45, sh // 2 - ph // 2, pw, ph)

        RoundRect().draw(self.pause_surface, rect, b_size=2)

        popup_x = 20
        btn_start_y = sh // 2 - ph // 2 + 20

        for i, btn in enumerate(self.pause_menu_buttons):
            btn.rect.x = popup_x
            btn.rect.y = btn_start_y + i * 60

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.pause_menu_buttons:
            btn.update(mouse_pos)
            btn.draw()

        vis.screen.blit(self.pause_surface, (0, 0))

    def draw_cheat_menu(self) -> None:
        vis = self.vis
        current_size = vis.screen.get_size()
        sw, sh = current_size

        self.cheat_surface.fill((0, 0, 0, 0))

        pw, ph = 250, 440
        popup_rect = pygame.Rect(sw - pw + 45, sh // 2 - ph // 2, pw, ph)
        RoundRect().draw(self.cheat_surface, popup_rect, b_size=2)

        self.close_cheat_button.rect.x = sw - pw + 70
        self.close_cheat_button.rect.y = sh // 2 - ph // 2 + 20

        btn_width = 150
        popup_x = sw - btn_width - 30
        btn_start_y = sh // 2 - ph // 2 + 70

        for i, btn in enumerate(self.cheat_menu_buttons):
            if btn.text == "-":
                btn.rect.x = popup_x + btn_width - 40
                btn.rect.y = btn_start_y + (i - 1) * 60
                continue

            btn.rect.x = popup_x
            btn.rect.y = btn_start_y + i * 60

        mouse_pos = pygame.mouse.get_pos()

        self.close_cheat_button.update(mouse_pos)
        self.close_cheat_button.draw()

        for btn in self.cheat_menu_buttons:
            if btn.action_value == "NONE":
                btn.text = f"Speed: {vis.maze.player_ctrl.speed}"
            btn.update(mouse_pos)
            btn.draw()

        vis.screen.blit(self.cheat_surface, (0, 0))
