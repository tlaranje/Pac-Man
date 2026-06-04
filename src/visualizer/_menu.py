from ._constants import TILE_COLOR, TILE_SIZE, SCREEN_SIZE
from typing import TYPE_CHECKING
from src.utils import RoundRect
from ._button import Button
from pygame import Rect
import pygame
import sys

if TYPE_CHECKING:
    from ._visualizer import Visualizer

BUTTON_SIZE = (250, 80)
SW, SH = SCREEN_SIZE
INS_SIZE = (500, 500)
CHEAT_MENU_SIZE = (250, 390)
PAUSE_MENU_SIZE = (250, 270)


class Menu:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer

        self.cheat_menu_open: bool = False

        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.pause_surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.cheat_surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.ins_surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.leaderboard_surface = pygame.Surface(
            SCREEN_SIZE, pygame.SRCALPHA
        )

        self.menu_buttons: list[Button] = []
        self.pause_menu_buttons: list[Button] = []
        self.cheat_menu_buttons: list[Button] = []
        self.cheat_button: Button
        self.close_button: Button

    def _make_button(self, screen, text, action, **kwargs) -> Button:
        return Button(screen=screen, text=text, action=action, **kwargs)

    def init_buttons(self) -> None:
        vis = self.vis
        cs = self.cheat_surface
        ps = self.pause_surface

        self.close_button = self._make_button(
            vis.screen, "Close", "CLOSE", text_size=30,
            size=(100, 50), offset_y=1
        )

        self.cheat_button = self._make_button(
            vis.screen, "Cheat Menu", "CHEAT",
            pos=(SW - 170, SH // 2 - 25)
        )

        self.close_cheat_button = self._make_button(
            cs, ">", "CLOSE_CHEAT", size=(50, 50), text_size=29
        )

        self.cheat_menu_buttons = [
            self._make_button(cs, "Invincibility", "CHEAT_INV"),
            self._make_button(cs, "Level skip", "CHEAT_SKIP"),
            self._make_button(cs, "Ghost freeze", "CHEAT_FREEZE"),
            self._make_button(cs, "Extra lives", "CHEAT_LIVES"),
            self._make_button(
                cs, "Player speed", "NONE", disabled=True
            ),
            self._make_button(cs, "+", "CHEAT_SPEED+", size=(50, 50)),
            self._make_button(cs, "-", "CHEAT_SPEED-", size=(50, 50)),
        ]

        self.pause_menu_buttons = [
            self._make_button(ps, "Return",    "PLAY",     pos=(20, 20)),
            self._make_button(ps, "Restart",   "RESTART",  pos=(20, 80)),
            self._make_button(
                ps, "Main Menu", "RMain", pos=(20, 140)
            ),
            self._make_button(
                ps, "Exit", "QUIT_APP", pos=(20, 200)
            ),
        ]

        self.menu_buttons = [
            self._make_button(
                vis.screen, "Play", "PLAY",
                size=BUTTON_SIZE, text_size=35
            ),
            self._make_button(
                vis.screen, "Instructions", "INSTRUCTIONS",
                size=BUTTON_SIZE, text_size=35
            ),
            self._make_button(
                vis.screen, "Leaderboard", "LEADERBOARD",
                size=BUTTON_SIZE, text_size=35
            ),
            self._make_button(
                vis.screen, "Exit", "QUIT_APP",
                size=BUTTON_SIZE, text_size=35
            ),
        ]

    def _quit(self) -> None:
        pygame.quit()
        sys.exit()

    def _draw_buttons(self, buttons: list[Button]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw()

    def handle_pause_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            vis.state = "GAME_PLAY"
            return

        for btn in self.pause_menu_buttons:
            if not btn.is_clicked(event):
                continue
            match btn.action_value:
                case "PLAY":
                    vis.state = "GAME_PLAY"
                case "RESTART":
                    vis.gameplay.level_start = None
                    vis.gameplay.gameplay_init(0)
                    vis.maze.init_level()
                    maze_grid = vis.maze.maze_grid[vis.gameplay.map_idx].maze
                    vis.maze_size = (
                        len(maze_grid) * TILE_SIZE, len(maze_grid) * TILE_SIZE
                    )
                    vis.maze.score = 0
                    vis.maze.lives = vis.gameplay.config.settings.lives
                    vis.gameplay.reset()
                    vis.maze.player_ctrl.reset_state()
                    vis.maze.ghost_renderer.reset_visual_positions()
                    vis.maze.maze_surface.fill((0, 0, 0))
                    vis.state = "GAME_PLAY"
                    vis.maze.reset_maze()
                case "RMain":
                    vis.state = "MAIN_MENU"
                    vis.maze.handle_player_death(0, True)
                case "QUIT_APP":
                    self._quit()
            return

    def handle_cheat_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis

        if not self.cheat_menu_open:
            if self.cheat_button.is_clicked(event):
                self.cheat_menu_open = True
            return

        if self.close_cheat_button.is_clicked(event):
            self.cheat_menu_open = False
            return

        for btn in self.cheat_menu_buttons:
            if not btn.is_clicked(event):
                continue
            match btn.action_value:
                case "CHEAT_INV":
                    vis.gameplay.player.toggle_invencibility()
                case "CHEAT_SKIP":
                    vis.maze.player_ctrl.game_started = False
                    vis.state = "GAME_PLAY"
                    vis.maze_surface.fill((0, 0, 0))
                    vis.gameplay.next_level()
                    vis.maze.init_level()
                    maze_grid = (
                        vis.maze.maze_grid[vis.gameplay.map_idx].maze
                    )
                    vis.maze_size = (len(maze_grid) * TILE_SIZE,) * 2
                    vis.maze.reset_maze()
                case "CHEAT_FREEZE":
                    vis.gameplay.toggle_freeze_ghosts()
                case "CHEAT_LIVES":
                    vis.maze.give_extra_lives()
                case "CHEAT_SPEED+":
                    vis.maze.increase_player_speed()
                case "CHEAT_SPEED-":
                    vis.maze.decrease_player_speed()
            return

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis
        gameplay = vis.gameplay

        for btn in self.menu_buttons:
            if not btn.is_clicked(event):
                continue
            match btn.action_value:
                case "PLAY":
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
                case "INSTRUCTIONS":
                    self._ins_bg = vis.screen.copy()
                    vis.state = "INSTRUCTIONS"
                case "QUIT_APP":
                    self._quit()
            return

    def draw_main_menu(self) -> None:
        vis = self.vis
        vis.screen.fill((50, 50, 50))

        center_x = SW // 2

        text_surf = vis.title_font.render("Pac-Man", True, TILE_COLOR)
        vis.screen.blit(
            text_surf, text_surf.get_rect(centerx=center_x, y=50)
        )

        popup_x = center_x - BUTTON_SIZE[0] // 2
        btn_start_y = SH // 2 - 160

        for i, btn in enumerate(self.menu_buttons):
            btn.rect.x = popup_x
            btn.rect.y = btn_start_y + i * 90

        self._draw_buttons(self.menu_buttons)

    def draw_pause_menu(self) -> None:
        vis = self.vis
        pw, ph = PAUSE_MENU_SIZE

        self.pause_surface.fill((0, 0, 0, 0))
        rect = pygame.Rect(-45, SH // 2 - ph // 2, pw, ph)
        RoundRect().draw(self.pause_surface, rect, b_size=2)

        btn_start_y = SH // 2 - ph // 2 + 20
        for i, btn in enumerate(self.pause_menu_buttons):
            btn.rect.x = 20
            btn.rect.y = btn_start_y + i * 60

        self._draw_buttons(self.pause_menu_buttons)
        vis.screen.blit(self.pause_surface, (0, 0))

    def draw_cheat_menu(self) -> None:
        vis = self.vis
        pw, ph = CHEAT_MENU_SIZE

        self.cheat_surface.fill((0, 0, 0, 0))
        rect = pygame.Rect(SW - pw + 45, SH // 2 - ph // 2, pw, ph)
        RoundRect().draw(self.cheat_surface, rect, b_size=2)

        self.close_cheat_button.rect.x = SW - 270
        self.close_cheat_button.rect.y = SH // 2 - 25

        btn_width = 150
        popup_x = SW - btn_width - 30
        btn_start_y = SH // 2 - ph // 2 + 20

        for i, btn in enumerate(self.cheat_menu_buttons):
            if btn.text == "-":
                btn.rect.x = popup_x + btn_width - 40
                btn.rect.y = btn_start_y + (i - 1) * 60
            else:
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

    def draw_instructions(self) -> None:
        vis = self.vis
        pw, ph = INS_SIZE
        mouse_pos = pygame.mouse.get_pos()
        close_btm = self.close_button

        if hasattr(self, '_ins_bg'):
            vis.screen.blit(self._ins_bg, (0, 0))

        self.ins_surface.fill((0, 0, 0, 0))

        left = SW // 2 - pw // 2
        top = SH // 2 - ph // 2

        rect = Rect(left, top, pw, ph)
        RoundRect().draw(self.ins_surface, rect, b_size=2)

        vis.screen.blit(self.ins_surface, (0, 0))

        close_btm.screen = vis.screen
        close_btm.rect.x = left
        close_btm.rect.y = top
        close_btm.update(mouse_pos)
        close_btm.draw()
