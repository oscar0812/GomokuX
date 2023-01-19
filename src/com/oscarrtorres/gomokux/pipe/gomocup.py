from enum import Enum
from subprocess import Popen, PIPE
from os import path

from src.com.oscarrtorres.gomokux.model.point import Point


class Commands(Enum):
    START = 0
    TURN = 1
    BEGIN = 2
    BOARD = 3
    INFO = 4
    END = 5
    ABOUT = 6


class PipeConnection:
    def __init__(self, exe_path):
        self.exe_path = exe_path
        if not exe_path.endswith(".exe"):
            raise Exception(f'Gomocup AI file must be an .exe file')

        if not path.exists(exe_path):
            raise Exception(f'Executable with path "{exe_path}" not found!')

        self.main_pipe: Popen = None
        self.__open_pipe__connection__()

    def __open_pipe__connection__(self):
        self.main_pipe = Popen([self.exe_path], stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='UTF-8', universal_newlines=True)

    def send_command(self, command):
        print(f'SENDING: {command}')
        self.main_pipe.stdin.write(command)
        self.main_pipe.stdin.flush()
        r = self.main_pipe.stdout.readline()
        print(f'DONE READING: {r}')
        return r
    

class GomocupAI:
    def __init__(self, name, exe_path):
        self.name = name
        self.exe_path = exe_path
        self.pipe = None
        
    def open_conn(self):
        print(f'OPENED CONNECTION: {self.exe_path}')
        self.pipe = PipeConnection(self.exe_path)

    def close_conn(self):
        self.pipe.main_pipe.stdout.close()
        self.pipe.main_pipe.stdin.close()
        self.pipe.main_pipe.terminate()
        
    def send_start_command(self, size: int = 19):
        return self.pipe.send_command(f'START {size}\n')

    def send_turn_command(self, point: Point):
        return self.pipe.send_command(f'TURN {point.x},{point.y}\n')

    def send_info_command(self, point: Point):
        return self.pipe.send_command(f'INFO {point.x},{point.y}\n')

    def send_about_command(self):
        return self.pipe.send_command(f'ABOUT\n')

class GomocupAIEnum(Enum):
    TIANSHU = GomocupAI("Tianshu", "C:\\Users\\Oscar\\PycharmProjects\\GomokuX\\exes\\TIANSHU\\pbrain-tianshu.exe")
    FAST_GOMOKU = GomocupAI("Fast Gomoku", "C:\\Users\\Oscar\\PycharmProjects\\GomokuX\\exes\\FASTGOMOKU14\\pbrain-fast-gomoku14.exe")

