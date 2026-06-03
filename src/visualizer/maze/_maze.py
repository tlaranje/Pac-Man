from ._ghost_renderer import GhostRenderer
from ._pacgum import PacgumController
from ._player import PlayerController
from typing import TYPE_CHECKING
from ._hud import HudRenderer
from pygame import Surface
from pygame import Event
import pygame

if TYPE_CHECKING:
    from .._visualizer import Visualizer


class Maze:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer

        self.gameplay = self.vis.gameplay
        self.gameplay.gameplay_init(0)

        self.ghost_delay: int = 500
        self.last_ghost_move: int = pygame.time.get_ticks()

        # Static maze surface for walls and pacgums
        info = pygame.display.Info()
        self.maze_surface: Surface = pygame.Surface(
            (info.current_w, info.current_h)
        )

        # Animation state
        self.current_frame: int = 0
        self.animation_timer: int = 0
        self.animation_speed: int = 15

        # Sprites (populated by MazeRenderer.init_sprites)
        self.player_frames: list[Surface] = []
        self.ghosts_frames: list[Surface] = []
        self.fruit_sprites: list[Surface] = []
        self.scared_ghosts_sprites: list[Surface] = []
        self.end_ghosts_sprites: list[Surface] = []
        self.dead_ghosts_sprites: list[Surface] = []

        # Game state
        self.score: int = 0
        self.lives: int = self.gameplay.config.settings.lives
        self.time: int = 90
        self.is_cheat_mode: bool = False

        # Sub-controllers
        self.player_ctrl = PlayerController(visualizer)
        self.ghost_renderer = GhostRenderer(visualizer)
        self.pacgum_ctrl = PacgumController(visualizer)

        self.hud = HudRenderer(visualizer)

        self.init_level()

    def reset_maze(self) -> None:
        vis = self.vis
        vis.renderer.draw_walls(
            vis.maze.maze_grid[vis.gameplay.map_idx].maze
        )
        vis.renderer.draw_pacgums(
            vis.maze.gameplay.pacgums_maps[
                vis.maze.gameplay.map_idx
            ],
            vis.maze.fruit_sprites
        )

    # Level setup
    def init_level(self) -> None:
        self.maze_grid = self.vis.gameplay.maps

        map_idx = self.gameplay.map_idx
        self.size = (
            self.maze_grid[map_idx]._width,
            self.maze_grid[map_idx]._height,
        )
        self.perfect = self.maze_grid[map_idx]._perfect
        self.entry_cell = self.maze_grid[map_idx].maze_entry
        self.exit_cell = self.maze_grid[map_idx].maze_exit
        self.seed = self.maze_grid[map_idx]._seed

        self.player_ctrl.init(self.maze_grid[map_idx].maze)
        self.ghost_renderer.reset_visual_positions()

    # Cheat helpers
    def give_extra_lives(self) -> None:
        self.lives += 1

    def increase_player_speed(self) -> None:
        self.player_ctrl.increase_speed()

    def decrease_player_speed(self) -> None:
        self.player_ctrl.decrease_speed()

    def toggle_cheat_mode(self) -> None:
        self.is_cheat_mode = not self.is_cheat_mode

    # Death / life handling
    def handle_player_death(self, score: int, is_win: bool = False) -> None:
        self.gameplay.scores.append(self.score)
        self.vis.state = "GAME_OVER"
        self.vis.game_over.title = "Game Over" if not is_win else "Win"
        self.maze_surface.fill((0, 0, 0))
        self.gameplay.reset()
        self.score = 0
        self.lives = self.gameplay.config.settings.lives
        self.player_ctrl.reset_state()
        self.ghost_renderer.reset_visual_positions()

    def handle_player_lose_life(self) -> None:
        self.player_ctrl.reset_state()

        self.gameplay.player.reset_position()
        for g in self.gameplay.ghosts_maps[self.gameplay.map_idx]:
            g.reset_position()

        self.maze_surface.fill((0, 0, 0))
        self.vis.maze.reset_maze()

        self.ghost_renderer.reset_visual_positions()

    # Event handling
    def handle_game_play_events(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.vis.state = "PAUSE"
                return

        from ._movement import MovementController
        new_dir = MovementController.get_direction_from_input(
            pygame.key.get_pressed()
        )
        self.player_ctrl.set_next_dir(new_dir)

    # Main game loop tick
    def move_player_ghosts(self) -> None:
        vis = self.vis
        vis.screen.blit(self.maze_surface, (0, 0))

        if self.gameplay.is_win():
            self.handle_player_death(self.score, is_win=True)
            return

        if self.gameplay.player.is_dead():
            self.lives -= 1
            if self.lives <= 0:
                self.handle_player_death(self.score)
            else:
                self.handle_player_lose_life()
            return

        self.hud.draw(self.score, self.lives, self.time)

        self.player_ctrl.update()

        self.score = self.pacgum_ctrl.try_eat(self.maze_surface, self.score)

        if self.gameplay.player.is_on_super():
            if self.gameplay.player.is_on_ghost():
                ghosts_ate = self.gameplay.player.eat_ghosts()
                self.score += (
                    ghosts_ate * self.gameplay.config.settings.points_per_ghost
                )
        else:
            for ghost in self.gameplay.ghosts_maps[self.gameplay.map_idx]:
                ghost.is_scared = False

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1

        curr_time = pygame.time.get_ticks()
        if self.player_ctrl.game_started and (
            curr_time - self.last_ghost_move >= self.ghost_delay
        ):
            self.gameplay.move_ghosts()
            self.last_ghost_move = curr_time

        self.ghost_renderer.update_and_draw(
            self.ghosts_frames, self.scared_ghosts_sprites,
            self.end_ghosts_sprites, self.current_frame,
        )

        self.player_ctrl.update_visual_position()
        self.player_ctrl.draw(self.player_frames, self.current_frame)
