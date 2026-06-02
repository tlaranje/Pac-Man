import random
import json
import re
from argparse import ArgumentParser
from pathlib import Path
from mazegenerator import MazeGenerator
from ..models import PacManMap, PacGumsMap, PacManConfigModel


class PacManCLI:
    """
    :TODO
    """

    def __init__(self) -> None:
        def json_file(path: str) -> str:
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
    """
    :TODO
    """

    def __init__(self, path: str) -> None:
        with open(path, "r") as file:
            content: str = re.sub(
                r"^\s*#.*$", "", file.read(), flags=re.MULTILINE
            )
            data = json.loads(content)

        if not isinstance(data, dict):
            print(
                "[Warning] Config file must be a JSON object. "
                "Using all defaults."
            )
            data = {}

        self.settings = PacManConfigModel(data)

    def load_maps(self) -> list[PacManMap]:
        maps: list[PacManMap] = []
        for i, level in enumerate(self.settings.levels):
            size: tuple[int, int] = (level.width, level.height)
            start_position: tuple[int, int] = (level.start_x, level.start_y)
            maps.append(
                MazeGenerator(
                    size=size,
                    entry_cell=start_position,
                    perfect=False,
                    seed=self.settings.seeds[i]
                    )
                )
        return maps

    def load_pacgums(self, maps: list[PacManMap]) -> list[PacGumsMap]:
        pacgums_maps: list[PacGumsMap] = []
        for map in maps:
            walkable: list[tuple[int, int]] = [
                (x, y)
                for y in range(map._height)
                for x in range(map._width)
                if (map._maze[y][x] & 0b1111) != 0b1111
            ]
            count: int = min(self.settings.pacgum, len(walkable))
            chosen = random.sample(walkable, count)

            pacgums_map = [
                [(False, "none") for _ in range(map._width)]
                for _ in range(map._height)
            ]

            for x, y in chosen:
                pacgums_map[y][x] = (True, "normal")

            for x, y in self.load_corners(map):
                pacgums_map[y][x] = (True, "super")

            pacgums_maps.append(pacgums_map)

        return pacgums_maps

    def load_corners(self, map: PacManMap) -> list[tuple[int, int]]:
        return [
                (0, 0),
                (map._width - 1, 0),
                (0, map._height - 1),
                (map._width - 1, map._height - 1)
            ]

    def load_maps_middle(self, maps: list[PacManMap]) -> list[tuple[int, int]]:
        return [self._find_closest_walkable_center(map) for map in maps]

    def _find_closest_walkable_center(self, map: PacManMap) -> tuple[int, int]:
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
