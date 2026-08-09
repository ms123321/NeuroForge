"""Serial sevens UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.serial7 import Serial7Engine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class Serial7Mode(BaseMode):
    key = "serial7"
    title = "Serial Sevens"

    def start(self):
        self.engine = Serial7Engine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["serial7"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["serial7"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Clinical serial sevens", T.MODE_COLORS["serial7"])
        Label(self.play, text="MMSE-style mental control · subtract repeatedly", size=11, color=T.TEXT_DIM).pack(
            pady=(10, 6)
        )
        Label(self.play, text=trial.prompt, size=22, bold=True, color=T.GOLD).pack(pady=16)
        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=10)

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
                bg=T.BG_ELEVATED, fg=T.TEXT, width=80, height=48, font_size=14,
            ).pack(side="left", padx=5)
        self.after(trial.deadline_ms, lambda: pick(None))
