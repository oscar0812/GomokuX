from enum import Enum
from subprocess import Popen, PIPE
from os import path


class Commands(Enum):
    START = 0
    TURN = 1
    BEGIN = 2
    BOARD = 3
    INFO = 4
    END = 5
    ABOUT = 6


class Executable:
    def __init__(self, name, exe_path):
        self.name = name
        self.exe_path = exe_path


class GomocupExecutable(Enum):
    TIANSHU = Executable("Tianshu", "C:\\Users\\Oscar\\PycharmProjects\\GomokuX\\exes\\TIANSHU\\pbrain-tianshu.exe")


class ExecutablePipeConnection:
    def __init__(self, executable: Executable):
        if not executable.exe_path.endswith(".exe"):
            raise Exception(f'Gomocup AI file must be an .exe file')

        if not path.exists(executable.exe_path):
            raise Exception(f'Executable with path "{executable.exe_path}" not found!')

        self.executable = executable
        self.main_pipe: Popen = None
        self.__open_pipe__connection__()

    def __open_pipe__connection__(self):
        self.main_pipe = Popen(self.executable.exe_path, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding="UTF-8")

    def __send_command__(self, command):
        self.main_pipe.stdin.write(command)
        self.main_pipe.stdin.flush()
        return self.main_pipe.stdout.read()

    def send_start_command(self, size: int = 19):
        return self.__send_command__(f'START {size}\n')
