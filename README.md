*This project has been created as part of the 42 curriculum by joesanto, tlaranje.*

# Pac-Man Ghosts! More ghosts!

## Description

Pac-Man Ghosts! More ghosts! is a Python implementation of a Pac-Man style game built for the 42 curriculum. The project combines procedural maze generation, ghost AI, collectible pacgums, super pacgums, and a persistent highscore leaderboard.

The goal is to clear each maze by collecting pacgums while avoiding ghosts, using configurable levels and a menu-driven Pygame interface.

## Instructions

### Requirements

- Python 3.11 or newer
- `pip` package manager
- Local `mazegenerator` wheel included in the repository

### Install dependencies

From the repository root:

```bash
python -m pip install -r requirements.txt
```

### Run the game

The game reads a configuration file in JSON format. A default file named `config.json` is included.

```bash
python pac-man.py config.json
```

### Controls

- `W` – Move up
- `A` – Move left
- `S` – Move down
- `D` – Move right
- `ESC` – Quit from menus or close the game window

## Configuration

The game uses a JSON configuration file to define level settings and runtime options.

### Example `config.json`

```json
{
  "levels": [
    {"width": 10, "height": 10},
    {"width": 10, "height": 10},
    {"width": 10, "height": 10}
  ],
  "pacgum": 0,
  "level_max_time": 90
}
```

### Supported configuration fields

- `highscore_filename` (string): output file for the leaderboard. Default: `scores.json`
- `lives` (positive integer): starting number of lives. Default: `3`
- `pacgum` (unsigned integer): number of normal pacgums generated. Default: `42`
- `points_per_pacgum` (positive integer): score for normal pacgum. Default: `10`
- `points_per_super_pacgum` (positive integer): score for super pacgum. Default: `50`
- `points_per_ghost` (positive integer): score for eating a ghost. Default: `200`
- `seed` (integer): seed for maze generation. Default: `42`
- `level_max_time` (positive integer): time limit per level in seconds. Default: `90`
- `levels` (list of level objects): each level object may include:
  - `width` (10–33)
  - `height` (10–33)
  - `start_x` (0..width-1)
  - `start_y` (0..height-1)

If any field is missing or invalid, the game falls back to the default value and prints a warning.

## Highscore

Highscores are stored in a JSON leaderboard file. By default, the file is `scores.json`.

When the game ends and a valid username is entered, the current score is appended to the leaderboard and sorted in descending order. The leaderboard keeps only the top 10 entries.

This approach keeps scoring persistent across sessions and simple to inspect or edit manually.

## Maze Generation

The project uses the `mazegenerator` (A-Maze-ing) package to generate each maze.

For each configured level, the game creates a `MazeGenerator` instance with:

- maze size from the config
- a start position entry cell
- `perfect=False` to allow more complex maze structure
- a seeded random generator for reproducible levels

After maze generation, the game places ghosts in the four maze corners and selects walkable cells for normal and super pacgums.

## Implementation

The implementation separates configuration, gameplay, and visualization.

- `pac-man.py` starts the game and initializes the visual manager.
- `src/visualizer/_visualizer.py` loads CLI arguments and configuration, then initializes all visual and game objects.
- `src/gameplay/Gameplay.py` contains the core entity classes for the player, ghosts, and game progression.
- `src/parser/Parser.py` builds mazes, pacgum placement, ghost spawn points, and helper functions for map layout.
- `src/models/__init__.py` defines config defaults and validation logic.
- `src/visualizer` contains UI, rendering, maze display, menus, and game over handling.
- `src/utils` contains supporting utilities for shape rendering and SVG loading.

## General Software Architecture

The main architecture is organized into these modules:

- `pac-man.py`: entrypoint and game bootstrapper
- `src/visualizer`: presentation layer, menus, window, and rendering
- `src/gameplay`: game state, entity behavior, and level flow
- `src/parser`: configuration parsing and maze/ghost generation
- `src/models`: configuration schema, defaults and validation rules
- `src/utils`: utility helpers used by the visualizer

Classes and relationships:

- `Manager` runs the main game loop and delegates update/draw actions
- `Visualizer` wires together `PacManGameplay`, `Window`, `Maze`, `MazeRenderer`, `Menu`, and `GameOver`
- `PacManGameplay` manages levels, score, lives, and win/lose transitions
- `PacManPlayer` and `PacManGhost` extend `PacManEntity` for movement and interaction
- `PacManConfig` and `PacManConfigModel` parse config data and build runtime map/ghost state

## Project Management

This project was managed with a lightweight task summary and planning notes in the dedicated project management directory:

- [project-management/README.md](project-management/README.md)

## Resources

- Pygame documentation: https://www.pygame.org/docs/
- Python 3 documentation: https://docs.python.org/3/
- Maze generation concepts: https://en.wikipedia.org/wiki/Maze_generation_algorithm
- A-Maze-ing package: provided via the local `mazegenerator-2.0.2-py3-none-any.whl`

### AI usage

AI was used to generate the README structure, summarize architecture and configuration, and help write consistent documentation for the project. Core game logic and implementation decisions were based on the existing repository code.
