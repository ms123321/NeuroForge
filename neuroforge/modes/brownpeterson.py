"""Brown-Peterson UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.brownpeterson import BrownPetersonEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class BrownPetersonMode(BaseMode):
    key = "brownpeterson"
    title = "Trigram Hold"

    def start(self):
        self.engine = BrownPetersonEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["brownpeterson"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["brownpeterson"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Remember the 3 letters…", T.MODE_COLORS["brownpeterson"])
        Label(self.play, text="Brown–Peterson · distractor during retention", size=11, color=T.TEXT_DIM).pack(
            pady=(8, 4)
        )
        Label(self.play, text=trial.trigram, size=40, bold=True, color=T.GOLD).pack(pady=20)

        def distract(i=0):
            if not self._alive:
                return
            if i >= len(trial.distractors):
                show_recall()
                return
            clear_frame(self.play)
            self.update_hud("Solve quickly (distractor)", T.WARNING)
            Label(self.play, text=trial.distractors[i], size=28, bold=True, color=T.TEXT).pack(pady=24)
            # auto-advance distractor (no need correct for core memory measure)
            self.after(trial.distract_ms // max(1, len(trial.distractors)), lambda: distract(i + 1))

        def show_recall():
            if not self._alive:
                return
            clear_frame(self.play)
            self.update_hud("What were the 3 letters?", T.TEAL)
            Label(self.play, text="Recall the trigram", size=12, color=T.TEXT_DIM).pack(pady=8)
            row = tk.Frame(self.play, bg=T.BG_DEEP)
            row.pack(pady=12)

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
                    bg=T.BG_ELEVATED, fg=T.TEXT, width=90, height=48, font_size=14,
                ).pack(side="left", padx=5)
            self.after(trial.deadline_ms, lambda: pick(None))

        self.after(trial.encode_ms, distract)
