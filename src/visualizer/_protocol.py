from typing import TYPE_CHECKING, Any
from typing import Protocol
import pygame

if TYPE_CHECKING:
    from ._button import Button
    from ._maze import Maze


class VisualizerProtocol(Protocol):
    maze_size: tuple[int, int]
    title_font: Any
    gameplay: Any
    screen: pygame.Surface
    maze: "Maze"
    menu_size: tuple[int, int]
    game_play_size: tuple[int, int]
    state: str
    menu_buttons: list["Button"]

    # _window.py
    def stetup_window(self) -> None: ...
    def update_display_mode(self, width: int, height: int) -> None: ...

    # _menu.py
    def handle_menu_events(self, event: pygame.event.Event) -> None: ...
    def draw_main_menu(self) -> None: ...

    # _maze.py
    def handle_game_play_events(self, event: pygame.event.Event) -> None: ...
    def draw_maze(self) -> None: ...
