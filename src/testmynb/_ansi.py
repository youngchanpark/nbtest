import re

def strip_ansi(text):
    """
    Removes all ANSI escape codes in a given text.
    """
    return re.sub(r'\x1b\[(\d|;)+m', '', text)

def green(text):
    return f"\033[38;5;82m{text}\033[0m"

def red(text):
    return f"\033[38;5;197m{text}\033[0m"

def orange(text):
    return f"\033[38;5;214m{text}\033[0m"
