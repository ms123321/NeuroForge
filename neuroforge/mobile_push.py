"""
Mobile-first push layer for NeuroForge (iPhone / Android / Web PWA).

Design:
  • Primary: local + remote push on iOS (APNs) and Android (FCM)
  • Secondary: Web Push / Notification API (PWA on phone browsers)
  • Desktop Windows toast is a last-resort fallback only

Native shells (BeeWare, Capacitor, Despia, React Native) should:
  1. Request OS permission
  2. Obtain device token
  3. Call register_token(...)
  4. Schedule local daily/evening reminders from prefs (no server required)
  5. Optionally POST /api/notifications/register for server-side remote push
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

from .notifications import NotificationPrefs
from . import push_devices

log = logging.getLogger("neuroforge.mobile_push")


# Copy used when scheduling local reminders on device
DEFAULT_COPY = {
    "daily_title": "Time to rewire",
    "daily_body": "Your Daily Circuit is ready — 5 short research drills.",
    "evening_title": "Evening brain check-in",
    "evening_body": "A short evening drill can seal today's progress.",
    "streak_title": "Streak at risk",
    "streak_body": "Train today to keep your streak alive.",
    "session_title": "Session complete!",
    "session_body": "Great work. Come back tomorrow to grow further.",
    "level_title": "Level up!",
    "level_body": "You leveled up. Keep building those circuits!",
    "test_title": "NeuroForge push OK",
    "test_body": "Push notifications are working on this device.",
    "weekly_title": "Your week in NeuroForge",
    "weekly_body": "Check your progress and start a new circuit.",
}


@dataclass
class PushPayload:
    title: str
    body: str
    tag: str = "neuroforge"
    data: dict[str, Any] | None = None
    sound: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "body": self.body,
            "tag": self.tag,
            "data": self.data or {"url": "/"},
            "sound": self.sound,
        }

    # Native-friendly shapes
    def apns_alert(self) -> dict[str, Any]:
        """APNs alert payload (iOS)."""
        return {
            "aps": {
                "alert": {"title": self.title, "body": self.body},
                "sound": "default" if self.sound else None,
                "badge": 1,
                "thread-id": "neuroforge",
            },
            "tag": self.tag,
            **(self.data or {}),
        }

    def fcm_message(self, token: str) -> dict[str, Any]:
        """FCM HTTP v1 message skeleton (Android / iOS via FCM)."""
        return {
            "message": {
                "token": token,
                "notification": {"title": self.title, "body": self.body},
                "data": {k: str(v) for k, v in (self.data or {"url": "/"}).items()},
                "android": {
                    "priority": "HIGH",
                    "notification": {
                        "channel_id": "neuroforge_training",
                        "sound": "default" if self.sound else None,
                        "tag": self.tag,
                    },
                },
                "apns": {
                    "payload": {
                        "aps": {
                            "alert": {"title": self.title, "body": self.body},
                            "sound": "default" if self.sound else None,
                        }
                    }
                },
            }
        }


def schedule_plan(prefs: NotificationPrefs | None = None) -> dict[str, Any]:
    """
    Machine-readable schedule for native local notifications.
    iOS: UNCalendarNotificationTrigger
    Android: AlarmManager / WorkManager
    """
    p = prefs or NotificationPrefs.load()
    days = [d for d, on in (p.days or {}).items() if on]
    return {
        "enabled": p.enabled,
        "platform_primary": "ios_android",
        "daily": {
            "enabled": p.daily_reminder and p.enabled,
            "hour": p.daily_hour,
            "minute": p.daily_minute,
            "title": DEFAULT_COPY["daily_title"],
            "body": DEFAULT_COPY["daily_body"],
            "id": "neuroforge_daily",
            "days": days,
        },
        "evening": {
            "enabled": p.evening_reminder and p.enabled,
            "hour": p.evening_hour,
            "minute": p.evening_minute,
            "title": DEFAULT_COPY["evening_title"],
            "body": DEFAULT_COPY["evening_body"],
            "id": "neuroforge_evening",
            "days": days,
        },
        "events": {
            "streak_alerts": p.streak_alerts,
            "session_complete": p.session_complete,
            "level_up": p.level_up,
            "weekly_summary": p.weekly_summary,
            "motivational": p.motivational,
        },
        "quiet_hours": {
            "enabled": p.quiet_hours,
            "start_hour": p.quiet_start_hour,
            "end_hour": p.quiet_end_hour,
        },
        "sound": p.sound,
    }


def register_token(
    token: str,
    platform: str,
    *,
    label: str = "",
    endpoint: str = "",
    p256dh: str = "",
    auth: str = "",
) -> dict[str, Any]:
    """Register an iOS APNs, Android FCM, or Web Push subscription."""
    dev = push_devices.register_device(
        token=token,
        platform=platform,
        label=label,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth,
    )
    prefs = NotificationPrefs.load()
    prefs.push_token = dev.token
    prefs.platform = dev.platform
    prefs.save()
    return {"ok": True, "device": dev.to_dict(), "schedule": schedule_plan(prefs)}


# Optional hook set by host (native shell or test harness)
_remote_sender: Callable[[PushPayload, list], int] | None = None


def set_remote_sender(fn: Callable[[PushPayload, list], int] | None) -> None:
    """Inject FCM/APNs sender (e.g. production backend). Returns # delivered."""
    global _remote_sender
    _remote_sender = fn


def deliver(payload: PushPayload, prefs: NotificationPrefs | None = None) -> dict[str, Any]:
    """
    Prefer mobile devices. Does not use Windows toast.
    Returns delivery report for clients.
    """
    p = prefs or NotificationPrefs.load()
    if not p.enabled and payload.tag != "test":
        return {"ok": False, "reason": "disabled", "delivered": 0}
    if p.is_quiet_now() and payload.tag not in ("test", "session", "level"):
        return {"ok": False, "reason": "quiet_hours", "delivered": 0}
    if not p.day_enabled_today() and payload.tag in ("daily", "evening", "motivational"):
        return {"ok": False, "reason": "day_off", "delivered": 0}

    payload.sound = p.sound
    devices = push_devices.mobile_devices()
    delivered = 0

    if _remote_sender and devices:
        try:
            delivered = int(_remote_sender(payload, devices) or 0)
        except Exception as e:
            log.warning("remote push failed: %s", e)

    # Always expose payload so the open web/PWA client can show it immediately
    return {
        "ok": True,
        "delivered_remote": delivered,
        "devices": len(devices),
        "payload": payload.to_dict(),
        "apns": payload.apns_alert(),
        "schedule": schedule_plan(p),
        "note": (
            "Show via Notification API / native local notification on device. "
            "Configure FCM/APNs credentials for server-side remote delivery."
        ),
    }


def build_event_payload(kind: str, **fmt) -> PushPayload | None:
    kind = (kind or "").lower()
    mapping = {
        "daily": ("daily_title", "daily_body", "daily"),
        "evening": ("evening_title", "evening_body", "evening"),
        "streak": ("streak_title", "streak_body", "streak"),
        "session": ("session_title", "session_body", "session"),
        "level": ("level_title", "level_body", "level"),
        "weekly": ("weekly_title", "weekly_body", "weekly"),
        "test": ("test_title", "test_body", "test"),
    }
    if kind not in mapping:
        return None
    tk, bk, tag = mapping[kind]
    title = DEFAULT_COPY[tk]
    body = DEFAULT_COPY[bk]
    try:
        body = body.format(**fmt) if fmt else body
        title = title.format(**fmt) if fmt else title
    except (KeyError, ValueError):
        pass
    return PushPayload(title=title, body=body, tag=tag, data={"url": "/", "kind": kind})


def export_for_native(prefs: NotificationPrefs | None = None) -> str:
    """JSON string a native shell can parse on startup."""
    return json.dumps(
        {
            "prefs": (prefs or NotificationPrefs.load()).to_dict(),
            "schedule": schedule_plan(prefs),
            "copy": DEFAULT_COPY,
            "channels": {
                "android": {
                    "id": "neuroforge_training",
                    "name": "Training reminders",
                    "importance": "HIGH",
                }
            },
        },
        indent=2,
    )
