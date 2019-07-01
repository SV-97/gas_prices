from enum import Enum

class Color(Enum):
    Black = 30
    DarkRed = 31
    DarkGreen = 32
    Grey = 37
    Default = 39
    Red = 91
    Green = 92
    Yellow = 93
    Magenta = 95
    Cyan = 96
    White = 97


class Modifier(Enum):
    Reset = 0
    Bold = 1
    Faint = 2
    Italic = 3
    Underline = 4
    SlowBlink = 5
    RapidBlink = 6
    Reverse = 7
    CrossedOut = 9
    DoubleUnderline = 21


class BgColor(Enum):
    Black = 40
    DarkRed = 41
    DargGreen = 42
    Grey = 47
    Default = 49
    Red = 101
    Green = 102
    Yellow = 103
    Blue = 104
    Magenta = 105
    Cyan = 106
    White = 107


def colored(string, *modifiers):
    return f"\33[{';'.join(map(lambda m: str(m.value), modifiers))}m{string}\33[0m"


def print_colored(string, *modifiers):
    print(colored(string, *modifiers))
