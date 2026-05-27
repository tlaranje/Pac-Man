from ._visualizer import Visualizer
import pygame
import sys


class Manager:
    def __init__(self) -> None:
        pygame.init()
        self.vis = Visualizer()

    def run(self) -> None:
        vis = self.vis
        menu = vis.menu
        maze = vis.maze
        window = vis.window

        window.stetup_window()
        menu.init_menu_buttons()

        clock: pygame.time.Clock = pygame.time.Clock()
        while True:
            vis.screen.fill((50, 50, 50))
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_ESCAPE
                        and vis.state == 'MAIN_MENU'
                    ):
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if vis.state == "MAIN_MENU":
                    menu.handle_menu_events(event)
                elif vis.state == "GAME_PLAY":
                    maze.handle_game_play_events(event)

            if vis.state == "MAIN_MENU":
                for btn in menu.menu_buttons:
                    btn.update(mouse_pos)
                menu.draw_main_menu()
            elif vis.state == "GAME_PLAY":
                maze.move_player_ghosts()

            pygame.display.flip()
            clock.tick(60)
