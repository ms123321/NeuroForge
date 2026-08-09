"""Focus Pulse UI — Go/No-Go."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.focus import FocusEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class FocusPulse(BaseMode):
    key = "focus"
    title = "Focus Pulse"

    def start(self):
        self.engine = FocusEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["focus"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["focus"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self.update_hud("Watch…", T.TEXT_DIM)
        self._responded = False

        fix = Label(self.play, text="+", size=36, bold=True, color=T.TEXT_MUTED)
        fix.pack(expand=True)

        def show_stim():
            if not self._alive:
                return
            clear_frame(self.play)
            is_go = trial.is_go
            color = T.TEAL if is_go else T.CORAL
            shape = "●" if is_go else "■"
            self.update_hud("TAP green · HOLD on red", T.TEXT_DIM)

            canvas = tk.Canvas(
                self.play, width=280, height=280, bg=T.BG_DEEP, highlightthickness=0
            )
            canvas.pack(expand=True)
            canvas.create_oval(40, 40, 240, 240, fill=color, outline="")
            canvas.create_text(140, 140, text=shape, font=font(42, bold=True), fill=T.BG_DEEP)

            def on_tap(_e=None):
                if self._responded or not self._alive:
                    return
                self._responded = True
                self.cancel_timers()
                event = self.engine.respond(tapped=True, timed_out=False)
                self.apply_event(event)
                self.next_or_finish()

            canvas.bind("<Button-1>", on_tap)
            self.play.focus_set()
            self.play.bind("<space>", on_tap)
            self.play.bind("<Return>", on_tap)

            def timeout():
                if self._responded or not self._alive:
                    return
                self._responded = True
                event = self.engine.respond(tapped=False, timed_out=True)
                self.apply_event(event)
                self.next_or_finish()

            self.after(trial.stimulus_ms, timeout)

        self.after(trial.isi_ms, show_stim)
