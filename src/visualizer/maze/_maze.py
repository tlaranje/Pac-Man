from .._constants import TILE_SIZE, MARGIN, MAZE_OFFSET, MENU_SIZE
from ._movement import MovementController
from typing import TYPE_CHECKING
from pygame import Surface
from pygame import Event
import pygame

if TYPE_CHECKING:
    from ._rendering import MazeRenderer
    from .._visualizer import Visualizer


class Maze:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer

        # Variables of Maze
        self.maze = self.vis.gameplay.maps[0]

        self.size = (self.maze._width, self.maze._height)
        self.perfect = self.maze._perfect
        self.entry_cell = self.maze.maze_entry
        self.exit_cell = self.maze.maze_exit
        self.seed = self.maze._seed

        # MovementController class
        self.movement_controller = MovementController(self.maze.maze)

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
        self.maze_surface.fill((50, 50, 50))

        # Score count for HighScore text
        self.score: int = 0

        # Variables for smooth movement
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 15
        self.lerp_speed = 0.15

        self.gameplay = self.vis.gameplay
        self.gameplay.gameplay_init(0)
        start_px = self.gameplay.player.x * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 1
        start_py = self.gameplay.player.y * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 1
        self.player_visual_x = float(start_px)
        self.player_visual_y = float(start_py)

        self.ghosts_visual_pos = []
        for g in self.gameplay.ghosts_maps[0]:
            start_gx = g.x * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            start_gy = g.y * TILE_SIZE + 16 + (
                TILE_SIZE) // 2 + 1
            self.ghosts_visual_pos.append(
                {"x": float(start_gx), "y": float(start_gy)}
            )

        self.ghosts_frames: list[Surface] = []
        self.fruit_sprites: list[Surface] = []

        self.high_score_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 20
        )

    def init_sprites(self, renderer: "MazeRenderer") -> None:
        sprite_loader = self.vis.sprite_loader
        self.player_frames = sprite_loader.load_frames(
            pos=21, num_frames=3
        )
        self.ghosts_frames = [
            sprite_loader.load_frames(num_frames=2, pos=17),
            sprite_loader.load_frames(num_frames=2, pos=18)
        ]
        self.fruit_sprites = [
            sprite_loader.load_frames(pos=18, is_fruit=True, start=13),
            sprite_loader.load_frames(pos=20, is_fruit=True, start=12)
        ]
        # renderer.draw_walls(
        #     self.maze.maze, self.entry_cell, self.exit_cell
        # )
        # renderer.draw_pacgums(
        #     self.gameplay.pacgums_maps[0], self.fruit_sprites
        # )

    def handle_game_play_events(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "MAIN_MENU"
            x, y = MENU_SIZE
            self.vis.window.update_display_mode(x, y)

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
        self.gameplay.player.eat(self.gameplay.pacgums_maps[0])
        type_pacgum = self.gameplay.pacgums_maps[0][y][x][1]

        if type_pacgum == "normal" and is_eat is True:
            self.score += 10
        if type_pacgum == "super" and is_eat is True:
            self.score += 100

        pos_x = (x * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 2
        pos_y = (y * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 2 + MAZE_OFFSET
        pygame.draw.rect(
            self.maze_surface, (50, 50, 50), (pos_x, pos_y, 16, 16)
        )

        high_score = self.high_score_font.render(
            f"High Score: {self.score}", True, (255, 255, 255)
        )
        x, y = self.vis.screen.get_size()
        self.vis.screen.blit(
            high_score, (x // 2 - high_score.get_width() // 2, 10)
        )

    def move_player_ghosts(self) -> None:
        vis = self.vis
        vis.screen.blit(self.maze_surface, (0, 0))

        if self.gameplay.player.is_dead():
            # x, y = MENU_SIZE
            # self.win.update_display_mode(x, y)
            self.state = "GAME_OVER"
            self.gameplay.reset()
            self.score = 0
            self.game_started = False
            self.current_dir = None
            self.next_dir = None
            self.player_angle = 0
            return

        self.update_player_movement()

        px, py = self.gameplay.player.x, self.gameplay.player.y
        if self.gameplay.pacgums_maps[0][py][px]:
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
            TILE_SIZE - 16) // 2 + 11
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
