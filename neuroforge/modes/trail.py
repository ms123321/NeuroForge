"""Number Path UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.trail import TrailEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class NumberPath(BaseMode):
    key = "trail"
    title = "Number Path"

    def start(self):
        self.engine = TrailEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["trail"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["trail"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._done = False
        self._hit = set()
        hint = "1→2→3…" if trial.mode == "numbers" else "1→A→2→B→3…"
        self.update_hud(f"Tap in order  {hint}", T.MODE_COLORS["trail"])
        Label(
            self.play,
            text=f"Connect the path · {trial.time_limit:.0f}s",
            size=12, color=T.TEXT_DIM,
        ).pack(pady=(8, 6))

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=8)
        self._canvases: dict[str, tk.Canvas] = {}
        size = 58

        def on_tap(label: str):
            if self._done or not self._alive or label in self._hit:
                return
            event = self.engine.tap(label)
            if event is None:
                # correct step
                self._hit.add(label)
                c = self._canvases[label]
                c.configure(bg=T.TEAL, highlightbackground=T.TEAL)
                c.itemconfig("txt", fill=T.BG_DEEP)
                return
            if event.get("continue"):
                self.update_hud(event["message"], T.WARNING)
                return
            self._done = True
            self.cancel_timers()
            self.apply_event(event)
            self.next_or_finish()

        for i, label in enumerate(trial.labels):
            r, c = divmod(i, trial.cols)
            cell = tk.Canvas(
                grid, width=size, height=size, bg=T.BG_CARD,
                highlightthickness=2, highlightbackground=T.BG_ELEVATED,
            )
            cell.grid(row=r, column=c, padx=5, pady=5)
            cell.create_text(
                size // 2, size // 2, text=label,
                font=font(16, bold=True), fill=T.TEXT, tags="txt",
            )
            cell.bind("<Button-1>", lambda e, lab=label: on_tap(lab))
            self._canvases[label] = cell

        def timeout():
            if self._done or not self._alive:
                return
            self._done = True
            self.apply_event(self.engine.timeout())
            self.next_or_finish()

        self.after(int(trial.time_limit * 1000), timeout)
