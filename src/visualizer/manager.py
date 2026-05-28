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
        renderer = vis.renderer
        game_over = vis.game_over

        window.stetup_window()
        menu.init_menu_buttons()
        renderer.init_sprites()

        renderer.draw_walls(maze.maze_grid.maze)
        renderer.draw_pacgums(
            maze.gameplay.pacgums_maps[0], maze.fruit_sprites
        )

        clock: pygame.time.Clock = pygame.time.Clock()
        while True:
            vis.screen.fill((50, 50, 50))
            mouse_pos = pygame.mouse.get_pos()
            state = vis.state

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

                if state == "MAIN_MENU":
                    menu.handle_menu_events(event)
                elif state == "GAME_PLAY":
                    maze.handle_game_play_events(event)
                elif state == "GAME_OVER":
                    game_over.handle_game_over_events(event)

            if state == "MAIN_MENU":
                for btn in menu.menu_buttons:
                    btn.update(mouse_pos)
                menu.draw_main_menu()
            elif state == "GAME_PLAY":
                maze.move_player_ghosts()
            elif state == "GAME_OVER":
                game_over.draw_game_over()

            pygame.display.flip()
            clock.tick(60)
