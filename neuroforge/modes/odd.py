"""Odd Spot UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.odd import OddEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class OddSpot(BaseMode):
    key = "odd"
    title = "Odd Spot"

    def start(self):
        self.engine = OddEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["odd"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["odd"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud(f"Find the odd one  ·  {trial.time_limit:.1f}s", T.MODE_COLORS["odd"])
        Label(self.play, text="Tap the symbol that doesn't match", size=12, color=T.TEXT_DIM).pack(
            pady=(10, 8)
        )

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=8)
        size = 56 if trial.cols >= 5 else 64

        def pick(i: int):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(i))
            self.next_or_finish()

        for i, sym in enumerate(trial.items):
            r, c = divmod(i, trial.cols)
            cell = tk.Canvas(
                grid, width=size, height=size, bg=T.BG_CARD,
                highlightthickness=2, highlightbackground=T.BG_ELEVATED,
            )
            cell.grid(row=r, column=c, padx=4, pady=4)
            cell.create_text(size // 2, size // 2, text=sym, font=font(20, bold=True), fill=T.TEXT)
            cell.bind("<Button-1>", lambda e, idx=i: pick(idx))

        def timeout():
            if self._answered or not self._alive:
                return
            self._answered = True
            self.apply_event(self.engine.choose(None))
            self.next_or_finish()

        self.after(int(trial.time_limit * 1000), timeout)
