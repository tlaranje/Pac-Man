from mazegenerator import MazeGenerator
from .button import Button
import pygame.gfxdraw
import pygame
import sys
import os

MAZE_WIDTH = 20
MAZE_HEIGHT = 20
TILE_SIZE = 32


class Manager:
    def __init__(self) -> None:
        pygame.init()

        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.menu_size: tuple[int, int] = (250, 250)
        self.game_play_size: tuple[int, int] = (
            (MAZE_WIDTH * TILE_SIZE) + 32, (MAZE_HEIGHT * TILE_SIZE) + 32
        )
        self.win_size: tuple[int, int] = self.menu_size
        Button.win_size = self.win_size

        self.screen: pygame.Surface = pygame.display.set_mode(self.win_size)
        Button.screen = self.screen

        pygame.display.set_caption("Pac-Man")

        self.state: str = "GAME_PLAY"
        self.update_display_mode(
            self.game_play_size[0], self.game_play_size[1]
        )
        self.menu_buttons: list[Button] = [
            Button(
                size=(150, 60), pos=(None, 100), text="Play", action="PLAY"
            ),
            Button(
                size=(150, 60), pos=(None, 170), text="Exit", action="QUIT_APP"
            )
        ]

        self.title_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 50
        )

    def update_display_mode(self, width: int, height: int) -> None:
        self.win_size = (width, height)
        Button.win_size = self.win_size
        self.screen = pygame.display.set_mode(self.win_size)
        pygame.event.post(
            pygame.event.Event(pygame.ACTIVEEVENT, gain=1, state=1)
        )

    def draw_maze(self) -> None:
        maze = MazeGenerator(
            size=(MAZE_WIDTH, MAZE_HEIGHT), perfect=True, exit_cell=(19, 19)
        )

        border_color = (0, 0, 0)
        inner_color = (25, 25, 166)

        border_size = 8
        inner_thickness = 4
        margin = 16

        def draw_square_cap(color: tuple, pos: tuple, thickness: int):
            rect = pygame.Rect(0, 0, thickness, thickness)
            rect.center = (pos[0] + 1, pos[1] + 1)
            pygame.draw.rect(self.screen, color, rect)

        for y, row in enumerate(maze.maze):
            for x, cell in enumerate(row):
                pos_x = (x * TILE_SIZE) + margin
                pos_y = (y * TILE_SIZE) + margin

                top_left = (pos_x, pos_y)
                top_right = (pos_x + TILE_SIZE, pos_y)
                bottom_left = (pos_x, pos_y + TILE_SIZE)
                bottom_right = (pos_x + TILE_SIZE, pos_y + TILE_SIZE)

                if cell & 1:  # Norte
                    pygame.draw.line(
                        self.screen, border_color, top_left,
                        top_right, border_size
                    )
                    draw_square_cap(border_color, top_left, border_size)
                    draw_square_cap(border_color, top_right, border_size)

                if cell & 2:  # Leste
                    pygame.draw.line(
                        self.screen, border_color, top_right,
                        bottom_right, border_size
                    )
                    draw_square_cap(border_color, top_right, border_size)
                    draw_square_cap(border_color, bottom_right, border_size)

                if cell & 4:  # Sul
                    pygame.draw.line(
                        self.screen, border_color, bottom_left,
                        bottom_right, border_size
                    )
                    draw_square_cap(border_color, bottom_left, border_size)
                    draw_square_cap(border_color, bottom_right, border_size)

                if cell & 8:  # Oeste
                    pygame.draw.line(
                        self.screen, border_color,
                        top_left, bottom_left, border_size
                    )
                    draw_square_cap(border_color, top_left, border_size)
                    draw_square_cap(border_color, bottom_left, border_size)

        for y, row in enumerate(maze.maze):
            for x, cell in enumerate(row):
                pos_x = (x * TILE_SIZE) + margin
                pos_y = (y * TILE_SIZE) + margin

                top_left = (pos_x, pos_y)
                top_right = (pos_x + TILE_SIZE, pos_y)
                bottom_left = (pos_x, pos_y + TILE_SIZE)
                bottom_right = (pos_x + TILE_SIZE, pos_y + TILE_SIZE)

                if cell & 1:  # Norte
                    pygame.draw.line(
                        self.screen, inner_color, top_left,
                        top_right, inner_thickness
                    )
                    draw_square_cap(inner_color, top_left, inner_thickness)
                    draw_square_cap(inner_color, top_right, inner_thickness)

                if cell & 2:  # Leste
                    pygame.draw.line(
                        self.screen, inner_color, top_right,
                        bottom_right, inner_thickness
                    )
                    draw_square_cap(inner_color, top_right, inner_thickness)
                    draw_square_cap(inner_color, bottom_right, inner_thickness)

                if cell & 4:  # Sul
                    pygame.draw.line(
                        self.screen, inner_color, bottom_left,
                        bottom_right, inner_thickness
                    )
                    draw_square_cap(inner_color, bottom_left, inner_thickness)
                    draw_square_cap(inner_color, bottom_right, inner_thickness)

                if cell & 8:  # Oeste
                    pygame.draw.line(
                        self.screen, inner_color, top_left,
                        bottom_left, inner_thickness
                    )
                    draw_square_cap(inner_color, top_left, inner_thickness)
                    draw_square_cap(inner_color, bottom_left, inner_thickness)

    def draw_main_menu(self) -> None:
        text_surf = self.title_font.render("Pac-Man", True, (215, 215, 215))
        text_rect = text_surf.get_rect(
            centerx=self.screen.get_rect().centerx, y=10
        )
        self.screen.blit(text_surf, text_rect)
        for btn in self.menu_buttons:
            btn.draw()

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        for btn in self.menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    self.state = 'GAME_PLAY'
                    x, y = self.game_play_size
                    self.update_display_mode(x, y)
                    pygame.event.clear()
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()

    def handle_game_play_events(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                self.state = "MAIN_MENU"
                x, y = self.menu_size
                self.update_display_mode(x, y)
            if (event.key == pygame.K_r):
                self.screen.fill((50, 50, 50))
                pygame.draw.rect(
                    self.screen, (100, 100, 100),
                    (
                        16, 16, (MAZE_WIDTH * TILE_SIZE),
                        (MAZE_HEIGHT * TILE_SIZE)
                    )
                )
                self.draw_maze()
                pygame.display.flip()

    def run(self) -> None:
        self.screen.fill((50, 50, 50))
        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_ESCAPE
                        and self.state == 'MAIN_MENU'
                    ):
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == "MAIN_MENU":
                    self.handle_menu_events(event)
                elif self.state == "GAME_PLAY":
                    self.handle_game_play_events(event)

            if self.state == "MAIN_MENU":
                for btn in self.menu_buttons:
                    btn.update(mouse_pos)
                self.draw_main_menu()

            pygame.display.flip()
