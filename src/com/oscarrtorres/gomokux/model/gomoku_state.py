from src.com.oscarrtorres.gomokux.model.enums import *
from src.com.oscarrtorres.gomokux.model.player import Player
from src.com.oscarrtorres.gomokux.model.point import Point


class GomokuState:
    def __init__(self):
        self.player1 = Player(State.BLACK)
        self.player2 = Player(State.WHITE)
        self.current_player = self.player1

        self.player_points_stack = {State.BLACK: [], State.WHITE: []}
        self.all_points_stack = []

        self.undone_moves = []  # in case we want to redo them

    def get_last_move(self) -> Point:
        if self.all_points_stack:
            return self.all_points_stack[-1]
        return None

    def get_last_undone_move(self) -> Point:
        if self.undone_moves:
            return self.undone_moves[-1]
        return None

    def start_new(self):
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

