"""CPT-AX UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.cpt import CptEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class CptMode(BaseMode):
    key = "cpt"
    title = "AX Vigil"

    def start(self):
        self.engine = CptEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["cpt"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["cpt"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("TAP only when A is followed by X", T.MODE_COLORS["cpt"])
        Label(self.play, text="CPT-AX · sustained attention / vigilance", size=11, color=T.TEXT_DIM).pack(pady=(10, 6))

        canvas = tk.Canvas(self.play, width=180, height=180, bg=T.BG_CARD, highlightthickness=0)
        canvas.pack(pady=12)
        canvas.create_oval(25, 25, 155, 155, fill=T.BG_ELEVATED, outline=T.MODE_COLORS["cpt"], width=3)
        canvas.create_text(90, 90, text=trial.letter, font=font(48, bold=True), fill=T.TEXT)

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
