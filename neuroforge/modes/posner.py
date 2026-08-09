"""Posner cueing UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.posner import PosnerEngine
from ..ui import Label, RoundedButton, clear_frame
from .base import BaseMode


class PosnerMode(BaseMode):
    key = "posner"
    title = "Cue Focus"

    def start(self):
        self.engine = PosnerEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["posner"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["posner"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Cue → then target. Respond to TARGET side.", T.MODE_COLORS["posner"])
        Label(self.play, text="Posner attention orienting", size=11, color=T.TEXT_DIM).pack(pady=(8, 4))

        stage = tk.Canvas(self.play, width=340, height=160, bg=T.BG_CARD, highlightthickness=0)
        stage.pack(pady=10)
        # boxes
        stage.create_rectangle(40, 40, 120, 120, outline=T.TEXT_MUTED, width=2)
        stage.create_rectangle(220, 40, 300, 120, outline=T.TEXT_MUTED, width=2)
        stage.create_text(170, 20, text="+", fill=T.TEXT_DIM, font=("Segoe UI", 16))

        def show_cue():
            if not self._alive:
                return
            if trial.cue_side == "left":
                stage.create_text(80, 80, text="→", fill=T.GOLD, font=("Segoe UI", 28, "bold"), tags="cue")
            elif trial.cue_side == "right":
                stage.create_text(260, 80, text="←", fill=T.GOLD, font=("Segoe UI", 28, "bold"), tags="cue")
            else:
                stage.create_text(170, 80, text="◆", fill=T.TEXT_MUTED, font=("Segoe UI", 20), tags="cue")
            self.after(trial.cue_ms + trial.soa_ms, show_target)

        def show_target():
            if not self._alive:
                return
            stage.delete("cue")
            cx = 80 if trial.target_side == "left" else 260
            stage.create_oval(cx - 18, 62, cx + 18, 98, fill=T.TEAL, outline="", tags="tgt")
            self.update_hud("Where is the target?", T.TEAL)

            row = tk.Frame(self.play, bg=T.BG_DEEP)
            row.pack(pady=12)

            def answer(side: str | None):
                if self._answered or not self._alive:
                    return
                self._answered = True
                self.cancel_timers()
                self.apply_event(self.engine.answer(side))
                self.next_or_finish()

            RoundedButton(row, text="← LEFT", command=lambda: answer("left"),
                          bg=T.ACCENT, fg=T.BG_DEEP, width=140, height=48).pack(side="left", padx=8)
            RoundedButton(row, text="RIGHT →", command=lambda: answer("right"),
                          bg=T.TEAL, fg=T.BG_DEEP, width=140, height=48).pack(side="left", padx=8)
            self.play.focus_set()
            self.play.bind("<Left>", lambda e: answer("left"))
            self.play.bind("<Right>", lambda e: answer("right"))
            self.after(trial.deadline_ms, lambda: answer(None))

        self.after(300, show_cue)
