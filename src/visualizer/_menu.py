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
        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 25
        )
        self.text_box_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 20
        )
        self.active: bool = False
        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.text: str = ""
        self.show_error: bool = False
        self.error_message: str = ""

    def init_menu_buttons(self) -> None:
        vis = self.vis

        self.menu_buttons = [
            Button(
                screen=vis.screen, win_size=MENU_SIZE,
                size=BUTTON_SIZE, pos=(None, 180), text="Play", action="PLAY"
            ),
            Button(
                screen=vis.screen, win_size=MENU_SIZE,
                size=BUTTON_SIZE, pos=(None, 250), text="Exit",
                action="QUIT_APP"
            )
        ]

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

    def draw_error_popup(self) -> None:
        vis = self.vis
        wx, wy = vis.screen.get_size()

        overlay = pygame.Surface((wx, wy), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        vis.screen.blit(overlay, (0, 0))

        pw, ph = 220, 90
        popup_rect = pygame.Rect(wx // 2 - pw // 2, wy // 2 - ph // 2, pw, ph)
        pygame.draw.rect(
            vis.screen, (60, 60, 60), popup_rect, border_radius=8
        )
        pygame.draw.rect(
            vis.screen, (200, 50, 50), popup_rect, 2, border_radius=8
        )

        txt = self.font.render(self.error_message, True, (255, 255, 255))
        vis.screen.blit(txt, (
            popup_rect.centerx - txt.get_width() // 2,
            popup_rect.centery - txt.get_height() // 2
        ))

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        vis = self.vis

        # Fecha o popup ao clicar ou pressionar tecla
        if self.show_error:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.show_error = False
            return

        self.handle_text_box_events(event)

        for btn in self.menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    if not self.text.strip():
                        self.error_message = "Username vazio!"
                        self.show_error = True
                        return

                    self.vis.user_name = self.text
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

        if vis.screen.get_size() != MENU_SIZE and vis.state == "MAIN_MENU":
            x, y = MENU_SIZE
            self.vis.window.update_display_mode(x, y)

        vis.screen.fill((50, 50, 50))

        text_surf = self.title_font.render("Pac-Man", True, TILE_COLOR)
        text_rect = text_surf.get_rect(
            centerx=vis.screen.get_rect().centerx, y=10
        )
        vis.screen.blit(text_surf, text_rect)

        self.draw_user_selection()

        for btn in self.menu_buttons:
            btn.draw()

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.menu_buttons:
            btn.update(mouse_pos)

        if self.show_error:
            self.draw_error_popup()
