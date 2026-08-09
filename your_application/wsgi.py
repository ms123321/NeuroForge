"""
WSGI entry for hosts that default to:
  gunicorn your_application.wsgi

Also works with:  gunicorn your_application.wsgi:application
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webapp.app import app as application  # noqa: E402

# Aliases some servers look for
app = application
