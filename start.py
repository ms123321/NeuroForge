"""
Production entrypoint for Railway / Docker.

Always binds 0.0.0.0:$PORT (default 8080) with a single gunicorn worker.
Avoids fragile shell $PORT expansion and CRLF issues on start.sh.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Project root on path (same as webapp.app)
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    port = int(os.environ.get("PORT") or "8080")
    # Railway public networking must forward to this same port
    os.environ["PORT"] = str(port)

    print("=" * 40, flush=True)
    print(" NeuroForge production start", flush=True)
    print(f" PORT={port}", flush=True)
    print(f" bind=0.0.0.0:{port}", flush=True)
    print(f" workers=1", flush=True)
    print("=" * 40, flush=True)

    # Import after path setup so failures show in logs
    from webapp.app import app  # noqa: WPS433

    print("Flask app loaded OK", flush=True)

    try:
        from gunicorn.app.base import BaseApplication
    except ImportError:
        # Fallback if gunicorn missing (should not happen in Docker image)
        print("gunicorn missing — using Flask dev server", flush=True)
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
    print(f"Starting gunicorn on {options['bind']}", flush=True)
    _App(app, options).run()


if __name__ == "__main__":
    main()
