import pygame
from typing import TYPE_CHECKING
from pygame import Event

from .._constants import TILE_SIZE, MARGIN
from ._sprites import SpriteLoader
from ._movement import MovementController
from ._rendering import MazeRenderer

if TYPE_CHECKING:
    from ._protocol import VisualizerProtocol as VProtocol


class Maze:
    def __init__(self, screen: pygame.Surface, maze, gameplay) -> None:
        self.maze = maze
        self.gameplay = gameplay
        self.screen = screen
        self.maze_size = (maze._width, maze._height)
        self.perfect = maze._perfect
        self.entry_cell = maze.maze_entry
        self.exit_cell = maze.maze_exit
        self.seed = maze._seed

        self.sprite_loader = SpriteLoader()
        self.movement_controller = MovementController(self.maze.maze)

        self.player_frames = self.sprite_loader.load_frames(
            pos=21, num_frames=3
        )
        self.ghosts_frames = [
            self.sprite_loader.load_frames(num_frames=2, pos=17),
            self.sprite_loader.load_frames(num_frames=2, pos=18)
        ]
        self.fruit_frames = [
            self.sprite_loader.load_frames(pos=18, is_fruit=True, start=13),
            self.sprite_loader.load_frames(pos=20, is_fruit=True, start=12),
            self.sprite_loader.load_frames(pos=20, is_fruit=True, start=13),
            self.sprite_loader.load_frames(pos=21, is_fruit=True, start=12),
            self.sprite_loader.load_frames(pos=22, is_fruit=True, start=12),
            self.sprite_loader.load_frames(pos=21, is_fruit=True, start=13),
            self.sprite_loader.load_frames(pos=22, is_fruit=True, start=13),
        ]

        self.ghost_delay = 500
        self.last_ghost_move = pygame.time.get_ticks()
        self.player_delay = 150
        self.last_player_move = pygame.time.get_ticks()

        self.current_dir = None
        self.next_dir = None
        self.player_angle = 0

        # Configuração da Superfície do Labirinto
        maze_pixel_width = self.maze_size[0] * TILE_SIZE + MARGIN
        maze_pixel_height = self.maze_size[1] * TILE_SIZE + MARGIN
        self.maze_surface = pygame.Surface(
            (maze_pixel_width, maze_pixel_height)
        )
        self.maze_surface.fill((50, 50, 50))

        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 15
        self.lerp_speed = 0.15

        # Posições Visuais Suaves (Lerp)
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

        self.renderer = MazeRenderer(self.maze_surface)
        self.renderer.draw_walls(
            self.maze.maze, self.entry_cell, self.exit_cell
        )
        self.renderer.draw_pacgums(
            self.gameplay.pacgums_maps[0], self.fruit_frames
        )

    def handle_game_play_events(self: "VProtocol", event: Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "MAIN_MENU"
            x, y = self.menu_size
            self.update_display_mode(x, y)

        new_dir = MovementController.get_direction_from_input(
            pygame.key.get_pressed()
        )
        if new_dir:
            self.next_dir = new_dir

    def update_player_movement(self) -> None:
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_player_move < self.player_delay:
            return

        px, py = self.gameplay.player.x, self.gameplay.player.y

        # Valida colisões através da instância do movement_controller
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
        pos_x = (x * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 2
        pos_y = (y * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 2
        pygame.draw.rect(
            self.maze_surface, (50, 50, 50), (pos_x, pos_y, 16, 16)
        )

    def move_player_ghosts(self) -> None:
        self.screen.blit(self.maze_surface, (0, 0))
        self.update_player_movement()

        px, py = self.gameplay.player.x, self.gameplay.player.y
        if self.gameplay.pacgums_maps[0][py][px]:
            self.clear_pacgum_at(px, py)

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1

        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_ghost_move >= self.ghost_delay:
            self.gameplay.move_ghosts()
            self.last_ghost_move = curr_time

        for i, g in enumerate(self.gameplay.ghosts_maps[0]):
            target_gx = g.x * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            target_gy = g.y * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1

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
                self.screen.blit(ghost_current_frame, ghost_rect)

        target_px = self.gameplay.player.x * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 11
        target_py = self.gameplay.player.y * TILE_SIZE + 16 + (
            TILE_SIZE - 16) // 2 + 9

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
            center=(int(self.player_visual_x), int(self.player_visual_y))
        )
        self.screen.blit(active_player_frame, player_rect)
