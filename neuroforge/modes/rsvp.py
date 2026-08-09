"""RSVP stream UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.rsvp import RsvpEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class RsvpMode(BaseMode):
    key = "rsvp"
    title = "Flash Stream"

    def start(self):
        self.engine = RsvpEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["rsvp"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["rsvp"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Watch the stream — report the DIGIT", T.MODE_COLORS["rsvp"])
        Label(self.play, text="RSVP · rapid serial visual presentation", size=11, color=T.TEXT_DIM).pack(
            pady=(8, 4)
        )

        canvas = tk.Canvas(self.play, width=200, height=120, bg=T.BG_CARD, highlightthickness=0)
        canvas.pack(pady=12)
        self._txt = canvas.create_text(100, 60, text="", font=font(40, bold=True), fill=T.TEXT)

        def show(i: int = 0):
            if not self._alive:
                return
            if i >= len(trial.stream):
                self._ask(trial)
                return
            item = trial.stream[i]
            color = T.GOLD if item.isdigit() else T.TEXT
            canvas.itemconfig(self._txt, text=item, fill=color)
            self.after(trial.soa_ms, lambda: show(i + 1))

        self.after(400, show)

    def _ask(self, trial):
        clear_frame(self.play)
        self.update_hud("Which digit appeared?", T.TEAL)
        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=20)

        def pick(v: str | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(v))
            self.next_or_finish()

        for v in trial.options:
            RoundedButton(
                row, text=v, command=lambda x=v: pick(x),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=60, height=48, font_size=16,
            ).pack(side="left", padx=6)
        self.after(trial.deadline_ms, lambda: pick(None))
