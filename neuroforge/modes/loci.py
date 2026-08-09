"""Method of loci / paired associate UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.loci import LociEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class LociMode(BaseMode):
    key = "loci"
    title = "Memory Palace"

    def start(self):
        self.engine = LociEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["loci"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["loci"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Study place → item pairs…", T.MODE_COLORS["loci"])
        Label(self.play, text="Method of loci / paired associates", size=11, color=T.TEXT_DIM).pack(pady=(6, 4))

        study = tk.Frame(self.play, bg=T.BG_CARD, padx=12, pady=10)
        study.pack(pady=8, fill="x", padx=20)
        for place, item in trial.pairs:
            Label(study, text=f"{place}  →  {item}", size=14, bold=True, color=T.TEXT).pack(anchor="w", pady=2)

        def show_cue():
            if not self._alive:
                return
            clear_frame(self.play)
            self.update_hud(f"What was at: {trial.cue_place}?", T.TEAL)
            Label(self.play, text=trial.cue_place, size=24, bold=True, color=T.GOLD).pack(pady=16)
            row = tk.Frame(self.play, bg=T.BG_DEEP)
            row.pack(pady=10)

            def pick(v: str | None):
                if self._answered or not self._alive:
                    return
                self._answered = True
                self.cancel_timers()
                self.apply_event(self.engine.choose(v))
                self.next_or_finish()

            for opt in trial.options:
                RoundedButton(
                    row, text=opt, command=lambda x=opt: pick(x),
                    bg=T.BG_ELEVATED, fg=T.TEXT, width=90, height=44, font_size=12,
                ).pack(side="left", padx=5)
            self.after(trial.deadline_ms, lambda: pick(None))

        self.after(trial.study_ms, show_cue)
