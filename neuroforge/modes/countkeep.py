"""Running count UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.countkeep import CountKeepEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class CountKeepMode(BaseMode):
    key = "countkeep"
    title = "Keep Count"

    def start(self):
        self.engine = CountKeepEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["countkeep"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["countkeep"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False

        if trial.ask:
            self.update_hud("What is your running TOTAL?", T.MODE_COLORS["countkeep"])
            Label(self.play, text="Mental updating · report the sum", size=11, color=T.TEXT_DIM).pack(pady=(12, 6))
            Label(self.play, text="?", size=42, bold=True, color=T.GOLD).pack(pady=16)
            row = tk.Frame(self.play, bg=T.BG_DEEP)
            row.pack(pady=8)

            def pick(v: int | None):
                if self._answered or not self._alive:
                    return
                self._answered = True
                self.cancel_timers()
                self.apply_event(self.engine.choose(v))
                self.next_or_finish()

            for opt in trial.options:
                RoundedButton(
                    row, text=str(opt), command=lambda x=opt: pick(x),
                    bg=T.BG_ELEVATED, fg=T.TEXT, width=70, height=48, font_size=14,
                ).pack(side="left", padx=5)
            self.after(trial.deadline_ms, lambda: pick(None))
        else:
            self.update_hud("Update or ignore — keep the total in mind", T.MODE_COLORS["countkeep"])
            Label(self.play, text=trial.display, size=28, bold=True, color=T.TEAL if trial.is_update else T.TEXT_MUTED).pack(
                expand=True, pady=30
            )

            def cont():
                if self._answered or not self._alive:
                    return
                self._answered = True
                # no score on non-ask steps
                self.engine.choose(None)
                self.next_or_finish()

            RoundedButton(
                self.play, text="Got it →", command=cont,
                bg=T.ACCENT, fg=T.BG_DEEP, width=160, height=44,
            ).pack(pady=12)
            self.after(trial.deadline_ms, cont)
