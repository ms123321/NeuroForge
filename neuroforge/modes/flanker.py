"""Flanker Force UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.flanker import FlankerEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class FlankerForce(BaseMode):
    key = "flanker"
    title = "Flanker Force"

    def start(self):
        self.engine = FlankerEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["flanker"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["flanker"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        tag = "match" if trial.congruent else "CONFLICT"
        self.update_hud(f"Center arrow only  ·  {tag}", T.MODE_COLORS["flanker"])
        Label(
            self.play,
            text="Which way does the MIDDLE arrow point?",
            size=12, color=T.TEXT_DIM,
        ).pack(pady=(16, 8))

        card = tk.Canvas(self.play, width=320, height=100, bg=T.BG_CARD, highlightthickness=0)
        card.pack(pady=12)
        card.create_text(160, 50, text=trial.display, font=font(32, bold=True), fill=T.TEXT)

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=20)

        def answer(d: str | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.answer(d))
            self.next_or_finish()

        RoundedButton(
            row, text="←  LEFT", command=lambda: answer("<"),
            bg=T.ACCENT, fg=T.BG_DEEP, width=140, height=52,
        ).pack(side="left", padx=10)
        RoundedButton(
            row, text="RIGHT  →", command=lambda: answer(">"),
            bg=T.TEAL, fg=T.BG_DEEP, width=140, height=52,
        ).pack(side="left", padx=10)

        self.play.focus_set()
        self.play.bind("<Left>", lambda e: answer("<"))
        self.play.bind("<Right>", lambda e: answer(">"))
        self.after(int(trial.time_limit * 1000), lambda: answer(None))
