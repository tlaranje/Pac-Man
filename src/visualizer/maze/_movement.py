import pygame


class MovementController:
    def __init__(self, maze_grid: list):
        self.maze_grid = maze_grid

    def can_move(self, px: int, py: int, direction: str) -> bool:
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
    def get_direction_from_input(keys) -> str | None:
        if keys[pygame.K_a]:
            return "LEFT"
        if keys[pygame.K_d]:
            return "RIGHT"
        if keys[pygame.K_w]:
            return "UP"
        if keys[pygame.K_s]:
            return "DOWN"
        return None
