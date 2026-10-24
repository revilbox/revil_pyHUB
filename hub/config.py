"""Persistent settings in ~/.config/revil_pyhub/config.json"""
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "revil_pyhub"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "start_dir": str(Path.home()),
    "auto_update": False,
    "editor": "nano",
    "python_bin": "",
}


def load() -> dict:
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            merged = dict(DEFAULTS)
            merged.update({k: v for k, v in data.items() if k in DEFAULTS})
            return merged
        except Exception:
            pass
    return dict(DEFAULTS)


def save(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
