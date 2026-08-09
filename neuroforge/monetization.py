"""
NeuroForge monetization tiers.

Desktop simulates IAP/ads for testing. On iOS/Android, replace purchase_*
and show_ad with StoreKit 2 / Google Play Billing + AdMob adapters.

Tiers
-----
free       — limited modes, interstitial ads between sessions
subscribe  — Pro monthly/yearly (all modes, no ads)
lifetime   — one-time unlock (all modes, no ads forever)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from .progress import _data_dir

ENTITLEMENT_FILE = _data_dir() / "entitlement.json"

# App Store product IDs (configure identically in App Store Connect / Play Console)
PRODUCT_MONTHLY = "com.neuroforge.app.pro.monthly"
PRODUCT_YEARLY = "com.neuroforge.app.pro.yearly"
PRODUCT_LIFETIME = "com.neuroforge.app.lifetime"

# Display prices (USD) — match App Store Connect pricing
PRICE_MONTHLY = 4.99
PRICE_YEARLY = 29.99
PRICE_LIFETIME = 49.99

TIER_FREE = "free"
TIER_SUBSCRIBE = "subscribe"
TIER_LIFETIME = "lifetime"

# Free tier: these modes only (research sampler + daily circuit core)
FREE_MODE_KEYS = (
    "focus",
    "memory",
    "speed",
    "nback",
    "flanker",
    "calc",
    "odd",
    "sart",
)

FREE_DAILY_SESSIONS = 5  # max free training sessions per calendar day


@dataclass
class Entitlement:
    tier: str = TIER_FREE
    # subscribe fields
    product_id: str = ""
    expires_iso: str = ""  # empty = not subscribed
    # lifetime
    lifetime_unlocked: bool = False
    # free tier counters
    last_free_day: str = ""
    free_sessions_today: int = 0
    # ads
    ads_enabled: bool = True
    # purchase history (local)
    purchases: list[dict[str, Any]] | None = None

    def __post_init__(self):
        if self.purchases is None:
            self.purchases = []

    def is_pro(self) -> bool:
        if self.lifetime_unlocked or self.tier == TIER_LIFETIME:
            return True
        if self.tier == TIER_SUBSCRIBE and self.expires_iso:
            try:
                exp = datetime.fromisoformat(self.expires_iso)
                return exp > datetime.now()
            except ValueError:
                return False
        return False

    def effective_tier(self) -> str:
        if self.lifetime_unlocked or self.tier == TIER_LIFETIME:
            return TIER_LIFETIME
        if self.is_pro() and self.tier == TIER_SUBSCRIBE:
            return TIER_SUBSCRIBE
        return TIER_FREE

    def shows_ads(self) -> bool:
        return not self.is_pro() and self.ads_enabled

    def can_play_mode(self, mode_key: str) -> bool:
        if self.is_pro():
            return True
        return mode_key in FREE_MODE_KEYS

    def can_start_session(self) -> tuple[bool, str]:
        """Return (ok, message). Free tier has daily session cap."""
        if self.is_pro():
            return True, ""
        today = date.today().isoformat()
        if self.last_free_day != today:
            self.free_sessions_today = 0
            self.last_free_day = today
        if self.free_sessions_today >= FREE_DAILY_SESSIONS:
            return (
                False,
                f"Free plan: {FREE_DAILY_SESSIONS} sessions/day used. "
                f"Upgrade to Pro for unlimited training.",
            )
        return True, ""

    def record_free_session(self) -> None:
        if self.is_pro():
            return
        today = date.today().isoformat()
        if self.last_free_day != today:
            self.free_sessions_today = 0
            self.last_free_day = today
        self.free_sessions_today += 1
        self.save()

    def free_remaining(self) -> int:
        if self.is_pro():
            return 999
        today = date.today().isoformat()
        if self.last_free_day != today:
            return FREE_DAILY_SESSIONS
        return max(0, FREE_DAILY_SESSIONS - self.free_sessions_today)

    # ── Purchases (desktop simulation of StoreKit / Play Billing) ─────

    def purchase_monthly(self) -> dict[str, Any]:
        return self._activate_subscribe(PRODUCT_MONTHLY, days=30, price=PRICE_MONTHLY)

    def purchase_yearly(self) -> dict[str, Any]:
        return self._activate_subscribe(PRODUCT_YEARLY, days=365, price=PRICE_YEARLY)

    def purchase_lifetime(self) -> dict[str, Any]:
        self.tier = TIER_LIFETIME
        self.lifetime_unlocked = True
        self.ads_enabled = False
        self.product_id = PRODUCT_LIFETIME
        self.expires_iso = ""
        rec = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "product": PRODUCT_LIFETIME,
            "price_usd": PRICE_LIFETIME,
            "kind": "lifetime",
        }
        self.purchases.append(rec)
        self.save()
        return rec

    def restore_purchases(self) -> str:
        """Re-validate local entitlement (on device: query StoreKit/Play)."""
        if self.lifetime_unlocked:
            self.tier = TIER_LIFETIME
            self.ads_enabled = False
            self.save()
            return "Lifetime Pro restored."
        if self.expires_iso:
            try:
                if datetime.fromisoformat(self.expires_iso) > datetime.now():
                    self.tier = TIER_SUBSCRIBE
                    self.ads_enabled = False
                    self.save()
                    return "Subscription active — Pro restored."
            except ValueError:
                pass
        self.tier = TIER_FREE
        self.ads_enabled = True
        self.save()
        return "No active Pro found. You are on Free (with ads)."

    def _activate_subscribe(self, product_id: str, days: int, price: float) -> dict[str, Any]:
        self.tier = TIER_SUBSCRIBE
        self.lifetime_unlocked = False
        self.ads_enabled = False
        self.product_id = product_id
        self.expires_iso = (datetime.now() + timedelta(days=days)).isoformat(timespec="seconds")
        rec = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "product": product_id,
            "price_usd": price,
            "kind": "subscribe",
            "days": days,
            "expires": self.expires_iso,
        }
        self.purchases.append(rec)
        self.save()
        return rec

    def status_line(self) -> str:
        t = self.effective_tier()
        if t == TIER_LIFETIME:
            return "Pro Lifetime · no ads"
        if t == TIER_SUBSCRIBE:
            try:
                exp = datetime.fromisoformat(self.expires_iso).strftime("%Y-%m-%d")
            except ValueError:
                exp = "?"
            return f"Pro Subscribe · renews/ends {exp} · no ads"
        return f"Free · ads on · {self.free_remaining()} sessions left today"

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier,
            "product_id": self.product_id,
            "expires_iso": self.expires_iso,
            "lifetime_unlocked": self.lifetime_unlocked,
            "last_free_day": self.last_free_day,
            "free_sessions_today": self.free_sessions_today,
            "ads_enabled": self.ads_enabled,
            "purchases": list(self.purchases or []),
        }

    def save(self) -> None:
        ENTITLEMENT_FILE.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> Entitlement:
        if not ENTITLEMENT_FILE.exists():
            e = cls()
            e.save()
            return e
        try:
            data = json.loads(ENTITLEMENT_FILE.read_text(encoding="utf-8"))
            e = cls(
                tier=data.get("tier", TIER_FREE),
                product_id=data.get("product_id", ""),
                expires_iso=data.get("expires_iso", ""),
                lifetime_unlocked=bool(data.get("lifetime_unlocked", False)),
                last_free_day=data.get("last_free_day", ""),
                free_sessions_today=int(data.get("free_sessions_today", 0)),
                ads_enabled=bool(data.get("ads_enabled", True)),
                purchases=list(data.get("purchases") or []),
            )
            # expire stale subs
            if e.tier == TIER_SUBSCRIBE and not e.is_pro() and not e.lifetime_unlocked:
                e.tier = TIER_FREE
                e.ads_enabled = True
                e.save()
            return e
        except (json.JSONDecodeError, TypeError, ValueError, OSError):
            return cls()


class AdService:
    """
    Simulated interstitial ads for Free tier.
    On iOS/Android: swap show_interstitial() for AdMob / AppLovin.
    """

    def __init__(self, root, entitlement: Entitlement):
        self.root = root
        self.entitlement = entitlement
        self._banner_frame = None
        self.sessions_since_ad = 0

    def show_banner(self, parent) -> Any:
        """Pack a fake ad banner into parent (Free only)."""
        import tkinter as tk
        from . import theme as T
        from .ui import Label

        if not self.entitlement.shows_ads():
            return None
        frame = tk.Frame(parent, bg="#2A2A2A", height=50)
        frame.pack(side="bottom", fill="x")
        frame.pack_propagate(False)
        try:
            from .i18n import t
            ad_text = t("ad.banner")
        except Exception:
            ad_text = "  AD  ·  Free plan  ·  Upgrade to remove ads  "
        Label(
            frame,
            text=ad_text,
            size=11,
            bold=True,
            color="#AAAAAA",
        ).pack(expand=True)
        self._banner_frame = frame
        return frame

    def hide_banner(self):
        if self._banner_frame is not None:
            try:
                self._banner_frame.destroy()
            except Exception:
                pass
            self._banner_frame = None

    def maybe_interstitial(self, on_closed: Callable | None = None) -> None:
        """Show full-screen simulated ad every 2 free sessions."""
        if not self.entitlement.shows_ads():
            if on_closed:
                on_closed()
            return
        self.sessions_since_ad += 1
        if self.sessions_since_ad < 2:
            if on_closed:
                on_closed()
            return
        self.sessions_since_ad = 0
        self._show_interstitial_window(on_closed)

    def _show_interstitial_window(self, on_closed: Callable | None):
        import tkinter as tk
        from . import theme as T
        from .ui import Label, RoundedButton

        top = tk.Toplevel(self.root)
        top.title("Advertisement")
        top.configure(bg="#111111")
        top.geometry("360x420+120+80")
        top.transient(self.root)
        top.grab_set()
        Label(
            top,
            text="ADVERTISEMENT",
            size=12,
            bold=True,
            color="#888888",
        ).pack(pady=(24, 8))
        Label(
            top,
            text="Simulated ad (Free plan)\n\n"
            "On the App Store this would be\nAdMob / Google ads.\n\n"
            "Go Pro to remove all ads.",
            size=13,
            color="#CCCCCC",
        ).pack(pady=20)
        secs = {"n": 3}
        skip_lbl = Label(top, text="Skip in 3…", size=11, color="#888888")
        skip_lbl.pack(pady=8)

        def tick():
            secs["n"] -= 1
            if secs["n"] <= 0:
                skip_lbl.configure(text="You can close this ad")
                RoundedButton(
                    top,
                    text="Close ad",
                    command=close,
                    bg=T.ACCENT,
                    fg=T.BG_DEEP,
                    width=200,
                    height=44,
                ).pack(pady=12)
            else:
                skip_lbl.configure(text=f"Skip in {secs['n']}…")
                top.after(1000, tick)

        def close():
            try:
                top.grab_release()
                top.destroy()
            except Exception:
                pass
            if on_closed:
                on_closed()

        top.after(1000, tick)
        # force close after 15s max
        top.after(15000, close)
