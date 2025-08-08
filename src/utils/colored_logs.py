"""Colored console logging utility similar to chalk/ansi colors."""

import json
from typing import Any, List


class AnsiColors:
    """ANSI color codes for terminal output."""
    BLACK = '\u001b[30m'
    RED = '\u001b[38;5;196m'
    GREEN = '\u001b[32m'
    YELLOW = '\u001b[38;5;11m'
    BLUE = '\u001b[34m'
    MAGENTA = '\u001b[35m'
    CYAN = '\u001b[36m'
    WHITE = '\u001b[37m'
    RESET = '\u001b[0m'
    GRAY = '\u001b[38;5;245m'
    GREY = '\u001b[38;5;245m'  # Alias for gray
    DARKGRAY = '\u001b[38;5;239m'


def _log_with_color(things: List[Any], color: str) -> None:
    """Log items with specified color."""
    color_code = getattr(AnsiColors, color.upper())
    
    for thing in things:
        if isinstance(thing, str):
            print(f"{color_code}{thing}{AnsiColors.RESET}")
        else:
            # Pretty print JSON for objects
            json_str = json.dumps(thing, indent=4, default=str)
            print(f"{color_code}{json_str}{AnsiColors.RESET}")


def blue(*things: Any) -> None:
    """Log in blue color."""
    _log_with_color(list(things), "blue")


def cyan(*things: Any) -> None:
    """Log in cyan color."""
    _log_with_color(list(things), "cyan")


def yellow(*things: Any) -> None:
    """Log in yellow color."""
    _log_with_color(list(things), "yellow")


def magenta(*things: Any) -> None:
    """Log in magenta color."""
    _log_with_color(list(things), "magenta")


def green(*things: Any) -> None:
    """Log in green color."""
    _log_with_color(list(things), "green")


def red(*things: Any) -> None:
    """Log in red color."""
    _log_with_color(list(things), "red")


def white(*things: Any) -> None:
    """Log in white color."""
    _log_with_color(list(things), "white")


def gray(*things: Any) -> None:
    """Log in gray color."""
    _log_with_color(list(things), "gray")


def grey(*things: Any) -> None:
    """Log in grey color (alias for gray)."""
    _log_with_color(list(things), "gray")


def darkgray(*things: Any) -> None:
    """Log in dark gray color."""
    _log_with_color(list(things), "darkgray")


# Divider constant
DIVIDER = "#########################################################\n#########################################################"


def divider() -> None:
    """Print a divider line."""
    print(DIVIDER)