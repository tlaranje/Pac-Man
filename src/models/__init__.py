import random
from typing import Any
from dataclasses import dataclass
from mazegenerator import MazeGenerator

PacManMap = MazeGenerator
PacGumsMap = list[list[tuple[bool, str]]]

DEFAULT_WIDTH: int = 20
DEFAULT_HEIGHT: int = 20


@dataclass
class PacManLevel:
    """Level configuration with maze dimensions and start position.

    Stores all parameters needed to generate a single game level,
    including maze size and player start coordinates.
    """
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT


DEFAULT_HIGHSCORE_FILENAME: str = "scores.json"
DEFAULT_LEVELS: list[PacManLevel] = [
    PacManLevel() for _ in range(10)
]
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

MAX_VALUE: int = 1000


class PacManConfigModel:
    """Validated configuration model with parsing and default fallback.

    Parses and validates individual configuration fields from JSON data,
    applying default values for missing or invalid entries.
    """

    def __init__(self, data: dict) -> None:
        self.highscore_filename = self._parse_str(
            data, "highscore_filename", DEFAULT_HIGHSCORE_FILENAME
        )
        self.lives = self._parse_bounded_int(
            data, "lives", DEFAULT_LIVES, 1, MAX_VALUE
        )
        self.pacgum = self._parse_bounded_int(
            data, "pacgum", DEFAULT_PACGUM, 0, MAX_VALUE
        )
        self.points_per_pacgum = self._parse_bounded_int(
            data, "points_per_pacgum", DEFAULT_POINTS_PER_PACGUM, 1, MAX_VALUE
        )
        self.points_per_super_pacgum = self._parse_bounded_int(
            data, "points_per_super_pacgum", DEFAULT_POINTS_PER_SUPER_PACGUM,
            1, MAX_VALUE
        )
        self.points_per_ghost = self._parse_bounded_int(
            data, "points_per_ghost", DEFAULT_POINTS_PER_GHOST, 1, MAX_VALUE
        )
        self.seed = self._parse_int(
            data, "seed", DEFAULT_SEED
        )
        self.level_max_time = self._parse_bounded_int(
            data, "level_max_time", DEFAULT_LEVEL_MAX_TIME, 1, MAX_VALUE
        )
        self.level_max_time_ms = self.level_max_time * 1000
        self.levels = self._parse_levels(
            data
        )
        self.seeds = [self.seed] + [
            random.randint(0, 2**32 - 1)
            for _ in range(len(self.levels) - 1)
        ]

    @staticmethod
    def _warning(field: str, value: Any, default: Any) -> None:
        """
        Print a configuration parsing warning message.

        Args:
            field: Field name that failed validation.
            value: Invalid value provided.
            default: Default value being used.
        """
        print(
            f"[Warning] Invalid value \"{value}\" for field \"{field}\". "
            f"Setting to default: \"{default}\"."
        )

    def _parse_unsigned_int(self, data: dict, field: str, default: int) -> int:
        """
        Parse and validate non-negative integer from config.

        Args:
            data: Configuration dictionary.
            field: Field name to parse.
            default: Default value if parsing fails.

        Returns:
            Validated non-negative integer.
        """
        v = data.get(field, None)
        if not isinstance(v, int) or v < 0:
            self._warning(field, v, default)
            return default
        return v

    def _parse_positive_int(self, data: dict, field: str, default: int) -> int:
        """
        Parse and validate positive integer from config.

        Args:
            data: Configuration dictionary.
            field: Field name to parse.
            default: Default value if parsing fails.

        Returns:
            Validated positive integer.
        """
        v = data.get(field, None)
        if not isinstance(v, int) or v <= 0:
            self._warning(field, v, default)
            return default
        return v

    def _parse_int(self, data: dict, field: str, default: int) -> int:
        """
        Parse and validate integer from config.

        Args:
            data: Configuration dictionary.
            field: Field name to parse.
            default: Default value if parsing fails.

        Returns:
            Validated integer.
        """
        v = data.get(field, None)
        if not isinstance(v, int):
            self._warning(field, v, default)
            return default
        return v

    def _parse_str(self, data: dict, field: str, default: str) -> str:
        """
        Parse and validate string from config.

        Args:
            data: Configuration dictionary.
            field: Field name to parse.
            default: Default value if parsing fails.

        Returns:
            Validated non-empty string.
        """
        v = data.get(field, None)
        if not isinstance(v, str) or not v:
            self._warning(field, v, default)
            return default
        return v

    def _parse_levels(self, data: dict) -> list:
        """
        Parse and validate level list from config.

        Args:
            data: Configuration dictionary.

        Returns:
            List of validated level objects.
        """
        v = data.get("levels", None)
        if not isinstance(v, list) or len(v) < 10:
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
        """
        Parse and validate integer within bounds.

        Args:
            data: Configuration dictionary.
            field: Field name to parse.
            default: Default value if parsing fails.
            low: Minimum valid value.
            high: Maximum valid value.

        Returns:
            Validated integer within bounds.
        """
        v = data.get(field, None)
        if not isinstance(v, int) or not (low <= v <= high):
            self._warning(field, v, default)
            return default
        return v

    def _parse_level(self, data: dict) -> PacManLevel:
        """
        Parse a single level configuration object.

        Args:
            data: Level configuration dictionary.

        Returns:
            Parsed and validated level object.
        """
        level = PacManLevel()
        level.width = self._parse_bounded_int(
            data, "width", DEFAULT_WIDTH, 10, 33
        )
        level.height = self._parse_bounded_int(
            data, "height", DEFAULT_HEIGHT, 10, 33
        )
        return level
