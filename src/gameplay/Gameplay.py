import curses
import time
import random
from ..parser import PacManConfig
from ..models import PacManMap, PacGumsMap

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

    def eat(self, objects_map: list[list[bool]]) -> None:
        objects_map[self.y][self.x] = False

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
        self.last_chase_x: int = None
        self.last_chase_y: int = None
        self.last_move = None

    def move_randomly(self) -> None:
        map = self.maze
        x: int = self.x
        y: int = self.y

        if self.repeat_move > 0 and not map[y][x] & self.last_diretion \
                and random.random() > 0.1:
            self.repeat_move -= 1
            self.last_move()
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


class PacManGameplay:
    """
    :TODO
    """

    def __init__(self, config: PacManConfig) -> None:
        self.maps: list[PacManMap] = config.load_maps()
        self.maps_count: int = len(self.maps)
        self.pacgums_maps: list[PacGumsMap] = config.load_pacgums(
            self.maps
        )
        self.ghosts_maps: list[list[PacManGhost]] = config.load_ghosts(
            self.maps
        )
        self.player: PacManEntity = None
        self.map_idx: int = 0

    def gameplay_init(self, map_idx: int) -> None:
        if map_idx < 0 or map_idx >= self.maps_count:
            return
        self.map_idx = map_idx
        x: int = self.maps[map_idx]._entryx
        y: int = self.maps[map_idx]._entryy
        self.player = PacManEntity(x, y, self.maps[map_idx])

    def move_ghosts(self) -> None:
        chasing_moves: list[int] = [0] * len(self.ghosts_maps[self.map_idx])
        for i, ghost in enumerate(self.ghosts_maps[self.map_idx]):
            playerx: int = self.player.x
            playery: int = self.player.y
            if ghost.is_on_corridor_pos(playerx, playery):
                chasing_moves[i] = 20
            if chasing_moves[i] > 0:
                chasing_moves[i] -= 1
                ghost.chase_position(playerx, playery)
            else:
                ghost.move_randomly()


def render_maze(
    stdscr,
    maze: list[list[int]],
    pacgums_map,
    player=None,
    ghosts: list = None
) -> None:

    rows = len(maze)
    cols = len(maze[0])

    y_offset = 0

    # Precompute ghost positions for fast lookup
    ghost_positions = {
        (g.x, g.y)
        for g in ghosts
    } if ghosts else set()

    # ------------------------
    # TOP BORDER
    # ------------------------
    line = ""

    for x in range(cols):
        cell = maze[0][x]

        if cell & (1 << 0):
            line += "+---"
        else:
            line += "+   "

    line += "+"

    stdscr.addstr(y_offset, 0, line)
    y_offset += 1

    # ------------------------
    # MAZE BODY
    # ------------------------
    for y in range(rows):

        # vertical walls + content
        line = ""

        for x in range(cols):

            cell = maze[y][x]

            # west wall
            if cell & (1 << 3):
                line += "|"
            else:
                line += " "

            # PLAYER
            if player is not None and player.x == x and player.y == y:
                line += " P "

            # GHOST
            elif (x, y) in ghost_positions:
                line += " G "

            # PACGUM
            elif pacgums_map[y][x]:
                line += " @ "

            # EMPTY
            else:
                line += "   "

        # east wall
        last = maze[y][-1]

        if last & (1 << 1):
            line += "|"

        stdscr.addstr(y_offset, 0, line)
        y_offset += 1

        # ------------------------
        # SOUTH WALLS
        # ------------------------
        line = ""

        for x in range(cols):

            cell = maze[y][x]

            line += "+"

            if cell & (1 << 2):
                line += "---"
            else:
                line += "   "

        line += "+"

        stdscr.addstr(y_offset, 0, line)
        y_offset += 1


# ----------------------------
# GAME LOOP
# ----------------------------
def main(stdscr):

    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.curs_set(0)

    config = PacManConfig("/home/joesanto/Downloads/test.json")

    pacman = PacManGameplay(config)
    pacman.gameplay_init(0)

    while True:

        # ------------------------
        # GAME UPDATE
        # ------------------------
        pacman.player.eat(
            pacman.pacgums_maps[0]
        )
        pacman.move_ghosts()

        # ------------------------
        # INPUT
        # ------------------------
        key = stdscr.getch()

        if key == ord('w'):
            pacman.player.move_up()

        elif key == ord('d'):
            pacman.player.move_right()

        elif key == ord('s'):
            pacman.player.move_down()

        elif key == ord('a'):
            pacman.player.move_left()

        elif key == ord('q'):
            break

        # ------------------------
        # RENDER
        # ------------------------
        stdscr.clear()

        render_maze(
            stdscr,
            pacman.maps[0].maze,
            pacman.pacgums_maps[0],
            pacman.player,
            pacman.ghosts_maps[0]
        )

        stdscr.refresh()

        # ------------------------
        # FPS CONTROL
        # ------------------------
        time.sleep(0.7)


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    curses.wrapper(main)
