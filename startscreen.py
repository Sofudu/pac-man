import pygame
import os
import sys
from itertools import cycle


def load_image(name, colorkey=None):
    fullname = os.path.join('sprites', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    images = pygame.image.load(fullname)
    return images


def ladi(name):
    fullname = os.path.join('sprites', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    images = pygame.image.load(fullname)
    images.set_colorkey((0, 0, 0))
    return images


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = load_image("start.png")
    blink = load_image("blink.png")
    clyde = load_image("clyde.png")
    ink = load_image("ink.png")
    pink = load_image("pink.png")
    tap = load_image("tap_any.png")

    FLESH = pygame.USEREVENT + 1
    screen.blit(fon, (0, 0))
    n = 0
    while True:
        for EVENT in pygame.event.get():
            if EVENT.type == pygame.QUIT:
                terminate()
            elif EVENT.type == pygame.KEYDOWN:
                return
        if n > 10:
            screen.blit(blink, (68, 105))
        if n > 30:
            screen.blit(pink, (68, 153))
        if n > 60:
            screen.blit(ink, (68, 201))
        if n > 80:
            screen.blit(clyde, (68, 249))
        if n > 100:
            screen.blit(tap, (150, 320))
        n += 24 / fps
        clock.tick(fps)
        pygame.display.flip()


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = 16

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        r = self.cell_size
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, "white", (self.left + r * j, self.top + r * i, r, r), 1)

    def get_cell(self, mouse_pos):
        x0 = self.left
        y0 = self.top
        x1 = self.cell_size * self.width
        y1 = self.cell_size * self.height
        if mouse_pos[0] < x0 or mouse_pos[1] < y0 or mouse_pos[0] > x1 + x0 or mouse_pos[1] > y1 + y0:
            return None
        else:
            x0, y0 = mouse_pos[0] - x0, mouse_pos[1] - y0
            x0, y0 = x0 // self.cell_size, y0 // self.cell_size
            return x0, y0


class Pacman(pygame.sprite.Sprite):
    pac = load_image("big_pac.png")

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Pacman.pac
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 212
        self.rect.y = 412


class Walls(pygame.sprite.Sprite):
    wall = load_image("wall.png")

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Walls.wall
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.top = 48


pygame.init()
all_sprites = pygame.sprite.Group()
wall = Walls()
all_sprites.add(wall)

p = Pacman()
all_sprites.add(p)

pygame.display.set_caption("Pac-Man")
screen = pygame.display.set_mode((448, 576))
board = Board(28, 36)

clock = pygame.time.Clock()
running = True
fps = 60
start_screen()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(board.get_cell(event.pos))
    screen.fill("black")
    clock.tick(fps)
    all_sprites.draw(screen)
    pygame.display.flip()
pygame.quit()