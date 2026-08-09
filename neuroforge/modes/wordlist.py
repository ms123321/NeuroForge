"""Word list learning UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.wordlist import WordListEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class WordListMode(BaseMode):
    key = "wordlist"
    title = "Word List"

    def start(self):
        self.engine = WordListEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["wordlist"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["wordlist"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._done = False
        self.update_hud("Study the word list…", T.MODE_COLORS["wordlist"])
        Label(self.play, text="RAVLT/CVLT-inspired free recall", size=11, color=T.TEXT_DIM).pack(pady=(6, 4))

        box = tk.Frame(self.play, bg=T.BG_CARD, padx=12, pady=10)
        box.pack(pady=8)
        Label(box, text="  ·  ".join(trial.study), size=13, bold=True, color=T.TEXT, wrap=320).pack()

        def recall_phase():
            if not self._alive:
                return
            clear_frame(self.play)
            self.update_hud("Tap all words you remember (no extras)", T.TEAL)
            Label(self.play, text="Free recall — avoid intrusions", size=11, color=T.TEXT_DIM).pack(pady=6)
            grid = tk.Frame(self.play, bg=T.BG_DEEP)
            grid.pack(pady=8)

            def tap(w: str):
                if self._done or not self._alive:
                    return
                event = self.engine.tap(w)
                if event is None:
                    return
                self._done = True
                self.cancel_timers()
                self.apply_event(event)
                self.next_or_finish()

            for i, w in enumerate(trial.pool):
                RoundedButton(
                    grid, text=w, command=lambda x=w: tap(x),
                    bg=T.BG_ELEVATED, fg=T.TEXT, width=90, height=36, font_size=11,
                ).grid(row=i // 4, column=i % 4, padx=3, pady=3)

            def done_early():
                if self._done or not self._alive:
                    return
                self._done = True
                self.cancel_timers()
                self.apply_event(self.engine.finish_early())
                self.next_or_finish()

            RoundedButton(
                self.play, text="I'm done recalling", command=done_early,
                bg=T.ACCENT, fg=T.BG_DEEP, width=200, height=40, font_size=12,
            ).pack(pady=10)
            self.after(trial.deadline_ms, done_early)

        self.after(trial.study_ms, recall_phase)
