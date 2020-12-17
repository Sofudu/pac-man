import pygame
import os
import sys
import random


class Position:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)

    def __pow__(self, power):
        return self.x ** 2 + self.y ** 2

    def __neg__(self):
        return Position(-self.x, self.y)

    def to_tuple(self):
        return self.x, self.y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)


DIRECTIONS = {'UP': Position(0, -1), 'LEFT': Position(-1, 0), 'DOWN': Position(0, 1), 'RIGHT': Position(1, 0)}


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


def calculate_distance(point1, point2):
    return (point1 - point2) ** 2


class Ghost(pygame.sprite.Sprite):
    points = {(5, 7): list(DIRECTIONS.values())}
    unique_points = dict()
    modes = {'chase': 1, 'scatter': 2, 'frightened': 3}

    def __init__(self, *groups):
        super().__init__(*groups)
        self.direction = DIRECTIONS['LEFT']
        self.mode = Ghost.modes['chase']
        self.pos = Position(5, 7)
        self.goal_point = Position(1, 2)

    def choice_direction(self):
        self.make_goal_point()
        possible = Ghost.points.get(self.pos.to_tuple(), list(DIRECTIONS.values()))
        possible.remove(-self.direction)
        if self.mode != Ghost.modes['frightened']:
            min_direction = possible[0]
            min_distance = calculate_distance(self.pos + min_direction, self.goal_point)
            for direction in possible:
                distance = calculate_distance(self.pos + direction, self.goal_point)
                if distance < min_distance:
                    min_distance = distance
                    min_direction = direction
            return min_direction
        else:
            return random.choice(possible)

    def make_step(self):
        self.direction = self.choice_direction()
        self.pos = self.pos + self.direction
        pass

    def make_goal_point(self):
        pass

    def get_pos(self):
        return self.pos.to_tuple()
