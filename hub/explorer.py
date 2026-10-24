"""File explorer - strict, monochrome."""
import shutil
import subprocess
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, print_header,
    box_top, box_line, box_sep, box_bottom, fit, vlen,
    ACCENT, TEXT, MUTED, RESET, BOLD,
    SUCCESS, ERROR, V,
)
from .runner import run_python
from .git_ops import git_pull
from .ui import REPO_ROOT
from . import config

INVERSE = "\033[7m"


def _list_dir(path: Path):
    try:
        return sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return []


def _preview(path: Path) -> str:
    try:
        if path.is_dir():
            return f"<directory> {path}"
        size = path.stat().st_size
        if size > 200_000:
            return f"<large file> {size} bytes"
        return path.read_text(errors="replace")
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
        height = 20
        two_pane = width >= 72

        if two_pane:
            left_inner = 32
            right_inner = width - 2 - left_inner - 3
        else:
            left_inner = width - 2
            right_inner = 0

        win = height
        start = max(0, index - win // 2)
        end = min(len(items), start + win)
        if end - start < win and start > 0:
            start = max(0, end - win)

        visible = items[start:end]

        sel_path = items[index] if items else None
        preview_lines = []
        if sel_path:
            preview_lines = _preview(sel_path).splitlines()[:win]

        clear()
        print_header("FILE EXPLORER")
        print(box_top(width=width))

        venv_note = ""
        if cfg.get("active_venv"):
            venv_note = f"  {MUTED}venv:{RESET} {Path(cfg['active_venv']).name}"
        print(box_line(f"{MUTED}path:{RESET} {cwd}{venv_note}", width))
        print(box_sep(width))

        if not items:
            print(box_line(f"{MUTED}(empty){RESET}", width))
        else:
            for i in range(len(visible)):
                abs_i = start + i
                item = items[abs_i]
                name = item.name or str(item)
                if item.is_dir():
                    name += "/"
                if abs_i == index:
                    # inverse video for selection - strict, monochrome
                    left = fit(f"{INVERSE} {name}{RESET}", left_inner)
                else:
                    left = fit(f"  {name}", left_inner)

                if two_pane:
                    pv = preview_lines[i] if i < len(preview_lines) else ""
                    pv = fit(f"{MUTED}{pv}{RESET}", right_inner)
                    print(MUTED + V + RESET + " " + left + " " + MUTED + V + RESET + " " + pv + " " + MUTED + V + RESET)
                else:
                    print(MUTED + V + RESET + " " + left + " " + MUTED + V + RESET)

        for _ in range(win - len(visible)):
            if two_pane:
                print(MUTED + V + RESET + " " + " " * left_inner + " " + MUTED + V + RESET + " " + " " * right_inner + " " + MUTED + V + RESET)
            else:
                print(MUTED + V + RESET + " " + " " * left_inner + " " + MUTED + V + RESET)

        print(box_sep(width))
        print(box_line(
            f"{MUTED}enter{RESET} open  "
            f"{MUTED}e{RESET} edit  "
            f"{MUTED}n{RESET} file  "
            f"{MUTED}m{RESET} dir  "
            f"{MUTED}f2{RESET} rename  "
            f"{MUTED}del{RESET} delete  "
            f"{MUTED}^l{RESET} goto  "
            f"{MUTED}b{RESET} back",
            width,
        ))
        sel = items[index].name if items else "-"
        left_status = message if message else f"{MUTED}{index + 1}/{len(items)}  {sel[:24]}{RESET}"
        right_status = f"{MUTED}u update  q quit{RESET}"
        print(box_line(f"{left_status}    {right_status}", width))
        print(box_bottom(width))
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
                print(box_top())
                for ln in _preview(target).splitlines()[:40]:
                    print(box_line(ln))
                print(box_bottom())
                wait_key()
        elif key in ("e", "E"):
            if items and items[index].is_file():
                target = items[index]
                clear()
                print(f"{MUTED}opening in {cfg['editor']}...{RESET}")
                try:
                    subprocess.run([cfg["editor"], str(target)])
                except FileNotFoundError:
                    print(f"{ERROR}editor not found: {cfg['editor']}{RESET}")
                    wait_key()
        elif key in ("b", "B"):
            return
        elif key in ("u", "U"):
            message = f"{MUTED}{git_pull(REPO_ROOT)[:60]}{RESET}"
            wait_key()
        elif key in ("q", "Q"):
            return
        elif key in ("n", "N"):
            clear()
            print("new file name (empty to cancel):")
            name = input("> ").strip()
            if name:
                p = cwd / name
                if p.exists():
                    message = f"{ERROR}exists{RESET}"
                else:
                    try:
                        p.write_text("")
                        message = f"{MUTED}created {name}{RESET}"
                    except Exception as e:
                        message = f"{ERROR}{e}{RESET}"
        elif key in ("m", "M"):
            clear()
            print("new directory name (empty to cancel):")
            name = input("> ").strip()
            if name:
                p = cwd / name
                try:
                    p.mkdir(exist_ok=False)
                    message = f"{MUTED}created {name}/{RESET}"
                except FileExistsError:
                    message = f"{ERROR}exists{RESET}"
                except Exception as e:
                    message = f"{ERROR}{e}{RESET}"
        elif key == getattr(readchar.key, "F2", "\x1bOQ"):
            if items and items[index].name != "..":
                target = items[index]
                clear()
                print(f"rename '{target.name}' to (empty to cancel):")
                new_name = input("> ").strip()
                if new_name:
                    try:
                        target.rename(target.parent / new_name)
                        message = f"{MUTED}renamed{RESET}"
                    except Exception as e:
                        message = f"{ERROR}{e}{RESET}"
        elif key == readchar.key.DELETE or key == "\x1b[3~":
            if items and items[index].name != "..":
                target = items[index]
                clear()
                print(f"delete '{target.name}'? y/N")
                if readchar.readkey().lower() == "y":
                    try:
                        if target.is_dir():
                            shutil.rmtree(target)
                        else:
                            target.unlink()
                        message = f"{MUTED}deleted{RESET}"
                        index = max(0, index - 1)
                    except Exception as e:
                        message = f"{ERROR}{e}{RESET}"
        elif key == "\x0c":
            clear()
            print("go to path (empty to cancel):")
            p = input("> ").strip()
            if p:
                t = Path(p).expanduser()
                if t.is_dir():
                    cwd = t
                    index = 0
                else:
                    message = f"{ERROR}not a directory{RESET}"
