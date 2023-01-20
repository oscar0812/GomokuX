import tkinter as tk
from tkinter import END

from scipy import spatial
from functools import partial

from src.com.oscarrtorres.gomokux.model.enums import *
from src.com.oscarrtorres.gomokux.model.gomoku_board import GomokuBoard
from src.com.oscarrtorres.gomokux.model.point import Point
from src.com.oscarrtorres.gomokux.pipe.gomocup import GomocupAIEnum, GomocupAIResponse


class TkinterApp:

    def draw_box(self, point):
        x2 = point.lat_x + self.gomoku_board.cell_w
        y2 = point.lat_y + self.gomoku_board.cell_h
        self.canvas.create_rectangle(point.lat_x, point.lat_y, x2, y2)

    def draw_grid(self):
        for point in self.gomoku_board.points:
            if point.x < self.gomoku_board.number_of_x_chips - 1 and point.y < self.gomoku_board.number_of_y_chips - 1:
                # don't draw out of bounds boxes
                self.draw_box(point)

    def closest_point(self, event) -> Point:
        coordinates = [(c.lat_x, c.lat_y) for c in self.gomoku_board.points]
        tree = spatial.KDTree(coordinates)
        res = tree.query([(event.x, event.y)])

        closest_dist = res[0][0]
        closest_index = res[1][0]

        closest = self.gomoku_board.points[closest_index]

        if closest.state != State.EMPTY:
            closest = None

        return closest

    def draw_circle(self, point):
        x = point.lat_x - (self.chip_circle_radius / 2)  # center circle
        y = point.lat_y - (self.chip_circle_radius / 2)  # center circle
        self.canvas.create_oval(x, y, x + self.chip_circle_radius, y + self.chip_circle_radius,
                                fill=self.gomoku_board.current_player.color, tags=f'playerchip playerchip_{point.index}')

    def enable_chip_numbers(self, event=None):
        self.disable_chip_numbers()
        self.chip_numbers_enabled = True
        self.draw_chip_numbers()

    def draw_chip_numbers(self):
        points = self.gomoku_board.all_points_stack

        for count, point in enumerate(points):
            if self.canvas.find_withtag(f'number_{point.index}'):
                continue  # already drew this chip number

            opposite_state = State.BLACK if point.state == State.WHITE else State.WHITE
            self.canvas.create_text(point.lat_x, point.lat_y, text=str(count + 1), fill=opposite_state.name,
                                    font=('Helvetica 15 bold'), tags=f'numbers number_{point.index}')

    def disable_chip_numbers(self, event=None):
        self.chip_numbers_enabled = False
        self.canvas.delete("numbers")

    def append_to_textbox(self, str_):
        self.text.insert(END, chars=str_)

    def place_chip(self, point: Point):
        self.draw_circle(point)
        # print(f'Placed chip: {point}')
        self.game_over, winning_moves, current_player = self.gomoku_board.take_turn(point)

        if self.chip_numbers_enabled:
            self.draw_chip_numbers()

        self.append_to_textbox(f'Move {len(self.gomoku_board.all_points_stack)}) Player {point.state.value} placed chip at {point.x}, {point.y}\n')

        if self.game_over:
            p1 = winning_moves[0]
            p2 = winning_moves[-1]
            self.canvas.create_line(p1.lat_x, p1.lat_y, p2.lat_x, p2.lat_y, fill="red", width=5, tags="gameover")
            self.append_to_textbox(f'Player {point.state.value} won!')

    # Determine the origin by clicking
    def canvas_click(self, event):
        if self.game_over:
            return

        closest = self.closest_point(event)
        if closest is None:
            # print("Couldn't click")
            pass
        else:
            self.place_chip(closest)
            self.canvas.update()

            if self.gomoku_board.has_ai_loaded():
                output_lines: list[GomocupAIResponse] = self.gomoku_board.gomocup_ai.send_turn_command(point=closest)
                for res in output_lines:
                    self.append_to_textbox(f'BOT) {res.response_str}\n')
                    if res.is_x_y_point:
                        x_y = res.x_y_points
                        bot_point = self.gomoku_board.x_y_to_point(x_y[0], x_y[1])
                        self.place_chip(bot_point)

    def undo_move(self, event=None):
        last_move: Point = self.gomoku_board.get_last_move()
        if not last_move:
            print('Can\'t undo move')
            return

        if self.game_over:
            self.game_over = False
            self.canvas.delete("gameover")

        self.canvas.delete(f'number_{last_move.index}')
        self.canvas.delete(f'playerchip_{last_move.index}')
        self.gomoku_board.undo_move()

    def redo_move(self, event=None):
        last_move = self.gomoku_board.get_last_undone_move()
        if not last_move:
            print('Can\'t redo move')
            return
        else:
            self.place_chip(last_move)

    def restart(self, event=None):
        [point.set_state(State.EMPTY) for point in self.gomoku_board.points]
        self.canvas.delete("playerchip")
        self.canvas.delete("gameover")
        self.disable_chip_numbers()

        self.gomoku_board.restart()
        self.game_over = False

        # clear textbox
        self.text.delete("1.0", END)

        if self.gomoku_board.has_ai_loaded():
            self.gomoku_board.gomocup_ai.send_start_command(self.gomoku_board.number_of_x_chips)
            self.append_to_textbox(f'{ self.gomoku_board.gomocup_ai.name} Bot Selected!\n')

    def set_gomocup_ai(self, gomocup_ai: GomocupAIEnum):
        self.gomoku_board.set_gomocup_ai(gomocup_ai)
        self.append_to_textbox(f'{gomocup_ai.value.name} Bot Selected!\n')
        self.gomoku_board.gomocup_ai.send_start_command(self.gomoku_board.number_of_x_chips)

    def set_up_menu(self):
        menubar = tk.Menu(self.mainwindow)
        self.mainwindow.config(menu=menubar)

        file_menu = tk.Menu(menubar)
        file_menu.add_command(label='Restart Game (q)', command=self.restart)
        file_menu.add_command(label="Exit", underline=0, command=quit)

        gomocup_menu = tk.Menu(menubar)
        for gomocup_ai in GomocupAIEnum:
            gomocup_menu.add_command(label=gomocup_ai.value.name, command=partial(self.set_gomocup_ai, gomocup_ai))

        shortcuts_menu = tk.Menu(menubar)

        shortcuts_menu.add_command(label='Show Chip Numbers (1)', command=self.enable_chip_numbers)
        shortcuts_menu.add_command(label='Hide Chip Numbers (2)', command=self.disable_chip_numbers)
        shortcuts_menu.add_command(label='Undo Last Move (u)', command=self.undo_move)
        shortcuts_menu.add_command(label='Redo Last Move (r)', command=self.redo_move)

        menubar.add_cascade(label="File", underline=0, menu=file_menu)
        menubar.add_cascade(label="Gomocup AI", underline=0, menu=gomocup_menu)
        menubar.add_cascade(label="Shortcuts", underline=0, menu=shortcuts_menu)

    def __init__(self, master=None):
        self.chip_numbers_enabled = False
        self.game_over = False
        min_h = 900
        min_w = 1200

        number_of_x_chips = 15
        number_of_y_chips = 15
        cell_w = min_w / (number_of_y_chips - 1)
        cell_h = min_h / (number_of_x_chips - 1)

        self.gomoku_board = GomokuBoard(number_of_x_chips=number_of_x_chips, number_of_y_chips=number_of_y_chips, cell_width=cell_w, box_height=cell_h, margin_x=40, margin_y = 40)

        self.chip_circle_radius = 40

        # build ui
        self.topLevel = tk.Tk() if master is None else tk.Toplevel(master)
        self.topLevel.configure(height=min_h, width=min_w)
        right_frame = tk.Frame(self.topLevel, height=min_h)

        self.canvas = tk.Canvas(right_frame)
        self.canvas.configure(height=min_h + 2 * self.gomoku_board.margin_y, state="normal",
                              width=min_w + 2 * self.gomoku_board.margin_x)

        self.draw_grid()
        self.canvas.pack(expand="true", fill="both", side="top")

        right_frame.pack(expand="true", fill="both", side="right")
        left_frame = tk.Frame(self.topLevel)
        self.text = tk.Text(left_frame)
        self.text.configure(height=55, padx=5, pady=5, width=50, wrap="word", font=('Helvetica 12'))
        self.text.pack(fill="y", side="top")
        left_frame.pack(side="left")

        # Main widget
        self.mainwindow = self.topLevel

        # events
        # mouseclick event
        self.canvas.bind("<Button 1>", self.canvas_click)

        self.mainwindow.bind('q', self.restart)
        self.mainwindow.bind('1', self.enable_chip_numbers)
        self.mainwindow.bind('2', self.disable_chip_numbers)
        self.mainwindow.bind('u', self.undo_move)
        self.mainwindow.bind('r', self.redo_move)
        self.set_up_menu()

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = TkinterApp()
    app.run()
