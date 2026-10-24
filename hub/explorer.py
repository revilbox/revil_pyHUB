"""File explorer with preview and file ops."""
import shutil
import subprocess
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, print_header,
    box_top, box_mid, box_sep, box_bottom, pad_ansi, strip_ansi,
    ACCENT, ACCENT2, BOLD, DIM, MUTED, RESET, V,
    CYAN, GREEN, YELLOW, RED, SUCCESS, ERROR, WARN,
)
from .runner import run_python
from .git_ops import git_pull
from .ui import REPO_ROOT
from . import config


def _list_dir(path: Path):
    items = []
    try:
        for entry in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            items.append(entry)
    except PermissionError:
        pass
    return items


def _preview(path: Path) -> str:
    try:
        if path.is_dir():
            return f"<directory> {path}"
        size = path.stat().st_size
        if size > 200_000:
            return f"<large file> {size} bytes"
        return path.read_text(errors="replace")[:4000]
    except Exception as e:
        return f"<cannot read: {e}>"


def _fmt_size(n: int) -> str:
    for unit in ("B", "K", "M", "G"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}T"


def _item_line(item: Path, selected: bool, left_w: int) -> str:
    name = item.name or str(item)
    if item.is_dir():
        name += "/"
    marker = ">" if selected else " "
    if selected:
        color = ACCENT if item.is_dir() else GREEN
        return color + BOLD + f"{marker} {name}"[: left_w].ljust(left_w) + RESET
    base = f"  {name}"
    if len(base) > left_w:
        base = base[: left_w - 1] + "~"
    return base.ljust(left_w)


def screen_explorer():
    cfg = config.load()
    cwd = Path(cfg["start_dir"]).expanduser()
    if not cwd.is_dir():
        cwd = Path.home()
    index = 0
    message = ""

    while True:
        items = ([Path("..")] + _list_dir(cwd)) if cwd != cwd.parent else _list_dir(cwd)
        if not items:
            index = 0
        elif index >= len(items):
            index = len(items) - 1

        width = term_width()
        two_pane = width >= 70
        left_w = 34 if two_pane else width - 2
        preview_w = max(10, width - left_w - 5) if two_pane else 0

        clear()
        print_header("FILE EXPLORER")
        path_line = f"{MUTED}path:{RESET} {cwd}"
        if cfg.get("active_venv"):
            path_line += f"  {MUTED}venv:{RESET} {ACCENT2}{Path(cfg['active_venv']).name}{RESET}"
        print(box_mid(path_line, width))
        print(box_sep(width))

        prev = _preview(items[index]) if items else ""
        prev_lines = [ln[:preview_w] for ln in prev.splitlines()[:20]] if two_pane else []

        rows = max(len(items), len(prev_lines)) if two_pane else len(items)
        for i in range(rows):
            if i < len(items):
                item = items[i]
                left = _item_line(item, i == index, left_w)
                if item.is_file() and i == index:
                    try:
                        size_str = f"{MUTED}{_fmt_size(item.stat().st_size)}{RESET}"
                    except Exception:
                        size_str = ""
                else:
                    size_str = ""
            else:
                left = " " * left_w
                size_str = ""

            if two_pane:
                right = prev_lines[i] if i < len(prev_lines) else ""
                print(ACCENT + V + RESET + " " + left + " " + ACCENT + V + RESET + " " + right.ljust(preview_w) + RESET)
            else:
                print(ACCENT + V + RESET + " " + left + " " + ACCENT + V + RESET)

        print(box_sep(width))
        keys_hint = (
            f"{ACCENT}ENTER{RESET} open  "
            f"{ACCENT}E{RESET} edit  "
            f"{ACCENT}N{RESET} file  "
            f"{ACCENT}M{RESET} dir  "
            f"{ACCENT}F2{RESET} rename  "
            f"{ACCENT}DEL{RESET} del  "
            f"{ACCENT}^L{RESET} goto  "
            f"{ACCENT}B{RESET} back"
        )
        print(box_mid(keys_hint, width))
        total = len(items)
        sel = items[index].name if items else "-"
        status_left = f"{MUTED}items:{RESET} {total}  {MUTED}selected:{RESET} {sel}"
        status_right = message if message else f"{MUTED}U update  Q quit{RESET}"
        print_status_bar_custom(status_left, status_right, width)
        message = ""

        key = readchar.readkey()

        if key == readchar.key.UP:
            index = max(0, index - 1)
        elif key == readchar.key.DOWN:
            index = min(len(items) - 1, index + 1)
        elif key in ("\r", "\n"):
            if not items:
                continue
            target = items[index]
            if target.name == "..":
                cwd = cwd.parent
                index = 0
            elif target.is_dir():
                cwd = target
                index = 0
            elif target.suffix == ".py":
                run_python(target, python_bin=cfg["python_bin"])
            else:
                clear()
                print_header("PREVIEW")
                print(_preview(target))
                wait_key()
        elif key in ("e", "E"):
            if items and items[index].is_file():
                target = items[index]
                editor = cfg["editor"]
                clear()
                print(f"{MUTED}Opening {target} in {editor}...{RESET}")
                try:
                    subprocess.run([editor, str(target)])
                except FileNotFoundError:
                    print(f"{ERROR}Editor not found: {editor}{RESET}")
                    wait_key()
        elif key in ("b", "B"):
            return
        elif key in ("u", "U"):
            message = f"{SUCCESS}{git_pull(REPO_ROOT)}{RESET}"
            wait_key()
        elif key in ("q", "Q"):
            return
        elif key in ("n", "N"):
            clear()
            print("New file name (empty to cancel):")
            name = input("> ").strip()
            if name:
                p = cwd / name
                if p.exists():
                    message = f"{ERROR}exists{RESET}"
                else:
                    try:
                        p.write_text("")
                        message = f"{SUCCESS}created {name}{RESET}"
                    except Exception as e:
                        message = f"{ERROR}{e}{RESET}"
        elif key in ("m", "M"):
            clear()
            print("New directory name (empty to cancel):")
            name = input("> ").strip()
            if name:
                p = cwd / name
                try:
                    p.mkdir(exist_ok=False)
                    message = f"{SUCCESS}created {name}/{RESET}"
                except FileExistsError:
                    message = f"{ERROR}exists{RESET}"
                except Exception as e:
                    message = f"{ERROR}{e}{RESET}"
        elif key == getattr(readchar.key, "F2", "\x1bOQ"):
            if items and items[index].name != "..":
                target = items[index]
                clear()
                print(f"Rename '{target.name}' to (empty to cancel):")
                new_name = input("> ").strip()
                if new_name:
                    try:
                        target.rename(target.parent / new_name)
                        message = f"{SUCCESS}renamed{RESET}"
                    except Exception as e:
                        message = f"{ERROR}{e}{RESET}"
        elif key == readchar.key.DELETE or key == "\x1b[3~":
            if items and items[index].name != "..":
                target = items[index]
                clear()
                print(f"{ERROR}Delete '{target.name}'? y/N{RESET}")
                if readchar.readkey().lower() == "y":
                    try:
                        if target.is_dir():
                            shutil.rmtree(target)
                        else:
                            target.unlink()
                        message = f"{SUCCESS}deleted{RESET}"
                        index = max(0, index - 1)
                    except Exception as e:
                        message = f"{ERROR}{e}{RESET}"
        elif key == "\x0c":
            clear()
            print("Go to path (empty to cancel):")
            p = input("> ").strip()
            if p:
                t = Path(p).expanduser()
                if t.is_dir():
                    cwd = t
                    index = 0
                else:
                    message = f"{ERROR}not a directory{RESET}"


def print_status_bar_custom(left: str, right: str, width: int):
    space = max(0, width - len(strip_ansi(left)) - len(strip_ansi(right)) - 4)
    print(ACCENT + V + RESET + " " + left + " " * space + right + " " + ACCENT + V + RESET)
    print(box_bottom(width))
