"""
Push / local notification service for NeuroForge.

Primary target: iPhone (APNs) + Android (FCM) + Web PWA push.
See neuroforge/mobile_push.py and MOBILE_PUSH.md.

Desktop OS toasts (Windows/macOS/Linux) are a development fallback only.

Preferences: notifications.json
Device tokens: push_devices.json
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from .progress import _data_dir

PREFS_FILE = _data_dir() / "notifications.json"

# Mon=0 … Sun=6
DAY_CODES = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


@dataclass
class NotificationPrefs:
    enabled: bool = True

    # Daily training
    daily_reminder: bool = True
    daily_hour: int = 9
    daily_minute: int = 0

    # Optional second reminder (evening)
    evening_reminder: bool = False
    evening_hour: int = 18
    evening_minute: int = 0

    # Event types
    streak_alerts: bool = True
    session_complete: bool = True
    level_up: bool = True
    weekly_summary: bool = True
    motivational: bool = False

    # Quiet hours (no non-forced toasts)
    quiet_hours: bool = False
    quiet_start_hour: int = 22
    quiet_end_hour: int = 7

    # Which weekdays daily reminders fire (all True by default)
    days: dict[str, bool] = field(default_factory=lambda: {d: True for d in DAY_CODES})

    # Presentation
    sound: bool = True

    # mobile
    push_token: str = ""
    platform: str = "desktop"

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "daily_reminder": self.daily_reminder,
            "daily_hour": self.daily_hour,
            "daily_minute": self.daily_minute,
            "evening_reminder": self.evening_reminder,
            "evening_hour": self.evening_hour,
            "evening_minute": self.evening_minute,
            "streak_alerts": self.streak_alerts,
            "session_complete": self.session_complete,
            "level_up": self.level_up,
            "weekly_summary": self.weekly_summary,
            "motivational": self.motivational,
            "quiet_hours": self.quiet_hours,
            "quiet_start_hour": self.quiet_start_hour,
            "quiet_end_hour": self.quiet_end_hour,
            "days": dict(self.days),
            "sound": self.sound,
            "push_token": self.push_token,
            "platform": self.platform,
        }

    def save(self) -> None:
        PREFS_FILE.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> NotificationPrefs:
        if not PREFS_FILE.exists():
            p = cls()
            p.save()
            return p
        try:
            d = json.loads(PREFS_FILE.read_text(encoding="utf-8"))
            days = {x: True for x in DAY_CODES}
            raw_days = d.get("days") or {}
            if isinstance(raw_days, dict):
                for k in DAY_CODES:
                    if k in raw_days:
                        days[k] = bool(raw_days[k])
            return cls(
                enabled=bool(d.get("enabled", True)),
                daily_reminder=bool(d.get("daily_reminder", True)),
                daily_hour=int(d.get("daily_hour", 9)),
                daily_minute=int(d.get("daily_minute", 0)),
                evening_reminder=bool(d.get("evening_reminder", False)),
                evening_hour=int(d.get("evening_hour", 18)),
                evening_minute=int(d.get("evening_minute", 0)),
                streak_alerts=bool(d.get("streak_alerts", True)),
                session_complete=bool(d.get("session_complete", True)),
                level_up=bool(d.get("level_up", True)),
                weekly_summary=bool(d.get("weekly_summary", True)),
                motivational=bool(d.get("motivational", False)),
                quiet_hours=bool(d.get("quiet_hours", False)),
                quiet_start_hour=int(d.get("quiet_start_hour", 22)),
                quiet_end_hour=int(d.get("quiet_end_hour", 7)),
                days=days,
                sound=bool(d.get("sound", True)),
                push_token=str(d.get("push_token", "")),
                platform=str(d.get("platform", "desktop")),
            )
        except (json.JSONDecodeError, TypeError, ValueError, OSError):
            return cls()

    def is_quiet_now(self) -> bool:
        if not self.quiet_hours:
            return False
        h = datetime.now().hour
        start, end = self.quiet_start_hour, self.quiet_end_hour
        if start == end:
            return False
        if start < end:
            return start <= h < end
        # wraps midnight e.g. 22–7
        return h >= start or h < end

    def day_enabled_today(self) -> bool:
        # Monday=0 in Python weekday()
        idx = datetime.now().weekday()
        code = DAY_CODES[idx]
        return bool(self.days.get(code, True))

    def time_label(self, hour: int, minute: int) -> str:
        return f"{hour:02d}:{minute:02d}"


class NotificationService:
    def __init__(self, prefs: NotificationPrefs | None = None):
        self.prefs = prefs or NotificationPrefs.load()

    def notify(self, title: str, body: str, *, force: bool = False) -> bool:
        """Deliver a notification. Mobile (iOS/Android/web) is preferred over desktop toast."""
        if not force:
            if not self.prefs.enabled:
                return False
            if self.prefs.is_quiet_now():
                return False
        # Prefer registered mobile / web push (never use Windows toast for phones)
        plat = (self.prefs.platform or "").lower()
        if plat in ("ios", "android", "web") or self.prefs.push_token:
            try:
                from .mobile_push import PushPayload, deliver

                report = deliver(
                    PushPayload(title=title, body=body, tag="event", sound=self.prefs.sound),
                    self.prefs,
                )
                if report.get("ok"):
                    return True
            except Exception:
                pass
            if plat in ("ios", "android", "web"):
                return True
        # Desktop OS fallback only
        if sys.platform == "win32":
            return self._windows_toast(title, body)
        if sys.platform == "darwin":
            return self._macos_notify(title, body)
        return self._linux_notify(title, body)

    def notify_async(self, title: str, body: str, *, force: bool = False) -> None:
        threading.Thread(
            target=self.notify, args=(title, body), kwargs={"force": force}, daemon=True
        ).start()

    def register_push_token(self, token: str, platform: str) -> None:
        self.prefs.push_token = token
        self.prefs.platform = platform
        self.prefs.save()

    def reschedule_all(self, daily_title: str, daily_body: str,
                       evening_title: str = "", evening_body: str = "") -> dict[str, bool]:
        """Apply prefs to OS schedules. Returns status per schedule."""
        self.cancel_all_schedules()
        result = {"morning": False, "evening": False}
        if not self.prefs.enabled:
            return result
        if self.prefs.daily_reminder:
            result["morning"] = self._schedule_named(
                "NeuroForgeDailyReminder",
                self.prefs.daily_hour,
                self.prefs.daily_minute,
                daily_title,
                daily_body,
            )
        if self.prefs.evening_reminder:
            result["evening"] = self._schedule_named(
                "NeuroForgeEveningReminder",
                self.prefs.evening_hour,
                self.prefs.evening_minute,
                evening_title or daily_title,
                evening_body or daily_body,
            )
        return result

    def schedule_daily_reminder(self, title: str, body: str) -> bool:
        if not self.prefs.enabled or not self.prefs.daily_reminder:
            return False
        return self._schedule_named(
            "NeuroForgeDailyReminder",
            self.prefs.daily_hour,
            self.prefs.daily_minute,
            title,
            body,
        )

    def cancel_daily_reminder(self) -> None:
        self._delete_task("NeuroForgeDailyReminder")

    def cancel_all_schedules(self) -> None:
        for name in (
            "NeuroForgeDailyReminder",
            "NeuroForgeEveningReminder",
        ):
            self._delete_task(name)

    def maybe_streak_alert(
        self,
        last_play_date: str,
        current_streak: int,
        title: str,
        body: str,
    ) -> bool:
        if not self.prefs.enabled or not self.prefs.streak_alerts:
            return False
        if current_streak <= 0:
            return False
        today = date.today().isoformat()
        if last_play_date == today:
            return False
        return self.notify(title, body)

    def notify_session_complete(self, title: str, body: str) -> bool:
        if not self.prefs.session_complete:
            return False
        return self.notify(title, body)

    def notify_level_up(self, title: str, body: str) -> bool:
        if not self.prefs.level_up:
            return False
        return self.notify(title, body)

    def maybe_weekly_summary(self, title: str, body: str) -> bool:
        """Send once per week on Monday if enabled (tracked in prefs file sidecar)."""
        if not self.prefs.enabled or not self.prefs.weekly_summary:
            return False
        if datetime.now().weekday() != 0:  # Monday
            return False
        marker = _data_dir() / "last_weekly_summary.txt"
        today = date.today().isoformat()
        if marker.exists() and marker.read_text(encoding="utf-8").strip() == today:
            return False
        ok = self.notify(title, body)
        if ok:
            marker.write_text(today, encoding="utf-8")
        return ok

    def maybe_motivational(self, title: str, body: str) -> bool:
        if not self.prefs.enabled or not self.prefs.motivational:
            return False
        return self.notify(title, body)

    # ── Windows scheduling ───────────────────────────────────

    def _delete_task(self, name: str) -> None:
        if sys.platform != "win32":
            return
        try:
            subprocess.run(
                ["schtasks", "/Delete", "/TN", name, "/F"],
                capture_output=True,
                timeout=15,
            )
        except Exception:
            pass

    def _schedule_named(
        self, task_name: str, hour: int, minute: int, title: str, body: str
    ) -> bool:
        if sys.platform != "win32":
            self.prefs.save()
            return True
        hour = max(0, min(23, hour))
        minute = max(0, min(59, minute))
        time_str = f"{hour:02d}:{minute:02d}"
        safe = task_name.replace(" ", "")
        script_path = _data_dir() / f"{safe}_toast.ps1"

        def esc(s: str) -> str:
            return s.replace("'", "''").replace('"', "'")

        audio = "" if not self.prefs.sound else ""
        # day filter checked inside script
        days_json = json.dumps(self.prefs.days)
        script_path.write_text(
            f"""
$ErrorActionPreference = 'SilentlyContinue'
$days = '{days_json}' | ConvertFrom-Json
$map = @{{ 1='mon'; 2='tue'; 3='wed'; 4='thu'; 5='fri'; 6='sat'; 0='sun' }}
$dow = [int](Get-Date).DayOfWeek
$code = $map[$dow]
if ($days.PSObject.Properties.Name -contains $code) {{
  if (-not $days.$code) {{ exit 0 }}
}}
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = @"
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>{esc(title)}</text>
      <text>{esc(body)}</text>
    </binding>
  </visual>
</toast>
"@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("NeuroForge").Show($toast)
""",
            encoding="utf-8",
        )
        try:
            self._delete_task(task_name)
            cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{script_path}"'
            r = subprocess.run(
                [
                    "schtasks", "/Create", "/TN", task_name,
                    "/TR", cmd, "/SC", "DAILY", "/ST", time_str, "/F",
                ],
                capture_output=True,
                timeout=20,
                text=True,
            )
            return r.returncode == 0
        except Exception:
            return False

    def _windows_toast(self, title: str, body: str) -> bool:
        def esc(s: str) -> str:
            return s.replace("'", "''")

        silent = "" if self.prefs.sound else '<audio silent="true"/>'
        ps = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = @"
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>{esc(title)}</text>
      <text>{esc(body)}</text>
    </binding>
  </visual>
  {silent}
</toast>
"@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("NeuroForge").Show($toast)
"""
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                capture_output=True,
                timeout=20,
            )
            return r.returncode == 0
        except Exception:
            try:
                ps2 = f"""
Add-Type -AssemblyName System.Windows.Forms
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon = [System.Drawing.SystemIcons]::Information
$n.Visible = $true
$n.ShowBalloonTip(4000, '{esc(title)}', '{esc(body)}', [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 4
$n.Dispose()
"""
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps2],
                    capture_output=True,
                    timeout=15,
                )
                return True
            except Exception:
                return False

    def _macos_notify(self, title: str, body: str) -> bool:
        try:
            script = f'display notification "{body}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)
            return True
        except Exception:
            return False

    def _linux_notify(self, title: str, body: str) -> bool:
        try:
            subprocess.run(["notify-send", title, body], capture_output=True, timeout=10)
            return True
        except Exception:
            return False
