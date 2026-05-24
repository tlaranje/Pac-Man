from ._protocol import VisualizerProtocol as VProtocol
from ._button import Button
from pygame import Font


class Menu:
    def __init__(self: VProtocol) -> None:
        self.menu_buttons: list[Button] = [
            Button(
                size=(150, 60), pos=(None, 100), text="Play", action="PLAY"
            ),
            Button(
                size=(150, 60), pos=(None, 170), text="Exit", action="QUIT_APP"
            )
        ]

        self.title_font = Font(
            "assets/fonts/Rajdhani-Bold.ttf", 50
        )

    def draw_main_menu(self) -> None:
        text_surf = self.title_font.render("Pac-Man", True, (215, 215, 215))
        text_rect = text_surf.get_rect(
            centerx=self.screen.get_rect().centerx, y=10
        )
        self.screen.blit(text_surf, text_rect)
        for btn in self.menu_buttons:
            btn.draw()

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        for btn in self.menu_buttons:
            if btn.is_clicked(event):
                if btn.action_value == "PLAY":
                    self.state = 'GAME_PLAY'
                    x, y = self.game_play_size
                    self.update_display_mode(x, y)
                    pygame.event.clear()
                    return
                elif btn.action_value == "QUIT_APP":
                    pygame.quit()
                    sys.exit()
