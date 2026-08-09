"""Quick Calc UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.calc import CalcEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class QuickCalc(BaseMode):
    key = "calc"
    title = "Quick Calc"

    def start(self):
        self.engine = CalcEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["calc"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["calc"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud(f"Solve  ·  {trial.time_limit:.1f}s", T.MODE_COLORS["calc"])
        Label(self.play, text="Pick the correct answer", size=12, color=T.TEXT_DIM).pack(pady=(12, 6))

        card = tk.Canvas(self.play, width=300, height=90, bg=T.BG_CARD, highlightthickness=0)
        card.pack(pady=10)
        card.create_text(150, 45, text=trial.expression, font=font(28, bold=True), fill=T.GOLD)

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=12)

        def pick(val: int | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(val))
            self.next_or_finish()

        for i, val in enumerate(trial.options):
            btn = RoundedButton(
                grid, text=str(val), command=lambda v=val: pick(v),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=130, height=46, font_size=16,
            )
            btn.grid(row=i // 2, column=i % 2, padx=8, pady=6)

        self.after(int(trial.time_limit * 1000), lambda: pick(None))
