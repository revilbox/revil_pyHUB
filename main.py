#!/usr/bin/env python3
"""revil_pyHUB entry point."""
import sys

try:
    import readchar  # noqa: F401
except ImportError:
    print("Missing dependency. Run: pip install -r requirements.txt")
    sys.exit(1)

from hub.menu import main_menu
from hub.ui import clear
from hub import config
from hub.git_ops import git_pull
from hub.ui import REPO_ROOT


def main():
    cfg = config.load()
    if cfg.get("auto_update"):
        print("Auto-updating...")
        msg = git_pull(REPO_ROOT)
        print(msg)
    try:
        result = main_menu()
    except KeyboardInterrupt:
        result = "exit"
    clear()
    if result == "exit":
        print("Bye.")


if __name__ == "__main__":
    main()
