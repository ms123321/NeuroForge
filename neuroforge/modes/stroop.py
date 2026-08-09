"""Stroop conflict UI — name the ink color."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.stroop import COLOR_WORDS, StroopEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode

# Map name -> hex for option buttons
NAME_TO_HEX = {n: h for n, h in COLOR_WORDS}


class StroopClash(BaseMode):
    key = "stroop"
    title = "Color Clash"

    def start(self):
        self.engine = StroopEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["stroop"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["stroop"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._answered = False

        kind = "match" if trial.congruent else "CONFLICT"
        self.update_hud(f"Name the INK color  ·  {kind}", T.MODE_COLORS["stroop"])
        Label(
            self.play,
            text="Ignore the word. Tap the color of the letters.",
            size=11, color=T.TEXT_DIM,
        ).pack(pady=(12, 8))

        card = tk.Canvas(self.play, width=280, height=120, bg=T.BG_CARD, highlightthickness=0)
        card.pack(pady=12)
        card.create_text(
            140, 60, text=trial.word,
            font=font(36, bold=True), fill=trial.ink_hex,
        )

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=12)

        def pick(name: str):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            event = self.engine.choose(name)
            self.apply_event(event)
            self.next_or_finish()

        for i, name in enumerate(trial.options):
            hex_c = NAME_TO_HEX.get(name, T.ACCENT)
            btn = RoundedButton(
                grid, text=name, command=lambda n=name: pick(n),
                bg=hex_c, fg=T.BG_DEEP, width=140, height=44, font_size=13,
            )
            btn.grid(row=i // 2, column=i % 2, padx=8, pady=6)

        def timeout():
            if self._answered or not self._alive:
                return
            self._answered = True
            event = self.engine.choose(None)
            self.apply_event(event)
            self.next_or_finish()

        self.after(int(trial.time_limit * 1000), timeout)
