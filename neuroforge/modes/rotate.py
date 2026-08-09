"""Mental Rotation UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.rotate import RotateEngine
from ..ui import Label, RoundedButton, clear_frame
from .base import BaseMode


def draw_poly(canvas: tk.Canvas, cells: list[tuple[int, int]], color: str, origin=(20, 20), scale=28):
    canvas.delete("shape")
    for x, y in cells:
        x1 = origin[0] + x * scale
        y1 = origin[1] + y * scale
        canvas.create_rectangle(
            x1, y1, x1 + scale - 3, y1 + scale - 3,
            fill=color, outline=T.BG_DEEP, width=2, tags="shape",
        )


class MentalRotate(BaseMode):
    key = "rotate"
    title = "Mind Rotate"

    def start(self):
        self.engine = RotateEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["rotate"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["rotate"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False

        tl = getattr(trial, "time_limit", 5.0)
        self.update_hud(
            f"Same shape rotated?  ·  {tl:.1f}s",
            T.MODE_COLORS["rotate"],
        )
        Label(
            self.play,
            text="Is the right shape a rotation of the left?\n(Mirrors count as DIFFERENT)",
            size=11, color=T.TEXT_DIM,
        ).pack(pady=(10, 8))

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=8)

        left = tk.Canvas(row, width=140, height=140, bg=T.BG_CARD, highlightthickness=0)
        left.pack(side="left", padx=12)
        draw_poly(left, trial.base_cells, T.ACCENT)

        Label(row, text="vs", size=14, bold=True, color=T.TEXT_MUTED).pack(side="left", padx=4)

        right = tk.Canvas(row, width=140, height=140, bg=T.BG_CARD, highlightthickness=0)
        right.pack(side="left", padx=12)
        draw_poly(right, trial.probe_cells, T.PURPLE)

        btn_row = tk.Frame(self.play, bg=T.BG_DEEP)
        btn_row.pack(pady=20)

        def answer(said_same: bool, timed_out: bool = False):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            event = self.engine.answer(said_same, timed_out=timed_out)
            self.apply_event(event)
            self.next_or_finish()

        RoundedButton(
            btn_row, text="SAME (rotated)", command=lambda: answer(True),
            bg=T.TEAL, fg=T.BG_DEEP, width=160, height=50, font_size=12,
        ).pack(side="left", padx=8)
        RoundedButton(
            btn_row, text="DIFFERENT", command=lambda: answer(False),
            bg=T.CORAL, fg=T.BG_DEEP, width=140, height=50, font_size=12,
        ).pack(side="left", padx=8)

        self.play.focus_set()
        self.play.bind("s", lambda e: answer(True))
        self.play.bind("d", lambda e: answer(False))

        self.after(int(tl * 1000), lambda: answer(False, timed_out=True))
