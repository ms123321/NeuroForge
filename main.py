#!/usr/bin/env python3
"""Launch NeuroForge brain-training game."""

import sys
import traceback
from pathlib import Path

# Ensure project root is on path when launched from anywhere
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    try:
        from neuroforge.app import main as run_app
        run_app()
    except Exception:
        traceback.print_exc()
        print("\nNeuroForge failed to start. See error above.", flush=True)
        try:
            input("Press Enter to close...")
        except EOFError:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
