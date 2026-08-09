"""Change detection UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.change import ChangeEngine
from ..ui import Label, RoundedButton, clear_frame
from .base import BaseMode


class ChangeDetect(BaseMode):
    key = "change"
    title = "Change Detect"

    def start(self):
        self.engine = ChangeEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["change"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["change"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Memorize the colors…", T.MODE_COLORS["change"])
        Label(self.play, text="Then decide: same or changed?", size=11, color=T.TEXT_DIM).pack(pady=(8, 4))

        canvas = tk.Canvas(self.play, width=320, height=220, bg=T.BG_CARD, highlightthickness=0)
        canvas.pack(pady=8)
        self._canvas = canvas
        self._draw_array(trial.sample)

        def show_test():
            if not self._alive:
                return
            clear_frame(self.play)
            self.update_hud("Same or changed?", T.MODE_COLORS["change"])
            c2 = tk.Canvas(self.play, width=320, height=220, bg=T.BG_CARD, highlightthickness=0)
            c2.pack(pady=8)
            for x, y, col in trial.test:
                px, py = 20 + x * 280, 20 + y * 180
                c2.create_oval(px - 14, py - 14, px + 14, py + 14, fill=col, outline="")

            row = tk.Frame(self.play, bg=T.BG_DEEP)
            row.pack(pady=12)

            def answer(changed: bool | None):
                if self._answered or not self._alive:
                    return
                self._answered = True
                self.cancel_timers()
                self.apply_event(self.engine.answer(changed))
                self.next_or_finish()

            RoundedButton(row, text="SAME", command=lambda: answer(False),
                          bg=T.TEAL, fg=T.BG_DEEP, width=130, height=48).pack(side="left", padx=8)
            RoundedButton(row, text="CHANGED", command=lambda: answer(True),
                          bg=T.CORAL, fg=T.BG_DEEP, width=130, height=48).pack(side="left", padx=8)
            self.after(int(trial.time_limit * 1000), lambda: answer(None))

        self.after(trial.encode_ms, show_test)

    def _draw_array(self, items):
        for x, y, col in items:
            px, py = 20 + x * 280, 20 + y * 180
            self._canvas.create_oval(px - 14, py - 14, px + 14, py + 14, fill=col, outline="")
