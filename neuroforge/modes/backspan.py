"""Backward spatial span UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.backward_span import BackwardSpanEngine
from ..ui import Label, clear_frame
from .base import BaseMode


class BackSpanMode(BaseMode):
    key = "backspan"
    title = "Reverse Blocks"

    def start(self):
        self.engine = BackwardSpanEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["backspan"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["backspan"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._accepting = False
        self.update_hud(f"Watch {len(trial.sequence)} blocks…", T.MODE_COLORS["backspan"])
        Label(self.play, text="Then tap them in REVERSE order", size=12, color=T.TEXT_DIM).pack(pady=(8, 6))

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(expand=True)
        self._cells = []
        size = 70
        for i in range(9):
            r, c = divmod(i, 3)
            cell = tk.Canvas(grid, width=size, height=size, bg=T.BG_CARD, highlightthickness=2, highlightbackground=T.BG_ELEVATED)
            cell.grid(row=r, column=c, padx=5, pady=5)
            cell.create_rectangle(8, 8, size - 8, size - 8, fill=T.BG_ELEVATED, outline="", tags="blk")
            cell.bind("<Button-1>", lambda e, j=i: self._tap(j))
            self._cells.append(cell)
        self._trial = trial
        self.after(500, self._play)

    def _flash(self, idx, on):
        self._cells[idx].itemconfig("blk", fill=T.ACCENT if on else T.BG_ELEVATED)
        self._cells[idx].configure(highlightbackground=T.ACCENT if on else T.BG_ELEVATED)

    def _play(self, step=0):
        if not self._alive:
            return
        if step >= len(self._trial.sequence):
            self._accepting = True
            self.update_hud("Reverse order — tap now", T.TEAL)
            return
        idx = self._trial.sequence[step]
        self._flash(idx, True)
        self.after(self._trial.flash_ms, lambda: self._un(idx, step))

    def _un(self, idx, step):
        if not self._alive:
            return
        self._flash(idx, False)
        self.after(140, lambda: self._play(step + 1))

    def _tap(self, idx):
        if not self._accepting or not self._alive:
            return
        self._flash(idx, True)
        self.after(100, lambda: self._flash(idx, False))
        event = self.engine.tap(idx)
        if event is None:
            return
        self._accepting = False
        self.apply_event(event)
        self.next_or_finish()
