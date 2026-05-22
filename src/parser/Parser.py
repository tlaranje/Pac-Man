import json
import re
from argparse import ArgumentParser
from pathlib import Path
from pydantic import BaseModel, model_validator


def json_file(path: str) -> str:
    """
    :TODO
    """
    file_path: Path = Path(path)

    if file_path.suffix != ".json":
        raise TypeError("Config must be .json format")

    return path


class PacManCLI:
    """
    :TODO
    """

    def __init__(self) -> None:
        self.parser: ArgumentParser = ArgumentParser()

        self.parser.add_argument(
            "config",
            type=json_file,
            help="Path to the .json config file"
        )

        self.args = self.parser.parse_args()


DEFAULT_WIDTH: int = 20
DEFAULT_HEIGHT: int = 20


class PacManLevel(BaseModel):
    """
    :TODO
    """
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT

    @model_validator(mode="after")
    def fallback_to_defaults(self):
        def warning(value: str, field: str) -> None:
            print(
                f"[Warning] Invalid value \"{value}\" to field \"{field}\". "
                "Setting to default value."
            )

        if not isinstance(self.width, int) \
                or self.width <= 0:
            warning(self.width, "width")
            self.width = DEFAULT_WIDTH

        if not isinstance(self.height, int) \
                or self.height <= 0:
            warning(self.height, "height")
            self.height = DEFAULT_HEIGHT

        return self


DEFAULT_HIGHSCORE_FILENAME: str = "output_test.txt"
DEFAULT_LEVELS: list[PacManLevel] = [PacManLevel()]
DEFAULT_LIVES: int = 3
DEFAULT_PACGUM: int = 42
DEFAULT_POINTS_PER_PACGUM: int = 10
DEFAULT_POINTS_PER_SUPER_PACGUM: int = 50
DEFAULT_POINTS_PER_GHOST: int = 200
DEFAULT_SEED: int = 42
DEFAULT_LEVEL_MAX_TIME: int = 90

POSITIVE_INT_FIELDS = {
    "lives": DEFAULT_LIVES,
    "pacgum": DEFAULT_PACGUM,
    "points_per_pacgum": DEFAULT_POINTS_PER_PACGUM,
    "points_per_super_pacgum": DEFAULT_POINTS_PER_SUPER_PACGUM,
    "points_per_ghost": DEFAULT_POINTS_PER_GHOST,
    "level_max_time": DEFAULT_LEVEL_MAX_TIME,
}


class PacManConfigModel(BaseModel):
    """
    :TODO
    """
    highscore_filename: str = DEFAULT_HIGHSCORE_FILENAME
    levels: list[PacManLevel] = DEFAULT_LEVELS
    lives: int = DEFAULT_LIVES
    pacgum: int = DEFAULT_PACGUM
    points_per_pacgum: int = DEFAULT_POINTS_PER_PACGUM
    points_per_super_pacgum: int = DEFAULT_POINTS_PER_SUPER_PACGUM
    points_per_ghost: int = DEFAULT_POINTS_PER_GHOST
    seed: int = DEFAULT_SEED
    level_max_time: int = DEFAULT_LEVEL_MAX_TIME

    @model_validator(mode="after")
    def fallback_to_defaults(self):
        def warning(value: str, field: str) -> None:
            print(
                f"[Warning] Invalid value \"{value}\" to field \"{field}\". "
                "Setting to default value."
            )

        for field, default in POSITIVE_INT_FIELDS.items():
            v = getattr(self, field)

            if not isinstance(v, int) or v <= 0:
                warning(v, field)
                setattr(self, field, default)

        if not isinstance(self.highscore_filename, str) \
                or not self.highscore_filename:
            warning(self.highscore_filename, "highscore_filename")
            self.highscore_filename = DEFAULT_HIGHSCORE_FILENAME

        if not isinstance(self.levels, list) or len(self.levels) == 0:
            warning(self.levels, "levels")
            self.levels = DEFAULT_LEVELS

        return self


class PacManConfig:
    """
    :TODO
    """

    def __init__(self) -> None:
        self.settings: PacManConfigModel = PacManConfigModel()

    def load_settings(self, path: str) -> PacManConfigModel:
        with open(path, "r") as file:
            content: str = re.sub(
                r"^\s*#.*$", "", file.read(), flags=re.MULTILINE
            )
            print(content)
            data: str = json.loads(content)
        self.settings = PacManConfigModel(**data)
        return self.settings
