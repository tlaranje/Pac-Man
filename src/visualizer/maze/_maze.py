from .._constants import (
    TILE_SIZE, MARGIN, MAZE_OFFSET, GAMEOVER_SIZE, MAX_PLAYER_DELAY, MAZE_SIZE
)
from ._movement import MovementController
from typing import TYPE_CHECKING
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

        self.ghost_delay = 500
        self.last_ghost_move = pygame.time.get_ticks()
        self.player_delay = 150
        self.last_player_move = pygame.time.get_ticks()

        self.current_dir: str | None = None
        self.next_dir: str | None = None
        self.player_angle: int = 0
        self.game_started: bool = False

        # Static maze surface for walls and pacgums
        maze_width = MAZE_SIZE[0] + MARGIN
        maze_height = MAZE_SIZE[1] + MARGIN + MAZE_OFFSET
        self.maze_surface = pygame.Surface((maze_width, maze_height))

        # Score count for HighScore text
        self.score: int = 0

        # Variables for smooth movement
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 15
        self.lerp_speed = 0.15

        # Init visual positions
        self.reset_visual_positions()

        # Sprites
        self.player_frames: list[Surface] = []
        self.ghosts_frames: list[Surface] = []
        self.fruit_sprites: list[Surface] = []
        self.scared_ghosts_sprites: list[Surface] = []

        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 20
        )
        self.lives: int = 3
        self.is_cheat_mode: bool = False

        self.init_level()

    def init_level(self) -> None:
        self.maze_grid = self.vis.gameplay.maps

        self.size = (
            self.maze_grid[self.gameplay.map_idx]._width,
            self.maze_grid[self.gameplay.map_idx]._height
        )
        self.perfect = self.maze_grid[self.gameplay.map_idx]._perfect
        self.entry_cell = self.maze_grid[self.gameplay.map_idx].maze_entry
        self.exit_cell = self.maze_grid[self.gameplay.map_idx].maze_exit
        self.seed = self.maze_grid[self.gameplay.map_idx]._seed

        self.movement_controller = MovementController(
            self.maze_grid[self.gameplay.map_idx].maze
        )

    def give_extra_lives(self) -> None:
        self.lives += 1

    def increase_player_speed(self) -> None:
        if self.player_delay >= 10:
            self.player_delay -= 10

    def decrease_player_speed(self) -> None:
        if self.player_delay + 10 < MAX_PLAYER_DELAY:
            self.player_delay += 10

    def toggle_cheat_mode(self) -> None:
        self.is_cheat_mode = not self.is_cheat_mode

    def reset_visual_positions(self) -> None:
        start_px = self.gameplay.player.x * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 1
        start_py = self.gameplay.player.y * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 1
        self.player_visual_x = float(start_px)
        self.player_visual_y = float(start_py)

        self.ghosts_visual_pos = []
        for g in self.gameplay.ghosts_maps[self.gameplay.map_idx]:
            start_gx = g.x * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            start_gy = g.y * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            self.ghosts_visual_pos.append(
                {"x": float(start_gx), "y": float(start_gy)}
            )

    def handle_player_death(self, score: int, is_win: bool = False) -> None:
        self.gameplay.scores.append(self.score)
        self.vis.state = "GAME_OVER"
        self.vis.game_over.title = "Game Over" if not is_win else "Win"
        self.maze_surface.fill((0, 0, 0))
        x, y = GAMEOVER_SIZE
        self.vis.window.update_display_mode(x, y)
        self.gameplay.reset()
        self.score = 0
        self.lives = 3
        self.game_started = False
        self.current_dir = None
        self.next_dir = None
        self.player_angle = 0

    def handle_player_lose_life(self) -> None:
        self.game_started = False
        self.current_dir = None
        self.next_dir = None
        self.player_angle = 0

        self.gameplay.player.reset_position()
        for g in self.gameplay.ghosts_maps[self.gameplay.map_idx]:
            g.reset_position()

        self.maze_surface.fill((0, 0, 0))
        self.vis.renderer.draw_walls(
            self.maze_grid[self.gameplay.map_idx].maze
        )
        self.vis.renderer.draw_pacgums(
            self.gameplay.pacgums_maps[self.gameplay.map_idx],
            self.fruit_sprites
        )

        self.reset_visual_positions()

    def handle_game_play_events(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.vis.state = 'PAUSE'
                return

        new_dir = MovementController.get_direction_from_input(
            pygame.key.get_pressed()
        )
        if new_dir:
            self.next_dir = new_dir

    def update_player_movement(self) -> None:
        curr_time = pygame.time.get_ticks()

        if not self.game_started:
            if self.next_dir:
                self.game_started = True
                self.last_player_move = curr_time
            else:
                return

        if curr_time - self.last_player_move < self.player_delay:
            return

        px, py = self.gameplay.player.x, self.gameplay.player.y

        if self.next_dir and self.movement_controller.can_move(
           px, py, self.next_dir):
            self.current_dir = self.next_dir
            self.next_dir = None

        if self.current_dir and self.movement_controller.can_move(
           px, py, self.current_dir):
            if self.current_dir == "LEFT":
                self.gameplay.player.move_left()
                self.player_angle = 180
            elif self.current_dir == "RIGHT":
                self.gameplay.player.move_right()
                self.player_angle = 0
            elif self.current_dir == "UP":
                self.gameplay.player.move_up()
                self.player_angle = 90
            elif self.current_dir == "DOWN":
                self.gameplay.player.move_down()
                self.player_angle = 270
            self.last_player_move = curr_time
        else:
            self.current_dir = None

    def clear_pacgum_at(self, x: int, y: int) -> None:
        is_eat = self.gameplay.pacgums_maps[self.gameplay.map_idx][y][x][0]
        type_pacgum = self.gameplay.pacgums_maps[
            self.gameplay.map_idx
        ][y][x][1]

        if type_pacgum == "normal" and is_eat is True:
            self.score += 10
        if type_pacgum == "super" and is_eat is True:
            self.gameplay.player.turn_on_super()
            self.score += 100

        self.gameplay.player.eat(
            self.gameplay.pacgums_maps[self.gameplay.map_idx]
        )

        pos_x = (x * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 4
        pos_y = (y * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 4 + MAZE_OFFSET
        pygame.draw.rect(
            self.maze_surface, (0, 0, 0), (pos_x, pos_y, 18, 18)
        )

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
                return
            else:
                self.handle_player_lose_life()
                return

        high_score_surface = self.font.render(
            f"High Score: {self.score}", True, (255, 255, 255)
        )
        lives_surface = self.font.render(
            f"Lives: {self.lives}", True, (255, 255, 255)
        )
        screen_w, screen_h = self.vis.screen.get_size()

        vis.screen.blit(
            high_score_surface,
            (screen_w // 2 - high_score_surface.get_width() // 2, 10)
        )
        vis.screen.blit(
            lives_surface,
            (20, 10)
        )

        self.update_player_movement()

        px, py = self.gameplay.player.x, self.gameplay.player.y
        if self.gameplay.pacgums_maps[
           self.gameplay.map_idx][py][px][0] is True:
            self.clear_pacgum_at(px, py)

        if self.gameplay.player.is_on_super():
            if self.gameplay.player.is_on_ghost():
                ghosts_ate: int = self.gameplay.player.eat_ghosts()
                self.score += ghosts_ate * 200
        else:
            for ghost in self.gameplay.ghosts_maps[self.gameplay.map_idx]:
                ghost.is_scared = False

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1

        curr_time = pygame.time.get_ticks()
        if self.game_started and (
           curr_time - self.last_ghost_move >= self.ghost_delay):
            self.gameplay.move_ghosts()
            self.last_ghost_move = curr_time

        for i, g in enumerate(
            self.gameplay.ghosts_maps[self.gameplay.map_idx]
        ):
            target_gx = g.x * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            target_gy = g.y * TILE_SIZE + 16 + (
                TILE_SIZE) // 2 + 1 + MAZE_OFFSET

            self.ghosts_visual_pos[i]["x"] += (
                target_gx - self.ghosts_visual_pos[i]["x"]) * self.lerp_speed
            self.ghosts_visual_pos[i]["y"] += (
                target_gy - self.ghosts_visual_pos[i]["y"]) * self.lerp_speed

            angle = getattr(g, "ghost_angle", 0)

            if g.is_scared:
                dir_key = '0'
                ghost_dict = self.scared_ghosts_sprites[0]
            else:
                dir_key = (
                    "W" if angle == 90
                    else "S" if angle == 270
                    else "A" if angle == 180
                    else "D"
                )
                ghost_dict = self.ghosts_frames[i % 2]

            if isinstance(ghost_dict, dict):
                dir_frames = ghost_dict[dir_key]
                ghost_current_frame = dir_frames[
                    self.current_frame % len(dir_frames)
                ]
                ghost_rect = ghost_current_frame.get_rect(
                    center=(
                        int(self.ghosts_visual_pos[i]["x"]),
                        int(self.ghosts_visual_pos[i]["y"])
                    )
                )
                vis.screen.blit(ghost_current_frame, ghost_rect)

        target_px = self.gameplay.player.x * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 12
        target_py = self.gameplay.player.y * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 9 + MAZE_OFFSET

        self.player_visual_x += (
            target_px - self.player_visual_x) * self.lerp_speed
        self.player_visual_y += (
            target_py - self.player_visual_y) * self.lerp_speed

        player_dir_key = (
            "W" if self.player_angle == 90
            else "S" if self.player_angle == 270
            else "A" if self.player_angle == 180
            else "D"
        )

        if isinstance(self.player_frames, dict):
            player_dir_frames = self.player_frames[player_dir_key]
            active_player_frame = player_dir_frames[
                self.current_frame % len(player_dir_frames)
            ]
        else:
            active_player_frame = self.player_frames[
                self.current_frame % len(self.player_frames)
            ]

        player_rect = active_player_frame.get_rect(
            center=(int(self.player_visual_x-1), int(self.player_visual_y))
        )
        vis.screen.blit(active_player_frame, player_rect)
