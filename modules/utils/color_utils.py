
import sys
# ANSI escape codes
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
RESET = '\033[0m'  # Reset to default color
WHITE = '\033[37m'

def error_print(msg, header='', header_color=''):
    if header == '':
        print(f'{RED}{msg}{RESET}')
    else:
        if header_color == '':
            header_color = WHITE
    print(f'{RED}{msg}{RESET}')
    sys.stdout.flush()

def warning_print(msg, header='', header_color=''):
    if header == '':
        print(f'{YELLOW}{msg}{RESET}')
    else:
        if header_color == '':
            header_color = WHITE
        else:
            header_color = header_color
        print(f'{header_color}[{header}] >> {YELLOW}{msg}{RESET}')
    sys.stdout.flush()
        
def info_print(msg, header='', header_color=''):
    if header == '':
        print(f'{BLUE}{msg}{RESET}')
    else:
        if header_color == '':
            header_color = WHITE
        else:
            header_color = header_color
        print(f'{header_color}[{header}] >> {BLUE}{msg}{RESET}')
    sys.stdout.flush()

def success_print(msg, header='', header_color=''):
    if header == '':
        print(f'{GREEN}{msg}{RESET}')
    else:
        if header_color == '':
            header_color = WHITE
        else:
            header_color = header_color
        print(f'{header_color}[{header}] >> {GREEN}{msg}{RESET}')
    sys.stdout.flush()

# def zephyr_print(msg):
#     print(f"\n[[{ColorPrint.MAGENTA} Z E P H Y R {ColorPrint.RESET}]] >> {msg}...")

# def warning_print(msg):
#     print(f"\n[[{ColorPrint.YELLOW} WARNING {ColorPrint.RESET}]] >> {msg}...")

# def error_print(msg):   
#     print(f"\n[[{ColorPrint.RED} ERROR {ColorPrint.RESET}]] >> {msg}...")

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