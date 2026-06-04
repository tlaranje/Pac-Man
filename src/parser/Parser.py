import random
import json
import re
from argparse import ArgumentParser
from pathlib import Path
from mazegenerator import MazeGenerator
from ..models import PacManMap, PacGumsMap, PacManConfigModel


class PacManCLI:
    """Command-line interface parser for Pac-Man game configuration.

    Parses command-line arguments and validates the JSON configuration
    file path before game initialization.
    """

    def __init__(self) -> None:
        def json_file(path: str) -> str:
            """
            Validate JSON file path.

            Args:
                path: File path to validate.

            Returns:
                Path if valid JSON file, raises error otherwise.
            """
            file_path: Path = Path(path)
            if file_path.suffix != ".json":
                raise TypeError("Config must be .json format")
            return path

        self.parser: ArgumentParser = ArgumentParser()
        self.parser.add_argument(
            "config",
            type=json_file,
            help="Path to the .json config file"
        )
        self.args = self.parser.parse_args()


class PacManConfig:
    """Configuration loader that constructs game entities from JSON.

    Reads and parses JSON configuration files, generates mazes,
    places pacgums, and initializes ghost spawn positions.
    """

    def __init__(self, path: str) -> None:
        with open(path, "r") as file:
            content: str = re.sub(
                r"^\s*#.*$", "", file.read(), flags=re.MULTILINE
            )
            try:
                data = json.loads(content)
            except Exception:
                data = {}

        if not isinstance(data, dict):
            print(
                "[Warning] Config file must be a JSON object. "
                "Using all defaults."
            )
            data = {}

        self.settings = PacManConfigModel(data)

    def load_maps(self) -> list[PacManMap]:
        """
        Load and generate all level mazes.

        Returns:
            List of generated maze objects.
        """
        maps: list[PacManMap] = []
        for i, level in enumerate(self.settings.levels):
            size: tuple[int, int] = (level.width, level.height)
            maps.append(
                MazeGenerator(
                    size=size,
                    perfect=False,
                    seed=self.settings.seeds[i]
                )
            )
        return maps

    def load_pacgums(self, maps: list[PacManMap]) -> list[PacGumsMap]:
        """
        Generate pacgum placement for all mazes.

        Args:
            maps: List of maze objects.

        Returns:
            List of pacgum maps.
        """
        pacgums_maps: list[PacGumsMap] = []
        for map in maps:
            corners = self.load_corners(map)
            walkable: list[tuple[int, int]] = [
                (x, y)
                for y in range(map._height)
                for x in range(map._width)
                if (map._maze[y][x] & 0b1111) != 0b1111
                if (x, y) not in corners
            ]
            count: int = min(self.settings.pacgum, len(walkable))
            chosen = random.sample(walkable, count)

            pacgums_map = [
                [(False, "none") for _ in range(map._width)]
                for _ in range(map._height)
            ]

            for x, y in chosen:
                pacgums_map[y][x] = (True, "normal")

            for x, y in corners:
                pacgums_map[y][x] = (True, "super")

            pacgums_maps.append(pacgums_map)

        return pacgums_maps

    def load_corners(self, map: PacManMap) -> list[tuple[int, int]]:
        """
        Get the four corner positions of a maze.

        Args:
            map: Maze object.

        Returns:
            List of four corner coordinate tuples.
        """
        return [
            (0, 0),
            (map._width - 1, 0),
            (0, map._height - 1),
            (map._width - 1, map._height - 1)
        ]

    def load_maps_middle(self, maps: list[PacManMap]) -> list[tuple[int, int]]:
        """
        Find center positions for all mazes.

        Args:
            maps: List of maze objects.

        Returns:
            List of center coordinate tuples.
        """
        return [self._find_closest_walkable_center(map) for map in maps]

    def _find_closest_walkable_center(self, map: PacManMap) -> tuple[int, int]:
        """
        Find the closest walkable cell to maze center.

        Args:
            map: Maze object.

        Returns:
            Closest walkable center coordinate tuple.
        """
        center_x = map._width // 2
        center_y = map._height // 2

        walkable = [
            (x, y)
            for y in range(map._height)
            for x in range(map._width)
            if (map.maze[y][x] & 0b1111) != 0b1111
        ]

        return min(
            walkable,
            key=lambda pos: abs(pos[0] - center_x) + abs(pos[1] - center_y)
        )

    def load_ghosts(self,
                    maps: list[PacManMap]) -> list[list]:
        """
        Create ghost entities at maze corners.

        Args:
            maps: List of maze objects.

        Returns:
            List of ghost lists, one per maze.
        """
        from ..gameplay import PacManGhost
        ghosts_maps: list[list[PacManGhost]] = []

        for i, map in enumerate(maps):
            ghosts: list[PacManGhost] = []
            corners: list[tuple[int, int]] = self.load_corners(map)

            for j in range(4):
                ghost = PacManGhost(
                    x=corners[j][0],
                    y=corners[j][1],
                    map=map,
                )

                ghosts.append(ghost)

            ghosts_maps.append(ghosts)

        return ghosts_maps
