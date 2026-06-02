from ._visualizer import Visualizer
from ._constants import TILE_SIZE
import pygame
import sys


class Manager:
    def __init__(self) -> None:
        pygame.init()
        pygame.key.set_repeat(500, 30)
        self.vis = Visualizer()

    def run(self) -> None:
        vis = self.vis
        menu = vis.menu
        maze = vis.maze
        window = vis.window
        renderer = vis.renderer
        game_over = vis.game_over

        window.stetup_window()
        menu.init_buttons()
        game_over.init_game_over_buttons()
        renderer.init_sprites()

        maze_grid = maze.maze_grid[vis.gameplay.map_idx].maze
        vis.maze_size = (
            len(maze_grid) * TILE_SIZE, len(maze_grid) * TILE_SIZE
        )
        renderer.draw_walls(maze_grid)
        renderer.draw_pacgums(
            maze.gameplay.pacgums_maps[maze.gameplay.map_idx],
            maze.fruit_sprites
        )

        clock: pygame.time.Clock = pygame.time.Clock()
        while True:
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
                    menu.handle_cheat_menu_events(event)
                elif state == "PAUSE":
                    menu.handle_pause_menu_events(event)
                elif state == "GAME_OVER":
                    game_over.handle_game_over_events(event)

            if state == "MAIN_MENU":
                menu.draw_main_menu()
            elif state == "GAME_PLAY":
                maze.move_player_ghosts()
                menu.draw_cheat_menu()
            elif state == "GAME_OVER":
                game_over.draw_game_over()
            elif state == 'PAUSE':
                renderer.draw_walls(maze.maze_grid[vis.gameplay.map_idx].maze)
                renderer.draw_pacgums(
                    maze.gameplay.pacgums_maps[maze.gameplay.map_idx],
                    maze.fruit_sprites
                )
                menu.draw_pause_menu()

            pygame.display.flip()
            clock.tick(60)
