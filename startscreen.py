import pygame
import os
import sys
from itertools import cycle
from entities import pacman, blinky, pinky, inky, clyde, screen, CELL_SIZE, enter_frightened_mode


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


def move():
    global pacman_deltax, pacman_deltay, blinky_deltax, blinky_deltay, pinky_deltax, pinky_deltay, inky_deltax, inky_deltay, clyde_deltax, clyde_deltay
    pacman_deltax += (pacman.get_direction() * 2).to_tuple()[0]
    pacman_deltay += (pacman.get_direction() * 2).to_tuple()[1]
    blinky_deltax += blinky.get_direction().to_tuple()[0]
    blinky_deltay += blinky.get_direction().to_tuple()[1]
    pinky_deltax += pinky.get_direction().to_tuple()[0]
    pinky_deltay += pinky.get_direction().to_tuple()[1]
    inky_deltax += inky.get_direction().to_tuple()[0]
    inky_deltay += inky.get_direction().to_tuple()[1]
    clyde_deltax += clyde.get_direction().to_tuple()[0]
    clyde_deltay += clyde.get_direction().to_tuple()[1]
    if blinky_deltax == blinky_deltay == 0:
        blinky.choice_direction()
    if pinky_deltax == pinky_deltay == 0:
        pinky.choice_direction()
    if inky_deltax == inky_deltay == 0:
        inky.choice_direction()
    if clyde_deltax == clyde_deltay == 0:
        clyde.choice_direction()

    if blinky_deltax == 16 or blinky_deltay == 16 or blinky_deltax == -16 or blinky_deltay == -16:
        blinky.make_step()
        blinky_deltax = blinky_deltay = 0
    if pinky_deltax == 16 or pinky_deltay == 16 or pinky_deltax == -16 or pinky_deltay == -16:
        pinky.make_step()
        pinky_deltax = pinky_deltay = 0
    if inky_deltax == 16 or inky_deltay == 16 or inky_deltax == -16 or inky_deltay == -16:
        inky.make_step()
        inky_deltax = inky_deltay = 0
    if clyde_deltax == 16 or clyde_deltay == 16 or clyde_deltax == -16 or clyde_deltay == -16:
        clyde.make_step()
        clyde_deltax = clyde_deltay = 0
    if pacman_deltax == 16 or pacman_deltax == -16:
        pacman.make_step()
        pacman_deltax = 0
    if pacman_deltay == 16 or pacman_deltay == -16:
        pacman.make_step()
        pacman_deltay = 0
    blinky.update_rect(blinky_deltax, blinky_deltay)
    pinky.update_rect(pinky_deltax, pinky_deltay)
    inky.update_rect(inky_deltax, inky_deltay)
    clyde.update_rect(clyde_deltax, clyde_deltay)
    pacman.update_rect(pacman_deltax, pacman_deltay)


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = CELL_SIZE

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        r = self.cell_size
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, pygame.color.Color(50, 50, 50), (self.left + r * j, self.top + r * i, r, r), 1)
        pygame.draw.rect(screen, 'red', (blinky.goal_point.to_tuple()[0] * CELL_SIZE, blinky.goal_point.to_tuple()[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
        pygame.draw.rect(screen, 'pink', (pinky.goal_point.to_tuple()[0] * CELL_SIZE, pinky.goal_point.to_tuple()[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
        pygame.draw.rect(screen, 'cyan', (inky.goal_point.to_tuple()[0] * CELL_SIZE, inky.goal_point.to_tuple()[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
        pygame.draw.rect(screen, 'orange', (clyde.goal_point.to_tuple()[0] * CELL_SIZE, clyde.goal_point.to_tuple()[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),2)

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

all_sprites.add(pacman, blinky, pinky, inky, clyde)

pygame.display.set_caption("Pac-Man")
board = Board(28, 36)

clock = pygame.time.Clock()
running = True
fps = 60
# start_screen()
pinky.change_mode('chase')
inky.change_mode('chase')
clyde.change_mode('chase')
pinky.pos = blinky.pos.copy()
inky.pos = blinky.pos.copy()
clyde.pos = blinky.pos.copy()
pinky.direction = blinky.direction.copy()
inky.direction = blinky.direction.copy()
clyde.direction = blinky.direction.copy()

pacman_deltax = pacman_deltay = 0
blinky_deltax = 10
blinky_deltay = 0
pinky_deltax = 7
pinky_deltay = 0
inky_deltax = -5
inky_deltay = 0
clyde_deltax = clyde_deltay = 0
blinky.update_rect(blinky_deltax, blinky_deltay)
pinky.update_rect(pinky_deltax, pinky_deltay)
inky.update_rect(inky_deltax, inky_deltay)
clyde.update_rect(clyde_deltax, clyde_deltay)
flag = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(board.get_cell(event.pos))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                pacman.change_direction('up')
            if event.key == pygame.K_s:
                pacman.change_direction('down')
            if event.key == pygame.K_a:
                pacman.change_direction('left')
            if event.key == pygame.K_d:
                pacman.change_direction('right')
            if event.key == pygame.K_SPACE:
                if flag:
                    blinky.change_mode('scatter')
                    pinky.change_mode('scatter')
                    inky.change_mode('scatter')
                    clyde.change_mode('scatter')
                    flag = False
                    print('changed to scatter')
                else:
                    blinky.change_mode('chase')
                    pinky.change_mode('chase')
                    inky.change_mode('chase')
                    clyde.change_mode('chase')
                    flag = True
                    print('changed to chase')
            if event.key == pygame.K_f:
                enter_frightened_mode()
    move()
    screen.fill("black")
    clock.tick(fps)
    all_sprites.draw(screen)
    board.render()
    pygame.display.flip()
pygame.quit()
