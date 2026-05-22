from .button import Button
import pygame
import sys
import os

NORTH = 0x01
EAST = 0x02
SOUTH = 0x04
WEST = 0x08

map = [
    "D39391391539553D5157915795153B",
    "BC6AEAEAC3C693C538556C15696BAA",
    "813C3C569693AC556C5393C57A96AA",
    "EAC7A9396D2AC53953BAAC553AC546",
    "96956AC6956C53AABA86AD53AC3953",
    "A96D52916D5396C6AAC3C53C43C47A",
    "869556AE953C69516ABC53C3BA9552",
    "A969792969693ABC56C5543AAC693A",
    "A83C3AC43C16C4455555396A8556AA",
    "AAC3C693AFC3F957FFFFAE9685396A",
    "AC7C53AAEF96FC51553FC56BA96A96",
    "C5553C2C3FC3F956B96F9516AAD6C3",
    "9553C3E92F96F83D2C3FABA96C553A",
    "C3BA9696EFC7FEC3C56FC2C6953BAA",
    "BC2C6D293FFFF952FFFFBC3D2BC2C6",
    "C3C393C6C393F83AF95543A96A96D3",
    "943AAC5556AAFAAAF8793AC692C552",
    "A96C6B913D2AFEAAFA96C4792C5796",
    "AE913AAAC56AF96EFEC5553AC553C3",
    "856AAAAC3B96FC53FFFF93AC39547A",
    "C57AAC69686D515297952C696C5396",
    "9556C556945556BAA947C53C3956C3",
    "C3B955556953D504687939296C5396",
    "968693957ABC53AB9696C6AA93BC6B",
    "A96D2AA956853AC6ABAD556C6A8552",
    'AC556C6C392D6C5546C39517968396',
    "C53939556EC39555393AA929696AC3",
    "952AC6D51552A953AAC6AAEC3ABABA",
    "AD6A9393C3BAAC7C46956C53AC6AAA",
    "C5546C6C56C6C5555545557C4556C6"
]


class Manager:
    def __init__(self) -> None:
        pygame.init()

        os.environ['SDL_VIDEO_CENTERED'] = '1'

        self.menu_size: tuple[int, int] = (250, 250)
        self.game_play_size: tuple[int, int] = (500, 500)
        self.win_size: tuple[int, int] = self.menu_size
        Button.win_size = self.win_size

        self.screen: pygame.Surface = pygame.display.set_mode(self.win_size)
        Button.screen = self.screen

        pygame.display.set_caption("Pac-Man")

        self.state: str = "MAIN_MENU"
        self.menu_buttons: list[Button] = [
            Button(
                size=(150, 60), pos=(None, 100), text="Play", action="PLAY"
            ),
            Button(
                size=(150, 60), pos=(None, 170), text="Exit", action="QUIT_APP"
            )
        ]

        self.title_font = pygame.font.Font(
            "assets/fonts/Rajdhani-Bold.ttf", 50
        )

        self.map_int: list

    def draw_main_menu(self) -> None:
        text_surf = self.title_font.render("Pac-Man", True, (215, 215, 215))
        text_rect = text_surf.get_rect(
            centerx=self.screen.get_rect().centerx, y=10
        )
        self.screen.blit(text_surf, text_rect)
        for btn in self.menu_buttons:
            btn.draw()

    def update_display_mode(self, width: int, height: int) -> None:
        self.win_size = (width, height)
        Button.win_size = self.win_size
        self.screen = pygame.display.set_mode(self.win_size)
        pygame.event.post(
            pygame.event.Event(pygame.ACTIVEEVENT, gain=1, state=1)
        )

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

    def handle_game_play_events(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                self.state = "MAIN_MENU"
                x, y = self.menu_size
                self.update_display_mode(x, y)
        self.draw_maze()

    def draw_maze(self) -> None:
        for y, row in enumerate(self.map_int):
            for x, cell in enumerate(row):
                if cell & NORTH:
                    print("NORTH")
                if cell & EAST:
                    print("EAST")
                if cell & SOUTH:
                    print("SOUTH")
                if cell & WEST:
                    print("WEST")

    def run(self) -> None:
        self.map_int = []
        for row in map:
            self.map_int.append(
                [int(row[i:i+2], 16) for i in range(0, len(row), 2)]
            )

        while True:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.fill((50, 50, 50))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_ESCAPE
                        and self.state == 'MAIN_MENU'
                    ):
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == "MAIN_MENU":
                    self.handle_menu_events(event)
                elif self.state == "GAME_PLAY":
                    self.handle_game_play_events(event)

            if self.state == "MAIN_MENU":
                for btn in self.menu_buttons:
                    btn.update(mouse_pos)
                self.draw_main_menu()

            pygame.display.flip()
