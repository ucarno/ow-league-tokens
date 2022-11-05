from constants import COLORS


def format_text(text: str):
    for color_code, color in COLORS:
        text = text.replace(color_code, color)
    return text


def print_fmt(text: str, end='\n'):
    print(format_text(text), end=end)
