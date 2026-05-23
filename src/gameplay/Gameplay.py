import curses
import time
from ..parser import PacManConfig
from ..models import PacManMap

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8


class PacManEntity:
    """
    :TODO
    """

    def __init__(self, map: PacManMap) -> None:
        self.current_map: list[list[int]] = map._maze
        self.x: int = map._entryx
        self.y: int = map._entryy

    def move_up(self) -> None:
        if self.current_map[self.y][self.x] & NORTH:
            return
        self.y -= 1

    def move_down(self) -> None:
        if self.current_map[self.y][self.x] & SOUTH:
            return
        self.y += 1

    def move_right(self) -> None:
        if self.current_map[self.y][self.x] & EAST:
            return
        self.x += 1

    def move_left(self) -> None:
        if self.current_map[self.y][self.x] & WEST:
            return
        self.x -= 1


class PacManGameplay:
    """
    :TODO
    """

    def __init__(self, config: PacManConfig) -> None:
        self.maps: list[PacManMap] = config.load_maps()
        self.maps_count: int = len(self.maps)
        self.player: PacManEntity = None

    def gameplay_init(self, map_idx: int) -> None:
        if map_idx < 0 or map_idx >= self.maps_count:
            return
        self.player = PacManEntity(self.maps[map_idx])


# ----------------------------
# MAZE RENDERER (CURSES)
# ----------------------------


def render_maze(stdscr, maze: list[list[int]], player=None) -> None:
    rows = len(maze)
    cols = len(maze[0])

    y_offset = 0

    # top border
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

            # player or empty
            if player is not None and player.x == x and player.y == y:
                line += " P "
            else:
                line += "   "

        # east wall
        last = maze[y][-1]
        if last & (1 << 1):
            line += "|"

        stdscr.addstr(y_offset, 0, line)
        y_offset += 1

        # bottom walls
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
    curses.curs_set(0)  # hide cursor

    config = PacManConfig("/home/joel/Downloads/test.json")
    pacman = PacManGameplay(config)
    pacman.gameplay_init(0)

    while True:
        key = stdscr.getch()

        # INPUT
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

        # RENDER
        stdscr.clear()
        render_maze(stdscr, pacman.maps[0].maze, pacman.player)
        stdscr.refresh()

        # GAME SPEED (adjust for smoothness)
        time.sleep(0.05)


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    curses.wrapper(main)
