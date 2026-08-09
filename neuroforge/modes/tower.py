"""Tower planning UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.tower import TowerEngine
from ..ui import Label, RoundedButton, clear_frame
from .base import BaseMode

DISK_COLORS = ["#6C8CFF", "#3DDCB5", "#F5C542", "#F687B3", "#B794F6"]


class TowerMode(BaseMode):
    key = "tower"
    title = "Tower Plan"

    def start(self):
        self.engine = TowerEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["tower"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["tower"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self._from = None
        self.update_hud("Pick best next move toward the GOAL", T.MODE_COLORS["tower"])
        Label(self.play, text="Tower of London–style planning · choose from→to peg", size=11, color=T.TEXT_DIM).pack(
            pady=(6, 4)
        )

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=6)
        self._draw_pegs(row, trial.start, "NOW")
        Label(row, text="→", size=18, bold=True, color=T.TEXT_MUTED).pack(side="left", padx=8)
        self._draw_pegs(row, trial.goal, "GOAL")

        Label(self.play, text="Tap FROM peg, then TO peg (legal moves only)", size=11, color=T.TEXT_DIM).pack(pady=8)
        btn_row = tk.Frame(self.play, bg=T.BG_DEEP)
        btn_row.pack(pady=6)
        self._status = Label(self.play, text="Select source peg", size=12, color=T.GOLD)
        self._status.pack(pady=4)

        def pick(peg: int):
            if self._answered or not self._alive:
                return
            if self._from is None:
                self._from = peg
                self._status.configure(text=f"From peg {peg+1} → select destination")
                return
            fr, to = self._from, peg
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(fr, to))
            self.next_or_finish()

        for i in range(3):
            RoundedButton(
                btn_row, text=f"Peg {i+1}", command=lambda p=i: pick(p),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=100, height=44,
            ).pack(side="left", padx=6)

        self.after(trial.deadline_ms, lambda: self._timeout())

    def _timeout(self):
        if self._answered or not self._alive:
            return
        self._answered = True
        self.apply_event(self.engine.choose(None, None))
        self.next_or_finish()

    def _draw_pegs(self, parent, pegs, title: str):
        box = tk.Frame(parent, bg=T.BG_CARD, padx=6, pady=6)
        box.pack(side="left")
        Label(box, text=title, size=10, bold=True, color=T.TEXT_DIM).pack()
        c = tk.Canvas(box, width=120, height=100, bg=T.BG_CARD, highlightthickness=0)
        c.pack()
        for pi in range(3):
            x = 20 + pi * 40
            c.create_line(x, 90, x, 20, fill=T.TEXT_MUTED, width=2)
            stack = pegs[pi]
            for di, disk in enumerate(stack):
                w = 8 + disk * 6
                y = 85 - di * 12
                col = DISK_COLORS[(disk - 1) % len(DISK_COLORS)]
                c.create_rectangle(x - w, y - 8, x + w, y, fill=col, outline="")
