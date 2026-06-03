from ._constants import TEXT_COLOR
from src.utils import load_svg
import pygame

SVG_BUTTON = "assets/img/Button.svg"
SVG_BUTTON_CLICK = "assets/img/Button_click.svg"
SVG_BUTTON_SQ = "assets/img/Button_sq.svg"
SVG_BUTTON_SQ_CLICK = "assets/img/Button_sq_click.svg"


class Button:
    def __init__(
        self,
        screen: pygame.Surface,
        pos: tuple[int | None, int | None] = (None, None),
        size: tuple[int, int] = (160, 50),
        text: str = "Hello",
        text_size: int = 25,
        font: pygame.font.Font | None = None,
        action: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.screen = screen
        self.pos = pos
        self.size = size
        self.text = text
        self.font = font or pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", text_size
        )
        self.action_value = action
        self.disabled = disabled

        raster_rect = pygame.Rect(0, 0, *self.size)
        is_square = size[0] == size[1]
        if is_square:
            self._img = load_svg(SVG_BUTTON_SQ, raster_rect)
            self._img_click = load_svg(SVG_BUTTON_SQ_CLICK, raster_rect)
        else:
            self._img = load_svg(SVG_BUTTON, raster_rect)
            self._img_click = load_svg(SVG_BUTTON_CLICK, raster_rect)

        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])

        self._hovered = False
        self._pressed = False
        self.setup_button()

    def setup_button(self) -> None:
        x, y = self.pos

        active_screen = pygame.display.get_surface()
        if active_screen is None:
            win_x, win_y = (800, 600)
        else:
            win_x, win_y = active_screen.get_size()

        pos_x = (win_x // 2) - (self.size[0] // 2) if x is None else x
        pos_y = (win_y // 2) - (self.size[1] // 2) if y is None else y
        self.rect.topleft = (pos_x, pos_y)

    def update(self, mouse_pos: tuple[int, int]) -> None:
        if self.disabled:
            return

        self._hovered = self.rect.collidepoint(mouse_pos)
        self._pressed = self._hovered and pygame.mouse.get_pressed()[0]

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if self.disabled:
            return False

        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self) -> None:
        if self._pressed or self._hovered:
            img = self._img_click
            draw_rect = self.rect.move(0, 4)
        else:
            img = self._img
            draw_rect = self.rect

        self.screen.blit(img, draw_rect)

        if self._pressed:
            dark = img.copy()
            dark.fill((0, 0, 0, 60), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(dark, draw_rect)

        if self.text:
            text_surf = self.font.render(self.text, True, TEXT_COLOR)

            if self._pressed or self._hovered:
                text_rect = text_surf.get_rect(
                    center=(draw_rect.centerx, draw_rect.centery)
                )
            else:
                text_rect = text_surf.get_rect(
                    center=(draw_rect.centerx, draw_rect.centery - 3)
                )

            self.screen.blit(text_surf, text_rect)
