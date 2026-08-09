"""Switch Path UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.switch import SwitchEngine
from ..ui import Label, clear_frame
from .base import BaseMode


class SwitchPath(BaseMode):
    key = "switch"
    title = "Switch Path"

    def start(self):
        self.engine = SwitchEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["switch"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["switch"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()

        rule_color = T.WARNING if trial.switched else T.TEAL
        rule_text = f"RULE: match {trial.rule.upper()}"
        if trial.switched:
            rule_text = f"⚡ RULE CHANGED → match {trial.rule.upper()}"
        self.update_hud(rule_text, rule_color)

        Label(
            self.play,
            text=f"Target  {trial.target_shape}   {trial.target_color_name}",
            size=16, bold=True, color=trial.target_color,
        ).pack(pady=(12, 4))
        Label(
            self.play, text="Pick the option that matches the current rule",
            size=11, color=T.TEXT_DIM,
        ).pack(pady=(0, 8))

        target_card = tk.Canvas(self.play, width=100, height=100, bg=T.BG_CARD, highlightthickness=0)
        target_card.pack(pady=6)
        target_card.create_oval(15, 15, 85, 85, fill=trial.target_color, outline="")
        target_card.create_text(
            50, 50, text=trial.target_shape, font=("Segoe UI", 28, "bold"), fill=T.BG_DEEP
        )

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=12)
        cols = 2 if len(trial.options) <= 2 else 2

        for i, opt in enumerate(trial.options):
            shape, cname, cval = opt
            btn_frame = tk.Frame(grid, bg=T.BG_CARD, padx=8, pady=8)
            btn_frame.grid(row=i // cols, column=i % cols, padx=8, pady=8)
            c = tk.Canvas(btn_frame, width=80, height=80, bg=T.BG_CARD, highlightthickness=0)
            c.pack()
            c.create_oval(8, 8, 72, 72, fill=cval, outline="")
            c.create_text(40, 40, text=shape, font=("Segoe UI", 22, "bold"), fill=T.BG_DEEP)
            Label(btn_frame, text=cname, size=10, color=T.TEXT_DIM).pack()

            def pick(_e=None, idx=i):
                if not self._alive:
                    return
                self.apply_event(self.engine.choose(idx))
                self.next_or_finish()

            c.bind("<Button-1>", pick)
            btn_frame.bind("<Button-1>", pick)
