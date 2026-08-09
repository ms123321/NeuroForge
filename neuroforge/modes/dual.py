"""Dual N-Back UI — letter + position."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.dual import DualNBackEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class DualNBack(BaseMode):
    key = "dual"
    title = "Dual Stream"

    def start(self):
        self.engine = DualNBackEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["dual"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["dual"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False
        self._letter_match = False
        self._pos_match = False

        self.update_hud(
            f"Dual {trial.n}-Back · toggle matches, then Submit",
            T.MODE_COLORS["dual"],
        )
        Label(
            self.play,
            text=f"Is LETTER and/or POSITION the same as {trial.n} step(s) ago?",
            size=11, color=T.TEXT_DIM, wrap=360,
        ).pack(pady=(8, 6))

        # 3x3 grid with letter in active cell
        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=8)
        cell_size = 56
        for i in range(9):
            r, c = divmod(i, 3)
            active = i == trial.position
            bg = T.BG_ELEVATED if active else T.BG_CARD
            canvas = tk.Canvas(
                grid, width=cell_size, height=cell_size, bg=bg,
                highlightthickness=2,
                highlightbackground=T.ACCENT if active else T.BG_ELEVATED,
            )
            canvas.grid(row=r, column=c, padx=4, pady=4)
            if active:
                canvas.create_text(
                    cell_size // 2, cell_size // 2,
                    text=trial.letter, font=font(22, bold=True), fill=T.TEXT,
                )

        # Toggle buttons
        toggles = tk.Frame(self.play, bg=T.BG_DEEP)
        toggles.pack(pady=12)

        self._l_btn = RoundedButton(
            toggles, text="Letter: NO", command=self._toggle_letter,
            bg=T.BG_ELEVATED, fg=T.TEXT, width=150, height=44, font_size=12,
        )
        self._l_btn.pack(side="left", padx=8)
        self._p_btn = RoundedButton(
            toggles, text="Position: NO", command=self._toggle_pos,
            bg=T.BG_ELEVATED, fg=T.TEXT, width=150, height=44, font_size=12,
        )
        self._p_btn.pack(side="left", padx=8)

        RoundedButton(
            self.play, text="Submit",
            command=self._submit,
            bg=T.MODE_COLORS["dual"], fg=T.BG_DEEP, width=200, height=48,
        ).pack(pady=8)

        Label(self.play, text="L key · P key · Enter to submit", size=10, color=T.TEXT_MUTED).pack()

        self.play.focus_set()
        self.play.bind("l", lambda e: self._toggle_letter())
        self.play.bind("p", lambda e: self._toggle_pos())
        self.play.bind("<Return>", lambda e: self._submit())

        self.after(trial.stim_ms, self._timeout)

    def _toggle_letter(self):
        if self._answered:
            return
        self._letter_match = not self._letter_match
        if self._letter_match:
            self._l_btn.set_text("Letter: YES")
            self._l_btn.set_colors(T.TEAL, T.BG_DEEP)
        else:
            self._l_btn.set_text("Letter: NO")
            self._l_btn.set_colors(T.BG_ELEVATED, T.TEXT)

    def _toggle_pos(self):
        if self._answered:
            return
        self._pos_match = not self._pos_match
        if self._pos_match:
            self._p_btn.set_text("Position: YES")
            self._p_btn.set_colors(T.TEAL, T.BG_DEEP)
        else:
            self._p_btn.set_text("Position: NO")
            self._p_btn.set_colors(T.BG_ELEVATED, T.TEXT)

    def _submit(self):
        if self._answered or not self._alive:
            return
        self._answered = True
        self.cancel_timers()
        event = self.engine.answer(self._letter_match, self._pos_match)
        self.apply_event(event)
        self.next_or_finish()

    def _timeout(self):
        if self._answered or not self._alive:
            return
        # timeout = both no
        self._letter_match = False
        self._pos_match = False
        self._submit()
