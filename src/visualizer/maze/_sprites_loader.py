from typing import Any
import pygame


class SpriteLoader:
    """Animation sprite loader from sprite sheets.

    Loads and parses sprite sheets to extract animation frames for
    players, ghosts, and fruit objects.
    """

    def __init__(self) -> None:
        self.spritesheet_path: str = "assets/img/pacman.png"

    def load_frames(
        self, is_fruit: bool = False, num_frames: int = 1,
        pos: int = 0, start: int = 0, dir_key: str = "0"
    ) -> Any:
        """
        Load animation frames from image files.

        Args:
            frame_names: List of frame names to load.
            size: Frame size tuple.

        Returns:
            List of loaded animation frames.
        """
        try:
            spritesheet = pygame.image.load(
                self.spritesheet_path
            ).convert_alpha()
        except pygame.error as e:
            print(f"Error on load the spritesheet: {e}")
            raise

        height = 16
        widths = [16] * num_frames
        max_w = max(widths)
        base_column = 16 * pos
        background_color = spritesheet.get_at((0, base_column))

        direcoes = dir_key if is_fruit else ["D", "S", "A", "W"]
        frames_dict: Any = {}
        current_x = start * 16

        for dir_key in direcoes:
            frames_dict[dir_key] = []
            for w in widths:
                rect = pygame.Rect(current_x, base_column, w, height)
                frame = spritesheet.subsurface(rect)

                standard_surface = pygame.Surface(
                    (max_w, height), pygame.SRCALPHA
                )
                standard_surface.set_colorkey(background_color)
                standard_surface.blit(frame, (0, 0))

                frames_dict[dir_key].append(standard_surface)
                current_x += w

        return frames_dict
