"""Conjunction search UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.conjunction import ConjunctionEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class ConjunctionMode(BaseMode):
    key = "conjunction"
    title = "Feature Hunt"

    def start(self):
        self.engine = ConjunctionEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["conjunction"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["conjunction"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud(f"Find: {trial.target_desc}", T.MODE_COLORS["conjunction"])
        Label(self.play, text="Conjunction search · both features must match", size=11, color=T.TEXT_DIM).pack(
            pady=(6, 4)
        )

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=8)
        size = 48

        def pick(i: int):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(i, said_absent=False))
            self.next_or_finish()

        for i, item in enumerate(trial.items):
            r, c = divmod(i, trial.cols)
            cell = tk.Canvas(grid, width=size, height=size, bg=T.BG_CARD, highlightthickness=1, highlightbackground=T.BG_ELEVATED)
            cell.grid(row=r, column=c, padx=2, pady=2)
            cell.create_text(size // 2, size // 2, text=item.shape, font=font(16, bold=True), fill=item.color_hex)
            cell.bind("<Button-1>", lambda e, idx=i: pick(idx))

        def absent():
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(None, said_absent=True))
            self.next_or_finish()

        RoundedButton(
            self.play, text="NOT PRESENT", command=absent,
            bg=T.CORAL, fg=T.BG_DEEP, width=180, height=40, font_size=12,
        ).pack(pady=8)
        self.after(trial.deadline_ms, lambda: self._timeout())

    def _timeout(self):
        if self._answered or not self._alive:
            return
        self._answered = True
        self.apply_event(self.engine.choose(None, said_absent=False))
        self.next_or_finish()
