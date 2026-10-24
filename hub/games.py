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
                    else:
                        row += f"{DIM}.{RESET}"
                lines.append(row)
            clear()
            print_header("GAMES / SNAKE")
            for ln in lines:
                print(ln)

            # move
            dx, dy = pending
            direction = pending
            hx, hy = head
            nx, ny = hx + dx, hy + dy
            if nx < 0 or nx >= W or ny < 0 or ny >= H or (nx, ny) in snake:
                print(f"\n{ERROR}game over.{RESET} score = {BOLD}{score}{RESET}")
                wait_key()
                return
            new_head = (nx, ny)
            snake.insert(0, new_head)
            if new_head == food:
                score += 1
                food = _snake_new_food(snake, W, H)
                if tick > 0.05:
                    tick -= 0.005
            else:
                snake.pop()

        key = _read_key_nonblocking(timeout=0.01)
        if key:
            if key in ("q", "Q"):
                return
            if key == readchar.key.UP and direction != (0, 1):
                pending = (0, -1)
            elif key == readchar.key.DOWN and direction != (0, -1):
                pending = (0, 1)
            elif key == readchar.key.LEFT and direction != (1, 0):
                pending = (-1, 0)
            elif key == readchar.key.RIGHT and direction != (-1, 0):
                pending = (1, 0)


def _snake_new_food(snake, W, H):
    while True:
        f = (random.randint(0, W - 1), random.randint(0, H - 1))
        if f not in snake:
            return f


# ---------- 3. 2048 ----------

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


def _grid_move(g, direction):
    """direction: 'up','down','left','right'. Returns (moved, gained)."""
    gained = 0
    moved = False
    for _ in range(4):
        pass
    if direction in ("left", "right"):
        rows = [[g[i][j] for j in range(4)] for i in range(4)]
        new_rows = []
        for row in rows:
            r = row if direction == "left" else row[::-1]
            merged, s = _merge_line(r)
            gained += s
            if direction == "right":
                merged = merged[::-1]
            new_rows.append(merged)
            if merged != row:
                moved = True
        for i in range(4):
            for j in range(4):
                g[i][j] = new_rows[i][j]
    else:
        cols = [[g[i][j] for i in range(4)] for j in range(4)]
        new_cols = []
        for col in cols:
            c = col if direction == "up" else col[::-1]
            merged, s = _merge_line(c)
            gained += s
            if direction == "down":
                merged = merged[::-1]
            new_cols.append(merged)
            if merged != col:
                moved = True
        for j in range(4):
            for i in range(4):
                g[i][j] = new_cols[j][i]
    return moved, gained


def _merge_line(line):
    nums = [x for x in line if x != 0]
    out = []
    i = 0
    gained = 0
    while i < len(nums):
        if i + 1 < len(nums) and nums[i] == nums[i + 1]:
            v = nums[i] * 2
            out.append(v)
            gained += v
            i += 2
        else:
            out.append(nums[i])
            i += 1
    while len(out) < 4:
        out.append(0)
    return out, gained


def _grid_check_win(g):
    return any(v >= 2048 for row in g for v in row)


def _grid_check_lose(g):
    if any(v == 0 for row in g for v in row):
        return False
    for i in range(4):
        for j in range(4):
            if i < 3 and g[i][j] == g[i + 1][j]:
                return False
            if j < 3 and g[i][j] == g[i][j + 1]:
                return False
    return True


def _grid_render(g, score):
    clear()
    print_header("GAMES / 2048")
    print(f"{MUTED}score:{RESET} {BOLD}{score}{RESET}    {MUTED}arrows move, Q quit, R restart{RESET}")
    print()
    sep = "+------+------+------+------+"
    print(sep)
    for row in g:
        cells = []
        for v in row:
            if v == 0:
                s = " " * 6
                cells.append(f"|{DIM}{s}{RESET}")
            else:
                color = _2048_color(v)
                s = str(v).center(6)
                cells.append(f"|{color}{BOLD}{s}{RESET}")
        print("".join(cells) + "|")
        print(sep)


def _2048_color(v):
    if v == 2: return CYAN
    if v == 4: return GREEN
    if v == 8: return YELLOW
    if v == 16: return MAGENTA
    if v == 32: return RED
    if v == 64: return BLUE
    return ACCENT2


def game_2048():
    g = _grid_new()
    score = 0
    while True:
        _grid_render(g, score)
        if _grid_check_win(g):
            print(f"\n{SUCCESS}you reached 2048!{RESET}")
            wait_key()
            return
        if _grid_check_lose(g):
            print(f"\n{ERROR}no moves left.{RESET} score = {BOLD}{score}{RESET}")
            wait_key()
            return

        key = readchar.readkey()
        if key in ("q", "Q"):
            return
        if key in ("r", "R"):
            g = _grid_new(); score = 0; continue

        direction = None
        if key == readchar.key.UP:
            direction = "up"
        elif key == readchar.key.DOWN:
            direction = "down"
        elif key == readchar.key.LEFT:
            direction = "left"
        elif key == readchar.key.RIGHT:
            direction = "right"

        if direction:
            moved, gained = _grid_move(g, direction)
            if moved:
                score += gained
                _grid_spawn(g)
