"""Thin launcher for the Pygame Scopone client."""

import os
import sys


def _enable_windows_dpi_awareness() -> None:
    """Abilita DPI awareness su Windows per evitare scaling sfocato."""
    if os.name != "nt":
        return

    try:
        import ctypes

        # Use Per-Monitor DPI awareness when available to avoid OS bitmap scaling blur.
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _ensure_src_on_path() -> None:
    """Aggiunge cartella src al PYTHONPATH runtime se non presente."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_root = os.path.join(project_root, "src")
    if src_root not in sys.path:
        sys.path.insert(0, src_root)


def main() -> int:
    """Entry point del launcher desktop del progetto."""
    _enable_windows_dpi_awareness()
    _ensure_src_on_path()

    from scopone.ui.game_app import main as run_app

    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
