"""Backward digit span UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.digits import DigitsEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class DigitSpan(BaseMode):
    key = "digits"
    title = "Digit Reverse"

    def start(self):
        self.engine = DigitsEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["digits"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["digits"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._accepting = False
        self.update_hud(f"Watch {len(trial.forward)} digits…", T.MODE_COLORS["digits"])
        Label(self.play, text="Then enter them BACKWARDS", size=12, color=T.TEXT_DIM).pack(pady=(10, 6))

        self._display = Label(self.play, text="", size=42, bold=True, color=T.GOLD)
        self._display.pack(expand=True)

        self._trial = trial
        self.after(400, lambda: self._show_seq(0))

    def _show_seq(self, i: int):
        if not self._alive:
            return
        if i >= len(self._trial.forward):
            self._display.configure(text="?")
            self._build_pad()
            self._accepting = True
            self.update_hud("Type the reverse order", T.TEAL)
            return
        self._display.configure(text=str(self._trial.forward[i]))
        self.after(self._trial.flash_ms, lambda: self._blank(i))

    def _blank(self, i: int):
        if not self._alive:
            return
        self._display.configure(text="")
        self.after(180, lambda: self._show_seq(i + 1))

    def _build_pad(self):
        pad = tk.Frame(self.play, bg=T.BG_DEEP)
        pad.pack(pady=8)
        for d in range(10):
            RoundedButton(
                pad, text=str(d), command=lambda x=d: self._tap(x),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=52, height=44, font_size=14,
            ).grid(row=d // 5, column=d % 5, padx=4, pady=4)

    def _tap(self, d: int):
        if not self._accepting or not self._alive:
            return
        event = self.engine.tap_digit(d)
        if event is None:
            self._display.configure(text=(self._display.cget("text") if self._display.cget("text") != "?" else "") + str(d))
            return
        self._accepting = False
        self.apply_event(event)
        self.next_or_finish()
