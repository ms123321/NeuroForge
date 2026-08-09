"""Stop-signal UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.stop import StopEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class StopSignal(BaseMode):
    key = "stop"
    title = "Stop Signal"

    def start(self):
        self.engine = StopEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["stop"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["stop"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud(
            "Arrow = GO  ·  Red flash = STOP (do not press)",
            T.MODE_COLORS["stop"],
        )
        Label(self.play, text="← / → or click the arrow", size=11, color=T.TEXT_DIM).pack(pady=(10, 6))

        self._canvas = tk.Canvas(self.play, width=280, height=180, bg=T.BG_CARD, highlightthickness=0)
        self._canvas.pack(pady=12)
        self._arrow = self._canvas.create_text(
            140, 90, text=trial.direction, font=font(56, bold=True), fill=T.TEXT
        )

        def press(direction: str):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            self.apply_event(self.engine.respond(True, direction))
            self.next_or_finish()

        def on_click(_e=None):
            press(trial.direction)

        self._canvas.bind("<Button-1>", on_click)
        self.play.focus_set()
        self.play.bind("<Left>", lambda e: press("<"))
        self.play.bind("<Right>", lambda e: press(">"))

        def maybe_stop():
            if not self._alive or self._answered:
                return
            if trial.is_stop:
                self._canvas.itemconfig(self._arrow, fill=T.CORAL)
                self._canvas.create_text(140, 150, text="STOP!", font=font(16, bold=True), fill=T.CORAL)
                # wait remaining window — if no press, success
                remain = max(200, trial.respond_window_ms - trial.go_ms)

                def timeout_stop():
                    if self._answered or not self._alive:
                        return
                    self._answered = True
                    self.apply_event(self.engine.respond(False))
                    self.next_or_finish()

                self.after(remain, timeout_stop)
            else:
                def timeout_go():
                    if self._answered or not self._alive:
                        return
                    self._answered = True
                    self.apply_event(self.engine.respond(False))
                    self.next_or_finish()

                self.after(trial.respond_window_ms, timeout_go)

        if trial.is_stop:
            self.after(trial.go_ms, maybe_stop)
        else:
            maybe_stop()
