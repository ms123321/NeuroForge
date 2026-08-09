"""WCST-lite rule discovery UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.rulesearch import RuleSearchEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class RuleSearchMode(BaseMode):
    key = "rulesearch"
    title = "Rule Hunt"

    def start(self):
        self.engine = RuleSearchEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["rulesearch"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["rulesearch"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        msg = "⚡ Hidden rule changed!" if trial.rule_changed else "Match the card by the hidden rule"
        self.update_hud(msg, T.WARNING if trial.rule_changed else T.MODE_COLORS["rulesearch"])
        Label(
            self.play,
            text="WCST-inspired · sort by color, shape, or count (rule is hidden)",
            size=10, color=T.TEXT_DIM,
        ).pack(pady=(6, 4))

        # target
        t = trial.target
        tgt = tk.Canvas(self.play, width=120, height=100, bg=T.BG_CARD, highlightthickness=0)
        tgt.pack(pady=6)
        self._draw_card(tgt, t, 60, 50)

        Label(self.play, text="Which option matches?", size=11, color=T.TEXT_DIM).pack(pady=4)
        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=8)

        def pick(idx: int | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(idx))
            self.next_or_finish()

        for i, card in enumerate(trial.options):
            c = tk.Canvas(row, width=100, height=90, bg=T.BG_CARD, highlightthickness=2,
                          highlightbackground=T.BG_ELEVATED)
            c.pack(side="left", padx=6)
            self._draw_card(c, card, 50, 45)
            c.bind("<Button-1>", lambda e, j=i: pick(j))

        self.after(trial.deadline_ms, lambda: pick(None))

    def _draw_card(self, canvas, card, cx, cy):
        # draw count copies of shape
        spacing = 18
        start = cx - (card.count - 1) * spacing / 2
        for i in range(card.count):
            canvas.create_text(
                start + i * spacing, cy, text=card.shape,
                font=font(16, bold=True), fill=card.color_hex,
            )
