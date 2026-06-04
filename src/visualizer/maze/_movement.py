import pygame
from pygame.key import ScancodeWrapper


class MovementController:
    """Movement validation and input direction detection.

    Provides collision detection for movement validation and converts
    keyboard input to direction codes.
    """

    def __init__(self, maze_grid: list):
        self.maze_grid = maze_grid

    def can_move(self, px: int, py: int, direction: str) -> bool:
        """
        Check if movement in a direction is valid.

        Args:
            px: Player X coordinate.
            py: Player Y coordinate.
            direction: Direction code.

        Returns:
            True if movement is valid, False otherwise.
        """
        if py < 0 or py >= len(self.maze_grid) \
           or px < 0 or px >= len(self.maze_grid[0]):
            return False

        current_cell = self.maze_grid[py][px]

        if direction == "UP" and not (current_cell & 1):
            return True
        if direction == "RIGHT" and not (current_cell & 2):
            return True
        if direction == "DOWN" and not (current_cell & 4):
            return True
        if direction == "LEFT" and not (current_cell & 8):
            return True
        return False

    @staticmethod
    def get_direction_from_input(keys: ScancodeWrapper) -> str | None:
        """
        Get movement direction from keyboard input.

        Args:
            keys: Pressed keys state.

        Returns:
            Direction code or None if no valid input.
        """
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            return "LEFT"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            return "RIGHT"
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            return "UP"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            return "DOWN"
        return None
