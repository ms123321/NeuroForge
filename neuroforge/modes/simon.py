"""Simon task UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.simon import COLOR_HEX, SimonEngine
from ..ui import Label, RoundedButton, clear_frame
from .base import BaseMode


class SimonClash(BaseMode):
    key = "simon"
    title = "Simon Side"

    def start(self):
        self.engine = SimonEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["simon"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["simon"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        tag = "aligned" if trial.congruent else "CONFLICT"
        self.update_hud(f"Blue=LEFT · Gold=RIGHT  ·  {tag}", T.MODE_COLORS["simon"])
        Label(
            self.play,
            text="Respond by COLOR, not side (ignore location)",
            size=11, color=T.TEXT_DIM,
        ).pack(pady=(10, 6))

        stage = tk.Canvas(self.play, width=340, height=140, bg=T.BG_CARD, highlightthickness=0)
        stage.pack(pady=12)
        cx = 70 if trial.side == "left" else 270
        stage.create_oval(cx - 35, 35, cx + 35, 105, fill=COLOR_HEX[trial.color], outline="")
        stage.create_text(170, 125, text=f"appears on {trial.side.upper()}", fill=T.TEXT_MUTED,
                          font=("Segoe UI", 10))

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=16)

        def answer(side: str | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.answer(side))
            self.next_or_finish()

        RoundedButton(row, text="← LEFT (blue)", command=lambda: answer("left"),
                      bg="#6C8CFF", fg=T.BG_DEEP, width=150, height=50, font_size=12).pack(side="left", padx=8)
        RoundedButton(row, text="RIGHT (gold) →", command=lambda: answer("right"),
                      bg="#F5C542", fg=T.BG_DEEP, width=150, height=50, font_size=12).pack(side="left", padx=8)

        self.play.focus_set()
        self.play.bind("<Left>", lambda e: answer("left"))
        self.play.bind("<Right>", lambda e: answer("right"))
        self.after(int(trial.time_limit * 1000), lambda: answer(None))
