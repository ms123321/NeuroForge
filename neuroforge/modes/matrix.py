"""Matrix pattern UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.matrix import MatrixEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class MatrixMode(BaseMode):
    key = "matrix"
    title = "Pattern Matrix"

    def start(self):
        self.engine = MatrixEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["matrix"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["matrix"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Complete the pattern", T.MODE_COLORS["matrix"])
        Label(self.play, text="Abstract reasoning · Raven-style matrix", size=11, color=T.TEXT_DIM).pack(pady=(8, 4))

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=10)
        for i, cell in enumerate(trial.grid):
            r, c = divmod(i, 3)
            canvas = tk.Canvas(grid, width=70, height=70, bg=T.BG_CARD, highlightthickness=1, highlightbackground=T.BG_ELEVATED)
            canvas.grid(row=r, column=c, padx=4, pady=4)
            canvas.create_text(35, 35, text=cell, font=font(22, bold=True), fill=T.GOLD if cell == "?" else T.TEXT)

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=12)

        def pick(v: str | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(v))
            self.next_or_finish()

        for opt in trial.options:
            RoundedButton(
                row, text=opt, command=lambda x=opt: pick(x),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=70, height=48, font_size=18,
            ).pack(side="left", padx=6)
        self.after(trial.deadline_ms, lambda: pick(None))
