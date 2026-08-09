"""Choice RT UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.choicert import ChoiceRtEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class ChoiceRtMode(BaseMode):
    key = "choicert"
    title = "Choice RT"

    def start(self):
        self.engine = ChoiceRtEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["choicert"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["choicert"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self.update_hud("Respond as FAST as you can", T.MODE_COLORS["choicert"])
        Label(self.play, text="Choice reaction time · clinical psychomotor speed", size=11, color=T.TEXT_DIM).pack(
            pady=(8, 6)
        )

        # brief blank then stimulus
        stage = tk.Canvas(self.play, width=280, height=120, bg=T.BG_CARD, highlightthickness=0)
        stage.pack(pady=10)
        fix = stage.create_text(140, 60, text="+", font=font(24), fill=T.TEXT_MUTED)

        def show():
            if not self._alive:
                return
            stage.delete(fix)
            label = trial.side.upper()
            stage.create_text(140, 60, text=label, font=font(28, bold=True), fill=T.GOLD)
            self.engine._t0 = __import__("time").perf_counter()

            row = tk.Frame(self.play, bg=T.BG_DEEP)
            row.pack(pady=12)

            def ans(c: str | None):
                if self._answered or not self._alive:
                    return
                self._answered = True
                self.cancel_timers()
                self.apply_event(self.engine.answer(c))
                self.next_or_finish()

            if trial.n_choices == 2:
                RoundedButton(row, text="← LEFT", command=lambda: ans("left"), bg=T.ACCENT, fg=T.BG_DEEP, width=130, height=50).pack(side="left", padx=8)
                RoundedButton(row, text="RIGHT →", command=lambda: ans("right"), bg=T.TEAL, fg=T.BG_DEEP, width=130, height=50).pack(side="left", padx=8)
                self.play.focus_set()
                self.play.bind("<Left>", lambda e: ans("left"))
                self.play.bind("<Right>", lambda e: ans("right"))
            else:
                grid = tk.Frame(self.play, bg=T.BG_DEEP)
                grid.pack()
                for lab, key in (("TL", "tl"), ("TR", "tr"), ("BL", "bl"), ("BR", "br")):
                    RoundedButton(
                        grid, text=lab, command=lambda k=key: ans(k),
                        bg=T.BG_ELEVATED, fg=T.TEXT, width=70, height=44,
                    ).grid(row=0 if lab[0] == "T" else 1, column=0 if lab[1] == "L" else 1, padx=4, pady=4)
            self.after(trial.deadline_ms, lambda: ans(None))

        self.after(trial.isi_ms, show)
