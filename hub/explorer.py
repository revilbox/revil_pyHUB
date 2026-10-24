"""File explorer with preview and file ops."""
import subprocess
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, print_status_bar,
    CYAN, GREEN, YELLOW, RED, BOLD, DIM, RESET, REPO_ROOT,
)
from .runner import run_python
from .git_ops import git_pull
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
        left_w = 34 if two_pane else width
        preview_w = max(10, width - left_w - 3) if two_pane else 0

        clear()
        print(f"{BOLD}revil_pyHUB{RESET} / file explorer")
        print(f"{DIM}Path: {cwd}{RESET}")
        if cfg.get("active_venv"):
            print(f"{DIM}venv: {cfg['active_venv']}{RESET}")
        print("=" * width)

        prev = _preview(items[index]) if items else ""
        prev_lines = [ln[:preview_w] for ln in prev.splitlines()[:20]] if two_pane else []

        rows = len(items) if two_pane else len(items)
        rows = max(rows, len(prev_lines)) if two_pane else rows

        for i in range(rows):
            left = ""
            if i < len(items):
                item = items[i]
                name = item.name or str(item)
                if item.is_dir():
                    name += "/"
                marker = ">" if i == index else " "
                color = (CYAN if item.is_dir() else GREEN) if i == index else RESET
                left = f"{marker} {name}"
                if len(left) > left_w:
                    left = left[: left_w - 1] + "~"
                left = color + left + RESET

            if two_pane:
                right = prev_lines[i] if i < len(prev_lines) else ""
                plain_left = left.replace(CYAN, "").replace(GREEN, "").replace(RESET, "")
                pad = " " * max(0, left_w - len(plain_left))
                print(left + pad + " | " + right)
            else:
                print(left)

        print("=" * width)
        hint = "UP/DOWN enter E edit N new M mkdir F2 rename DEL del B back U update ^L goto Q quit"
        print(f"{DIM}{hint[:width]}{RESET}")
        print_status_bar(
            f"items: {len(items)}  selected: {items[index].name if items else '-'}",
            message,
        )
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
                print(_preview(target))
                wait_key()
        elif key in ("e", "E"):
            if items and items[index].is_file():
                target = items[index]
                editor = cfg["editor"]
                clear()
                print(f"Opening {target} in {editor}...")
                try:
                    subprocess.run([editor, str(target)])
                except FileNotFoundError:
                    print(f"Editor not found: {editor}")
                    wait_key()
        elif key in ("b", "B"):
            return
        elif key in ("u", "U"):
            message = git_pull(REPO_ROOT)[:width]
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
                    message = "File already exists"
                else:
                    try:
                        p.write_text("")
                        message = f"Created {name}"
                    except Exception as e:
                        message = f"Failed: {e}"
        elif key in ("m", "M"):
            clear()
            print("New directory name (empty to cancel):")
            name = input("> ").strip()
            if name:
                p = cwd / name
                try:
                    p.mkdir(exist_ok=False)
                    message = f"Created {name}/"
                except FileExistsError:
                    message = "Directory already exists"
                except Exception as e:
                    message = f"Failed: {e}"
        elif key == getattr(readchar.key, "F2", "\x1bOQ"):
            if items and items[index].name != "..":
                target = items[index]
                clear()
                print(f"Rename '{target.name}' to (empty to cancel):")
                new_name = input("> ").strip()
                if new_name:
                    try:
                        target.rename(target.parent / new_name)
                        message = f"Renamed to {new_name}"
                    except Exception as e:
                        message = f"Failed: {e}"
        elif key == readchar.key.DELETE or key == "\x1b[3~":
            if items and items[index].name != "..":
                target = items[index]
                clear()
                print(f"{RED}Delete '{target.name}'? y/N{RESET}")
                confirm = readchar.readkey().lower()
                if confirm == "y":
                    try:
                        if target.is_dir():
                            import shutil
                            shutil.rmtree(target)
                        else:
                            target.unlink()
                        message = f"Deleted {target.name}"
                        index = max(0, index - 1)
                    except Exception as e:
                        message = f"Failed: {e}"
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
                    message = "Not a directory"
