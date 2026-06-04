from typing import Any
import cairosvg
import pygame
import io
import re


def load_svg(path: str, rect: pygame.Rect) -> pygame.Surface:
    with open(path, "rb") as f:
        svg_data = f.read().decode("utf-8")

    svg_data = re.sub(
        r'width="[^"]*"', f'width="{rect.width}"', svg_data, count=1
    )
    svg_data = re.sub(
        r'height="[^"]*"', f'height="{rect.height}"', svg_data, count=1
    )
    svg_data = re.sub(
        r'preserveAspectRatio="[^"]*"', 'preserveAspectRatio="none"', svg_data
    )
    if "preserveAspectRatio" not in svg_data:
        svg_data = svg_data.replace(
            "<svg ", '<svg preserveAspectRatio="none" ', 1
        )

    png: Any = cairosvg.svg2png(
        bytestring=svg_data.encode("utf-8"),
        output_width=rect.width,
        output_height=rect.height,
    )
    surf = pygame.image.load(io.BytesIO(png))
    return surf
