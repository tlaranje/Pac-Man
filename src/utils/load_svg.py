from typing import Any
import cairosvg
import pygame
import io


def load_svg(path: str, rect: pygame.Rect) -> pygame.Surface:
    png: Any = cairosvg.svg2png(url=path)
    surf = pygame.image.load(io.BytesIO(png))
    return pygame.transform.scale(surf, (rect.width, rect.height))
