from src.com.oscarrtorres.gomokux.model.enums import State


class Point:
    def __init__(self, x, y, lat_x, lat_y):
        self.x = x
        self.y = y
        self.lat_x = lat_x
        self.lat_y = lat_y
        self.state = State.EMPTY
        self.point_lists = []  # what points are connected to this to trigger a win
        self.index = 0

    def set_state(self, state):
        self.state = state

    def set_index(self, index: int):
        self.index = index

    def add_point_list(self, point_list):
        self.point_lists.append(point_list)

    def __str__(self) -> str:
        return f'[index={self.index}, x={self.x}, y={self.y}, lat_x={self.lat_x}, lat_y={self.lat_y}, state={self.state}]'
