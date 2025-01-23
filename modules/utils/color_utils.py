
# ANSI escape codes
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
RESET = '\033[0m'  # Reset to default color

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