"""
Device registry for iOS / Android / Web Push tokens.

Prefs live in notifications.json; tokens live in push_devices.json so many
devices can register against the same account on a phone.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .progress import _data_dir

DEVICES_FILE = _data_dir() / "push_devices.json"


@dataclass
class PushDevice:
    token: str
    platform: str  # ios | android | web
    label: str = ""
    endpoint: str = ""  # web push endpoint
    p256dh: str = ""
    auth: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "token": self.token,
            "platform": self.platform,
            "label": self.label,
            "endpoint": self.endpoint,
            "p256dh": self.p256dh,
            "auth": self.auth,
            "updated_at": self.updated_at,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_devices() -> list[PushDevice]:
    if not DEVICES_FILE.exists():
        return []
    try:
        raw = json.loads(DEVICES_FILE.read_text(encoding="utf-8"))
        out: list[PushDevice] = []
        for d in raw.get("devices") or []:
            if not d.get("token") and not d.get("endpoint"):
                continue
            out.append(
                PushDevice(
                    token=str(d.get("token") or d.get("endpoint") or ""),
                    platform=str(d.get("platform") or "web"),
                    label=str(d.get("label") or ""),
                    endpoint=str(d.get("endpoint") or ""),
                    p256dh=str(d.get("p256dh") or ""),
                    auth=str(d.get("auth") or ""),
                    updated_at=str(d.get("updated_at") or ""),
                )
            )
        return out
    except (json.JSONDecodeError, TypeError, OSError):
        return []


def save_devices(devices: list[PushDevice]) -> None:
    DEVICES_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEVICES_FILE.write_text(
        json.dumps({"devices": [d.to_dict() for d in devices]}, indent=2),
        encoding="utf-8",
    )


def register_device(
    *,
    token: str = "",
    platform: str = "web",
    label: str = "",
    endpoint: str = "",
    p256dh: str = "",
    auth: str = "",
) -> PushDevice:
    platform = (platform or "web").lower().strip()
    if platform not in ("ios", "android", "web"):
        platform = "web"
    key = (endpoint or token or "").strip()
    if not key:
        raise ValueError("token or endpoint required")

    devices = load_devices()
    # upsert by token/endpoint
    for d in devices:
        if d.token == key or (endpoint and d.endpoint == endpoint):
            d.token = token or d.token or key
            d.platform = platform
            d.label = label or d.label
            d.endpoint = endpoint or d.endpoint
            d.p256dh = p256dh or d.p256dh
            d.auth = auth or d.auth
            d.updated_at = _now()
            save_devices(devices)
            return d

    dev = PushDevice(
        token=token or key,
        platform=platform,
        label=label,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth,
        updated_at=_now(),
    )
    devices.append(dev)
    # keep last 20 devices
    devices = devices[-20:]
    save_devices(devices)
    return dev


def unregister_device(token_or_endpoint: str) -> bool:
    key = (token_or_endpoint or "").strip()
    if not key:
        return False
    devices = load_devices()
    new = [d for d in devices if d.token != key and d.endpoint != key]
    if len(new) == len(devices):
        return False
    save_devices(new)
    return True


def mobile_devices() -> list[PushDevice]:
    return [d for d in load_devices() if d.platform in ("ios", "android", "web")]


def summary() -> dict[str, Any]:
    devices = load_devices()
    by = {"ios": 0, "android": 0, "web": 0}
    for d in devices:
        by[d.platform] = by.get(d.platform, 0) + 1
    return {
        "count": len(devices),
        "by_platform": by,
        "devices": [
            {
                "platform": d.platform,
                "label": d.label,
                "updated_at": d.updated_at,
                "token_preview": (d.token[:12] + "…") if len(d.token) > 12 else d.token,
            }
            for d in devices
        ],
    }
