from ._constants import TILE_COLOR, TILE_SIZE, SCREEN_SIZE
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
        self.pause_menu_buttons: list[Button] = []
        self.cheat_menu_buttons: list[Button] = []

        self.title_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 50
        )
        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 25
        )
        self.text_box_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 19
        )

        self.active: bool = False
        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.text: str = "Hi"
        self.show_error: bool = False

        self.pause_surface = pygame.Surface((0, 0), pygame.SRCALPHA)
        self.cheat_surface = pygame.Surface((0, 0), pygame.SRCALPHA)

    def init_buttons(self) -> None:
        vis = self.vis
        x = SCREEN_SIZE[0] - 170

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
                screen=self.cheat_surface, size=(50, 50), pos=(x + 100, 320),
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
                text="Main Menu", action="RMain"
            ),
            Button(
                screen=self.pause_surface, pos=(20, 140),
                text="Exit", action="QUIT_APP"
            ),
        ]

        self.menu_buttons = [
            Button(
                screen=vis.screen, pos=(None, 180),
                text="Play", action="PLAY"
            ),
            Button(
                screen=vis.screen, pos=(None, 250),
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
                    vis.state = "GAME_PLAY"
                    vis.maze_surface.fill((0, 0, 0))
                    vis.gameplay.next_level()
                    vis.maze.init_level()
                    maze_grid = vis.maze.maze_grid[vis.gameplay.map_idx].maze
                    vis.maze_size = (
                        len(maze_grid) * TILE_SIZE, len(maze_grid) * TILE_SIZE
                    )
                    vis.renderer.draw_walls(maze_grid)
                    vis.renderer.draw_pacgums(
                        vis.maze.gameplay.pacgums_maps[
                            vis.maze.gameplay.map_idx
                        ],
                        vis.maze.fruit_sprites
                    )
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

    def handle_text_box_events(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.vis.user_name = self.text
                self.text = ""
            else:
                test = self.text_box_font.render(
                    self.text + event.unicode, True, (255, 255, 255)
                )
                if test.get_width() < self.rect.width - 10:
                    self.text += event.unicode

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis

        if self.show_error:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.show_error = False
            return

        self.handle_text_box_events(event)

        for btn in self.menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    username = self.text.strip()

                    if username == "":
                        self.show_error = True
                        return

                    vis.user_name = username
                    vis.state = 'GAME_PLAY'
                    vis.renderer.draw_walls(
                        vis.maze.maze_grid[vis.gameplay.map_idx].maze
                    )
                    vis.renderer.draw_pacgums(
                        vis.maze.gameplay.pacgums_maps[
                            vis.maze.gameplay.map_idx
                        ],
                        vis.maze.fruit_sprites
                    )
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()

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

        txt = self.font.render(error_message, True, (255, 255, 255))
        vis.screen.blit(txt, (
            popup_rect.centerx - txt.get_width() // 2,
            popup_rect.centery - txt.get_height() // 2
        ))

    def draw_user_selection(self) -> None:
        vis = self.vis
        text = self.font.render("Enter username", True, TILE_COLOR)
        text_rect = text.get_rect(centerx=vis.screen.get_rect().centerx, y=80)
        vis.screen.blit(text, text_rect)

        text_box_size = (150, 40)
        tx, ty = text_box_size
        wx, wy = vis.screen.get_size()
        self.rect = pygame.Rect(wx // 2 - tx // 2, 120, tx, ty)

        pygame.draw.rect(vis.screen, (60, 60, 60), self.rect)
        color = (255, 255, 255) if self.active else (100, 100, 100)
        pygame.draw.rect(vis.screen, color, self.rect, 2)

        txt_surface = self.text_box_font.render(
            self.text, True, (255, 255, 255)
        )
        vis.screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 7))

    def draw_main_menu(self) -> None:
        vis = self.vis

        vis.screen.fill((50, 50, 50))

        text_surf = self.title_font.render("Pac-Man", True, TILE_COLOR)
        text_rect = text_surf.get_rect(
            centerx=vis.screen.get_rect().centerx, y=10
        )
        vis.screen.blit(text_surf, text_rect)

        self.draw_user_selection()

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.menu_buttons:
            btn.update(mouse_pos)
            btn.draw()

        if self.show_error:
            self.draw_error_popup("Empty username!")

    def draw_pause_menu(self) -> None:
        vis = self.vis
        current_size = vis.screen.get_size()

        if self.pause_surface.get_size() != current_size:
            self.pause_surface = pygame.Surface(current_size, pygame.SRCALPHA)
            for btn in self.pause_menu_buttons:
                btn.screen = self.pause_surface

        self.pause_surface.fill((0, 0, 0, 0))

        wx, wy = current_size
        pw, ph = 190, wy
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
        pw, ph = 190, wy
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
