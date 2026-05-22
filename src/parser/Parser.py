import json
import re
from argparse import ArgumentParser
from pathlib import Path
from mazegenerator import MazeGenerator
from ..models import PacManMap, PacManConfigModel


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
            maps.append(
                MazeGenerator(
                    size=size,
                    entry_cell=start_position,
                    perfect=False,
                    seed=self.settings.seed
                )
            )
        return maps
