"""Oddball UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.oddball import OddballEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class OddballMode(BaseMode):
    key = "oddball"
    title = "Oddball"

    def start(self):
        self.engine = OddballEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["oddball"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["oddball"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud(f"TAP rare target  {self.engine.target}  · ignore  {self.engine.standard}", T.MODE_COLORS["oddball"])
        Label(self.play, text="Oddball / P300-style vigilance", size=11, color=T.TEXT_DIM).pack(pady=(10, 6))

        canvas = tk.Canvas(self.play, width=180, height=180, bg=T.BG_CARD, highlightthickness=0)
        canvas.pack(pady=12)
        col = T.GOLD if trial.is_target else T.TEXT
        canvas.create_text(90, 90, text=trial.symbol, font=font(48, bold=True), fill=col)

        def press(_e=None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.respond(True))
            self.next_or_finish()

        canvas.bind("<Button-1>", press)
        self.play.focus_set()
        self.play.bind("<space>", press)

        def timeout():
            if self._answered or not self._alive:
                return
            self._answered = True
            self.apply_event(self.engine.respond(False))
            self.next_or_finish()

        self.after(trial.deadline_ms, timeout)
