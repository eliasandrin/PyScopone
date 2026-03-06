# ============================================================================
# SCOPONE - Entry Point
# ============================================================================
# Punto di ingresso principale dell'applicazione
# ============================================================================

"""
SCOPONE - Traditional Italian Card Game

A complete implementation of the Scopone card game with:
- Full game rules implementation
- AI players with multiple difficulty levels
- Beginner-friendly interface
- Complete scoring system
- Game statistics and history

Usage:
    python main.py
"""

import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.modern_app import ModernScoponeApp


def main():
    """Launch the modern Scopone game application."""
    try:
        print("🎴 Avvio dell'applicazione Scopone moderna...")
        app = ModernScoponeApp()
        app.mainloop()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\\nPlease install required dependencies:")
        print("  pip install customtkinter pillow")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
