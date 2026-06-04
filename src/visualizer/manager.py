from ._constants import TILE_SIZE
from ._visualizer import Visualizer
import pygame
import sys


class Manager:
    """Main game loop manager coordinating all game systems.

    Initializes Pygame and all game components, then executes the main
    event-driven game loop with 60 FPS timing.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.key.set_repeat(500, 30)
        self.vis = Visualizer()

    def run(self) -> None:
        """
        Start the main game loop and run until quit.
        """
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
        maze.player_ctrl.reset_visual_position()
        maze.ghost_renderer.reset_visual_positions()
        maze.reset_maze()

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
                elif state == "INSTRUCTIONS":
                    close_btn = menu.close_button
                    if close_btn.is_clicked(event) and \
                       close_btn.action_value == "CLOSE":
                        vis.state = "MAIN_MENU"
                elif state == "LEADERBOARD":
                    close_btn = menu.close_button
                    if close_btn.is_clicked(event) and \
                       close_btn.action_value == "CLOSE":
                        vis.state = "MAIN_MENU"
                elif state == "PAUSE":
                    menu.handle_pause_menu_events(event)
                elif state == "GAME_OVER":
                    game_over.handle_game_over_events(event)

            if state == "MAIN_MENU":
                menu.draw_main_menu()
            elif state == "INSTRUCTIONS":
                menu.draw_instructions()
            elif state == "LEADERBOARD":
                menu.draw_leaderboard()
            elif state == "GAME_PLAY":
                maze.move_player_ghosts()
                if menu.cheat_menu_open:
                    menu.draw_cheat_menu()
                else:
                    mouse_pos = pygame.mouse.get_pos()
                    menu.cheat_button.update(mouse_pos)
                    menu.cheat_button.draw()
            elif state == "GAME_OVER":
                game_over.draw_game_over()
            elif state == 'PAUSE':
                maze.reset_maze()
                menu.draw_pause_menu()

            pygame.display.flip()
            clock.tick(60)
