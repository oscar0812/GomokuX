import time
import tkinter as tk
from scipy import spatial

from constants import *
from gomoku_state import GomokuState


class TkinterApp:

    # array_points will have 1 more value in each row and col since we can click on the edges
    def generate_points(self):
        self.points = [Point(x, y, x * self.cell_w + self.margin_x, y * self.cell_h + self.margin_y)
                       for y in range(self.num_row_boxes + 1) for x in range(self.num_col_boxes + 1)]

        # calculate neighbors
        for index, point in enumerate(self.points):
            # get 5 to right
            if point.x + 3 < self.num_col_boxes:
                points = [self.points[index + x] for x in range(0, 5)]
                [p_.add_point_list(points) for p_ in points]

            # get 5 to the bottom
            if point.y + 3 < self.num_row_boxes:
                points = [self.points[index + (i * (self.num_col_boxes + 1))] for i in range(0, 5)]
                [p_.add_point_list(points) for p_ in points]

            # diagonal \
            if point.x + 3 < self.num_col_boxes and point.y + 3 < self.num_row_boxes:
                points = [self.points[index + (i * (self.num_col_boxes + 1)) + i] for i in range(0, 5)]
                [p_.add_point_list(points) for p_ in points]

            # diagonal /
            if point.x + 3 < self.num_col_boxes and point.y - 3 > 0:
                points = [self.points[index - x * self.num_col_boxes] for x in range(0, 5)]
                [p_.add_point_list(points) for p_ in points]

    def draw_box(self, point):
        x2 = point.lat_x + self.cell_w
        y2 = point.lat_y + self.cell_h
        self.canvas.create_rectangle(point.lat_x, point.lat_y, x2, y2)

    def draw_grid(self):
        for point in self.points:
            if point.x < self.num_col_boxes and point.y < self.num_row_boxes:
                # don't draw out of bounds boxes
                self.draw_box(point)

    def closest_coordinate(self, event) -> Point:
        coordinates = [(c.lat_x, c.lat_y) for c in self.points]
        tree = spatial.KDTree(coordinates)
        res = tree.query([(event.x, event.y)])

        closest_dist = res[0][0]
        closest_index = res[1][0]

        closest = self.points[closest_index]

        if closest.state != State.EMPTY:
            closest = None

        return closest

    def draw_circle(self, coordinate):
        x = coordinate.lat_x - (self.chip_circle_radius / 2)  # center circle
        y = coordinate.lat_y - (self.chip_circle_radius / 2)  # center circle
        self.canvas.create_oval(x, y, x + self.chip_circle_radius, y + self.chip_circle_radius,
                                fill=self.gomoku.current_player.color, tags="player_chip")

    def draw_numbers(self, event=None):
        self.clear_numbers()
        for count, point in enumerate(self.gomoku.point_stack):
            opposite_state = State.BLACK if point.state == State.WHITE else State.WHITE
            self.canvas.create_text(point.lat_x, point.lat_y, text=str(count + 1), fill=opposite_state.name, font=('Helvetica 15 bold'), tags="numbers")

    def clear_numbers(self, event=None):
        self.canvas.delete("numbers")

    # Determine the origin by clicking
    def canvas_click(self, event):
        if self.game_over:
            return

        closest = self.closest_coordinate(event)
        if closest is None:
            # print("Couldn't click")
            pass
        else:
            self.draw_circle(closest)
            self.game_over, winning_moves, current_player = self.gomoku.take_turn(closest)

            if self.game_over:
                p1 = winning_moves[0]
                p2 = winning_moves[-1]
                self.canvas.create_line(p1.lat_x, p1.lat_y, p2.lat_x, p2.lat_y, fill="red", width=5, tags="gameover")

    def restart(self, event=None):
        [point.set_state(State.EMPTY) for point in self.points]
        self.canvas.delete("player_chip")
        self.canvas.delete("gameover")
        self.clear_numbers()
        self.gomoku.clear()
        self.game_over = False

    def __init__(self, master=None):
        self.game_over = False
        self.points = []
        self.min_h = 900
        self.min_w = 1200
        self.num_col_boxes = 14
        self.num_row_boxes = 14

        self.margin_x = 40
        self.margin_y = 40
        self.cell_w = self.min_w / self.num_col_boxes
        self.cell_h = self.min_h / self.num_row_boxes

        self.chip_circle_radius = 40

        if self.num_col_boxes < 5 or self.num_row_boxes < 5:
            raise Exception("Minimum number of boxes is 5")
        self.generate_points()
        self.gomoku = GomokuState()

        # build ui
        self.topLevel = tk.Tk() if master is None else tk.Toplevel(master)
        self.topLevel.configure(height=self.min_h, width=self.min_w)
        right_frame = tk.Frame(self.topLevel, height=self.min_h)

        self.canvas = tk.Canvas(right_frame)
        self.canvas.configure(height=self.min_h + 2 * self.margin_y, state="normal",
                              width=self.min_w + 2 * self.margin_x)

        self.draw_grid()
        self.canvas.pack(expand="true", fill="both", side="top")

        right_frame.pack(expand="true", fill="both", side="right")
        left_frame = tk.Frame(self.topLevel)
        self.text = tk.Text(left_frame)
        self.text.configure(height=55, padx=5, pady=5, width=50, wrap="word")
        self.text.pack(fill="y", side="top")
        left_frame.pack(side="left")

        # Main widget
        self.mainwindow = self.topLevel

        # events
        # mouseclick event
        self.canvas.bind("<Button 1>", self.canvas_click)

        self.mainwindow.bind('q', self.restart)
        self.mainwindow.bind('1', self.draw_numbers)
        self.mainwindow.bind('2', self.clear_numbers)

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = TkinterApp()
    app.run()
