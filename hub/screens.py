"""Run, settings, update, about, envs, history screens."""
import sys
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, print_header,
    box_top, box_mid, box_sep, box_bottom, pad_ansi, strip_ansi,
    ACCENT, ACCENT2, BOLD, DIM, MUTED, RESET, V,
    GREEN, RED, YELLOW, CYAN, SUCCESS, ERROR, WARN,
)
from .runner import run_python
from .git_ops import git_pull
from .ui import REPO_ROOT
from . import config, history, envs, __version__


def _wrap(text: str) -> str:
    return f"{ACCENT}{V}{RESET} {pad_ansi(text, term_width() - 4)} {ACCENT}{V}{RESET}"


def _screen(title: str, lines: list[str]):
    clear()
    print_header(title)
    print(box_top())
    for ln in lines:
        print(_wrap(ln))
    print(box_bottom())


# ---------- run ----------

def screen_run():
    cfg = config.load()
    clear()
    print_header("RUN PYTHON SCRIPT")
    print(box_top())
    print(_wrap("Path to .py file (empty to cancel):"))
    print(box_bottom())
    path_str = input(f"{ACCENT}> {RESET}").strip()
    if not path_str:
        return
    p = Path(path_str).expanduser()
    if not p.is_file() or p.suffix != ".py":
        print(f"{ERROR}Not a valid .py file: {p}{RESET}")
        wait_key()
        return
    print("Arguments (empty for none):")
    args = input(f"{ACCENT}> {RESET}").strip()
    run_python(p, args=args, python_bin=cfg["python_bin"])


# ---------- settings ----------

def _settings_lines(cfg):
    return [
        f"{ACCENT}[1]{RESET} start_dir    {MUTED}={RESET} {cfg['start_dir']}",
        f"{ACCENT}[2]{RESET} auto_update  {MUTED}={RESET} {cfg['auto_update']}",
        f"{ACCENT}[3]{RESET} editor       {MUTED}={RESET} {cfg['editor']}",
        f"{ACCENT}[4]{RESET} python_bin   {MUTED}={RESET} {cfg['python_bin'] or '(auto)'}",
        f"{ACCENT}[5]{RESET} active_venv  {MUTED}={RESET} {cfg['active_venv'] or '(none)'}",
        f"{MUTED}[9]{RESET} {MUTED}clear active venv{RESET}",
        f"{MUTED}B back  Q quit{RESET}",
    ]


def screen_settings():
    cfg = config.load()
    while True:
        clear()
        print_header("SETTINGS")
        print(box_top())
        for ln in _settings_lines(cfg):
            print(_wrap(ln))
        print(box_sep())
        print(_wrap(f"{MUTED}config: {config.CONFIG_FILE}{RESET}"))
        print(box_bottom())

        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            config.save(cfg)
            return
        elif key == "1":
            clear(); print("start_dir (expanded with ~):")
            v = input("> ").strip()
            if v:
                cfg["start_dir"] = v; config.save(cfg)
        elif key == "2":
            cfg["auto_update"] = not cfg["auto_update"]; config.save(cfg)
        elif key == "3":
            clear(); print("editor (nano, vim, micro):")
            v = input("> ").strip()
            if v:
                cfg["editor"] = v; config.save(cfg)
        elif key == "4":
            clear(); print("python_bin (path, empty = auto):")
            v = input("> ").strip()
            cfg["python_bin"] = v; config.save(cfg)
        elif key == "5":
            clear(); print("active_venv (path, empty = unset):")
            v = input("> ").strip()
            cfg["active_venv"] = v; config.save(cfg)
        elif key == "9":
            cfg["active_venv"] = ""; config.save(cfg)


# ---------- update ----------

def screen_update():
    clear()
    print_header("UPDATE FROM GIT")
    print(box_top())
    print(_wrap(f"{MUTED}running: git pull --ff-only{RESET}"))
    print(_wrap(""))
    for line in git_pull(REPO_ROOT).splitlines():
        print(_wrap(line))
    print(box_bottom())
    wait_key()


# ---------- about ----------

def screen_about():
    clear()
    print_header("ABOUT")
    print(box_top())
    for ln in [
        f"{BOLD}revil_pyHUB{RESET} {MUTED}terminal hub for python on termux{RESET}",
        "",
        f"version    {MUTED}={RESET} {__version__}",
        f"repo root  {MUTED}={RESET} {REPO_ROOT}",
        f"python     {MUTED}={RESET} {sys.version.split()[0]}",
        f"executable {MUTED}={RESET} {sys.executable}",
    ]:
        print(_wrap(ln))
    print(box_bottom())
    wait_key()


# ---------- envs ----------

def screen_envs():
    cfg = config.load()
    root = Path(cfg["start_dir"]).expanduser()
    if not root.is_dir():
        root = Path.home()
    index = 0

    while True:
        found = envs.find_venvs(root)
        if not found:
            index = 0
        elif index >= len(found):
            index = len(found) - 1

        clear()
        print_header("ENVIRONMENTS (venv)")
        print(box_top())
        print(_wrap(f"{MUTED}root:{RESET} {root}"))
        print(_wrap(f"{MUTED}active:{RESET} {cfg.get('active_venv') or '(none)'}"))
        print(box_sep())
        if not found:
            print(_wrap(f"{MUTED}(no venv found){RESET}"))
        else:
            for i, v in enumerate(found):
                mark = f"{ACCENT}>{RESET}" if i == index else " "
                star = f"{GREEN}*{RESET}" if str(v) == cfg.get("active_venv") else " "
                print(_wrap(f"{mark} {star} {v}"))
        print(box_sep())
        print(_wrap(f"{MUTED}ENTER activate  C create  D delete  B back{RESET}"))
        print(box_bottom())

        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            return
        elif key == readchar.key.UP:
            index = max(0, index - 1)
        elif key == readchar.key.DOWN:
            index = min(len(found) - 1, index + 1)
        elif key in ("\r", "\n"):
            if found:
                cfg["active_venv"] = str(found[index]); config.save(cfg)
                clear(); print(f"{SUCCESS}Activated: {found[index]}{RESET}")
                wait_key()
        elif key in ("c", "C"):
            clear()
            print(f"Create venv at (empty to cancel, example {root}/.venv):")
            p = input("> ").strip()
            if p:
                target = Path(p).expanduser()
                ok, msg = envs.create_venv(target)
                clear()
                print((SUCCESS if ok else ERROR) + msg + RESET)
                if ok:
                    cfg["active_venv"] = str(target.resolve()); config.save(cfg)
                    print(f"{SUCCESS}Activated{RESET}")
                wait_key()
        elif key in ("d", "D"):
            if found:
                target = found[index]
                clear()
                print(f"{ERROR}Delete venv '{target}'? y/N{RESET}")
                if readchar.readkey().lower() == "y":
                    ok, msg = envs.remove_venv(target)
                    if ok and cfg.get("active_venv") == str(target):
                        cfg["active_venv"] = ""; config.save(cfg)
                    clear()
                    print((SUCCESS if ok else ERROR) + msg + RESET)
                    wait_key()


# ---------- history ----------

def screen_history():
    index = 0
    while True:
        items = history.load()
        if not items:
            index = 0
        elif index >= len(items):
            index = len(items) - 1

        clear()
        print_header("RUN HISTORY")
        print(box_top())
        if not items:
            print(_wrap(f"{MUTED}(empty){RESET}"))
        else:
            for i, e in enumerate(items):
                mark = f"{ACCENT}>{RESET}" if i == index else " "
                path = Path(e.get("path", "?")).name
                ts = e.get("ts", "?")
                code = e.get("exit", "?")
                color = SUCCESS if code == 0 else ERROR
                line = f"{mark} {MUTED}{ts}{RESET}  {color}{path}{RESET}  {MUTED}exit={code}{RESET}  {MUTED}args={e.get('args','')!r}{RESET}"
                print(_wrap(line))
        print(box_sep())
        print(_wrap(f"{MUTED}ENTER rerun  C clear  B back{RESET}"))
        print(box_bottom())

        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            return
        elif key == readchar.key.UP:
            index = max(0, index - 1)
        elif key == readchar.key.DOWN:
            index = min(len(items) - 1, index + 1)
        elif key in ("\r", "\n"):
            if items:
                e = items[index]
                p = Path(e.get("path", ""))
                if p.is_file():
                    run_python(p, args=e.get("args", ""), python_bin=e.get("python", ""))
                else:
                    clear(); print(f"{ERROR}Missing file: {p}{RESET}")
                    wait_key()
        elif key in ("c", "C"):
            clear()
            print(f"{WARN}Clear all history? y/N{RESET}")
            if readchar.readkey().lower() == "y":
                history.clear()
