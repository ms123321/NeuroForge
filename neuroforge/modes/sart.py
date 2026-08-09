"""SART UI — sustained attention."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.sart import SartEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class SartMode(BaseMode):
    key = "sart"
    title = "Sustained Go"

    def start(self):
        self.engine = SartEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["sart"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["sart"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("TAP every digit · HOLD on 3", T.MODE_COLORS["sart"])
        Label(self.play, text="SART — sustained attention to response", size=11, color=T.TEXT_DIM).pack(
            pady=(10, 6)
        )

        canvas = tk.Canvas(self.play, width=200, height=200, bg=T.BG_CARD, highlightthickness=0)
        canvas.pack(pady=12)
        canvas.create_oval(30, 30, 170, 170, fill=T.BG_ELEVATED, outline=T.MODE_COLORS["sart"], width=3)
        canvas.create_text(100, 100, text=str(trial.digit), font=font(56, bold=True), fill=T.TEXT)

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

        self.after(trial.stim_ms + trial.isi_ms, timeout)
