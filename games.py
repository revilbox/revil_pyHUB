"""Games: guess number, snake, 2048."""
import os
import random
import sys
import time
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, print_header,
    box_top, box_mid, box_sep, box_bottom, pad_ansi,
    ACCENT, ACCENT2, BOLD, DIM, MUTED, RESET, V,
    GREEN, RED, YELLOW, CYAN, MAGENTA, BLUE, SUCCESS, ERROR, WARN,
)

GAMES = [
    ("1", "Guess the number", "guess 1..100"),
    ("2", "Snake", "arrows to move"),
    ("3", "2048", "arrows to merge"),
    ("0", "Back", ""),
]


def screen_games():
    while True:
        clear()
        print_header("GAMES")
        print(box_top())
        for key, label, desc in GAMES:
            line = f"{ACCENT}[{key}]{RESET} {BOLD}{label}{RESET}" + (f"  {MUTED}{desc}{RESET}" if desc else "")
            print(ACCENT + V + RESET + " " + pad_ansi(line, term_width() - 4) + " " + ACCENT + V + RESET)
        print(box_bottom())
        key = readchar.readkey()
        if key in ("q", "Q", "0", "b", "B"):
            return
        elif key == "1":
            game_guess_number()
        elif key == "2":
            game_snake()
        elif key == "3":
            game_2048()


# ---------- 1. guess number ----------

def game_guess_number():
    target = random.randint(1, 100)
    attempts = 7
    clear()
    print_header("GAMES / GUESS THE NUMBER")
    print(box_top())
    print(ACCENT + V + RESET + " " + f"I picked a number 1..100. {YELLOW}7 tries{RESET}." + " " * (term_width() - 40) + ACCENT + V + RESET)
    print(box_bottom())

    for attempt in range(1, attempts + 1):
        prompt = f"{MUTED}try {attempt}/{attempts}{RESET} {ACCENT}> {RESET}"
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return
        if not raw:
            return
        try:
            guess = int(raw)
        except ValueError:
            print(f"{ERROR}not a number{RESET}")
            continue
        if guess == target:
            print(f"{SUCCESS}correct!{RESET} the number was {BOLD}{target}{RESET}")
            wait_key()
            return
        elif guess < target:
            print(f"{YELLOW}higher{RESET}")
        else:
            print(f"{YELLOW}lower{RESET}")

    print(f"{ERROR}out of tries.{RESET} the number was {BOLD}{target}{RESET}")
    wait_key()


# ---------- 2. snake ----------

def _read_key_nonblocking(timeout=0.0):
    """readchar blocks; we approximate snake tick by polling with timeout via select."""
    import select
    try:
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if r:
            return readchar.readkey()
    except Exception:
        pass
    return None


def game_snake():
    W, H = 30, 14
    snake = [(W // 2, H // 2)]
    direction = (1, 0)
    pending = direction
    food = _snake_new_food(snake, W, H)
    score = 0
    tick = 0.15
    last = time.time()

    while True:
        # input
        if time.time() - last >= tick:
            last = time.time()
            # draw
            lines = []
            lines.append(f"{MUTED}score:{RESET} {BOLD}{score}{RESET}   {MUTED}arrows move, Q quit{RESET}")
            lines.append("")
            head = snake[0]
            for y in range(H):
                row = ""
                for x in range(W):
                    if (x, y) == head:
                        row += f"{GREEN}{BOLD}O{RESET}"
                    elif (x, y) in snake:
                        row += f"{GREEN}o{RESET}"
                    elif (x, y) == food:
                        row += f"{RED}*{RESET}"
                   
