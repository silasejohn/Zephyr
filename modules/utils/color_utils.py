
import sys
# ANSI escape codes
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
RESET = '\033[0m'  # Reset to default color

def error_print(msg):
    print(f'{RED}{msg}{RESET}')
    sys.stdout.flush()

def warning_print(msg):
    print(f'{YELLOW}{msg}{RESET}')
    sys.stdout.flush()

def info_print(msg):
    print(f'{BLUE}{msg}{RESET}')
    sys.stdout.flush()

def success_print(msg):
    print(f'{GREEN}{msg}{RESET}')
    sys.stdout.flush()

class ColorPrint:
    def __init__(self, color):
        self.color = color
        self.RED = RED
        self.GREEN = GREEN
        self.YELLOW = YELLOW
        self.BLUE = BLUE
        self.MAGENTA = MAGENTA
        self.CYAN = CYAN
        self.RESET = RESET

    def __call__(self, msg):
        print(f'{self.color}{msg}{RESET}')

def pretty_print(msg, color):
    print(f'{color}{msg}{RESET}')