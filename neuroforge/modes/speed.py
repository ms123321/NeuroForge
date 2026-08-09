"""Speed Mirror UI."""

from __future__ import annotations

import time
import tkinter as tk

from .. import theme as T
from ..logic.speed import SpeedEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class SpeedMirror(BaseMode):
    key = "speed"
    title = "Speed Mirror"

    def start(self):
        self.engine = SpeedEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["speed"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["speed"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud(f"Match the target · {trial.time_limit:.1f}s", T.GOLD)
        Label(self.play, text="Find this symbol", size=12, color=T.TEXT_DIM).pack(pady=(10, 4))

        target_c = tk.Canvas(self.play, width=100, height=100, bg=T.BG_CARD, highlightthickness=0)
        target_c.pack(pady=6)
        target_c.create_rectangle(8, 8, 92, 92, fill=T.BG_ELEVATED, outline="")
        target_c.create_text(50, 50, text=trial.target, font=font(36, bold=True), fill=T.GOLD)

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=16)
        start = time.time()
        cols = 3 if len(trial.options) > 4 else 2

        def pick(sym: str):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            event = self.engine.choose(sym, time.time() - start)
            self.apply_event(event)
            self.next_or_finish()

        for i, sym in enumerate(trial.options):
            r, c = divmod(i, cols)
            cell = tk.Canvas(
                grid, width=88, height=88, bg=T.BG_CARD,
                highlightthickness=2, highlightbackground=T.BG_ELEVATED,
            )
            cell.grid(row=r, column=c, padx=8, pady=8)
            cell.create_text(44, 44, text=sym, font=font(28, bold=True), fill=T.TEXT)
            cell.bind("<Button-1>", lambda e, s=sym: pick(s))

        def timeout():
            if self._answered or not self._alive:
                return
            self._answered = True
            event = self.engine.choose(None, trial.time_limit)
            self.apply_event(event)
            self.next_or_finish()

        self.after(int(trial.time_limit * 1000), timeout)
