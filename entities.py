import pygame
import os
import sys
import random


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
        return Position(-self.x, self.y)

    def to_tuple(self):
        return self.x, self.y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)


# Основные векторы
DIRECTIONS = {'up': Position(0, -1), 'left': Position(-1, 0), 'down': Position(0, 1), 'right': Position(1, 0)}


# Функция загрузки изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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


# Основной класс
class Entity(pygame.sprite.Sprite):
    # Скоро будет
    points = {(5, 7): list(DIRECTIONS.values())}
    unique_points = dict()
    # Режимы поведения
    modes = {'in_house': 0, 'chase': 1, 'scatter': 2, 'frightened': 3, 'eaten': 4}
    # Основная точка, к которой лятят призраки после поедания их героем
    eaten_point = Position(13, 14)
    # Изображения
    image_frightened = {'up': load_image('frightened_up.png', colorkey=-1),
                        'down': load_image('frightened_down.png', colorkey=-1),
                        'right': load_image('frightened_right.png', colorkey=-1),
                        'left': load_image('frightened_left.png', colorkey=-1)}
    image_eaten = {'up': load_image('eaten_up.png', colorkey=-1),
                   'down': load_image('eaten_down.png', colorkey=-1),
                   'right': load_image('eaten_right.png', colorkey=-1),
                   'left': load_image('eaten_left.png', colorkey=-1)}

    def __init__(self, *groups):
        super().__init__(*groups)
        self.direction = DIRECTIONS['left']
        self.mode = Entity.modes['chase']

    def choice_direction(self):
        self.make_goal_point()
        possible = Entity.points.get(self.pos.to_tuple(), list(DIRECTIONS.values()))
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
        self.direction = self.choice_direction()
        self.pos = self.pos + self.direction

    def make_goal_point(self):
        pass

    def get_pos(self):
        return self.pos

    def get_direction(self):
        return self.direction

    def change_mode(self, mode):
        self.mode = Entity.modes[mode]
        self.direction = -self.direction


class Pacman(Entity):
    image = {'up': [load_image(f'pacman_up{i}' for i in range(1, 4))],
             'left': [load_image(f'pacman_left{i}' for i in range(1, 4))],
             'down': [load_image(f'pacman_down{i}' for i in range(1, 4))],
             'right': [load_image(f'pacman_right{i}' for i in range(1, 4))]}

    def __init__(self, *groups):
        super().__init__(*groups)
        self.pos = Position(13, 26)

    def choice_direction(self):
        return DIRECTIONS[last_key]


class Blinky(Entity):
    image = {'up': load_image('blinky_up.png', colorkey=-1),
             'down': load_image('blinky_down.png', colorkey=-1),
             'right': load_image('blinky_right.png', colorkey=-1),
             'left': load_image('blinky_left.png', colorkey=-1)}
    scatter_point = Position(25, -1)

    def __init__(self, *groups):
        super().__init__(*groups)
        self.make_goal_point()
        self.pos = Position(13, 16)

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
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_frightened[direction]
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
    scatter_point = Position(25, -1)

    def __init__(self, *groups):
        super().__init__(*groups)
        self.make_goal_point()
        self.pos = Position(13, 18)
        self.mode = Entity.modes['in_house']
        self.direction = DIRECTIONS['down']

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
        if self.mode == Entity.modes['chase'] or self.mode == Entity.modes['scatter']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Pinky.image[direction]
        elif self.mode == Entity.modes['frightened']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_frightened[direction]
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
    scatter_point = Position(29, 36)

    def __init__(self, *groups):
        super().__init__(*groups)
        self.make_goal_point()
        self.pos = Position(15, 18)
        self.mode = Entity.modes['in_house']
        self.direction = DIRECTIONS['up']

    def change_mode(self, mode):
        super().change_mode(mode)
        self.update_image()

    def make_goal_point(self):
        if self.mode == Entity.modes['chase']:
            self.goal_point = blinky.get_pos() + (pacman.get_pos() + pacman.get_direction() * 2 - blinky.get_pos) * 2
        if self.mode == Entity.modes['scatter']:
            self.goal_point = Inky.scatter_point
        if self.mode == Entity.modes['eaten']:
            self.goal_point = Entity.eaten_point

    def update_image(self):
        if self.mode == Entity.modes['chase'] or self.mode == Entity.modes['scatter']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Inky.image[direction]
        elif self.mode == Entity.modes['frightened']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_frightened[direction]
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
    scatter_point = Position(0, 36)

    def __init__(self, *groups):
        super().__init__(*groups)
        self.make_goal_point()
        self.pos = Position(11, 38)
        self.mode = Entity.modes['in_house']
        self.direction = DIRECTIONS['up']

    def change_mode(self, mode):
        super().change_mode(mode)
        self.update_image()

    def make_goal_point(self):
        if self.mode == Entity.modes['chase']:
            if (pacman.get_pos() - self.get_pos()) ** 2 > 8:
                self.goal_point = pacman.get_pos()
            else:
                self.goal_point = Clyde.scatter_point
        if self.mode == Entity.modes['scatter']:
            self.goal_point = Inky.scatter_point
        if self.mode == Entity.modes['eaten']:
            self.goal_point = Entity.eaten_point

    def update_image(self):
        if self.mode == Entity.modes['chase'] or self.mode == Entity.modes['scatter']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Clyde.image[direction]
        elif self.mode == Entity.modes['frightened']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_frightened[direction]
        elif self.mode == Entity.modes['eaten']:
            for direction, vector in DIRECTIONS.items():
                if vector == self.direction:
                    break
            self.image = Entity.image_eaten[direction]
