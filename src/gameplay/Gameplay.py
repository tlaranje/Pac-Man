import random
from ..parser import PacManConfig
from ..models import PacManMap, PacGumsMap
from typing import Any

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8


class PacManEntity:
    """
    :TODO
    """

    def __init__(self, x: int, y: int, map: PacManMap) -> None:
        self.map: PacManMap = map
        self.maze: list[list[int]] = map._maze
        self.x: int = x
        self.y: int = y

    def eat(self, objects_map: list[list[tuple[bool, str]]]) -> None:
        cell_type: str = objects_map[self.y][self.x][1]
        objects_map[self.y][self.x] = (False, cell_type)

    def move(self, direction: str) -> None:
        if direction == "N":
            self.move_up()
        elif direction == "S":
            self.move_down()
        elif direction == "E":
            self.move_right()
        elif direction == "W":
            self.move_left()

    def move_up(self) -> None:
        if self.maze[self.y][self.x] & NORTH:
            return
        self.y -= 1

    def move_down(self) -> None:
        if self.maze[self.y][self.x] & SOUTH:
            return
        self.y += 1

    def move_right(self) -> None:
        if self.maze[self.y][self.x] & EAST:
            return
        self.x += 1

    def move_left(self) -> None:
        if self.maze[self.y][self.x] & WEST:
            return
        self.x -= 1

    def is_on_corridor_pos(self, x: int, y: int) -> bool:
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
    """
    :TODO
    """

    def __init__(self, x: int, y: int, map: PacManMap) -> None:
        super().__init__(x, y, map)
        self.repeat_move: int = 0
        self.last_diretion: int = 0
        self.shortest_path: str = ""
        self.last_chase_x: int = 0
        self.last_chase_y: int = 0
        self.last_move: Any
        self.ghost_angle: int = 0

    def update_ghost_angle(self) -> None:
        if self.last_diretion == NORTH:
            self.ghost_angle = 90
        elif self.last_diretion == SOUTH:
            self.ghost_angle = 270
        elif self.last_diretion == WEST:
            self.ghost_angle = 180
        elif self.last_diretion == EAST:
            self.ghost_angle = 0

    def move(self, direction: str) -> None:
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

    def move_randomly(self) -> None:
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


class PacManPlayer(PacManEntity):
    """
    :TODO
    """

    def __init__(self, x: int, y: int, map: PacManMap,
                 ghosts_map: list[PacManGhost]) -> None:
        super().__init__(x, y, map)
        self.ghosts_map: list[PacManGhost] = ghosts_map

    def is_dead(self) -> bool:
        for ghost in self.ghosts_map:
            if ghost.x == self.x \
                    and ghost.y == self.y:
                return True
        return False


class PacManGameplay:
    """
    :TODO
    """

    def __init__(self, config: PacManConfig) -> None:
        self.config: PacManConfig = config
        self.maps: list[PacManMap] = config.load_maps()
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

    def reset(self) -> None:
        self.pacgums_maps = self.config.load_pacgums(self.maps)
        self.ghosts_maps = self.config.load_ghosts(self.maps)
        self.gameplay_init(0)

    def gameplay_init(self, map_idx: int) -> None:
        if map_idx < 0 or map_idx >= self.maps_count:
            return
        self.map_idx = map_idx
        x: int = self.maps[map_idx]._entryx
        y: int = self.maps[map_idx]._entryy
        self.player = PacManPlayer(
            x, y, self.maps[map_idx],
            self.ghosts_maps[self.map_idx]
        )

    def move_ghosts(self) -> None:
        for i, ghost in enumerate(self.ghosts_maps[self.map_idx]):
            player_x: int = self.player.x
            player_y: int = self.player.y
            if ghost.is_on_corridor_pos(player_x, player_y):
                self.chase_moves[i] = 20
            if self.chase_moves[i] > 0:
                self.chase_moves[i] -= 1
                ghost.chase_position(player_x, player_y)
            else:
                ghost.move_randomly()
