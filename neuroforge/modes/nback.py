"""N-Back Lite UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.nback import NBackEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class NBackLite(BaseMode):
    key = "nback"
    title = "N-Back Lite"

    def start(self):
        self.engine = NBackEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["nback"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["nback"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud(f"{trial.n}-Back · same as {trial.n} ago?", T.PINK)

        Label(
            self.play,
            text=f"N = {trial.n}   ·   Match = same letter as {trial.n} step(s) back",
            size=11, color=T.TEXT_DIM,
        ).pack(pady=(12, 8))

        card = tk.Canvas(self.play, width=160, height=160, bg=T.BG_CARD, highlightthickness=0)
        card.pack(pady=12)
        card.create_oval(20, 20, 140, 140, fill=T.BG_ELEVATED, outline=T.PINK, width=3)
        card.create_text(80, 80, text=trial.letter, font=font(48, bold=True), fill=T.TEXT)

        if self.level <= 3 and len(trial.history) > 1:
            trail = " → ".join(trial.history[-(trial.n + 2):])
            Label(self.play, text=f"Recent: {trail}", size=10, color=T.TEXT_MUTED).pack()

        btn_row = tk.Frame(self.play, bg=T.BG_DEEP)
        btn_row.pack(pady=20)

        def answer(said_match: bool, timed_out: bool = False):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            event = self.engine.answer(said_match, timed_out=timed_out)
            self.apply_event(event)
            self.next_or_finish()

        RoundedButton(
            btn_row, text="MATCH", command=lambda: answer(True),
            bg=T.TEAL, fg=T.BG_DEEP, width=140, height=52,
        ).pack(side="left", padx=10)
        RoundedButton(
            btn_row, text="NO MATCH", command=lambda: answer(False),
            bg=T.CORAL, fg=T.BG_DEEP, width=140, height=52,
        ).pack(side="left", padx=10)

        self.play.focus_set()
        self.play.bind("m", lambda e: answer(True))
        self.play.bind("n", lambda e: answer(False))
        self.play.bind("<Left>", lambda e: answer(False))
        self.play.bind("<Right>", lambda e: answer(True))

        self.after(trial.stim_ms, lambda: answer(False, timed_out=True))
