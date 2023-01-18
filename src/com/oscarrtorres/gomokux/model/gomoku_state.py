from src.com.oscarrtorres.gomokux.model.enums import *
from src.com.oscarrtorres.gomokux.model.player import Player
from src.com.oscarrtorres.gomokux.model.point import Point


class GomokuState:
    def __init__(self):
        self.point_stack = []

        self.player1 = Player(State.BLACK)
        self.player2 = Player(State.WHITE)

        self.current_player = self.player1

    def switch_player(self):
        if self.current_player == self.player1:
            self.current_player = self.player2
        elif self.current_player == self.player2:
            self.current_player = self.player1

    # return game_over (boolean), winning_moves (list of moves that caused game over), current_player
    def take_turn(self, point: Point):
        if point.state == State.EMPTY:
            # save data
            self.point_stack.append(point)

            point.state = self.current_player.state

            game_over, winning_moves = self.check_game_over(point)
            if game_over:
                return game_over, winning_moves, self.current_player
            else:
                self.switch_player()
                return False, None, self.current_player
        else:
            print("This point isn't empty")
            return False, None, self.current_player

    def clear(self):
        self.current_player = self.player1
        self.point_stack.clear()

    def check_game_over(self, last_point: Point):
        game_over = False
        winning_moves = None
        for point_list in last_point.point_lists:
            game_over = point_list and all(point_list[0].state == point.state for point in point_list)
            if game_over:
                winning_moves = point_list
                break

        return game_over, winning_moves

