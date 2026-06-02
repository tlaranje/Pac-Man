from .._constants import TILE_SIZE, SCREEN_MIDPOINT
from ._movement import MovementController
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from .._visualizer import Visualizer

BASE_DELAY = 150
MIN_DELAY = 10
MAX_DELAY = 1000
DELAY_STEP = 10


class PlayerController:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer

        self.current_dir: str | None = None
        self.next_dir: str | None = None
        self.angle: int = 0
        self.game_started: bool = False

        self.visual_x: float = 0.0
        self.visual_y: float = 0.0
        self.lerp_speed: float = 0.15

        self.player_delay: int = BASE_DELAY
        self.last_move: int = pygame.time.get_ticks()

        self.movement_controller: MovementController

    @property
    def speed(self) -> int:
        return max(1, (MAX_DELAY - self.player_delay) // DELAY_STEP + 1)

    def init(self, maze_grid: list) -> None:
        self.movement_controller = MovementController(maze_grid)
        self.reset_visual_position()

    def reset_visual_position(self) -> None:
        player = self.vis.gameplay.player
        self.visual_x = float(
            player.x * TILE_SIZE + 16 + (TILE_SIZE - 16) // 2 + 1
        )
        self.visual_y = float(
            player.y * TILE_SIZE + 16 + (TILE_SIZE - 16) // 2 + 1
        )

    def reset_state(self) -> None:
        self.game_started = False
        self.current_dir = None
        self.next_dir = None
        self.angle = 0
        self.reset_visual_position()

    def set_next_dir(self, direction: str | None) -> None:
        if direction:
            self.next_dir = direction

    def increase_speed(self) -> None:
        if self.player_delay - DELAY_STEP >= MIN_DELAY:
            self.player_delay -= DELAY_STEP

    def decrease_speed(self) -> None:
        if self.player_delay + DELAY_STEP <= MAX_DELAY:
            self.player_delay += DELAY_STEP

    def update(self) -> None:
        curr_time = pygame.time.get_ticks()

        if not self.game_started:
            if self.next_dir:
                self.game_started = True
                self.last_move = curr_time
            else:
                return

        if curr_time - self.last_move < self.player_delay:
            return

        player = self.vis.gameplay.player
        px, py = player.x, player.y

        if self.next_dir and self.movement_controller.can_move(
                px, py, self.next_dir):
            self.current_dir = self.next_dir
            self.next_dir = None

        if self.current_dir and self.movement_controller.can_move(
                px, py, self.current_dir):
            if self.current_dir == "LEFT":
                player.move_left()
                self.angle = 180
            elif self.current_dir == "RIGHT":
                player.move_right()
                self.angle = 0
            elif self.current_dir == "UP":
                player.move_up()
                self.angle = 90
            elif self.current_dir == "DOWN":
                player.move_down()
                self.angle = 270
            self.last_move = curr_time
        else:
            self.current_dir = None

    def update_visual_position(self) -> None:
        vis = self.vis
        target_x = (
            (vis.gameplay.player.x * TILE_SIZE) + SCREEN_MIDPOINT[0]
            - vis.maze_size[0] // 2 + 17
        )
        target_y = (
            (vis.gameplay.player.y * TILE_SIZE) + SCREEN_MIDPOINT[1]
            - vis.maze_size[1] // 2 + 15
        )
        self.visual_x += (target_x - self.visual_x) * self.lerp_speed
        self.visual_y += (target_y - self.visual_y) * self.lerp_speed

    def draw(self, player_frames, current_frame: int) -> None:
        vis = self.vis

        dir_key = (
            "W" if self.angle == 90
            else "S" if self.angle == 270
            else "A" if self.angle == 180
            else "D"
        )

        if isinstance(player_frames, dict):
            active_frame = player_frames[dir_key][
                current_frame % len(player_frames[dir_key])
            ]
        else:
            active_frame = player_frames[current_frame % len(player_frames)]

        rect = active_frame.get_rect(
            center=(int(self.visual_x - 1), int(self.visual_y))
        )
        vis.screen.blit(active_frame, rect)
