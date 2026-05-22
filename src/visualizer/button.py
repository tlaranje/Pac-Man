import cairosvg
import pygame
import io

SVG_PLAY = "assets/img/Button.svg"
SVG_PLAY_CLICK = "assets/img/Button_click.svg"


def load_svg(path: str, rect: pygame.Rect) -> pygame.Surface:
    png = cairosvg.svg2png(url=path)
    surf = pygame.image.load(io.BytesIO(png)).convert_alpha()
    return pygame.transform.scale(surf, (rect.width, rect.height))


class Button:
    screen: pygame.Surface
    win_size: tuple[int, int]

    def __init__(
        self,
        pos: tuple[int | None, int | None] = (None, None),
        size: tuple[int, int] = (150, 50),
        text: str = "Hello",
        font: pygame.Font | None = None,
        action: str | None = None,
    ) -> None:
        self.pos: tuple[int | None, int | None] = pos
        self.size: tuple[int, int] = size
        self.text: str = text
        self.font = font or pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 30
        )
        self.action_value: str | None = action

        self.rect: pygame.Rect = pygame.Rect(0, 0, size[0], size[1])
        self._img = load_svg(SVG_PLAY, self.rect)
        self._img_click = load_svg(SVG_PLAY_CLICK, self.rect)

        self._hovered = False
        self._pressed = False
        self.setup_button()

    def setup_button(self) -> None:
        x, y = self.pos
        win_x, win_y = self.win_size

        pos_x: int = (win_x // 2) - (self.size[0] // 2) if x is None else x
        pos_y: int = (win_y // 2) - (self.size[1] // 2) if y is None else y
        self.rect.topleft = (pos_x, pos_y)

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self._hovered = self.rect.collidepoint(mouse_pos)
        self._pressed = self._hovered and pygame.mouse.get_pressed()[0]

    def is_clicked(self, event: pygame.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self) -> None:
        if self._pressed:
            img = self._img_click
            draw_rect = self.rect.move(0, 4)
        else:
            img = self._img
            draw_rect = self.rect

        self.screen.blit(img, draw_rect)

        if self._hovered and not self._pressed:
            dark = img.copy()
            dark.fill((0, 0, 0, 60), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(dark, draw_rect)

        if self.text:
            text_surf = self.font.render(self.text, True, (215, 215, 215))
            if self._pressed:
                text_rect = text_surf.get_rect(
                    center=(draw_rect.centerx, draw_rect.centery)
                )
            else:
                text_rect = text_surf.get_rect(
                    center=(draw_rect.centerx, draw_rect.centery - 3)
                )

            self.screen.blit(text_surf, text_rect)
