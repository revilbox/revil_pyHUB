"""Run python scripts with args and optional custom interpreter."""
import shlex
import subprocess
import sys
from pathlib import Path

from .ui import clear, wait_key, DIM, RESET


def run_python(path: Path, args: str = "", python_bin: str = ""):
    clear()
    py = python_bin or sys.executable
    argv = [py, str(path)] + (shlex.split(args) if args.strip() else [])
    print(f"{DIM}Running: {' '.join(argv)}{RESET}")
    print("-" * 46)
    try:
        subprocess.run(argv, cwd=path.parent)
    except KeyboardInterrupt:
        pass
    except FileNotFoundError:
        print(f"Interpreter not found: {py}")
    wait_key("Finished. Press any key to return.")
