""" from .._constants import (
    TILE_SIZE, MARGIN, BORDER_SIZE, INNER_THICKNESS,
    BORDER_COLOR, INNER_COLOR
)
from typing import TYPE_CHECKING, Any
from pygame import Event
import pygame

if TYPE_CHECKING:
    from pygame.typing import ColorLike
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

        self.player_frames = self.init_frames(pos=21, num_frames=3)
        self.ghosts_frames: list[list[pygame.Surface]] = [
            self.init_frames(num_frames=2, pos=17),
            self.init_frames(num_frames=2, pos=18)
        ]
        self.fruit_frames = [
            self.init_frames(pos=18, is_fruit=True, start=13),
            self.init_frames(pos=20, is_fruit=True, start=12),
            self.init_frames(pos=20, is_fruit=True, start=13),
            self.init_frames(pos=21, is_fruit=True, start=12),
            self.init_frames(pos=22, is_fruit=True, start=12),

            self.init_frames(pos=21, is_fruit=True, start=13),
            self.init_frames(pos=22, is_fruit=True, start=13),
        ]
        self.ghost_delay = 500
        self.last_ghost_move = pygame.time.get_ticks()

        self.player_delay = 150
        self.last_player_move = pygame.time.get_ticks()

        self.current_dir = None
        self.next_dir = None
        self.player_angle = 0

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

        start_px = self.gameplay.player.x * TILE_SIZE + 16 + (
            TILE_SIZE - 16
        ) // 2 + 1
        start_py = self.gameplay.player.y * TILE_SIZE + 16 + (
            TILE_SIZE - 16
        ) // 2 + 1
        self.player_visual_x = float(start_px)
        self.player_visual_y = float(start_py)

        self.ghosts_visual_pos = []
        for g in self.gameplay.ghosts_maps[0]:
            start_gx = g.x * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            start_gy = g.y * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            self.ghosts_visual_pos.append(
                {"x": float(start_gx), "y": float(start_gy)}
            )

        self.draw_maze()
        self.draw_all_pacgums()

    def init_frames(
        self, is_fruit: bool = False, num_frames: int = 1, pos: int = 0,
        start: int = 0
    ) -> Any:
        spritesheet = pygame.image.load(
            "assets/img/pacman.png"
        ).convert_alpha()

        height = 16
        widths = [16] * num_frames
        max_w = max(widths)

        base_column = 16 * pos

        background_color = spritesheet.get_at((0, base_column))

        if is_fruit:
            direcoes = ["0"]
        else:
            direcoes = ["D", "S", "A", "W"]

        frames_dict: Any = {}
        current_x = start * 16

        for dir_key in direcoes:
            frames_dict[dir_key] = []

            for w in widths:
                rect = pygame.Rect(current_x, base_column, w, height)
                frame = spritesheet.subsurface(rect)

                standard_surface = pygame.Surface(
                    (max_w, height), pygame.SRCALPHA
                )

                standard_surface.set_colorkey(background_color)
                standard_surface.blit(frame, (0, 0))

                frames_dict[dir_key].append(standard_surface)
                current_x += w

        return frames_dict

    def handle_game_play_events(self: "VProtocol", event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "MAIN_MENU"
                x, y = self.menu_size
                self.update_display_mode(x, y)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.next_dir = "LEFT"
        elif keys[pygame.K_d]:
            self.next_dir = "RIGHT"
        elif keys[pygame.K_w]:
            self.next_dir = "UP"
        elif keys[pygame.K_s]:
            self.next_dir = "DOWN"

    def can_move(self, direction: str) -> bool:
        px = self.gameplay.player.x
        py = self.gameplay.player.y
        current_cell = self.maze.maze[py][px]

        if direction == "UP" and not (current_cell & 1):
            return True
        if direction == "RIGHT" and not (current_cell & 2):
            return True
        if direction == "DOWN" and not (current_cell & 4):
            return True
        if direction == "LEFT" and not (current_cell & 8):
            return True
        return False

    def update_player_movement(self) -> None:
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_player_move < self.player_delay:
            return

        if self.next_dir and self.can_move(self.next_dir):
            self.current_dir = self.next_dir
            self.next_dir = None

        if self.current_dir and self.can_move(self.current_dir):
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

    def move_player_ghosts(self) -> None:
        self.screen.blit(self.maze_surface, (0, 0))

        self.update_player_movement()

        px = self.gameplay.player.x
        py = self.gameplay.player.y

        if self.gameplay.pacgums_maps[0][py][px]:
            self.clear_pacgum_at(px, py)

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (
                self.current_frame + 1)

        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_ghost_move >= self.ghost_delay:
            self.gameplay.move_ghosts()
            self.last_ghost_move = curr_time

        for i, g in enumerate(self.gameplay.ghosts_maps[0]):
            target_gx = g.x * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1
            target_gy = g.y * TILE_SIZE + 16 + (TILE_SIZE) // 2 + 1

            self.ghosts_visual_pos[i]["x"] += (
                target_gx - self.ghosts_visual_pos[i]["x"]
            ) * self.lerp_speed
            self.ghosts_visual_pos[i]["y"] += (
                target_gy - self.ghosts_visual_pos[i]["y"]
            ) * self.lerp_speed

            angle = getattr(g, "ghost_angle", 0)
            if angle == 90:
                dir_key = "W"
            elif angle == 270:
                dir_key = "S"
            elif angle == 180:
                dir_key = "A"
            else:
                dir_key = "D"

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

        if self.player_angle == 90:
            player_dir_key = "W"
        elif self.player_angle == 270:
            player_dir_key = "S"
        elif self.player_angle == 180:
            player_dir_key = "A"
        else:
            player_dir_key = "D"

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

    def draw_all_pacgums(self) -> None:
        for y, row in enumerate(self.gameplay.pacgums_maps[0]):
            for x, cell in enumerate(row):
                if cell:
                    pacguns_size = 16
                    pos_x = (x * TILE_SIZE) + 16 + (
                        TILE_SIZE - pacguns_size) // 2 + 2
                    pos_y = (y * TILE_SIZE) + 16 + (
                        TILE_SIZE - pacguns_size) // 2 + 1
                    self.maze_surface.blit(
                        self.fruit_frames[x % len(self.fruit_frames)]["0"][0],
                        (pos_x, pos_y, pacguns_size, pacguns_size)
                    )

    def clear_pacgum_at(self, x: int, y: int) -> None:
        pos_x = (x * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 2
        pos_y = (y * TILE_SIZE) + 16 + (TILE_SIZE - 8) // 2 - 2
        pygame.draw.rect(
            self.maze_surface, (50, 50, 50),
            (pos_x, pos_y, 16, 16)
        )

    def draw_maze(self) -> None:
        def draw_square(color: "ColorLike", pos: tuple[int, int]) -> None:
            padding = BORDER_SIZE - 8 // 2
            s_size = 16
            start_rect = pygame.Rect(
                pos[0] + padding, pos[1] + padding, s_size, s_size
            )
            pygame.draw.rect(self.maze_surface, color, start_rect)

        def draw_square_cap(pos: tuple) -> None:
            rect = pygame.Rect(0, 0, BORDER_SIZE, BORDER_SIZE)
            rect.center = (pos[0], pos[1])
            pygame.draw.rect(self.maze_surface, BORDER_COLOR, rect)

        for y, row in enumerate(self.maze.maze):
            for x, cell in enumerate(row):

                pos_x = (x * TILE_SIZE) + MARGIN // 2
                pos_y = (y * TILE_SIZE) + MARGIN // 2

                top_left = (pos_x, pos_y)
                top_right = (pos_x + TILE_SIZE, pos_y)
                bottom_left = (pos_x, pos_y + TILE_SIZE)
                bottom_right = (pos_x + TILE_SIZE, pos_y + TILE_SIZE)

                if x == self.entry_cell[0] and y == self.entry_cell[1]:
                    draw_square(pygame.Color("green"), (pos_x + 1, pos_y + 1))

                if x == self.exit_cell[0] and y == self.exit_cell[1]:
                    draw_square(pygame.Color("red"), (pos_x + 1, pos_y + 1))

                if cell & 1:
                    pygame.draw.line(
                        self.maze_surface, BORDER_COLOR,
                        (top_left[0] - 1, top_left[1]),
                        (top_right[0] + 1, top_right[1]),
                        BORDER_SIZE
                    )
                    draw_square_cap(top_left)
                    draw_square_cap(top_right)

                if cell & 2:
                    pygame.draw.line(
                        self.maze_surface, BORDER_COLOR,
                        (top_right[0], top_right[1] - 1),
                        (bottom_right[0], bottom_right[1] + 1),
                        BORDER_SIZE
                    )
                    draw_square_cap(top_right)
                    draw_square_cap(bottom_right)

                if cell & 4:
                    pygame.draw.line(
                        self.maze_surface, BORDER_COLOR,
                        (bottom_left[0] - 1, bottom_left[1]),
                        (bottom_right[0] + 1, bottom_right[1]),
                        BORDER_SIZE
                    )
                    draw_square_cap(bottom_left)
                    draw_square_cap(bottom_right)

                if cell & 8:
                    pygame.draw.line(
                        self.maze_surface, BORDER_COLOR,
                        (top_left[0], top_left[1] - 1),
                        (bottom_left[0], bottom_left[1] + 1),
                        BORDER_SIZE
                    )
                    draw_square_cap(top_left)
                    draw_square_cap(bottom_left)

        for y, row in enumerate(self.maze.maze):
            for x, cell in enumerate(row):
                pos_x = (x * TILE_SIZE) + MARGIN // 2
                pos_y = (y * TILE_SIZE) + MARGIN // 2

                top_left = (pos_x, pos_y)
                top_right = (pos_x + TILE_SIZE, pos_y)
                bottom_left = (pos_x, pos_y + TILE_SIZE)
                bottom_right = (pos_x + TILE_SIZE, pos_y + TILE_SIZE)

                if cell & 1:
                    pygame.draw.line(
                        self.maze_surface, INNER_COLOR,
                        (top_left[0] - 1, top_left[1]),
                        (top_right[0] + 1, top_right[1]),
                        INNER_THICKNESS
                    )

                if cell & 2:
                    pygame.draw.line(
                        self.maze_surface, INNER_COLOR,
                        (top_right[0], top_right[1] - 1),
                        (bottom_right[0], bottom_right[1] + 1),
                        INNER_THICKNESS
                    )

                if cell & 4:
                    pygame.draw.line(
                        self.maze_surface, INNER_COLOR,
                        (bottom_left[0] - 1, bottom_left[1]),
                        (bottom_right[0] + 1, bottom_right[1]),
                        INNER_THICKNESS
                    )

                if cell & 8:
                    pygame.draw.line(
                        self.maze_surface, INNER_COLOR,
                        (top_left[0], top_left[1] - 1),
                        (bottom_left[0], bottom_left[1] + 1),
                        INNER_THICKNESS
                    )
 """
