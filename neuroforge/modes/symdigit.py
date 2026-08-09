"""Symbol-digit UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.symdigit import SymDigitEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class SymDigitMode(BaseMode):
    key = "symdigit"
    title = "Symbol Code"

    def start(self):
        self.engine = SymDigitEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["symdigit"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["symdigit"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud(f"Code the symbol  ·  {trial.deadline_ms}ms", T.MODE_COLORS["symdigit"])
        Label(self.play, text="SDMT-inspired processing speed", size=11, color=T.TEXT_DIM).pack(pady=(6, 4))

        # legend
        key_fr = tk.Frame(self.play, bg=T.BG_CARD, padx=8, pady=8)
        key_fr.pack(fill="x", pady=6)
        for sym, dig in trial.key_map:
            cell = tk.Frame(key_fr, bg=T.BG_CARD)
            cell.pack(side="left", padx=4)
            Label(cell, text=sym, size=14, bold=True, color=T.TEXT).pack()
            Label(cell, text=str(dig), size=11, color=T.GOLD).pack()

        Label(self.play, text=trial.probe_symbol, size=42, bold=True, color=T.ACCENT_SOFT).pack(pady=12)

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=8)

        def pick(d: int | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.choose(d))
            self.next_or_finish()

        for d in trial.options:
            RoundedButton(
                row, text=str(d), command=lambda x=d: pick(x),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=60, height=48, font_size=16,
            ).pack(side="left", padx=6)
        self.after(trial.deadline_ms, lambda: pick(None))
