import pygame
import os
import sys
import random
import pprint

pygame.display.init()
screen = pygame.display.set_mode((448, 576))
CELL_SIZE = 16
MAP = '''11111111111111111111111111111111
10000000000001100000000000011111
10111101111101101111101111011111
10111101111101101111101111011111
10111101111101101111101111011111
10000000000000000000000000011111
10111101101111111101101111011111
10111101101111111101101111011111
10000001100001100001100000011111
11111101111101101111101111111111
11111101111101101111101111111111
11111101100222222001101111111111
11111101101111111101101111111111
11111101101000000101101111111111
00000000001000000100000000000000
11111101101000000101101111111111
11111101101111111101101111111111
11111101100000000001101111111111
11111101101111111101101111111111
11111101101111111101101111111111
10000000000001100000000000011111
10111101111101101111101111011111
10111101111101101111101111011111
10001100000222222000001100011111
11101101101111111101101101111111
11101101101111111101101101111111
10000001100001100001100000011111
10111111111101101111111111011111
10111111111101101111111111011111
10000000000000000000000000011111
11111111111111111111111111111111'''.split('\n')


# Поле 28 в ширину, в высоту 33 (+ 3 клетки сверху для скорбара, + 2 клетки снизу для уровня и кол-ва жизней)
# Векторы. Начало координат верхний левый угол экрана.
class Position:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)

    def __pow__(self, power):
        return self.x ** power + self.y ** power

    def __mul__(self, other):
        return Position(self.x * other, self.y * other)

    def __neg__(self):
        return Position(-self.x, -self.y)

    def to_tuple(self):
        return self.x, self.y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def copy(self):
        return Position(self.x, self.y)


# Основные векторы
DIRECTIONS = {'up': Position(0, -1), 'left': Position(-1, 0), 'down': Position(0, 1), 'right': Position(1, 0)}


# Функция загрузки изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('sprites', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cant load image:', name)
        raise SystemExit(message)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# Вычисления расстояния между концами векторов
def calculate_distance(point1, point2):
    return (point1 - point2) ** 2


class Point(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.image = load_image('point.png', colorkey=-1)
        self.pos = Position(x, y)
        self.eaten = 0

    def check(self):
        if self.eaten == 0:
            if pacman.get_pos() == self.pos:
                self.eaten = 1


class Energizer(Point):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        self.image = load_image('energizer.png', colorkey=-1)

    def check(self):
        if self.eaten == 0:
            if pacman.get_pos() == self.pos:
                self.eaten = 1
                enter_frightened_mode()


def enter_frightened_mode():
    blinky.change_mode('frightened')
    pinky.change_mode('frightened')
    inky.change_mode('frightened')
    clyde.change_mode('frightened')


def fun(x):
    return x[0], list(map(lambda y: y.to_tuple(), x[1]))


# Основной класс
class Entity(pygame.sprite.Sprite):
    # Скоро будет
    points = {}
    for i in range(28):
        for j in range(1, 30):
            if MAP[j][i] == '0' or MAP[j][i] == '2':
                points[(i, j + 3)] = []
                if (MAP[j - 1][i] == '0' or MAP[j - 1][i] == '2') and MAP[j][i] == '0':
                    points[(i, j + 3)].append(DIRECTIONS['up'])
                if MAP[j][i - 1] == '0' or MAP[j][i - 1] == '2':
                    points[(i, j + 3)].append(DIRECTIONS['left'])
                if MAP[j + 1][i] == '0' or MAP[j + 1][i] == '2':
                    points[(i, j + 3)].append(DIRECTIONS['down'])
                if MAP[j][i + 1] == '0' or MAP[j][i + 1] == '2':
                    points[(i, j + 3)].append(DIRECTIONS['right'])
    points[(-1, 17)] = [DIRECTIONS['left'], DIRECTIONS['right']]
    points[(-2, 17)] = [DIRECTIONS['left'], DIRECTIONS['right']]
    points[(28, 17)] = [DIRECTIONS['left'], DIRECTIONS['right']]
    points[(29, 17)] = [DIRECTIONS['left'], DIRECTIONS['right']]
    points[(-3, 17)] = [DIRECTIONS['left'], DIRECTIONS['right']]
    points[(30, 17)] = [DIRECTIONS['left'], DIRECTIONS['right']]
    pprint.pprint(tuple(map(fun, points.items())))
    # Режимы поведения
    modes = {'in_house': 0, 'chase': 1, 'scatter': 2, 'frightened': 3, 'eaten': 4}
    # Основная точка, к которой лятят призраки после поедания их героем
    eaten_point = Position(13, 14)
    # Изображения
    image_frightened = load_image('frightened.png', colorkey=-1)
    """
    image_eaten = {'up': load_image('eaten_up.png', colorkey=-1),
                   'down': load_image('eaten_down.png', colorkey=-1),
                   'right': load_image('eaten_right.png', colorkey=-1),
                   'left': load_image('eaten_left.png', colorkey=-1)}
    """

    def __init__(self, *groups):
        super().__init__(*groups)
        self.direction = DIRECTIONS['left']
        self.mode = Entity.modes['chase']

    def choice_direction(self):
        self.make_goal_point()
        possible = Entity.points.get(self.pos.to_tuple(), list(DIRECTIONS.values())).copy()
        if possible.count(-self.direction):
            possible.remove(-self.direction)
        if self.mode != Entity.modes['frightened'] and self.mode != Entity.modes['in_house']:
            min_direction = possible[0]
            min_distance = calculate_distance(self.pos + min_direction, self.goal_point)
            for direction in possible:
                distance = calculate_distance(self.pos + direction, self.goal_point)
                if distance < min_distance:
                    min_distance = distance
                    min_direction = direction
            return min_direction
        elif self.mode == Entity.modes['in_house']:
            return -self.direction
        else:
            return random.choice(possible)

    def make_step(self):
        self.pos = self.pos + self.direction
        self.direction = self.choice_direction()
        self.update_image()
        if self.pos.to_tuple()[0] <= -2:
            self.pos = self.pos + Position(32, 0)
        elif self.pos.to_tuple()[0] >= 30:
            self.pos = self.pos + Position(-32, 0)

    def make_goal_point(self):
        pass

    def get_pos(self):
        return self.pos

    def get_direction(self):
        return self.direction

    def change_mode(self, mode):
        self.mode = Entity.modes[mode]
        self.direction = -self.direction

    def update_image(self):
        pass

    def update_rect(self, deltax, deltay):
        self.rect = self.image.get_rect()
        self.rect.x = CELL_SIZE * self.pos.to_tuple()[0] - CELL_SIZE / 4 + deltax
        self.rect.y = CELL_SIZE * self.pos.to_tuple()[1] - CELL_SIZE / 4 + deltay


class Pacman(Entity):
    image = {'up': load_image(f'pacman_up.png', colorkey=-1),
             'left': load_image(f'pacman_left.png', colorkey=-1),
             'down': load_image(f'pacman_down.png', colorkey=-1),
             'right': load_image(f'pacman_right.png', colorkey=-1)}

    def __init__(self, *groups):
        self.pos = Position(13, 26)
        super().__init__(*groups)
        self.image = load_image('pacman_left.png', colorkey=-1)
        self.update_rect(0, 0)

    def change_direction(self, dir):
        self.direction = DIRECTIONS[dir]
        self.update_image()

    def choice_direction(self):
        return self.direction

    def update_image(self):
        for dir, vec in DIRECTIONS.items():
            if self.direction == vec:
                break
        self.image = Pacman.image[dir]


class Blinky(Entity):
    image = {'up': load_image('blinky_up.png', colorkey=-1),
             'down': load_image('blinky_down.png', colorkey=-1),
             'right': load_image('blinky_right.png', colorkey=-1),
             'left': load_image('blinky_left.png', colorkey=-1)}
    scatter_point = Position(25, 0)

    def __init__(self, *groups):
        self.pos = Position(13, 14)
        super().__init__(*groups)
        self.make_goal_point()
        self.update_image()
        self.update_rect(0, 0)

    def change_mode(self, mode):
        super().change_mode(mode)
        self.update_image()

    def make_goal_point(self):
        if self.mode == Entity.modes['chase']:
            self.goal_point = pacman.get_pos()
        if self.mode == Entity.modes['scatter']:
            self.goal_point = Blinky.scatter_point
        if self.mode == Entity.modes['eaten']:
            self.goal_point = Entity.eaten_point

    def update_image(self):
        if self.mode == Entity.modes['chase'] or self.mode == Entity.modes['scatter']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Blinky.image[direction]
        elif self.mode == Entity.modes['frightened']:
            self.image = Entity.image_frightened
        elif self.mode == Entity.modes['eaten']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_eaten[direction]


class Pinky(Entity):
    image = {'up': load_image('pinky_up.png', colorkey=-1),
             'down': load_image('pinky_down.png', colorkey=-1),
             'right': load_image('pinky_right.png', colorkey=-1),
             'left': load_image('pinky_left.png', colorkey=-1)}
    scatter_point = Position(2, 0)

    def __init__(self, *groups):
        self.pos = Position(13, 17)
        super().__init__(*groups)
        self.make_goal_point()
        self.mode = Entity.modes['in_house']
        self.direction = DIRECTIONS['down']
        self.update_image()
        self.update_rect(0, 0)

    def change_mode(self, mode):
        super().change_mode(mode)
        self.update_image()

    def make_goal_point(self):
        if self.mode == Entity.modes['chase']:
            self.goal_point = pacman.get_pos() + pacman.get_direction() * 4
        if self.mode == Entity.modes['scatter']:
            self.goal_point = Pinky.scatter_point
        if self.mode == Entity.modes['eaten']:
            self.goal_point = Entity.eaten_point

    def update_image(self):
        if self.mode == Entity.modes['chase'] or self.mode == Entity.modes['scatter'] or self.mode == Entity.modes[
            'in_house']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Pinky.image[direction]
        elif self.mode == Entity.modes['frightened']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_frightened
        elif self.mode == Entity.modes['eaten']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_eaten[direction]


class Inky(Entity):
    image = {'up': load_image('inky_up.png', colorkey=-1),
             'down': load_image('inky_down.png', colorkey=-1),
             'right': load_image('inky_right.png', colorkey=-1),
             'left': load_image('inky_left.png', colorkey=-1)}
    scatter_point = Position(27, 35)

    def __init__(self, *groups):
        self.pos = Position(15, 17)
        super().__init__(*groups)
        self.make_goal_point()
        self.mode = Entity.modes['in_house']
        self.direction = DIRECTIONS['up']
        self.update_image()
        self.update_rect(0, 0)

    def change_mode(self, mode):
        super().change_mode(mode)
        self.update_image()

    def make_goal_point(self):
        if self.mode == Entity.modes['chase']:
            self.goal_point = blinky.get_pos() + (pacman.get_pos() + pacman.get_direction() * 2 - blinky.get_pos()) * 2
        if self.mode == Entity.modes['scatter']:
            self.goal_point = Inky.scatter_point
        if self.mode == Entity.modes['eaten']:
            self.goal_point = Entity.eaten_point

    def update_image(self):
        if self.mode == Entity.modes['chase'] or self.mode == Entity.modes['scatter'] or self.mode == Entity.modes[
            'in_house']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Inky.image[direction]
        elif self.mode == Entity.modes['frightened']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_frightened
        elif self.mode == Entity.modes['eaten']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_eaten[direction]


class Clyde(Entity):
    image = {'up': load_image('clyde_up.png', colorkey=-1),
             'down': load_image('clyde_down.png', colorkey=-1),
             'right': load_image('clyde_right.png', colorkey=-1),
             'left': load_image('clyde_left.png', colorkey=-1)}
    scatter_point = Position(0, 35)

    def __init__(self, *groups):
        self.pos = Position(11, 17)
        super().__init__(*groups)
        self.make_goal_point()
        self.mode = Entity.modes['in_house']
        self.direction = DIRECTIONS['up']
        self.update_image()
        self.update_rect(0, 0)

    def change_mode(self, mode):
        super().change_mode(mode)
        self.update_image()

    def make_goal_point(self):
        if self.mode == Entity.modes['chase']:
            if (pacman.get_pos() - self.get_pos()) ** 2 > 64:
                self.goal_point = pacman.get_pos()
            else:
                self.goal_point = Clyde.scatter_point
        if self.mode == Entity.modes['scatter']:
            self.goal_point = Clyde.scatter_point
        if self.mode == Entity.modes['eaten']:
            self.goal_point = Entity.eaten_point

    def update_image(self):
        if self.mode == Entity.modes['chase'] or self.mode == Entity.modes['scatter'] or self.mode == Entity.modes[
            'in_house']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Clyde.image[direction]
        elif self.mode == Entity.modes['frightened']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_frightened
        elif self.mode == Entity.modes['eaten']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_eaten[direction]


pacman = Pacman()
blinky = Blinky()
pinky = Pinky()
inky = Inky()
clyde = Clyde()