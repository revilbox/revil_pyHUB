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

            if not paused:
                direction = pending
                hx, hy = snake[0]
                nx, ny = hx + direction[0], hy + direction[1]
                if nx < 0 or nx >= W or ny < 0 or ny >= H or (nx, ny) in snake:
                    break
                snake.insert(0, (nx, ny))
                if (nx, ny) == food:
                    score += 1
                    food = _snake_food(snake, W, H)
                    if speed > 0.07:
                        speed -= 0.004
                else:
                    snake.pop()

            # render
            buf = []
            buf.append("\033[H\033[2J")
            buf.append(f"{BOLD}{TEXT}revil_pyHUB{RESET} {MUTED}/ SNAKE{RESET}\n\n")
            buf.append(f"{MUTED}score:{RESET} {BOLD}{score}{RESET}   {MUTED}speed:{RESET} {1/speed:.1f}   {MUTED}wasd/arrows  p pause  r restart  q quit{RESET}\n")
            if paused:
                buf.append(f"{WARN}[paused]{RESET}\n")
            else:
                buf.append("\n")
            for ln in _snake_frame(snake, food, W, H, score, speed):
                buf.append(ln + "\n")
            sys.stdout.write("".join(buf))
            sys.stdout.flush()

            # wait tick with polling for input
            deadline = time.time() + speed
            while time.time() < deadline:
                key = _read_key(fd, timeout=0.01)
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

        # game over
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        print(f"\n{ERROR}game over{RESET}. score = {BOLD}{score}{RESET}")
        print(f"{MUTED}r restart  any other key back{RESET}")
        k = _read_key(fd, timeout=30)
        if k == "restart":
            _restore_stdin(fd, old)
            return game_snake()
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        try:
            _restore_stdin(fd, old)
        except Exception:
            pass


def _snake_food(snake, W, H):
    while True:
        f = (random.randint(0, W - 1), random.randint(0, H - 1))
        if f not in snake:
            return f


# ---------- 2048 ----------

def _grid_new():
    g = [[0] * 4 for _ in range(4)]
    _grid_spawn(g); _grid_spawn(g)
    return g


def _grid_spawn(g):
    empty = [(i, j) for i in range(4) for j in range(4) if g[i][j] == 0]
    if not empty:
        return
    i, j = random.choice(empty)
    g[i][j] = 4 if random.random() < 0.1 else 2


def _merge_line(line):
    nums = [x for x in line if x != 0]
    out = []
    i = 0
    gained = 0
    while i < len(nums):
        if i + 1 < len(nums) and nums[i] == nums[i + 1]:
            v = nums[i] * 2
            out.append(v); gained += v; i += 2
        else:
            out.append(nums[i]); i += 1
    while len(out) < 4:
        out.append(0)
    return out, gained


def _grid_move(g, direction):
    moved = False
    gained = 0
    if direction in ("left", "right"):
        for i in range(4):
            row = g[i]
            r = row if direction == "left" else row[::-1]
            merged, s = _merge_line(r)
            if direction == "right":
                merged = merged[::-1]
            gained += s
            if merged != row:
                moved = True
            g[i] = merged
    else:
        for j in range(4):
            col = [g[i][j] for i in range(4)]
            c = col if direction == "up" else col[::-1]
            merged, s = _merge_line(c)
            if direction == "down":
                merged = merged[::-1]
            gained += s
            if merged != col:
                moved = True
            for i in range(4):
                g[i][j] = merged[i]
    return moved, gained


def _grid_win(g):
    return any(v >= 2048 for row in g for v in row)


def _grid_lose(g):
    if any(v == 0 for row in g for v in row):
        return False
    for i in range(4):
        for j in range(4):
            if i < 3 and g[i][j] == g[i + 1][j]:
                return False
            if j < 3 and g[i][j] == g[i][j + 1]:
                return False
    return True


def _2048_color(v):
    if v == 0: return MUTED
    if v <= 4: return TEXT
    if v <= 16: return YELLOW
    if v <= 64: return WARN
    return ACCENT


def _grid_render(g, score):
    width = term_width()
    buf = []
    buf.append("\033[H\033[2J")
    buf.append(f"{BOLD}{TEXT}revil_pyHUB{RESET} {MUTED}/ 2048{RESET}\n\n")
    buf.append(f"{MUTED}score:{RESET} {BOLD}{score}{RESET}   {MUTED}arrows  r restart  q quit{RESET}\n\n")
    sep = "+------+------+------+------+"
    buf.append(sep + "\n")
    for row in g:
        line = "|"
        for v in row:
            if v == 0:
                line += "      |"
            else:
                c = _2048_color(v)
                line += c + BOLD + str(v).center(6) + RESET + "|"
        buf.append(line + "\n")
        buf.append(sep + "\n")
    sys.stdout.write("".join(buf))
    sys.stdout.flush()


def game_2048():
    g = _grid_new()
    score = 0

    fd, old = _raw_stdin()
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    try:
        while True:
            _grid_render(g, score)
            if _grid_win(g):
                sys.stdout.write(f"\n{SUCCESS}2048 reached{RESET}\n")
                sys.stdout.flush()
                _read_key(fd, timeout=30)
                return
            if _grid_lose(g):
                sys.stdout.write(f"\n{ERROR}no moves{RESET}. score={BOLD}{score}{RESET}\n")
                sys.stdout.flush()
                _read_key(fd, timeout=30)
                return

            key = None
            while not key:
                key = _read_key(fd, timeout=0.05)
            if key == "quit":
                return
            if key == "restart":
                g = _grid_new(); score = 0; continue
            d = {"up": "up", "down": "down", "left": "left", "right": "right"}.get(key)
            if d:
                moved, gained = _grid_move(g, d)
                if moved:
                    score += gained
                    _grid_spawn(g)
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        try:
            _restore_stdin(fd, old)
        except Exception:
            pass
