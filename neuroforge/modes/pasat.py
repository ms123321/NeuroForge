"""PASAT-lite UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.pasat import PasatEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class PasatLite(BaseMode):
    key = "pasat"
    title = "Add Stream"

    def start(self):
        self.engine = PasatEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["pasat"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["pasat"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False

        if trial.correct_sum is None:
            self.update_hud("First number — just remember it", T.MODE_COLORS["pasat"])
        else:
            self.update_hud("What is THIS + PREVIOUS?", T.MODE_COLORS["pasat"])

        Label(self.play, text="Paced serial addition", size=11, color=T.TEXT_DIM).pack(pady=(10, 4))
        card = tk.Canvas(self.play, width=160, height=160, bg=T.BG_CARD, highlightthickness=0)
        card.pack(pady=10)
        card.create_oval(20, 20, 140, 140, fill=T.BG_ELEVATED, outline=T.MODE_COLORS["pasat"], width=3)
        card.create_text(80, 80, text=str(trial.number), font=font(48, bold=True), fill=T.TEXT)

        def finish(val: int | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            event = self.engine.choose(val)
            if event.get("warmup"):
                self.update_hud(event["message"], T.TEXT_DIM)
            else:
                self.apply_event(event)
            self.next_or_finish()

        if trial.correct_sum is None:
            self.after(trial.stim_ms, lambda: finish(None))
            return

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=8)
        for i, v in enumerate(trial.options):
            RoundedButton(
                grid, text=str(v), command=lambda x=v: finish(x),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=70, height=44, font_size=14,
            ).grid(row=0, column=i, padx=5)
        self.after(trial.stim_ms, lambda: finish(None))
