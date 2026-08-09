"""Running span UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.running import LETTERS, RunningSpanEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class RunningSpanMode(BaseMode):
    key = "running"
    title = "Running Span"

    def start(self):
        self.engine = RunningSpanEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["running"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["running"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._accepting = False
        self.update_hud(f"Watch stream · recall last {trial.window}", T.MODE_COLORS["running"])
        Label(self.play, text="Running memory span — only the final items matter", size=11, color=T.TEXT_DIM).pack(
            pady=(8, 4)
        )
        self._disp = Label(self.play, text="", size=40, bold=True, color=T.GOLD)
        self._disp.pack(expand=True)
        self._trial = trial
        self.after(400, lambda: self._show(0))

    def _show(self, i: int):
        if not self._alive:
            return
        if i >= len(self._trial.stream):
            self._disp.configure(text="?")
            self._pad()
            self._accepting = True
            self.update_hud(f"Enter last {self._trial.window} letters", T.TEAL)
            return
        self._disp.configure(text=self._trial.stream[i])
        self.after(self._trial.flash_ms, lambda: self._blank(i))

    def _blank(self, i: int):
        if not self._alive:
            return
        self._disp.configure(text="")
        self.after(120, lambda: self._show(i + 1))

    def _pad(self):
        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=8)
        for i, let in enumerate(LETTERS):
            RoundedButton(
                grid, text=let, command=lambda L=let: self._tap(L),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=48, height=40, font_size=13,
            ).grid(row=i // 6, column=i % 6, padx=3, pady=3)

    def _tap(self, let: str):
        if not self._accepting or not self._alive:
            return
        event = self.engine.tap(let)
        if event is None:
            return
        self._accepting = False
        self.apply_event(event)
        self.next_or_finish()
