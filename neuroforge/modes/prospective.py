"""Prospective memory UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.prospective import ProspectiveEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class ProspectiveMode(BaseMode):
    key = "prospective"
    title = "Remember When"

    def start(self):
        self.engine = ProspectiveEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["prospective"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["prospective"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Odd/Even · if ×5 press PM CUE", T.MODE_COLORS["prospective"])
        Label(
            self.play,
            text="Prospective memory: ongoing parity task + remember the special rule",
            size=11, color=T.TEXT_DIM,
        ).pack(pady=(10, 6))

        canvas = tk.Canvas(self.play, width=160, height=160, bg=T.BG_CARD, highlightthickness=0)
        canvas.pack(pady=10)
        canvas.create_text(80, 80, text=str(trial.number), font=font(42, bold=True), fill=T.GOLD)

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=12)

        def ans(choice: str | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.answer(choice))
            self.next_or_finish()

        RoundedButton(row, text="ODD", command=lambda: ans("odd"), bg=T.ACCENT, fg=T.BG_DEEP, width=100, height=48).pack(side="left", padx=6)
        RoundedButton(row, text="EVEN", command=lambda: ans("even"), bg=T.TEAL, fg=T.BG_DEEP, width=100, height=48).pack(side="left", padx=6)
        RoundedButton(row, text="PM CUE", command=lambda: ans("pm"), bg=T.CORAL, fg=T.BG_DEEP, width=100, height=48).pack(side="left", padx=6)
        self.after(trial.deadline_ms, lambda: ans(None))
