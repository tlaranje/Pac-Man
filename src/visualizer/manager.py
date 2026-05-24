from ._button import Button
import pygame
import sys

MAZE_WIDTH = 20
MAZE_HEIGHT = 20
TILE_SIZE = 32


class Manager:
    def __init__(self) -> None:
        pygame.init()

        self.state: str = "GAME_PLAY"



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
