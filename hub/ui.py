"""Shared UI helpers: terminal width, colors, logo, boxes, clear, wait."""
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

# ---------- palette ----------
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BG_BLACK = "\033[40m"
BG_BLUE = "\033[44m"
BG_CYAN = "\033[46m"
BG_MAGENTA = "\033[45m"

ACCENT = CYAN
ACCENT2 = MAGENTA
MUTED = DIM
SUCCESS = GREEN
ERROR = RED
WARN = YELLOW

# ---------- box chars ----------
TL, TR, BL, BR = "╭", "╮", "╰", "╯"
H, V = "─", "│"
LT, RT, LL, RR = "├", "┤", "╰", "╯"

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
    print(f"\n{MUTED}{msg}{RESET}")
    readchar.readkey()


def hr(char=H):
    print(MUTED + char * term_width() + RESET)


# ---------- boxes ----------
def box_top(title: str = "", width: int | None = None) -> str:
    width = width or term_width()
    if not title:
        return ACCENT + TL + H * (width - 2) + TR + RESET
    t = f" {title} "
    pad = width - 2 - len(t)
    if pad < 0:
        t = t[: width - 2]
        pad = 0
    left = pad // 2
    right = pad - left
    return ACCENT + TL + H * left + BOLD + t + RESET + ACCENT + H * right + TR + RESET


def box_mid(text: str = "", width: int | None = None) -> str:
    width = width or term_width()
    inner = width - 4
    if len(text) > inner:
        text = text[: inner - 1] + "~"
    return ACCENT + V + RESET + " " + text.ljust(inner) + " " + ACCENT + V + RESET


def box_sep(width: int | None = None) -> str:
    width = width or term_width()
    return ACCENT + LT + H * (width - 2) + RT + RESET


def box_bottom(width: int | None = None) -> str:
    width = width or term_width()
    return ACCENT + BL + H * (width - 2) + BR + RESET


def strip_ansi(s: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


def pad_ansi(s: str, width: int) -> str:
    return s + " " * max(0, width - len(strip_ansi(s)))


# ---------- header ----------
def print_header(section: str = ""):
    width = term_width()
    title = f"{BOLD}{ACCENT}revil_pyHUB{RESET}"
    if section:
        title += f" {MUTED}/{RESET} {section}"
    right = f"{MUTED}v0.4.0{RESET}"
    left_plain = "revil_pyHUB" + (f" / {section}" if section else "")
    pad = " " * max(1, width - len(left_plain) - len("v0.4.0"))
    print(box_top())
    print(ACCENT + V + RESET + " " + title + pad + right + " " + ACCENT + V + RESET)
    print(box_sep())


def print_logo():
    clear()
    print(ACCENT + LOGO + RESET)


def print_status_bar(left: str, right: str = ""):
    width = term_width()
    l = left
    if right:
        r = right
        space = max(0, width - len(strip_ansi(l)) - len(strip_ansi(r)) - 4)
        line = ACCENT + V + RESET + " " + l + " " * space + r + " " + ACCENT + V + RESET
    else:
        line = ACCENT + V + RESET + " " + l + " " * max(0, width - len(strip_ansi(l)) - 3) + ACCENT + V + RESET
    print(line)
    print(box_bottom())


# ---------- helpers ----------
def badge(text: str, color: str = CYAN) -> str:
    return f"{color}{BOLD}{text}{RESET}"


def hint(keys: dict[str, str]) -> str:
    parts = []
    for k, v in keys.items():
        parts.append(f"{ACCENT}{k}{RESET} {MUTED}{v}{RESET}")
    return "  ".join(parts)
