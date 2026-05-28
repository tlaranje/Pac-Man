from .._constants import TILE_SIZE, MARGIN, MAZE_OFFSET
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

        # Variables of Maze
        self.maze_grid = self.vis.gameplay.maps[0]

        self.size = (self.maze_grid._width, self.maze_grid._height)
        self.perfect = self.maze_grid._perfect
        self.entry_cell = self.maze_grid.maze_entry
        self.exit_cell = self.maze_grid.maze_exit
        self.seed = self.maze_grid._seed

        # MovementController class
        self.movement_controller = MovementController(self.maze_grid.maze)

        self.ghost_delay = 500
        self.last_ghost_move = pygame.time.get_ticks()
        self.player_delay = 150
        self.last_player_move = pygame.time.get_ticks()

        self.current_dir: str | None = None
        self.next_dir: str | None = None
        self.player_angle: int = 0
        self.game_started: bool = False

        # Static maze surface for walls and pacgums
        maze_width = self.size[0] * TILE_SIZE + MARGIN
        maze_height = self.size[1]*TILE_SIZE + MARGIN + MAZE_OFFSET
        self.maze_surface = pygame.Surface((maze_width, maze_height))

        # Score count for HighScore text
        self.score: int = 0

        # Gameplay class
        self.gameplay = self.vis.gameplay
        self.gameplay.gameplay_init(0)

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

        self.font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 20
        )
        self.lives: int = 3

    def reset_visual_positions(self) -> None:
        start_px = self.gameplay.player.x * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 1
        start_py = self.gameplay.player.y * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 1
        self.player_visual_x = float(start_px)
        self.player_visual_y = float(start_py)

        self.ghosts_visual_pos = []
        for g in self.gameplay.ghosts_maps[0]:
            start_gx = g.x * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            start_gy = g.y * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            self.ghosts_visual_pos.append(
                {"x": float(start_gx), "y": float(start_gy)}
            )

    def handle_player_death(self) -> None:
        self.gameplay.reset()
        self.score = 0
        self.lives = 3
        self.game_started = False
        self.current_dir = None
        self.next_dir = None
        self.player_angle = 0

        self.maze_surface.fill((0, 0, 0))

        self.vis.renderer.draw_walls(self.maze_grid.maze)

        self.vis.renderer.draw_pacgums(
            self.gameplay.pacgums_maps[0], self.fruit_sprites
        )

        self.reset_visual_positions()

    def handle_player_lose_life(self) -> None:
        self.game_started = False
        self.current_dir = None
        self.next_dir = None
        self.player_angle = 0

        self.gameplay.player.reset_position()
        for g in self.gameplay.ghosts_maps[0]:
            g.reset_position()

        self.reset_visual_positions()

    def handle_game_play_events(self, event: Event) -> None:
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
        is_eat = self.gameplay.pacgums_maps[0][y][x][0]
        type_pacgum = self.gameplay.pacgums_maps[0][y][x][1]

        if type_pacgum == "normal" and is_eat is True:
            self.score += 10
        if type_pacgum == "super" and is_eat is True:
            self.score += 100

        self.gameplay.player.eat(self.gameplay.pacgums_maps[0])

        pos_x = (x * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 4
        pos_y = (y * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 4 + MAZE_OFFSET
        pygame.draw.rect(
            self.maze_surface, (0, 0, 0), (pos_x, pos_y, 18, 18)
        )

    def move_player_ghosts(self) -> None:
        vis = self.vis
        vis.screen.blit(self.maze_surface, (0, 0))

        if self.gameplay.player.is_dead():
            self.lives -= 1
            if self.lives <= 0:
                vis.state = "GAME_OVER"
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
        if self.gameplay.pacgums_maps[0][py][px][0] is True:
            self.clear_pacgum_at(px, py)

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1

        curr_time = pygame.time.get_ticks()
        if self.game_started and (
           curr_time - self.last_ghost_move >= self.ghost_delay):
            self.gameplay.move_ghosts()
            self.last_ghost_move = curr_time

        for i, g in enumerate(self.gameplay.ghosts_maps[0]):
            target_gx = g.x * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            target_gy = g.y * TILE_SIZE + 16 + (
                TILE_SIZE) // 2 + 1 + MAZE_OFFSET

            self.ghosts_visual_pos[i]["x"] += (
                target_gx - self.ghosts_visual_pos[i]["x"]) * self.lerp_speed
            self.ghosts_visual_pos[i]["y"] += (
                target_gy - self.ghosts_visual_pos[i]["y"]) * self.lerp_speed

            angle = getattr(g, "ghost_angle", 0)
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
