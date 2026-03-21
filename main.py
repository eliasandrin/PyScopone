"""Thin launcher for the Pygame Scopone client."""

import os
import sys


def _ensure_src_on_path() -> None:
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_root = os.path.join(project_root, "src")
    if src_root not in sys.path:
        sys.path.insert(0, src_root)


def main() -> int:
    _ensure_src_on_path()

    from scopone.ui.game_app import main as run_app

    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
