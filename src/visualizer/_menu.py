from ._constants import TILE_COLOR, TILE_SIZE, SCREEN_SIZE
from typing import TYPE_CHECKING
from ._button import Button
import pygame
import sys

if TYPE_CHECKING:
    from ._visualizer import Visualizer

BUTTON_SIZE = (300, 100)


class Menu:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer

        self.menu_buttons: list[Button] = []
        self.pause_menu_buttons: list[Button] = []
        self.cheat_menu_buttons: list[Button] = []

        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self.pause_surface = pygame.Surface((0, 0), pygame.SRCALPHA)
        self.cheat_surface = pygame.Surface((0, 0), pygame.SRCALPHA)

    def init_buttons(self) -> None:
        vis = self.vis
        x = SCREEN_SIZE[0] - 180

        self.cheat_menu_buttons = [
            Button(
                screen=self.cheat_surface, pos=(x, 20),
                text="Invincibility", action="CHEAT_INV"
            ),
            Button(
                screen=self.cheat_surface, pos=(x, 80),
                text="Level skip", action="CHEAT_SKIP"
            ),
            Button(
                screen=self.cheat_surface, pos=(x, 140),
                text="Ghost freeze", action="CHEAT_FREEZE"
            ),
            Button(
                screen=self.cheat_surface, pos=(x, 200),
                text="Extra lives", action="CHEAT_LIVES"
            ),
            Button(
                screen=self.cheat_surface, pos=(x, 260),
                text="Player speed", action="NONE", disabled=True
            ),
            Button(
                screen=self.cheat_surface, size=(50, 50), pos=(x, 320),
                text="+", action="CHEAT_SPEED+"
            ),
            Button(
                screen=self.cheat_surface, size=(50, 50), pos=(x + 110, 320),
                text="-", action="CHEAT_SPEED-"
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
                action="PLAY", text_size=40

            ),
            Button(
                size=BUTTON_SIZE, screen=vis.screen, text_size=40,
                text="Leaderboard", action="LEADERBOARD"
            ),
            Button(
                size=BUTTON_SIZE, screen=vis.screen, text_size=40,
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
                    vis.make.level_score = 0
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.vis.state = 'PAUSE'
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

        screen_w, screen_h = vis.screen.get_size()
        center_x = screen_w // 2
        center_y = screen_h // 2

        text_surf = vis.title_font.render("Pac-Man", True, TILE_COLOR)
        text_rect = text_surf.get_rect(centerx=center_x, y=50)
        vis.screen.blit(text_surf, text_rect)

        btn_width = BUTTON_SIZE[0]
        popup_x = center_x - btn_width // 2
        btn_start_y = center_y - 160

        for i, btn in enumerate(self.menu_buttons):
            btn.rect.x = popup_x
            btn.rect.y = btn_start_y + i * 110

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.menu_buttons:
            btn.update(mouse_pos)
            btn.draw()

    def draw_pause_menu(self) -> None:
        vis = self.vis
        current_size = vis.screen.get_size()

        if self.pause_surface.get_size() != current_size:
            self.pause_surface = pygame.Surface(current_size, pygame.SRCALPHA)
            for btn in self.pause_menu_buttons:
                btn.screen = self.pause_surface

        self.pause_surface.fill((0, 0, 0, 0))

        wx, wy = current_size
        pw, ph = 200, wy
        popup_rect = pygame.Rect(0, 0, pw, ph)

        pygame.draw.rect(self.pause_surface, (40, 40, 40), popup_rect)
        pygame.draw.line(
            self.pause_surface, TILE_COLOR, (pw, 0), (pw, wy), 2
        )

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.pause_menu_buttons:
            btn.update(mouse_pos)
            btn.draw()

        vis.screen.blit(self.pause_surface, (0, 0))

    def draw_cheat_menu(self) -> None:
        vis = self.vis
        current_size = vis.screen.get_size()

        if self.cheat_surface.get_size() != current_size:
            self.cheat_surface = pygame.Surface(current_size, pygame.SRCALPHA)
            for btn in self.cheat_menu_buttons:
                btn.screen = self.cheat_surface

        self.cheat_surface.fill((0, 0, 0, 0))

        wx, wy = current_size
        pw, ph = 200, wy
        popup_rect = pygame.Rect(wx - pw, 0, pw, ph)

        pygame.draw.rect(self.cheat_surface, (40, 40, 40), popup_rect)
        pygame.draw.line(
            self.cheat_surface, TILE_COLOR, (wx - pw, 0), (wx - pw, wy), 2
        )

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.cheat_menu_buttons:
            if btn.action_value == "NONE":
                btn.text = f"Speed: {vis.maze.player_ctrl.speed}"
            btn.update(mouse_pos)
            btn.draw()

        vis.screen.blit(self.cheat_surface, (0, 0))
