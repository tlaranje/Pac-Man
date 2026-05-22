from ..parser import PacManConfig
from ..models import PacManMap


class PacManEntity:
    """
    :TODO
    """

    def __init__(self, map: PacManMap) -> None:
        self.current_map: PacManMap = map
        self.x: int = map._entryx
        self.y: int = map._entryy


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


def render_maze(maze: list[list[int]], player: PacManEntity = None) -> None:
    """
    Render a maze in terminal.
    Each cell uses 4 bits:
        bit 0 -> North
        bit 1 -> East
        bit 2 -> South
        bit 3 -> West
    If a bit is 1 => wall exists.
    """
    rows = len(maze)
    cols = len(maze[0])

    # top border
    for x in range(cols):
        cell = maze[0][x]
        if cell & (1 << 0):  # north wall
            print("+---", end="")
        else:
            print("+   ", end="")
    print("+")

    for y in range(rows):
        # vertical walls + cell content
        for x in range(cols):
            cell = maze[y][x]
            # west wall
            if cell & (1 << 3):
                print("|", end="")
            else:
                print(" ", end="")
            # cell content
            if player is not None and player.x == x and player.y == y:
                print(" P ", end="")
            else:
                print("   ", end="")
        # east wall of last cell
        last = maze[y][-1]
        if last & (1 << 1):
            print("|")
        else:
            print(" ")
        # south walls
        for x in range(cols):
            cell = maze[y][x]
            print("+", end="")
            if cell & (1 << 2):
                print("---", end="")
            else:
                print("   ", end="")
        print("+")


config = PacManConfig("/home/joesanto/Downloads/test.json")
pacman = PacManGameplay(config)
pacman.gameplay_init(0)
render_maze(pacman.maps[0].maze, pacman.player)
