"""Antisaccade UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.antisaccade import AntisaccadeEngine
from ..ui import Label, RoundedButton, clear_frame
from .base import BaseMode


class AntisaccadeMode(BaseMode):
    key = "antisaccade"
    title = "Anti Saccade"

    def start(self):
        self.engine = AntisaccadeEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["antisaccade"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["antisaccade"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Flash appears — tap the OPPOSITE side", T.MODE_COLORS["antisaccade"])
        Label(self.play, text="Inhibit the reflex · look opposite (antisaccade)", size=11, color=T.TEXT_DIM).pack(
            pady=(10, 6)
        )

        stage = tk.Canvas(self.play, width=320, height=140, bg=T.BG_CARD, highlightthickness=0)
        stage.pack(pady=10)
        stage.create_rectangle(30, 30, 110, 110, outline=T.TEXT_MUTED, width=2)
        stage.create_rectangle(210, 30, 290, 110, outline=T.TEXT_MUTED, width=2)
        cx = 70 if trial.flash_side == "left" else 250
        stage.create_oval(cx - 20, 50, cx + 20, 90, fill=T.GOLD, outline="")

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=16)

        def ans(side: str | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.answer(side))
            self.next_or_finish()

        RoundedButton(row, text="← LEFT", command=lambda: ans("left"), bg=T.ACCENT, fg=T.BG_DEEP, width=140, height=50).pack(side="left", padx=8)
        RoundedButton(row, text="RIGHT →", command=lambda: ans("right"), bg=T.TEAL, fg=T.BG_DEEP, width=140, height=50).pack(side="left", padx=8)
        self.play.focus_set()
        self.play.bind("<Left>", lambda e: ans("left"))
        self.play.bind("<Right>", lambda e: ans("right"))
        self.after(trial.deadline_ms, lambda: ans(None))
