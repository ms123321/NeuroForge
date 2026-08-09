"""Dichotic selective attention UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.dichotic import DichoticEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class DichoticMode(BaseMode):
    key = "dichotic"
    title = "Two Streams"

    def start(self):
        self.engine = DichoticEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["dichotic"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["dichotic"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        cue = f"⚡ ATTEND {trial.attend.upper()}" if trial.switched else f"Attend {trial.attend.upper()} only"
        self.update_hud(cue, T.WARNING if trial.switched else T.MODE_COLORS["dichotic"])
        Label(self.play, text="Dichotic-style · report the attended side", size=11, color=T.TEXT_DIM).pack(pady=(8, 6))

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=12)
        for side, word, col in (
            ("LEFT", trial.left_word, T.ACCENT),
            ("RIGHT", trial.right_word, T.TEAL),
        ):
            box = tk.Frame(row, bg=T.BG_CARD, padx=16, pady=12)
            box.pack(side="left", padx=10)
            Label(box, text=side, size=10, color=T.TEXT_MUTED).pack()
            Label(box, text=word, size=22, bold=True, color=col).pack()

        opts = tk.Frame(self.play, bg=T.BG_DEEP)
        opts.pack(pady=12)

        def pick(w: str | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(w))
            self.next_or_finish()

        for w in trial.options:
            RoundedButton(
                opts, text=w, command=lambda x=w: pick(x),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=90, height=42, font_size=12,
            ).pack(side="left", padx=4)
        self.after(trial.deadline_ms, lambda: pick(None))
