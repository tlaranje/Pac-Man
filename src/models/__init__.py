from typing import Any
from dataclasses import dataclass
from mazegenerator import MazeGenerator

PacManMap = MazeGenerator
PacGumsMap = list[list[tuple[bool, str]]]

DEFAULT_WIDTH: int = 20
DEFAULT_HEIGHT: int = 20
DEFAULT_START_X: int = 0
DEFAULT_START_Y: int = 0


@dataclass
class PacManLevel:
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    start_x: int = DEFAULT_START_X
    start_y: int = DEFAULT_START_Y


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


class PacManConfigModel:
    """
    :TODO
    """

    def __init__(self, data: dict) -> None:
        self.highscore_filename = self._parse_str(
            data, "highscore_filename", DEFAULT_HIGHSCORE_FILENAME
        )
        self.lives = self._parse_positive_int(
            data, "lives", DEFAULT_LIVES
        )
        self.pacgum = self._parse_positive_int(
            data, "pacgum", DEFAULT_PACGUM
        )
        self.points_per_pacgum = self._parse_positive_int(
            data, "points_per_pacgum", DEFAULT_POINTS_PER_PACGUM
        )
        self.points_per_super_pacgum = self._parse_positive_int(
            data, "points_per_super_pacgum", DEFAULT_POINTS_PER_SUPER_PACGUM
        )
        self.points_per_ghost = self._parse_positive_int(
            data, "points_per_ghost", DEFAULT_POINTS_PER_GHOST
        )
        self.seed = self._parse_int(
            data, "seed", DEFAULT_SEED
        )
        self.level_max_time = self._parse_positive_int(
            data, "level_max_time", DEFAULT_LEVEL_MAX_TIME
        )
        self.levels = self._parse_levels(
            data
        )

    @staticmethod
    def _warning(field: str, value: Any, default: Any) -> None:
        print(
            f"[Warning] Invalid value \"{value}\" for field \"{field}\". "
            f"Setting to default: \"{default}\"."
        )

    def _parse_positive_int(self, data: dict, field: str, default: int) -> int:
        v = data.get(field, default)
        if not isinstance(v, int) or v <= 0:
            self._warning(field, v, default)
            return default
        return v

    def _parse_int(self, data: dict, field: str, default: int) -> int:
        v = data.get(field, default)
        if not isinstance(v, int):
            self._warning(field, v, default)
            return default
        return v

    def _parse_str(self, data: dict, field: str, default: str) -> str:
        v = data.get(field, default)
        if not isinstance(v, str) or not v:
            self._warning(field, v, default)
            return default
        return v

    def _parse_levels(self, data: dict) -> list:
        v = data.get("levels", None)
        if not isinstance(v, list) or len(v) == 0:
            if v is not None:
                self._warning("levels", v, DEFAULT_LEVELS)
            return DEFAULT_LEVELS
        levels = []
        for i, level in enumerate(v):
            if not isinstance(level, dict):
                self._warning(f"levels[{i}]", level, DEFAULT_LEVELS[0])
                levels.append(DEFAULT_LEVELS[0])
            else:
                levels.append(self._parse_level(level))
        return levels

    def _parse_bounded_int(self, data: dict, field: str,
                           default: int, low: int, high: int) -> int:
        v = data.get(field, default)
        if not isinstance(v, int) or not (low <= v <= high):
            self._warning(field, v, default)
            return default
        return v

    def _parse_level(self, data: dict) -> PacManLevel:
        level = PacManLevel()
        level.width = self._parse_positive_int(
            data, "width", DEFAULT_WIDTH
        )
        level.height = self._parse_positive_int(
            data, "height", DEFAULT_HEIGHT
        )
        level.start_x = self._parse_bounded_int(
            data, "start_x", DEFAULT_START_X, 0, level.width - 1
        )
        level.start_y = self._parse_bounded_int(
            data, "start_y", DEFAULT_START_Y, 0, level.height - 1
        )
        return level
