from enum import Enum


class Point:
    def __init__(self, x, y, lat_x, lat_y):
        self.x = x
        self.y = y
        self.lat_x = lat_x
        self.lat_y = lat_y
        self.state = State.EMPTY
        self.point_lists = []  # what points are connected to this to trigger a win

    def set_state(self, state):
        self.state = state

    def add_point_list(self, point_list):
        self.point_lists.append(point_list)


class Player:
    def __init__(self, state):
        self.state = state
        if state == State.EMPTY:
            raise Exception("Invalid player state")
        self.color = state.name.lower()


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class State(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2
