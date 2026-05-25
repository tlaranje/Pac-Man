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
        for level in self.settings.levels:
            size: tuple[int, int] = (level.width, level.height)
            start_position: tuple[int, int] = (level.start_x, level.start_y)
            print(size)
            maps.append(
                MazeGenerator(
                    size=size,
                    entry_cell=start_position,
                    perfect=False,
                    seed=self.settings.seed
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
                if (map._maze[y][x] & 0b1111) != 0
            ]

            count: int = min(self.settings.pacgum, len(walkable))
            chosen = random.sample(walkable, count)

            pacgums_map = [[False] * map._width for _ in range(map._height)]
            for x, y in chosen:
                pacgums_map[y][x] = True
            pacgums_maps.append(pacgums_map)
        return pacgums_maps

    def load_ghosts(self, maps: list[PacManMap]) -> list[list]:
        from ..gameplay import PacManGhost
        ghosts_maps: list[list[PacManGhost]] = []

        for map in maps:
            ghosts: list[PacManGhost] = []

            for _ in range(5):
                ghost = PacManGhost(
                    x=map._exitx,
                    y=map._exity,
                    map=map
                )

                ghosts.append(ghost)

            ghosts_maps.append(ghosts)

        return ghosts_maps
