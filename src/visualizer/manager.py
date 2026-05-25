from src.gameplay import PacManGameplay
from ._visualizer import Visualizer
from src.parser import PacManConfig
from ._maze import Maze
import pygame
import sys

MAZE_WIDTH = 20
MAZE_HEIGHT = 20
TILE_SIZE = 32


class Manager:
    def __init__(self) -> None:
        pygame.init()
        self.vis = Visualizer()
        self.config = PacManConfig("./config.json")
        self.gameplay = PacManGameplay(self.config)

    def run(self) -> None:
        self.vis.stetup_window()
        self.gameplay.gameplay_init(0)
        maze = self.gameplay.maps[0]

        Maze.__init__(
            self.vis,
            screen=self.vis.screen,
            maze=maze,
            gameplay=self.gameplay
        )
        self.vis.init_menu_buttons()
        clock: pygame.time.Clock = pygame.time.Clock()
        while True:
            self.vis.screen.fill((50, 50, 50))
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_ESCAPE
                        and self.vis.state == 'MAIN_MENU'
                    ):
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.vis.state == "MAIN_MENU":
                    self.vis.handle_menu_events(event)
                elif self.vis.state == "GAME_PLAY":
                    self.vis.handle_game_play_events(event)

            if self.vis.state == "MAIN_MENU":
                for btn in self.vis.menu_buttons:
                    btn.update(mouse_pos)
                self.vis.draw_main_menu()
            elif self.vis.state == "GAME_PLAY":
                self.vis.screen.blit(self.vis.maze_surface, (0, 0))
                self.vis.move_player_ghosts()

            pygame.display.flip()
            clock.tick(60)
