"""NeuroForge main application — mobile-style shell."""

from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, ttk

from . import __version__
from . import feedback
from . import theme as T
from .i18n import (
    LANGUAGES,
    get_language,
    language_code_from_dropdown,
    language_dropdown_choices,
    language_dropdown_label,
    mode_title,
    set_language,
    t,
)
from .modes import MODE_META, MODES
from .modes.base import ModeResult
from .monetization import (
    FREE_MODE_KEYS,
    PRICE_LIFETIME,
    PRICE_MONTHLY,
    PRICE_YEARLY,
    AdService,
    Entitlement,
)
from .notifications import NotificationPrefs, NotificationService
from .progress import Progress
from .ui import Card, HeaderBar, Label, ProgressBar, RoundedButton, clear_frame


# Core daily circuit (manageable length) + optional full gym
DAILY_ORDER = ("focus", "memory", "switch", "speed", "nback")
FULL_ORDER = tuple(MODE_META.keys())


class NeuroForgeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NeuroForge — Brain Training")
        self.root.configure(bg=T.BG_DEEP)
        self.root.minsize(360, 640)
        self.root.resizable(True, True)

        # Always place on the primary monitor (avoids "opened on another display")
        self.root.geometry(f"{T.WINDOW_W}x{T.WINDOW_H}+80+40")
        self.root.deiconify()
        try:
            self.root.state("normal")
        except tk.TclError:
            pass
        self.root.lift()
        try:
            self.root.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.root.focus_force()

        self.progress = Progress.load()
        set_language(self.progress.language or "en")
        self.entitlement = Entitlement.load()
        self.ads = AdService(self.root, self.entitlement)
        self.notif_prefs = NotificationPrefs.load()
        self.notifs = NotificationService(self.notif_prefs)
        feedback.set_enabled(self.progress.sound_enabled)
        self.mode_instance = None
        self._circuit_queue: list[str] | None = None
        self._circuit_label = "Circuit"

        self.root.title(t("app.title"))

        self.shell = tk.Frame(self.root, bg=T.BG_DEEP)
        self.shell.pack(fill="both", expand=True)

        self.show_home()
        # Streak risk alert (async toast) once per launch
        self.root.after(
            1500,
            lambda: self.notifs.maybe_streak_alert(
                self.progress.last_play_date,
                self.progress.current_streak,
                t("notif.streak_title"),
                t("notif.streak_body"),
            ),
        )

        # After first paint, drop topmost but keep window front
        def _front():
            try:
                self.root.attributes("-topmost", False)
            except tk.TclError:
                pass
            self.root.lift()
            self.root.focus_force()

        self.root.after(400, _front)
        self.root.after(50, self.root.update_idletasks)

    def run(self):
        print("NeuroForge is running — look for the dark blue game window.", flush=True)
        self.root.mainloop()

    # ── Screens ──────────────────────────────────────────────

    def show_home(self):
        if self.mode_instance:
            self.mode_instance.destroy()
            self.mode_instance = None
        clear_frame(self.shell)
        self.shell.configure(bg=T.BG_DEEP)

        hero = tk.Frame(self.shell, bg=T.BG_DEEP)
        hero.pack(fill="x", padx=T.PAD, pady=(12, 4))

        # ── Language dropdown ────────────────────────────────
        lang_bar = tk.Frame(hero, bg=T.BG_PANEL, padx=8, pady=8)
        lang_bar.pack(fill="x", pady=(0, 10))
        Label(lang_bar, text=t("home.language") + ":", size=11, bold=True, color=T.TEXT_DIM).pack(
            side="left", padx=(2, 8)
        )
        self._lang_var = tk.StringVar(value=language_dropdown_label(get_language()))
        lang_combo = ttk.Combobox(
            lang_bar,
            textvariable=self._lang_var,
            values=language_dropdown_choices(),
            state="readonly",
            width=28,
            font=("Segoe UI", 11, "bold"),
            style="Lang.TCombobox",
        )
        self._style_lang_dropdown(lang_combo)
        lang_combo.pack(side="left", fill="x", expand=True, ipady=4)
        lang_combo.bind("<<ComboboxSelected>>", self._on_language_dropdown)

        Label(hero, text="NEUROFORGE", size=11, bold=True, color=T.ACCENT_SOFT).pack(anchor="w")
        Label(hero, text=t("home.tagline"), size=22, bold=True, color=T.TEXT).pack(anchor="w", pady=(4, 2))
        n_modes = len(MODE_META)
        Label(
            hero,
            text=t("home.subtitle", n=n_modes) + "\n" + self.entitlement.status_line(),
            size=11,
            color=T.TEXT_DIM,
        ).pack(anchor="w", pady=(4, 0))

        gcard = Card(self.shell)
        gcard.pack(fill="x", padx=T.PAD, pady=8)

        top = tk.Frame(gcard, bg=T.BG_CARD)
        top.pack(fill="x")
        Label(top, text=self.progress.growth_title(), size=14, bold=True, color=T.TEAL).pack(side="left")
        Label(top, text=f"{self.progress.growth_points} GP", size=12, bold=True, color=T.GOLD).pack(side="right")

        Label(
            gcard,
            text=t(
                "home.streak",
                n=self.progress.current_streak,
                best=self.progress.best_streak,
                sessions=self.progress.total_sessions,
            ),
            size=10,
            color=T.TEXT_DIM,
        ).pack(anchor="w", pady=(6, 4))

        bar = ProgressBar(gcard, width=360, height=8)
        bar.pack(pady=(4, 0))
        fill = min(1.0, (self.progress.growth_points % 200) / 200)
        bar.set(fill if self.progress.growth_points else 0.05, T.TEAL)

        actions = tk.Frame(self.shell, bg=T.BG_DEEP)
        actions.pack(fill="x", padx=T.PAD, pady=(4, 2))

        RoundedButton(
            actions,
            text=t("home.daily"),
            command=self.start_daily_circuit,
            bg=T.ACCENT,
            fg=T.BG_DEEP,
            width=380,
            height=46,
            font_size=13,
        ).pack(pady=3)

        full_label = (
            t("home.full_gym", n=n_modes) if self.entitlement.is_pro() else t("home.full_gym_pro")
        )
        RoundedButton(
            actions,
            text=full_label,
            command=self.start_full_circuit,
            bg=T.PURPLE,
            fg=T.BG_DEEP,
            width=380,
            height=42,
            font_size=12,
        ).pack(pady=3)

        RoundedButton(
            actions,
            text=t("home.train"),
            command=self.show_mode_picker,
            bg=T.BG_ELEVATED,
            fg=T.TEXT,
            width=380,
            height=42,
        ).pack(pady=3)

        RoundedButton(
            actions,
            text=t("home.pro"),
            command=self.show_paywall,
            bg=T.GOLD,
            fg=T.BG_DEEP,
            width=380,
            height=42,
            font_size=12,
        ).pack(pady=3)

        RoundedButton(
            actions,
            text=t("home.progress"),
            command=self.show_progress,
            bg=T.BG_CARD,
            fg=T.TEXT,
            width=380,
            height=38,
        ).pack(pady=2)

        RoundedButton(
            actions,
            text=t("home.settings"),
            command=self.show_settings,
            bg=T.BG_ELEVATED,
            fg=T.TEXT,
            width=380,
            height=38,
            font_size=12,
        ).pack(pady=2)

        sound_label = t("home.sound_on") if self.progress.sound_enabled else t("home.sound_off")
        RoundedButton(
            actions,
            text=sound_label,
            command=self._toggle_sound,
            bg=T.BG_PANEL,
            fg=T.TEXT_DIM,
            width=380,
            height=34,
            font_size=11,
        ).pack(pady=2)

        # Free-tier ad banner
        self.ads.hide_banner()
        self.ads.entitlement = self.entitlement
        self.ads.show_banner(self.shell)

        foot = tk.Frame(self.shell, bg=T.BG_DEEP)
        foot.pack(side="bottom", fill="x", padx=T.PAD, pady=8)
        Label(
            foot,
            text=t("home.player", name=self.progress.player_name, version=__version__),
            size=10,
            color=T.TEXT_MUTED,
        ).pack(side="left")
        rename = Label(foot, text=t("home.edit_name"), size=10, color=T.ACCENT_SOFT)
        rename.pack(side="right")
        rename.configure(cursor="hand2")
        rename.bind("<Button-1>", lambda e: self._rename())

    def _style_lang_dropdown(self, combo: ttk.Combobox) -> None:
        """Blue box, black text for language Combobox (Windows-friendly)."""
        blue = "#4A90E2"
        black = "#000000"
        white = "#FFFFFF"
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Lang.TCombobox",
            fieldbackground=blue,
            background=blue,
            foreground=black,
            arrowcolor=black,
            bordercolor=blue,
            lightcolor=blue,
            darkcolor=blue,
            selectbackground=blue,
            selectforeground=black,
            padding=6,
            font=("Segoe UI", 11, "bold"),
        )
        style.map(
            "Lang.TCombobox",
            fieldbackground=[
                ("readonly", blue),
                ("!disabled", blue),
                ("active", "#5BA3F5"),
                ("focus", blue),
            ],
            foreground=[
                ("readonly", black),
                ("!disabled", black),
                ("active", black),
            ],
            background=[
                ("readonly", blue),
                ("active", "#5BA3F5"),
            ],
            arrowcolor=[("readonly", black), ("active", black)],
            selectbackground=[("readonly", blue)],
            selectforeground=[("readonly", black)],
        )
        # Force colors on the underlying entry (helps on Windows)
        try:
            self.root.option_add("*TCombobox*Listbox.background", white)
            self.root.option_add("*TCombobox*Listbox.foreground", black)
            self.root.option_add("*TCombobox*Listbox.selectBackground", blue)
            self.root.option_add("*TCombobox*Listbox.selectForeground", black)
        except tk.TclError:
            pass
        combo.configure(style="Lang.TCombobox")

    def _set_language(self, code: str):
        set_language(code)
        self.progress.language = code
        self.progress.save()
        self.root.title(t("app.title"))
        self.show_home()

    def _on_language_dropdown(self, _event=None):
        label = self._lang_var.get() if hasattr(self, "_lang_var") else ""
        code = language_code_from_dropdown(label)
        if code != get_language():
            self._set_language(code)

    def _add_time_row(self, parent, hour_attr: str, minute_attr: str, reschedule: bool = False):
        row = tk.Frame(parent, bg=T.BG_CARD)
        row.pack(fill="x", pady=4)
        p = self.notif_prefs
        hour_var = tk.StringVar(value=f"{getattr(p, hour_attr):02d}")
        min_var = tk.StringVar(value=f"{getattr(p, minute_attr):02d}")

        def commit(*_a):
            try:
                h = max(0, min(23, int(hour_var.get())))
                m = max(0, min(59, int(min_var.get())))
            except ValueError:
                return
            setattr(p, hour_attr, h)
            setattr(p, minute_attr, m)
            hour_var.set(f"{h:02d}")
            min_var.set(f"{m:02d}")
            p.save()
            self.notifs.prefs = p

        ttk.Combobox(
            row, textvariable=hour_var, values=[f"{h:02d}" for h in range(24)],
            width=4, state="readonly", font=("Segoe UI", 11),
        ).pack(side="left")
        Label(row, text=" : ", size=12, bold=True, color=T.TEXT).pack(side="left")
        ttk.Combobox(
            row, textvariable=min_var, values=[f"{m:02d}" for m in (0, 15, 30, 45)],
            width=4, state="readonly", font=("Segoe UI", 11),
        ).pack(side="left")
        hour_var.trace_add("write", commit)
        min_var.trace_add("write", commit)

    def _hour_spin(self, parent, attr: str):
        p = self.notif_prefs
        var = tk.StringVar(value=f"{getattr(p, attr):02d}")

        def commit(*_a):
            try:
                h = max(0, min(23, int(var.get())))
            except ValueError:
                return
            setattr(p, attr, h)
            p.save()
            self.notifs.prefs = p

        ttk.Combobox(
            parent, textvariable=var, values=[f"{h:02d}" for h in range(24)],
            width=4, state="readonly", font=("Segoe UI", 10),
        ).pack(side="left", padx=4)
        var.trace_add("write", commit)

    def _apply_notif_schedule(self):
        from tkinter import messagebox
        self.notifs.prefs = self.notif_prefs
        result = self.notifs.reschedule_all(
            t("notif.daily_title"),
            t("notif.daily_body"),
            t("notif.evening_title"),
            t("notif.evening_body"),
        )
        parts = []
        if self.notif_prefs.daily_reminder:
            parts.append(
                f"Morning {self.notif_prefs.daily_hour:02d}:{self.notif_prefs.daily_minute:02d}"
                f" {'OK' if result.get('morning') else 'failed'}"
            )
        if self.notif_prefs.evening_reminder:
            parts.append(
                f"Evening {self.notif_prefs.evening_hour:02d}:{self.notif_prefs.evening_minute:02d}"
                f" {'OK' if result.get('evening') else 'failed'}"
            )
        if not parts:
            parts.append("All scheduled reminders cleared.")
        messagebox.showinfo("Schedule", "\n".join(parts))


    def _toggle_sound(self):
        self.progress.sound_enabled = not self.progress.sound_enabled
        feedback.set_enabled(self.progress.sound_enabled)
        self.progress.save()
        if self.progress.sound_enabled:
            feedback.play_correct()
        self.show_home()

    def _rename(self):
        name = simpledialog.askstring("Player name", "What should we call you?", parent=self.root)
        if name and name.strip():
            self.progress.player_name = name.strip()[:24]
            self.progress.save()
            self.show_home()

    def show_settings(self):
        """Language bar + notification toggles."""
        clear_frame(self.shell)
        HeaderBar(self.shell, t("home.settings"), on_back=self.show_home).pack(
            fill="x", padx=T.PAD, pady=(12, 4)
        )

        # Language section
        Label(self.shell, text=t("lang.title"), size=16, bold=True, color=T.TEXT).pack(
            anchor="w", padx=T.PAD, pady=(8, 4)
        )
        Label(self.shell, text=t("lang.hint"), size=11, color=T.TEXT_DIM, wrap=360).pack(
            anchor="w", padx=T.PAD, pady=(0, 8)
        )

        lang_card = Card(self.shell)
        lang_card.pack(fill="x", padx=T.PAD, pady=4)
        Label(lang_card, text=t("home.language"), size=12, bold=True, color=T.TEXT_DIM).pack(
            anchor="w", pady=(0, 6)
        )
        self._lang_var = tk.StringVar(value=language_dropdown_label(get_language()))
        lang_combo = ttk.Combobox(
            lang_card,
            textvariable=self._lang_var,
            values=language_dropdown_choices(),
            state="readonly",
            width=36,
            font=("Segoe UI", 12, "bold"),
            style="Lang.TCombobox",
        )
        self._style_lang_dropdown(lang_combo)
        lang_combo.pack(fill="x", pady=4, ipady=6)
        lang_combo.bind("<<ComboboxSelected>>", self._on_language_dropdown)
        Label(
            lang_card,
            text=f"{len(LANGUAGES)} languages",
            size=10,
            color=T.TEXT_MUTED,
        ).pack(anchor="w", pady=(4, 0))

        # Notifications section (scrollable body for extra settings)
        Label(self.shell, text=t("notif.title"), size=16, bold=True, color=T.TEXT).pack(
            anchor="w", padx=T.PAD, pady=(12, 4)
        )

        canvas = tk.Canvas(self.shell, bg=T.BG_DEEP, highlightthickness=0, height=360)
        scroll = tk.Scrollbar(self.shell, orient="vertical", command=canvas.yview)
        notif_host = tk.Frame(canvas, bg=T.BG_DEEP)
        notif_host.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=notif_host, anchor="nw", width=T.WINDOW_W - 28)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(T.PAD, 0))
        scroll.pack(side="right", fill="y", padx=(0, 4))
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        notif_card = Card(notif_host)
        notif_card.pack(fill="x", pady=4, padx=2)
        p = self.notif_prefs

        def _save_prefs(reschedule: bool = False):
            p.save()
            self.notifs.prefs = p
            if reschedule:
                self._apply_notif_schedule()

        def _toggle(attr: str, reschedule: bool = False):
            setattr(p, attr, not getattr(p, attr))
            _save_prefs(reschedule=reschedule)
            self.show_settings()

        def test_push():
            ok = self.notifs.notify(
                t("notif.test_title"), t("notif.test_body"), force=True
            )
            from tkinter import messagebox
            if ok:
                messagebox.showinfo("OK", t("notif.test_body"))
            else:
                messagebox.showwarning(
                    "Notifications",
                    "Could not show a system toast. "
                    "Check Windows notification settings.",
                )

        def _toggle_btn(parent, label: str, attr: str, reschedule: bool = False):
            on = bool(getattr(p, attr))
            RoundedButton(
                parent,
                text=("✓ " if on else "○ ") + label,
                command=lambda: _toggle(attr, reschedule),
                bg=T.TEAL if on and attr == "enabled" else T.BG_ELEVATED,
                fg=T.BG_DEEP if on and attr == "enabled" else T.TEXT,
                width=340,
                height=36,
                font_size=11,
            ).pack(pady=2, anchor="w")

        _toggle_btn(notif_card, t("notif.enabled") if p.enabled else t("notif.disabled"), "enabled", True)
        _toggle_btn(notif_card, t("notif.daily"), "daily_reminder", True)
        _toggle_btn(notif_card, t("notif.evening"), "evening_reminder", True)
        _toggle_btn(notif_card, t("notif.streak"), "streak_alerts")
        _toggle_btn(notif_card, t("notif.session"), "session_complete")
        _toggle_btn(notif_card, t("notif.levelup"), "level_up")
        _toggle_btn(notif_card, t("notif.weekly"), "weekly_summary")
        _toggle_btn(notif_card, t("notif.motivational"), "motivational")
        _toggle_btn(notif_card, t("notif.sound"), "sound")
        _toggle_btn(notif_card, t("notif.quiet"), "quiet_hours")

        # Time pickers
        time_card = Card(notif_host)
        time_card.pack(fill="x", pady=6, padx=2)
        Label(time_card, text=t("notif.time_morning"), size=11, bold=True, color=T.TEXT_DIM).pack(anchor="w")
        self._add_time_row(time_card, "daily_hour", "daily_minute", reschedule=True)
        Label(time_card, text=t("notif.time_evening"), size=11, bold=True, color=T.TEXT_DIM).pack(
            anchor="w", pady=(8, 0)
        )
        self._add_time_row(time_card, "evening_hour", "evening_minute", reschedule=True)

        if p.quiet_hours:
            Label(
                time_card,
                text=t("notif.quiet_range", start=p.quiet_start_hour, end=p.quiet_end_hour),
                size=10,
                color=T.TEXT_MUTED,
            ).pack(anchor="w", pady=(8, 0))
            quiet_row = tk.Frame(time_card, bg=T.BG_CARD)
            quiet_row.pack(fill="x", pady=4)
            Label(quiet_row, text="Start", size=10, color=T.TEXT_DIM).pack(side="left")
            self._hour_spin(quiet_row, "quiet_start_hour")
            Label(quiet_row, text="  End", size=10, color=T.TEXT_DIM).pack(side="left")
            self._hour_spin(quiet_row, "quiet_end_hour")

        # Days of week
        days_card = Card(notif_host)
        days_card.pack(fill="x", pady=6, padx=2)
        Label(days_card, text=t("notif.days"), size=11, bold=True, color=T.TEXT_DIM).pack(anchor="w")
        day_row = tk.Frame(days_card, bg=T.BG_CARD)
        day_row.pack(fill="x", pady=4)
        day_labels = {
            "mon": "Mo", "tue": "Tu", "wed": "We", "thu": "Th",
            "fri": "Fr", "sat": "Sa", "sun": "Su",
        }
        from .notifications import DAY_CODES

        for code in DAY_CODES:
            on = p.days.get(code, True)

            def _flip(c=code):
                p.days[c] = not p.days.get(c, True)
                p.save()
                self.notifs.prefs = p
                self.show_settings()

            tk.Label(
                day_row,
                text=f" {day_labels[code]} ",
                font=("Segoe UI", 10, "bold"),
                bg=T.ACCENT if on else T.BG_ELEVATED,
                fg=T.BG_DEEP if on else T.TEXT_MUTED,
                cursor="hand2",
                padx=4,
                pady=4,
            ).pack(side="left", padx=2)
            day_row.winfo_children()[-1].bind("<Button-1>", lambda e, c=code: _flip(c))

        actions = tk.Frame(notif_host, bg=T.BG_DEEP)
        actions.pack(fill="x", pady=8)
        RoundedButton(
            actions,
            text=t("notif.apply"),
            command=self._apply_notif_schedule,
            bg=T.TEAL,
            fg=T.BG_DEEP,
            width=340,
            height=42,
            font_size=12,
        ).pack(pady=3)
        RoundedButton(
            actions,
            text=t("notif.test"),
            command=test_push,
            bg=T.ACCENT,
            fg=T.BG_DEEP,
            width=340,
            height=40,
            font_size=12,
        ).pack(pady=3)

        Label(
            notif_host,
            text="Primary: iPhone APNs + Android FCM (see MOBILE_PUSH.md).\n"
                 "Desktop toast is only a fallback when no phone token is registered.",
            size=9,
            color=T.TEXT_MUTED,
        ).pack(pady=8)

    def show_mode_picker(self):
        clear_frame(self.shell)
        HeaderBar(self.shell, t("choose_skill"), on_back=self.show_home).pack(
            fill="x", padx=T.PAD, pady=(12, 4)
        )
        free_note = (
            f"Free: {len(FREE_MODE_KEYS)} modes · ads · "
            f"{self.entitlement.free_remaining()} sessions left today"
            if not self.entitlement.is_pro()
            else "Pro: all modes unlocked · no ads"
        )
        Label(
            self.shell,
            text=f"{len(MODE_META)} research paradigms · {free_note}",
            size=11,
            color=T.TEXT_DIM,
        ).pack(anchor="w", padx=T.PAD, pady=(0, 6))

        # Scrollable list
        canvas = tk.Canvas(self.shell, bg=T.BG_DEEP, highlightthickness=0)
        scroll = tk.Scrollbar(self.shell, orient="vertical", command=canvas.yview)
        scroll_host = tk.Frame(canvas, bg=T.BG_DEEP)
        scroll_host.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scroll_host, anchor="nw", width=T.WINDOW_W - 24)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(T.PAD, 0))
        scroll.pack(side="right", fill="y", padx=(0, 4))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        for key, meta in MODE_META.items():
            color = T.MODE_COLORS.get(key, T.ACCENT)
            level = self.progress.level_for(key)
            locked = not self.entitlement.can_play_mode(key)
            card = Card(scroll_host)
            card.pack(fill="x", pady=5, padx=4)

            row = tk.Frame(card, bg=T.BG_CARD)
            row.pack(fill="x")
            title = mode_title(key, meta["title"]) + ("  🔒" if locked else "")
            Label(row, text=title, size=13, bold=True, color=color).pack(side="left")
            Label(row, text=f"Lv {level}", size=11, bold=True, color=T.GOLD).pack(side="right")

            Label(card, text=meta["subtitle"], size=10, color=T.TEXT_DIM).pack(anchor="w", pady=(2, 0))
            Label(card, text=meta["blurb"], size=10, color=T.TEXT_MUTED, wrap=320).pack(anchor="w", pady=(3, 5))

            if locked:
                RoundedButton(
                    card,
                    text=t("unlock_pro"),
                    command=self.show_paywall,
                    bg=T.GOLD,
                    fg=T.BG_DEEP,
                    width=140,
                    height=34,
                    font_size=12,
                ).pack(anchor="e")
            else:
                RoundedButton(
                    card,
                    text=t("start"),
                    command=lambda k=key: self._start_from_picker(k),
                    bg=color,
                    fg=T.BG_DEEP,
                    width=110,
                    height=34,
                    font_size=12,
                ).pack(anchor="e")

    def _start_from_picker(self, key: str):
        try:
            self.root.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass
        self.start_mode(key)

    def show_progress(self):
        clear_frame(self.shell)
        HeaderBar(self.shell, "Progress & science", on_back=self.show_home).pack(
            fill="x", padx=T.PAD, pady=(12, 4)
        )

        canvas = tk.Canvas(self.shell, bg=T.BG_DEEP, highlightthickness=0)
        scroll = tk.Scrollbar(self.shell, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=T.BG_DEEP)
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw", width=T.WINDOW_W - 24)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(T.PAD, 0))
        scroll.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        card = Card(body)
        card.pack(fill="x", pady=6, padx=4)
        Label(card, text="Your growth", size=14, bold=True, color=T.TEAL).pack(anchor="w")
        Label(
            card,
            text=f"{self.progress.growth_title()}  ·  {self.progress.growth_points} growth points\n"
                 f"Streak: {self.progress.current_streak} days (best {self.progress.best_streak})\n"
                 f"Sessions: {self.progress.total_sessions}  ·  "
                 f"~{self.progress.total_minutes:.0f} minutes trained",
            size=11,
            color=T.TEXT_DIM,
        ).pack(anchor="w", pady=(6, 0))

        for key, meta in MODE_META.items():
            stats = self.progress.modes.get(key)
            if not stats:
                continue
            c = Card(body)
            c.pack(fill="x", pady=3, padx=4)
            Label(c, text=meta["title"], size=12, bold=True, color=T.MODE_COLORS[key]).pack(anchor="w")
            acc = f"{stats.accuracy * 100:.0f}%" if stats.total_attempts else "—"
            Label(
                c,
                text=f"Level {stats.level}  ·  High {stats.high_score}  ·  Acc {acc}  ·  {stats.sessions} plays",
                size=10,
                color=T.TEXT_DIM,
            ).pack(anchor="w", pady=(2, 0))

        science = Card(body)
        science.pack(fill="x", pady=10, padx=4)
        Label(science, text="Why this helps plasticity", size=13, bold=True, color=T.ACCENT_SOFT).pack(anchor="w")
        Label(
            science,
            text=(
                "Neuroplasticity is the brain's ability to reorganize connections "
                "through practice. Effective training is:\n\n"
                "• Adaptive — hard enough to stretch you\n"
                "• Varied — multiple cognitive domains\n"
                "• Consistent — short daily sessions beat cramming\n"
                "• Focused — attention + feedback on errors\n\n"
                "27 paradigms aligned with NIH/neurology cognitive tasks: "
                "n-back, dual n-back, complex span, SART, Posner cueing, SDMT, "
                "stop-signal, WCST-lite, dual-task, RSVP, TMT, PASAT, MOT, and more.\n\n"
                "Adaptive Difficulty Engine keeps you in the challenge zone "
                "(~72–85% accuracy) via multi-axis load + promote/demote rules. "
                "See RESEARCH.md. Not a medical device."

            ),
            size=10,
            color=T.TEXT_DIM,
            wrap=340,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

        port = Card(body)
        port.pack(fill="x", pady=6, padx=4)
        Label(port, text="iOS / App Store port", size=12, bold=True, color=T.GOLD).pack(anchor="w")
        Label(
            port,
            text=(
                "All scoring & trial generation lives in neuroforge/logic/ "
                "with zero UI imports. Port that package to Toga or SwiftUI; "
                "see PORTING.md and APP_STORE.md."
            ),
            size=10,
            color=T.TEXT_DIM,
            wrap=340,
        ).pack(anchor="w", pady=(4, 0))

        Label(
            body,
            text="Not a medical device. For entertainment & personal training only.",
            size=9,
            color=T.TEXT_MUTED,
        ).pack(pady=12)

    # ── Gameplay flow ────────────────────────────────────────

    def start_mode(self, key: str, circuit_queue: list[str] | None = None):
        # Entitlement gates
        ok, msg = self.entitlement.can_start_session()
        if not ok:
            from tkinter import messagebox
            if messagebox.askyesno("Free limit reached", msg + "\n\nView Pro plans?"):
                self.show_paywall()
            else:
                self.show_home()
            return
        if not self.entitlement.can_play_mode(key):
            self.show_paywall(highlight=key)
            return

        clear_frame(self.shell)
        level = self.progress.level_for(key)
        cls = MODES[key]
        self._circuit_queue = circuit_queue

        def on_complete(result: ModeResult):
            self.entitlement.record_free_session()
            entry = self.progress.record_session(
                mode=result.mode_key,
                score=result.score,
                correct=result.correct,
                attempts=result.attempts,
                duration_sec=result.duration_sec,
                level=result.level,
                max_streak=result.max_streak,
            )

            def after_ad():
                self.show_results(result, entry)

            # Free tier: simulated interstitial ad
            self.ads.maybe_interstitial(on_closed=after_ad)

        def on_abort():
            self._circuit_queue = None
            self.show_home()

        self.mode_instance = cls(
            root=self.root,
            container=self.shell,
            level=level,
            on_complete=on_complete,
            on_abort=on_abort,
        )
        self.mode_instance.start()

    def start_daily_circuit(self):
        self._circuit_label = "Daily Circuit"
        # Free users only get free modes in circuit
        if self.entitlement.is_pro():
            order = list(DAILY_ORDER)
        else:
            order = [k for k in DAILY_ORDER if k in FREE_MODE_KEYS]
        if not order:
            self.show_paywall()
            return
        self.start_mode(order[0], circuit_queue=order[1:])

    def start_full_circuit(self):
        if not self.entitlement.is_pro():
            self.show_paywall()
            return
        self._circuit_label = "Full Gym"
        order = list(MODE_META.keys())
        self.start_mode(order[0], circuit_queue=order[1:])

    def show_paywall(self, highlight: str | None = None):
        """Free / Subscribe / One-time payment plans."""
        clear_frame(self.shell)
        HeaderBar(self.shell, "Go Pro", on_back=self.show_home).pack(
            fill="x", padx=T.PAD, pady=(12, 4)
        )
        Label(
            self.shell,
            text=self.entitlement.status_line(),
            size=11,
            color=T.TEAL,
        ).pack(anchor="w", padx=T.PAD, pady=(0, 8))

        if highlight:
            title = MODE_META.get(highlight, {}).get("title", highlight)
            Label(
                self.shell,
                text=f"“{title}” is a Pro mode. Unlock below.",
                size=11,
                color=T.WARNING,
            ).pack(anchor="w", padx=T.PAD, pady=(0, 8))

        # Free
        free = Card(self.shell)
        free.pack(fill="x", padx=T.PAD, pady=5)
        Label(free, text="Free  (with ads)", size=14, bold=True, color=T.TEXT).pack(anchor="w")
        Label(
            free,
            text=f"• {len(FREE_MODE_KEYS)} core research modes\n"
                 f"• Daily Circuit\n"
                 f"• {5} sessions/day · banner + interstitial ads\n"
                 f"• Adaptive levels on free modes",
            size=11,
            color=T.TEXT_DIM,
        ).pack(anchor="w", pady=(6, 4))
        if not self.entitlement.is_pro():
            Label(free, text="✓ Current plan", size=11, bold=True, color=T.TEAL).pack(anchor="e")

        # Subscribe
        sub = Card(self.shell)
        sub.pack(fill="x", padx=T.PAD, pady=5)
        Label(sub, text="Pro Subscribe", size=14, bold=True, color=T.ACCENT_SOFT).pack(anchor="w")
        Label(
            sub,
            text=f"• All {len(MODE_META)} modes · Full Gym\n"
                 f"• Unlimited sessions · no ads\n"
                 f"• Monthly ${PRICE_MONTHLY:.2f}  or  Yearly ${PRICE_YEARLY:.2f}\n"
                 f"• Cancel anytime (App Store / Play)",
            size=11,
            color=T.TEXT_DIM,
        ).pack(anchor="w", pady=(6, 6))
        row = tk.Frame(sub, bg=T.BG_CARD)
        row.pack(fill="x")
        RoundedButton(
            row,
            text=f"Monthly  ${PRICE_MONTHLY:.2f}",
            command=self._buy_monthly,
            bg=T.ACCENT,
            fg=T.BG_DEEP,
            width=160,
            height=40,
            font_size=12,
        ).pack(side="left", padx=(0, 8))
        RoundedButton(
            row,
            text=f"Yearly  ${PRICE_YEARLY:.2f}",
            command=self._buy_yearly,
            bg=T.PURPLE,
            fg=T.BG_DEEP,
            width=160,
            height=40,
            font_size=12,
        ).pack(side="left")

        # Lifetime
        life = Card(self.shell)
        life.pack(fill="x", padx=T.PAD, pady=5)
        Label(life, text="Pro Lifetime  (one-time)", size=14, bold=True, color=T.GOLD).pack(anchor="w")
        Label(
            life,
            text=f"• One payment ${PRICE_LIFETIME:.2f} — own it forever\n"
                 f"• All modes · no ads · no renewal\n"
                 f"• Best if you dislike subscriptions",
            size=11,
            color=T.TEXT_DIM,
        ).pack(anchor="w", pady=(6, 6))
        RoundedButton(
            life,
            text=f"Buy Lifetime  ${PRICE_LIFETIME:.2f}",
            command=self._buy_lifetime,
            bg=T.GOLD,
            fg=T.BG_DEEP,
            width=240,
            height=44,
            font_size=13,
        ).pack(anchor="e")

        RoundedButton(
            self.shell,
            text="Restore purchases",
            command=self._restore,
            bg=T.BG_ELEVATED,
            fg=T.TEXT,
            width=380,
            height=40,
            font_size=12,
        ).pack(pady=(12, 4), padx=T.PAD)

        Label(
            self.shell,
            text="Desktop simulates IAP. On iOS use StoreKit product IDs in monetization.py.\n"
                 "Not a medical device.",
            size=9,
            color=T.TEXT_MUTED,
        ).pack(pady=8, padx=T.PAD)

    def _buy_monthly(self):
        self.entitlement.purchase_monthly()
        self.ads.entitlement = self.entitlement
        feedback.play_level()
        self._purchase_ok(f"Pro Monthly active (~${PRICE_MONTHLY:.2f}/mo). Ads off.")

    def _buy_yearly(self):
        self.entitlement.purchase_yearly()
        self.ads.entitlement = self.entitlement
        feedback.play_level()
        self._purchase_ok(f"Pro Yearly active (~${PRICE_YEARLY:.2f}/yr). Ads off.")

    def _buy_lifetime(self):
        self.entitlement.purchase_lifetime()
        self.ads.entitlement = self.entitlement
        feedback.play_level()
        self._purchase_ok(f"Pro Lifetime unlocked (${PRICE_LIFETIME:.2f} one-time).")

    def _restore(self):
        msg = self.entitlement.restore_purchases()
        self.ads.entitlement = self.entitlement
        from tkinter import messagebox
        messagebox.showinfo("Restore", msg)
        self.show_home()

    def _purchase_ok(self, msg: str):
        from tkinter import messagebox
        messagebox.showinfo("Purchase successful", msg + "\n\n(Simulated on desktop — wire StoreKit for production.)")
        self.show_home()

    def show_results(self, result: ModeResult, entry: dict):
        if self.mode_instance:
            self.mode_instance.destroy()
            self.mode_instance = None

        clear_frame(self.shell)
        color = T.MODE_COLORS.get(result.mode_key, T.ACCENT)
        meta = MODE_META[result.mode_key]

        HeaderBar(self.shell, t("session.complete"), on_back=self.show_home).pack(
            fill="x", padx=T.PAD, pady=(16, 8)
        )

        card = Card(self.shell)
        card.pack(fill="x", padx=T.PAD, pady=8)

        Label(card, text=meta["title"], size=16, bold=True, color=color).pack(anchor="w")
        Label(card, text=f"{result.score}", size=42, bold=True, color=T.GOLD).pack(anchor="w", pady=(8, 0))
        Label(card, text="score", size=11, color=T.TEXT_MUTED).pack(anchor="w")

        acc = (result.correct / result.attempts * 100) if result.attempts else 0
        ld = entry.get("level_delta", 0)

        # Push notifications for session / level-up
        try:
            self.notifs.notify_session_complete(
                t("notif.session_title"),
                t("notif.session_body", score=result.score, acc=f"{acc:.0f}"),
            )
            if ld > 0:
                self.notifs.notify_level_up(
                    t("notif.level_title"),
                    t(
                        "notif.level_body",
                        level=entry.get("level_after", result.level),
                    ),
                )
            self.notifs.maybe_weekly_summary(
                t("notif.weekly_title"),
                t(
                    "notif.weekly_body",
                    sessions=self.progress.total_sessions,
                    streak=self.progress.current_streak,
                ),
            )
        except Exception:
            pass

        if ld > 0:
            level_note = f"Level UP → {entry.get('level_after', result.level)} ⬆"
        elif ld < 0:
            level_note = f"Level eased → {entry.get('level_after', result.level)} ⬇"
        else:
            level_note = f"Level holds at {entry.get('level_after', result.level)}"
        Label(
            card,
            text=(
                f"Accuracy  {acc:.0f}%   ({result.correct}/{result.attempts})\n"
                f"Best streak  {result.max_streak}   ·   Played Lv {result.level}\n"
                f"{level_note}\n"
                f"+{entry.get('growth_gained', 0)} growth points   ·   {result.duration_sec:.0f}s"
            ),
            size=12,
            color=T.TEXT_DIM,
        ).pack(anchor="w", pady=(12, 0))

        tip = Card(self.shell)
        tip.pack(fill="x", padx=T.PAD, pady=8)
        if acc >= 85:
            msg = "Strong session. Difficulty will edge up — that's the plasticity sweet spot."
        elif acc >= 60:
            msg = "Solid work. Stay consistent; small daily gains compound."
        else:
            msg = "Tough round — struggle is information. Level may ease so you can build back up."
        Label(tip, text=msg, size=11, color=T.TEXT_DIM, wrap=360).pack(anchor="w")

        actions = tk.Frame(self.shell, bg=T.BG_DEEP)
        actions.pack(fill="x", padx=T.PAD, pady=16)

        queue = getattr(self, "_circuit_queue", None) or []
        if queue:
            nxt = queue[0]
            rest = queue[1:]
            RoundedButton(
                actions,
                text=f"Next: {MODE_META[nxt]['title']}",
                command=lambda: self.start_mode(nxt, circuit_queue=rest),
                bg=T.ACCENT,
                fg=T.BG_DEEP,
                width=380,
                height=50,
            ).pack(pady=6)
            Label(
                actions,
                text=f"{len(queue)} mode(s) left in {self._circuit_label}",
                size=10,
                color=T.TEXT_MUTED,
            ).pack()
        else:
            if getattr(self, "_circuit_queue", None) is not None:
                Label(
                    actions,
                    text=f"{self._circuit_label} complete 🎉",
                    size=13,
                    bold=True,
                    color=T.TEAL,
                ).pack(pady=6)
            RoundedButton(
                actions,
                text="Train again",
                command=lambda: self.start_mode(result.mode_key),
                bg=color,
                fg=T.BG_DEEP,
                width=380,
                height=48,
            ).pack(pady=6)

        RoundedButton(
            actions,
            text="Home",
            command=self.show_home,
            bg=T.BG_ELEVATED,
            fg=T.TEXT,
            width=380,
            height=44,
        ).pack(pady=6)

        self._circuit_queue = None if not queue else queue


def main():
    app = NeuroForgeApp()
    app.run()


if __name__ == "__main__":
    main()
