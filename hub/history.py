"""Recent script run history. Stored next to config."""
import json
from pathlib import Path

from .config import CONFIG_DIR

HISTORY_FILE = CONFIG_DIR / "history.json"
MAX_ITEMS = 20


def load() -> list:
    if HISTORY_FILE.exists():
        try:
            data = json.loads(HISTORY_FILE.read_text())
            if isinstance(data, list):
                return data[:MAX_ITEMS]
        except Exception:
            pass
    return []


def add(entry: dict) -> None:
    items = load()
    items.insert(0, entry)
    items = items[:MAX_ITEMS]
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(items, indent=2))


def clear() -> None:
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
