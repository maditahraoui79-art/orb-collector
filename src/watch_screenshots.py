"""Watch a folder for new screenshots and read the Orb count with OCR.

This tool only reads screenshots. It does not click, collect, navigate, or
perform unattended actions in Discord.
"""

import sys
import time
from pathlib import Path

from orb_reader import read_from_file
from config import SCREENSHOTS_DIR

SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}


def scan_once(seen: set[Path]) -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(
        (p for p in SCREENSHOTS_DIR.iterdir() if p.suffix.lower() in SUPPORTED),
        key=lambda p: p.stat().st_mtime,
    )

    for path in files:
        if path in seen:
            continue

        try:
            value = read_from_file(path)
        except Exception as exc:
            print(f"[{path.name}] OCR error: {exc}")
            seen.add(path)
            continue

        print(f"[{path.name}] Orbs: {value if value is not None else 'not detected'}")
        seen.add(path)


def main() -> None:
    seen: set[Path] = set()
    previous: int | None = None

    print("Orb screenshot watcher started.")
    print(f"Watching: {SCREENSHOTS_DIR.resolve()}")
    print("Add screenshots to that folder. Press Ctrl+C to stop.")

    try:
        while True:
            before = len(seen)
            scan_once(seen)
            if len(seen) != before:
                newest = max(seen, key=lambda p: p.stat().st_mtime)
                current = read_from_file(newest)
                if current is not None and previous is not None:
                    delta = current - previous
                    if delta:
                        print(f"Change: {previous} -> {current} ({delta:+d})")
                if current is not None:
                    previous = current
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nWatcher stopped.")


if __name__ == "__main__":
    main()
