"""Partial report UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.partial import LETTERS, PartialReportEngine
from ..logic.scoring import apply_hit
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class PartialMode(BaseMode):
    key = "partial"
    title = "Flash Report"

    def start(self):
        self.engine = PartialReportEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["partial"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["partial"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._accepting = False
        self._done = False
        self.update_hud("Memorize the grid…", T.MODE_COLORS["partial"])
        Label(self.play, text="Sperling-style partial report", size=11, color=T.TEXT_DIM).pack(pady=(6, 4))

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=8)
        cells = []
        for i, let in enumerate(trial.grid):
            r, c = divmod(i, trial.cols)
            lab = tk.Label(grid, text=let, font=font(18, bold=True), fg=T.TEXT, bg=T.BG_CARD, width=3, height=1)
            lab.grid(row=r, column=c, padx=3, pady=3)
            cells.append(lab)
        self._trial = trial

        def blank_and_cue():
            if not self._alive or self._done:
                return
            for lab in cells:
                lab.configure(text="·", fg=T.TEXT_MUTED)
            for c in range(trial.cols):
                cells[trial.cue_row * trial.cols + c].configure(bg=T.BG_ELEVATED, fg=T.GOLD)
            self.update_hud(f"Report ROW {trial.cue_row + 1} left→right", T.TEAL)
            self._accepting = True
            pad = tk.Frame(self.play, bg=T.BG_DEEP)
            pad.pack(pady=8)
            for i, let in enumerate(LETTERS[:18]):
                RoundedButton(
                    pad, text=let, command=lambda L=let: self._tap(L),
                    bg=T.BG_ELEVATED, fg=T.TEXT, width=36, height=32, font_size=11,
                ).grid(row=i // 9, column=i % 9, padx=2, pady=2)
            self.after(trial.deadline_ms, self._timeout)

        self.after(trial.encode_ms, blank_and_cue)

    def _timeout(self):
        if self._done or not self._alive or not self._accepting:
            return
        self._done = True
        self._accepting = False
        self.engine.ad.observe(False)
        event = apply_hit(self.engine.state, 12, False, "Time's up")
        self.apply_event(event)
        self.next_or_finish()

    def _tap(self, let: str):
        if not self._accepting or not self._alive or self._done:
            return
        event = self.engine.tap(let)
        if event is None:
            return
        self._done = True
        self._accepting = False
        self.cancel_timers()
        self.apply_event(event)
        self.next_or_finish()
