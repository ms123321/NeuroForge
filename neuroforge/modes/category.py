"""Category Flex UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.category import CategoryEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class CategoryFlex(BaseMode):
    key = "category"
    title = "Category Flex"

    def start(self):
        self.engine = CategoryEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["category"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["category"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False

        rule_color = T.WARNING if trial.switched else T.TEAL
        rule_text = trial.rule_prompt
        if trial.switched:
            rule_text = f"⚡ NEW RULE: {trial.rule_prompt}"
        self.update_hud(rule_text, rule_color)

        Label(self.play, text="Does this word fit the rule?", size=12, color=T.TEXT_DIM).pack(
            pady=(14, 8)
        )

        card = tk.Canvas(self.play, width=280, height=110, bg=T.BG_CARD, highlightthickness=0)
        card.pack(pady=10)
        card.create_text(140, 55, text=trial.word, font=font(28, bold=True), fill=T.TEXT)

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=18)

        def answer(yes: bool | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.answer(yes))
            self.next_or_finish()

        RoundedButton(
            row, text="YES", command=lambda: answer(True),
            bg=T.TEAL, fg=T.BG_DEEP, width=130, height=52,
        ).pack(side="left", padx=10)
        RoundedButton(
            row, text="NO", command=lambda: answer(False),
            bg=T.CORAL, fg=T.BG_DEEP, width=130, height=52,
        ).pack(side="left", padx=10)

        self.play.focus_set()
        self.play.bind("y", lambda e: answer(True))
        self.play.bind("n", lambda e: answer(False))
        self.after(int(trial.time_limit * 1000), lambda: answer(None))
