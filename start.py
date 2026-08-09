"""
Production entrypoint for Railway / Docker / Procfile.

Uses gunicorn as a Python module (never the bare `gunicorn` shell command),
so "gunicorn: command not found" cannot happen.
Binds 0.0.0.0:$PORT (default 8080), 1 worker.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    port = int(os.environ.get("PORT") or "8080")
    os.environ["PORT"] = str(port)

    print("=" * 40, flush=True)
    print(" NeuroForge production start", flush=True)
    print(f" PORT={port}", flush=True)
    print(f" bind=0.0.0.0:{port}", flush=True)
    print(" workers=1", flush=True)
    print("=" * 40, flush=True)

    from webapp.app import app

    print("Flask app loaded OK", flush=True)

    # Prefer programmatic gunicorn (no PATH needed)
    try:
        from gunicorn.app.base import BaseApplication
    except ImportError:
        print("WARNING: gunicorn not installed — Flask fallback", flush=True)
        app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
        return

    class _App(BaseApplication):
        def __init__(self, application, options: dict):
            self.application = application
            self.options = options
            super().__init__()

        def load_config(self) -> None:
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        "bind": f"0.0.0.0:{port}",
        "workers": 1,
        "threads": 4,
        "timeout": 120,
        "graceful_timeout": 30,
        "keepalive": 5,
        "accesslog": "-",
        "errorlog": "-",
        "capture_output": True,
        "loglevel": "info",
        "preload_app": True,
    }
    print(f"Starting gunicorn (python module) on {options['bind']}", flush=True)
    _App(app, options).run()


if __name__ == "__main__":
    main()
