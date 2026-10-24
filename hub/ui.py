"""Shared UI helpers: width, colors, boxes, ansi-safe fit."""
import os
import re
import shutil
import sys
from pathlib import Path

try:
    import readchar
except ImportError:
    print("Missing dependency. Run: pip install readchar")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------- palette: strict, white + red accent ----------
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
WHITE = "\033[37m"
BRIGHT_RED = "\033[91m"
BRIGHT_WHITE = "\033[97m"

ACCENT = BRIGHT_RED
TEXT = BRIGHT_WHITE
MUTED = DIM
SUCCESS = GREEN
ERROR = RED
WARN = YELLOW

# ---------- box chars ----------
TL, TR, BL, BR = "┌", "┐", "└", "┘"
H, V = "─", "│"
LT, RT = "├", "┤"

ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def vlen(s: str) -> int:
    return len(strip_ansi(s))


def fit(s: str, width: int) -> str:
    """Cut a possibly-colored string to visible width, ANSI-safe, then pad to exactly width."""
    if width <= 0:
        return ""
    out = []
    visible = 0
    i = 0
    while i < len(s):
        m = ANSI_RE.match(s, i)
        if m:
            out.append(m.group(0))
            i = m.end()
            continue
        if visible >= width:
            # skip rest but keep reset at end
            break
        out.append(s[i])
        visible += 1
        i += 1
    # pad
    if visible < width:
        out.append(" " * (width - visible))
    out.append(RESET)
    return "".join(out)


def term_width() -> int:
    try:
        w = shutil.get_terminal_size((80, 24)).columns
    except Exception:
        w = 80
    return max(40, min(w, 200))


def term_height() -> int:
    try:
        h = shutil.get_terminal_size((80, 24)).lines
    except Exception:
        h = 24
    return max(12, h)


def clear():
    os.system("clear")


def wait_key(msg="press any key"):
    print(f"\n{DIM}{msg}{RESET}")
    readchar.readkey()


def box_top(title: str = "", width: int | None = None) -> str:
    width = width or term_width()
    inner = width - 2
    if not title:
        return ACCENT + TL + H * inner + TR + RESET
    t = f" {title} "
    t = fit(t, inner)
    t_plain = strip_ansi(t)
    left = max(0, (inner - len(t_plain)) // 2)
    right = max(0, inner - len(t_plain) - left)
    return ACCENT + TL + H * left + RESET + BOLD + t + RESET + ACCENT + H * right + TR + RESET


def box_line(content: str, width: int | None = None) -> str:
    width = width or term_width()
    inner = width - 4
    return ACCENT + V + RESET + " " + fit(content, inner) + " " + ACCENT + V + RESET


def box_sep(width: int | None = None) -> str:
    width = width or term_width()
    return ACCENT + LT + H * (width - 2) + RT + RESET


def box_bottom(width: int | None = None) -> str:
    width = width or term_width()
    return ACCENT + BL + H * (width - 2) + BR + RESET


def print_header(section: str = ""):
    width = term_width()
    left = f"{BOLD}{TEXT}revil_pyHUB{RESET}"
    if section:
        left += f" {MUTED}/{RESET} {ACCENT}{section}{RESET}"
    right = f"{MUTED}v0.5.0{RESET}"
    lv = vlen(left)
    rv = vlen(right)
    space = max(1, width - lv - rv - 1)
    print(box_top(width=width))
    print(ACCENT + V + RESET + " " + left + " " * space + right + ACCENT + V + RESET)
    print(box_sep(width))


def print_status_bar(left: str, right: str = ""):
    width = term_width()
    lv = vlen(left)
    rv = vlen(right)
    space = max(0, width - lv - rv - 3)
    print(ACCENT + V + RESET + " " + left + " " * space + right + " " + ACCENT + V + RESET)
    print(box_bottom())
