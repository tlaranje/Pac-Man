from pygame import Surface, Rect, Color, draw, transform
from pygame.locals import SRCALPHA
from typing import Any


class RoundRect:
    def draw(
        self, surface: Surface, rect: Rect, color: Any = (50, 50, 50),
        radius: Any = 0.4, b_size: int = 0, b_color: Any = (255, 255, 255)
    ) -> None:
        if b_size > 0:
            border_size = b_size * 2
            f_width = rect.width + border_size
            f_height = rect.height + border_size
            f_x = rect.x - 2
            f_y = rect.y - 2
            f_rect = Rect(f_x, f_y, f_width, f_height)
            self.draw_rect(surface, f_rect, b_color, radius)
        self.draw_rect(surface, rect, color, radius)

    def draw_rect(
        self, surface: Surface, rect: Rect, color: Any = (50, 50, 50),
        radius: Any = 0.4,
    ) -> Rect:
        # Normalise inputs
        rect = Rect(rect)
        color = Color(*color)

        # Remember the original position, then work in local (0, 0) space.
        pos = rect.topleft
        rect.topleft = 0, 0

        # Create a transparent working surface matching the rectangle's size.
        rectangle = Surface(rect.size, SRCALPHA)

        # --- Build the corner circle ---
        circle_size = min(rect.size) * 3
        circle = Surface([circle_size] * 2, SRCALPHA)
        draw.ellipse(circle, color, circle.get_rect(), 0)
        circle = transform.smoothscale(
            circle, [int(min(rect.size) * radius)] * 2
        )

        # --- Stamp the corner circle into all four corners ---
        # Top-left corner
        radius_rect = rectangle.blit(circle, (0, 0))

        # Bottom-right corner
        radius_rect.bottomright = rect.bottomright
        rectangle.blit(circle, radius_rect)

        # Top-right corner
        radius_rect.topright = rect.topright
        rectangle.blit(circle, radius_rect)

        # Bottom-left corner
        radius_rect.bottomleft = rect.bottomleft
        rectangle.blit(circle, radius_rect)

        # --- Fill the interior area ---
        rectangle.fill(color, rect.inflate(-radius_rect.w, 0))

        # Vertical bar: full height, minus the rounded cap width on each side.
        rectangle.fill(color, rect.inflate(0, -radius_rect.h))

        # Blit the finished rounded rectangle onto the target surface.
        return surface.blit(rectangle, pos)
