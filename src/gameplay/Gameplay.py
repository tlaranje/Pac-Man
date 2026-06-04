from ..models import PacManMap, PacGumsMap
from src.visualizer._constants import SUPER_TIME
from ..parser import PacManConfig
from typing import Any
from math import ceil
import random
import pygame

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8


class PacManEntity:
    """Base class for game entities with movement and interaction logic.

    Provides directional movement, collision detection with maze walls,
    and the ability to consume objects on the maze.
    """

    def __init__(self, x: int, y: int, map: PacManMap) -> None:
        self.map: PacManMap = map
        self.maze: list[list[int]] = map._maze
        self.x: int = x
        self.y: int = y

    def get_possible_moves(self) -> list[str]:
        """
        Get valid movement directions from current position.

        Returns:
            List of valid direction codes.
        """
        possible_moves: list[str] = []
        cell: int = self.maze[self.y][self.x]
        if not cell & NORTH:
            possible_moves.append("N")
        if not cell & SOUTH:
            possible_moves.append("S")
        if not cell & EAST:
            possible_moves.append("E")
        if not cell & WEST:
            possible_moves.append("W")
        return possible_moves

    def eat(self, objects_map: list[list[tuple[bool, str]]]) -> None:
        """
        Consume an object at the entity's current position.

        Args:
            objects_map: 2D map of objects on the maze.
        """
        cell_type: str = objects_map[self.y][self.x][1]
        objects_map[self.y][self.x] = (False, cell_type)

    def move(self, direction: str) -> None:
        """
        Move in the specified direction if not blocked.

        Args:
            direction: Direction code (N, S, E, W).
        """
        if direction == "N":
            self.move_up()
        elif direction == "S":
            self.move_down()
        elif direction == "E":
            self.move_right()
        elif direction == "W":
            self.move_left()

    def move_up(self) -> None:
        """
        Move one cell up if not blocked by a wall.
        """
        if self.maze[self.y][self.x] & NORTH:
            return
        self.y -= 1

    def move_down(self) -> None:
        """
        Move one cell down if not blocked by a wall.
        """
        if self.maze[self.y][self.x] & SOUTH:
            return
        self.y += 1

    def move_right(self) -> None:
        """
        Move one cell right if not blocked by a wall.
        """
        if self.maze[self.y][self.x] & EAST:
            return
        self.x += 1

    def move_left(self) -> None:
        """
        Move one cell left if not blocked by a wall.
        """
        if self.maze[self.y][self.x] & WEST:
            return
        self.x -= 1

    def is_on_corridor_pos(self, x: int, y: int) -> bool:
        """
        Check if a position lies on the same corridor.

        Args:
            x: X coordinate of target position.
            y: Y coordinate of target position.

        Returns:
            True if position is on the same corridor, False otherwise.
        """
        save_entryx: int = self.map._entryx
        save_entryy: int = self.map._entryy
        save_exitx: int = self.map._exitx
        save_exity: int = self.map._exity

        self.map._entryx = self.x
        self.map._entryy = self.y
        self.map._exitx = x
        self.map._exity = y

        self.map._find_short_path()
        is_on_same_corridor = len(set(self.map._shortest_path)) == 1

        self.map._entryx = save_entryx
        self.map._entryy = save_entryy
        self.map._exitx = save_exitx
        self.map._exity = save_exity

        return is_on_same_corridor


class PacManGhost(PacManEntity):
    """Ghost entity with pathfinding, respawn behavior, and AI modes.

    Extends PacManEntity with pathfinding algorithms (chase, run-away),
    random movement, scared state, and respawn timing.
    """

    TIME_TO_RESPAWN = 5000

    def __init__(self,
                 x: int,
                 y: int,
                 map: PacManMap) -> None:
        super().__init__(x, y, map)
        self.spawn_x: int = x
        self.spawn_y: int = y

        self.repeat_move: int = 0
        self.last_diretion: int = 0
        self.shortest_path: Any = ""
        self.last_chase_x: int = 0
        self.last_chase_y: int = 0
        self.last_move: Any
        self.ghost_angle: int = 0
        self.is_scared: bool = False
        self.last_death: int | None = None

    def die(self) -> None:
        """
        Mark the ghost as dead and record the timestamp.
        """
        self.last_death = pygame.time.get_ticks()

    def is_dead(self) -> bool:
        """
        Check if the ghost is in the respawn cooldown period.

        Returns:
            True if still in respawn cooldown, False otherwise.
        """
        if self.last_death is None:
            return False
        return pygame.time.get_ticks() - self.last_death < self.TIME_TO_RESPAWN

    def reset_position(self) -> None:
        """
        Reset the entity to its spawn point.
        """
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.shortest_path = ""
        self.last_chase_x = 0
        self.last_chase_y = 0
        self.repeat_move = 0
        self.last_diretion = 0
        self.is_scared = False

    def update_ghost_angle(self) -> None:
        """
        Update the ghost's rotation angle based on movement direction.
        """
        if self.last_diretion == NORTH:
            self.ghost_angle = 90
        elif self.last_diretion == SOUTH:
            self.ghost_angle = 270
        elif self.last_diretion == WEST:
            self.ghost_angle = 180
        elif self.last_diretion == EAST:
            self.ghost_angle = 0

    def move(self, direction: str) -> None:
        """
        Move in the specified direction if not blocked.

        Args:
            direction: Direction code (N, S, E, W).
        """
        super().move(direction)

        if direction == "N":
            self.last_diretion = NORTH
        elif direction == "S":
            self.last_diretion = SOUTH
        elif direction == "E":
            self.last_diretion = EAST
        elif direction == "W":
            self.last_diretion = WEST

        self.update_ghost_angle()

    def move_away(self, direction: str) -> None:
        """
        Move away from a specified direction.

        Args:
            direction: Direction code to move away from.
        """
        possible_moves = [
            move for move in super().get_possible_moves()
            if move != direction
        ]
        if not possible_moves:
            return
        self.move(random.choice(possible_moves))

    def move_randomly(self) -> None:
        """
        Move randomly with weighted preference for previous direction.
        """
        map = self.maze
        x: int = self.x
        y: int = self.y

        if self.repeat_move > 0 and not map[y][x] & self.last_diretion \
                and random.random() > 0.1:
            self.repeat_move -= 1
            self.last_move()
            self.update_ghost_angle()
            return

        self.repeat_move = 4
        cell: int = map[y][x]
        directions = [
            (self.move_up, NORTH),
            (self.move_right, EAST),
            (self.move_down, SOUTH),
            (self.move_left, WEST),
        ]
        options = []
        weights = []

        for direction in directions:
            if cell & direction[1]:
                continue
            options.append(direction)
            if direction[1] == self.last_diretion:
                weights.append(0.15)
            else:
                weights.append(1.0)

        if options:
            move = random.choices(options, weights=weights, k=1)[0]
            move[0]()
            self.last_move = move[0]
            self.last_diretion = move[1]
            self.update_ghost_angle()

    def chase_position(self, x: int, y: int) -> None:
        """
        Chase a target position using pathfinding algorithm.

        Args:
            x: X coordinate of target.
            y: Y coordinate of target.
        """
        if self.last_chase_x == x and self.last_chase_y == y \
                and self.shortest_path:
            self.move(self.shortest_path[0])
            self.shortest_path = self.shortest_path[1:]
            return

        save_entryx: int = self.map._entryx
        save_entryy: int = self.map._entryy
        save_exitx: int = self.map._exitx
        save_exity: int = self.map._exity

        self.map._entryx = self.x
        self.map._entryy = self.y
        self.map._exitx = x
        self.map._exity = y

        self.last_chase_x = x
        self.last_chase_y = y

        self.map._find_short_path()
        self.shortest_path = self.map._shortest_path[:]
        if self.shortest_path:
            self.move(self.shortest_path[0])
            self.shortest_path = self.shortest_path[1:]

        self.map._entryx = save_entryx
        self.map._entryy = save_entryy
        self.map._exitx = save_exitx
        self.map._exity = save_exity

    def run_away(self, x: int, y: int) -> None:
        """
        Run away from a target position using pathfinding.

        Args:
            x: X coordinate to flee from.
            y: Y coordinate to flee from.
        """
        self.shortest_path = None
        save_entryx: int = self.map._entryx
        save_entryy: int = self.map._entryy
        save_exitx: int = self.map._exitx
        save_exity: int = self.map._exity

        self.map._entryx = self.x
        self.map._entryy = self.y
        self.map._exitx = x
        self.map._exity = y

        self.map._find_short_path()
        if self.map._shortest_path:
            self.move_away(self.map._shortest_path[0])

        self.map._entryx = save_entryx
        self.map._entryy = save_entryy
        self.map._exitx = save_exitx
        self.map._exity = save_exity


class PacManPlayer(PacManEntity):
    """Player-controlled Pac-Man entity with power-ups and ghost interaction.

    Extends PacManEntity with invincibility toggling, super pacgum activation,
    ghost collision detection, and multi-ghost consumption.
    """

    def __init__(self, x: int, y: int, map: PacManMap,
                 ghosts_map: list[PacManGhost]) -> None:
        super().__init__(x, y, map)
        self.ghosts_map: list[PacManGhost] = ghosts_map
        self.spawn_x: int = x
        self.spawn_y: int = y
        self.super_start: int | None = None
        self.is_invencible: bool = False

    def toggle_invencibility(self) -> None:
        """
        Toggle the player's invincibility state.
        """
        self.is_invencible = not self.is_invencible

    def turn_on_super(self) -> None:
        """
        Activate super pacgum mode and scare all ghosts.
        """
        self.super_start = pygame.time.get_ticks()
        for ghost in self.ghosts_map:
            if not ghost.is_dead():
                ghost.is_scared = True

    def is_on_super(self) -> bool:
        """
        Check if the player is in super mode.

        Returns:
            True if super mode is active, False otherwise.
        """
        if self.super_start is None:
            return False
        return pygame.time.get_ticks() - self.super_start <= SUPER_TIME

    def reset_position(self) -> None:
        """
        Reset the entity to its spawn point.
        """
        self.x = self.spawn_x
        self.y = self.spawn_y

    def is_on_ghost(self) -> bool:
        """
        Check if the player occupies the same cell as a ghost.

        Returns:
            True if player collides with a ghost, False otherwise.
        """
        for ghost in self.ghosts_map:
            if ghost.is_dead():
                continue
            if ghost.x == self.x \
                    and ghost.y == self.y:
                return True
        return False

    def is_dead(self) -> bool:
        """
        Check if the ghost is in the respawn cooldown period.

        Returns:
            True if still in respawn cooldown, False otherwise.
        """
        if self.is_invencible:
            return False
        if not self.is_on_super():
            return self.is_on_ghost()
        for ghost in self.ghosts_map:
            if ghost.is_dead():
                continue
            if ghost.x == self.x \
                    and ghost.y == self.y \
                    and (not ghost.is_scared):
                return True
        return False

    def eat_ghosts(self) -> int:
        """
        Consume scared ghosts at the player's position.

        Returns:
            Number of ghosts consumed.
        """
        ghosts_ate: int = 0
        for ghost in self.ghosts_map:
            if ghost.is_dead():
                continue
            if ghost.x == self.x \
                    and ghost.y == self.y and ghost.is_scared:
                ghosts_ate += 1
                ghost.die()
                ghost.reset_position()

        return ghosts_ate


class PacManGameplay:
    """Central game controller managing levels, entities, and progression.

    Loads configuration, manages multiple levels, coordinates ghost and player
    behavior, tracks score and lives, and handles level transitions.
    """

    def __init__(self, config: PacManConfig) -> None:
        self.config: PacManConfig = config
        self.maps: list[PacManMap] = config.load_maps()
        self.maps_middle: list[tuple[int, int]] = config.load_maps_middle(
            self.maps
        )
        self.maps_count: int = len(self.maps)
        self.pacgums_maps: list[PacGumsMap] = config.load_pacgums(
            self.maps
        )
        self.ghosts_maps: list[list[PacManGhost]] = config.load_ghosts(
            self.maps
        )
        self.player: PacManPlayer
        self.map_idx: int = 0
        self.chase_moves: list[int] = [0] * len(self.ghosts_maps[self.map_idx])
        self.freeze_ghosts: bool = False
        self.level_start: int | None = None

    def toggle_freeze_ghosts(self) -> None:
        """
        Pause or resume ghost movement.
        """
        self.freeze_ghosts = not self.freeze_ghosts

    def next_level(self) -> bool:
        """
        Advance to the next level if available.

        Returns:
            True if next level exists, False if game is won.
        """
        index_map = self.map_idx + 1

        if index_map >= len(self.config.settings.levels):
            return False

        self.map_idx = index_map
        self.gameplay_init(self.map_idx)

        return True

    def is_win(self) -> bool:
        """
        Check if all pacgums on current level are consumed.

        Returns:
            True if all pacgums eaten, False otherwise.
        """
        for row in self.pacgums_maps[self.map_idx]:
            for pacgum in row:
                if pacgum[0]:
                    return False
        return True

    def reset(self) -> None:
        """
        Reset game state for the current level.
        """
        self.pacgums_maps = self.config.load_pacgums(self.maps)
        self.ghosts_maps = self.config.load_ghosts(
            self.maps
        )
        self.gameplay_init(self.map_idx)

    def get_level_time(self) -> int:
        """
        Get elapsed time in milliseconds since level start.

        Returns:
            Elapsed time in milliseconds.
        """
        if self.level_start is None:
            return 0
        return (pygame.time.get_ticks() - self.level_start)

    def get_level_time_remaining(self) -> int:
        """
        Get remaining time in seconds for the level.

        Returns:
            Remaining time in seconds, or 0 if time limit exceeded.
        """
        level_time: int = self.get_level_time()
        if level_time >= self.config.settings.level_max_time_ms:
            return 0
        return ceil(
            (self.config.settings.level_max_time_ms - level_time) / 1000
        )

    def gameplay_init(self, map_idx: int) -> None:
        """
        Initialize gameplay state for a specific level.

        Args:
            map_idx: Index of the level to initialize.
        """
        if map_idx < 0 or map_idx >= self.maps_count:
            return
        self.map_idx = map_idx
        x: int = self.maps_middle[map_idx][0]
        y: int = self.maps_middle[map_idx][1]
        self.player = PacManPlayer(
            x, y, self.maps[map_idx],
            self.ghosts_maps[self.map_idx]
        )

    def move_ghosts(self) -> None:
        """
        Execute movement logic for all ghosts in current level.
        """
        if self.freeze_ghosts:
            return
        for i, ghost in enumerate(self.ghosts_maps[self.map_idx]):
            if ghost.is_dead():
                continue
            player_x: int = self.player.x
            player_y: int = self.player.y
            if ghost.is_scared:
                self.chase_moves[i] = 0
                ghost.run_away(player_x, player_y)
                continue
            if ghost.is_on_corridor_pos(player_x, player_y):
                self.chase_moves[i] = 20
            if self.chase_moves[i] > 0:
                self.chase_moves[i] -= 1
                ghost.chase_position(player_x, player_y)
            else:
                ghost.move_randomly()
