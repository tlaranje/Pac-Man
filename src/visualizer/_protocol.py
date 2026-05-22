from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pygame import Surface


class VisualizerProtocol(Protocol):
    # --- Rendering constants ---
    scale: int
    margin: int

    # --- Computed window geometry ---
    width: int
    height: int
    # offset_x: float
    # offset_y: float
    # center_offset_x: int

    # --- pygame objects ---
    screen: "Surface"

    # --- Window ---
    def setup_main_menu_win(self) -> None: ...
