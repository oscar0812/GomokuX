from src.com.oscarrtorres.gomokux.model.enums import State
from src.com.oscarrtorres.gomokux.model.player import Player
from src.com.oscarrtorres.gomokux.model.point import Point
from src.com.oscarrtorres.gomokux.pipe.gomocup import GomocupAIEnum, PipeConnection, GomocupAI


class GomokuBoard:
    def __init__(self, number_of_x_chips, number_of_y_chips, cell_width, box_height, margin_x, margin_y):
        if number_of_x_chips < 5 or number_of_y_chips < 5:
            raise Exception("Minimum number of boxes is 5")

        self.number_of_x_chips = number_of_x_chips
        self.number_of_y_chips = number_of_y_chips
        self.cell_w = cell_width
        self.margin_x = margin_x
        self.cell_h = box_height
        self.margin_y = margin_y

        self.player1 = Player(State.BLACK)
        self.player2 = Player(State.WHITE)
        self.current_player = self.player1

        self.player_points_stack = {State.BLACK: [], State.WHITE: []}
        self.all_points_stack = []

        self.undone_moves = []  # in case we want to redo them

        self.gomocup_ai: GomocupAI = None

        self.points: list[Point] = []
        self.__generate_points__()

    # array_points will have 1 more value in each row and col since we can click on the edges
    def __generate_points__(self):
        self.points = [Point(x, y, x * self.cell_w + self.margin_x, y * self.cell_h + self.margin_y)
                       for y in range(self.number_of_x_chips) for x in range(self.number_of_y_chips)]

        max_in_a_row = 5

        # calculate neighbors
        for index, point in enumerate(self.points):
            point.set_index(index)
            in_x_boundary = point.x + (max_in_a_row - 1) < self.number_of_x_chips
            in_y_boundary = point.y + (max_in_a_row - 1) < self.number_of_y_chips

            # get 5 to right
            if in_x_boundary:
                points = [self.points[index + x] for x in range(0, max_in_a_row)]
                [p_.add_point_list(points) for p_ in points]

            # get 5 to the bottom
            if in_y_boundary:
                points = [self.points[index + (i * self.number_of_y_chips)] for i in range(0, max_in_a_row)]
                [p_.add_point_list(points) for p_ in points]

            # diagonal \
            if in_x_boundary and in_y_boundary:
                points = [self.points[index + (i * self.number_of_y_chips) + i] for i in range(0, max_in_a_row)]
                [p_.add_point_list(points) for p_ in points]

            # diagonal /
            if point.y > (max_in_a_row - 2) and in_x_boundary:
                points = [self.points[index - (i * self.number_of_x_chips - i)] for i in range(0, max_in_a_row)]
                [p_.add_point_list(points) for p_ in points]

    def x_y_to_point(self, x: int, y: int):
        return self.points[y * self.number_of_x_chips + x]

    def set_gomocup_ai(self, gomocup_ai: GomocupAIEnum):
        if self.has_ai_loaded():
            # close previous connection
            self.gomocup_ai.close_conn()

        self.gomocup_ai = gomocup_ai.value
        self.gomocup_ai.open_conn()

    def has_ai_loaded(self):
        return self.gomocup_ai is not None

    def get_last_move(self) -> Point:
        if self.all_points_stack:
            return self.all_points_stack[-1]
        return None

    def get_last_undone_move(self) -> Point:
        if self.undone_moves:
            return self.undone_moves[-1]
        return None

    def restart(self):
        self.current_player = self.player1
        self.all_points_stack.clear()
        self.player_points_stack = {State.BLACK: [], State.WHITE: []}

    def get_opposite_player(self):
        if self.current_player == self.player1:
            return self.player2
        elif self.current_player == self.player2:
            return self.player1

    def switch_player(self):
        self.current_player = self.get_opposite_player()

    # return game_over (boolean), winning_moves (list of moves that caused game over), current_player
    def take_turn(self, point: Point):
        if point.state == State.EMPTY:
            # check if not redo: clear out redo list
            if self.undone_moves:
                if self.undone_moves[-1] == point:
                    self.undone_moves.pop()
                else:
                    self.undone_moves.clear()

            # save data
            self.all_points_stack.append(point)
            self.player_points_stack[self.current_player.state].append(point)

            point.state = self.current_player.state

            game_over, winning_moves = self.check_game_over(point)
            self.switch_player()
            if game_over:
                return game_over, winning_moves, self.current_player
            else:
                return False, None, self.current_player
        else:
            print("This point isn't empty")
            return False, None, self.current_player

    def undo_move(self):
        if self.all_points_stack:
            point: Point = self.all_points_stack.pop()
            self.player_points_stack[self.get_opposite_player().state].pop()

            point.state = State.EMPTY

            self.undone_moves.append(point)

            self.switch_player()

        else:
            print('No moves to undo')

    def redo_move(self):
        if self.undone_moves:
            point: Point = self.undone_moves[-1]
            self.take_turn(point)
            self.undone_moves.pop()
            self.switch_player()
        else:
            print('No moves to redo')

    def check_game_over(self, last_point: Point):
        game_over = False
        winning_moves = None
        for point_list in last_point.point_lists:
            game_over = point_list and all(point_list[0].state == point.state for point in point_list)
            if game_over:
                winning_moves = point_list
                break

        return game_over, winning_moves
