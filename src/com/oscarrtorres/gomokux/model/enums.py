from enum import Enum


class State(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
