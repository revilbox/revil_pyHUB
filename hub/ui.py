"""Shared UI helpers: terminal width, colors, logo, clear, wait."""
import os
import shutil
import sys
from pathlib import Path

try:
    import readchar
except ImportError:
    print("Missing dependency. Run: pip install readchar")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent

# ANSI colors (reset always)
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

LOGO = r"""
 ____            _ _   ____       _   _ _   _ ____
|  _ \ _____   _(_) | |  _ \_   _| | | | | | | __ )
| |_) / _ \ \ / / | | | |_) | | | | |_| | | |  _ \
|  _ <  __/\ V /| | | |  __/| |_| |  _  | |_| |_) |
|_| \_\___| \_/ |_|_| |_|    \__, |_| |_|\___/|____/
                             |___/
"""


def term_width() -> int:
    try:
        w = shutil.get_terminal_size((80, 24)).columns
    except Exception:
        w = 80
    return max(40, min(w, 200))


def clear():
    os.system("clear")


def wait_key(msg="Press any key to return."):
    print(f"\n{DIM}{msg}{RESET}")
    readchar.readkey()


def hr(char="="):
    print(char * term_width())


def print_logo():
    print(CYAN + LOGO + RESET)
    print(f"{BOLD}  revil_pyHUB{RESET} {DIM}(terminal hub){RESET}")
    hr("-")


def print_status_bar(left: str, right: str = ""):
    width = term_width()
    if right:
        left_part = left[: max(0, width - len(right) - 1)]
        line = left_part + " " * max(0, width - len(left_part) - len(right)) + right
    else:
        line = left
    print(f"{DIM}{line[:width]}{RESET}")
