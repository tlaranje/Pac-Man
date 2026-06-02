import pygame

# Menu constants
TILE_COLOR = pygame.Color("white")
TEXT_COLOR = pygame.Color("light grey")

# Screen constants
pygame.init()

info = pygame.display.Info()
x = info.current_w
y = info.current_h

SCREEN_SIZE = (x, y)
SCREEN_MIDPOINT = (x / 2, y / 2)

# Maze constants
TILE_SIZE = 27
MARGIN = 32
MAZE_OFFSET = 32

BACKGROUND_COLOR = pygame.Color("black")
BORDER_COLOR = pygame.Color("blue")
INNER_COLOR = pygame.Color("black")

BORDER_SIZE = 9
INNER_THICKNESS = 3

GHOST_DELAY_MS = 500
MAX_PLAYER_DELAY = 1000
ANIMATION_SPEED = 15
