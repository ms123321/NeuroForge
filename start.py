"""
Production entrypoint for Railway / Docker / Render.

Uses Waitress (pure Python WSGI server) — no gunicorn binary/PATH issues.
Binds 0.0.0.0:$PORT (default 8080).
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    try:
        port = int(os.environ.get("PORT") or "8080")
    except ValueError:
        port = 8080
    os.environ["PORT"] = str(port)

    print("=" * 40, flush=True)
    print(" NeuroForge production start", flush=True)
    print(f" PORT={port}", flush=True)
    print(f" bind=0.0.0.0:{port}", flush=True)
    print(" server=waitress", flush=True)
    print("=" * 40, flush=True)

    try:
        from webapp.app import app
    except Exception:
        print("FATAL: failed to import Flask app", flush=True)
        traceback.print_exc()
        return 1

    print("Flask app loaded OK", flush=True)

    try:
        from waitress import serve
    except ImportError:
        print("waitress missing — Flask fallback server", flush=True)
        app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
        return 0

    print(f"Starting Waitress on 0.0.0.0:{port}", flush=True)
    # threads: concurrent requests without multi-process complexity
    serve(
        app,
        host="0.0.0.0",
        port=port,
        threads=8,
        url_scheme=os.environ.get("WAITER_URL_SCHEME", "https"),
        ident="NeuroForge",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
