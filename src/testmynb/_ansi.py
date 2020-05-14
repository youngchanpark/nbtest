import re


def strip_ansi(text):
    """
    Removes all ANSI escape codes in a given text.
    """
    return re.sub(r"\x1b\[(\d|;)+m", "", text)


def green(text):
    return "\033[38;5;82m{}\033[0m".format(text)


def red(text):
    return "\033[38;5;197m{}\033[0m".format(text)


def orange(text):
    return "\033[38;5;214m{}\033[0m".format(text)
