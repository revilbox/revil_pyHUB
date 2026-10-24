"""Games: guess number, snake (smooth), 2048. Strict palette."""
import os
import random
import select
import sys
import time
import tty
import termios
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, print_header,
    box_top, box_line, box_bottom,
    ACCENT, TEXT, MUTED, RESET, BOLD,
    GREEN, RED, YELLOW, SUCCESS, ERROR, WARN,
)

GAMES = [
    ("1", "guess the number"),
    ("2", "snake"),
    ("3", "2048"),
    ("0", "back"),
]


def screen_games():
    while True:
        clear()
        width = term_width()
        print_header("GAMES")
        print(box_top(width=width))
        for key, label in GAMES:
            print(box_line(f"{ACCENT}{BOLD}[{key}]{RESET}  {TEXT}{label}{RESET}", width))
        print(box_bottom(width))
        print(f"{MUTED}press 0-3, q to quit{RESET}")
        key = readchar.readkey()
        if key in ("q", "Q", "0", "b", "B"):
            return
        elif key == "1":
            game_guess_number()
        elif key == "2":
            game_snake()
        elif key == "3":
            game_2048()


# ---------- guess number ----------

def game_guess_number():
    target = random.randint(1, 100)
    tries = 7
    clear()
    width = term_width()
    print_header("GAMES / GUESS THE NUMBER")
    print(box_top(width=width))
    print(box_line(f"i picked 1..100. {WARN}{tries} tries{RESET}.", width))
    print(box_bottom(width))
    for attempt in range(1, tries + 1):
        try:
            raw = input(f"{MUTED}{attempt}/{tries}{RESET} {ACCENT}> {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if not raw:
            return
        try:
            g = int(raw)
        except ValueError:
            print(f"{ERROR}not a number{RESET}"); continue
        if g == target:
            print(f"{SUCCESS}correct: {BOLD}{target}{RESET}"); wait_key(); return
        print(f"{WARN}{'higher' if g < target else 'lower'}{RESET}")
    print(f"{ERROR}out of tries. was {BOLD}{target}{RESET}"); wait_key()


# ---------- snake ----------

def _raw_stdin():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    return fd, old


def _restore_stdin(fd, old):
    termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _read_key(fd, timeout=0.0):
    r, _, _ = select.select([fd], [], [], timeout)
    if not r:
        return None
    data = os.read(fd, 8)
    if not data:
        return None
    if data == b"\x1b[A": return "up"
    if data == b"\x1b[B": return "down"
    if data == b"\x1b[C": return "right"
    if data == b"\x1b[D": return "left"
    if data in (b"w", b"W"): return "up"
    if data in (b"s", b"S"): return "down"
    if data in (b"a", b"A"): return "left"
    if data in (b"d", b"D"): return "right"
    if data in (b"q", b"Q"): return "quit"
    if data in (b"p", b"P"): return "pause"
    if data in (b"r", b"R"): return "restart"
    return None


def _snake_frame(snake, food, W, H, score, speed):
    head = snake[0]
    lines = []
    top = "+" + "-" * (W * 2) + "+"
    lines.append(top)
    body = set(snake[1:])
    for y in range(H):
        row = ["|"]
        for x in range(W):
            if (x, y) == head:
                row.append(f"{ACCENT}██{RESET}")
            elif (x, y) in body:
                row.append(f"{TEXT}▓▓{RESET}")
            elif (x, y) == food:
                row.append(f"{YELLOW}()​{RESET}"[:2] if False else f"{YELLOW}()​{RESET}")
            else:
                row.append("  ")
        row.append("|")
        lines.append("".join(row))
    lines.append(top)
    return lines


def game_snake():
    W, H = 20, 12
    snake = [(W // 2, H // 2), (W // 2 - 1, H // 2), (W // 2 - 2, H // 2)]
    direction = (1, 0)
    pending = direction
    food = _snake_food(snake, W, H)
    score = 0
    speed = 0.16
    paused = False

    fd, old = _raw_stdin()
    # hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        while True:
            # input
            while True:
                key = _read_key(fd, timeout=0)
                if not key:
                    break
                if key == "quit":
                    return
                if key == "pause":
                    paused = not paused
                elif key == "restart":
                    return game_snake()
                elif key == "up" and direction != (0, 1):
                    pending = (0, -1)
                elif key == "down" and direction != (0, -1):
                    pending = (0, 1)
                elif key == "left" and direction != (1, 0):
                    pending = (-1, 0)
                elif key == "right" and direction != (-1, 0):
                    pending = (1, 0)

            if not paused
