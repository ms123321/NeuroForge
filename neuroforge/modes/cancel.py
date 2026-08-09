"""Cancellation test UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.cancel import CancellationEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class CancelMode(BaseMode):
    key = "cancel"
    title = "Cancel Marks"

    def start(self):
        self.engine = CancellationEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["cancel"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["cancel"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._done = False
        self._hit = set()
        self.update_hud(f"Cancel every  {trial.target}  — ignore others", T.MODE_COLORS["cancel"])
        Label(self.play, text="Clinical cancellation · visual attention / neglect screening lineage", size=10, color=T.TEXT_DIM).pack(
            pady=(6, 4)
        )
        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=6)
        size = 36
        self._cells = []

        def tap(i: int):
            if self._done or not self._alive or i in self._hit:
                return
            event = self.engine.tap(i)
            if i in self.engine.found:
                self._hit.add(i)
                self._cells[i].configure(bg=T.TEAL)
            if event is None:
                return
            self._done = True
            self.cancel_timers()
            self.apply_event(event)
            self.next_or_finish()

        for i, sym in enumerate(trial.cells):
            r, c = divmod(i, trial.cols)
            lab = tk.Label(
                grid, text=sym, font=font(12, bold=True),
                fg=T.GOLD if sym == trial.target else T.TEXT,
                bg=T.BG_CARD, width=2, height=1, cursor="hand2",
            )
            lab.grid(row=r, column=c, padx=1, pady=1)
            lab.bind("<Button-1>", lambda e, idx=i: tap(idx))
            self._cells.append(lab)

        def timeout():
            if self._done or not self._alive:
                return
            self._done = True
            self.apply_event(self.engine.timeout())
            self.next_or_finish()

        self.after(trial.deadline_ms, timeout)
