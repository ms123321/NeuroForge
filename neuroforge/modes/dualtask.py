"""Cognitive dual-task UI — letter 1-back + digit memory probe."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.dualtask import DualTaskEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class DualTaskMode(BaseMode):
    key = "dualtask"
    title = "Dual Load"

    def start(self):
        self.engine = DualTaskEngine(self.level)
        self.rounds = self.engine.rounds
        self._phase = "idle"  # idle | letter | digit | done
        self.build_shell(T.MODE_COLORS["dualtask"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["dualtask"])

    def next_round(self):
        if not self._alive:
            return
        self.cancel_timers()
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._trial = trial
        self._phase = "letter"

        if trial.is_first:
            self.update_hud("First trial — pick NEW letter · remember the gold digit", T.MODE_COLORS["dualtask"])
        else:
            self.update_hud("Is the letter SAME as last? · remember the gold digit", T.MODE_COLORS["dualtask"])

        Label(
            self.play,
            text="Primary: letter match   ·   Secondary: store the digit",
            size=11,
            color=T.TEXT_DIM,
        ).pack(pady=(8, 4))

        card = tk.Canvas(self.play, width=300, height=130, bg=T.BG_CARD, highlightthickness=0)
        card.pack(pady=10)
        card.create_text(90, 55, text=trial.letter, font=font(44, bold=True), fill=T.TEXT)
        card.create_text(220, 55, text=str(trial.digit), font=font(44, bold=True), fill=T.GOLD)
        card.create_text(90, 105, text="letter", fill=T.TEXT_MUTED, font=("Segoe UI", 10))
        card.create_text(220, 105, text="digit to store", fill=T.TEXT_MUTED, font=("Segoe UI", 10))

        if trial.is_first:
            Label(
                self.play,
                text="No previous letter yet → choose NEW",
                size=11,
                color=T.WARNING,
            ).pack(pady=(0, 6))

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=12)

        RoundedButton(
            row,
            text="SAME letter",
            command=lambda: self._on_letter(True),
            bg=T.TEAL,
            fg=T.BG_DEEP,
            width=140,
            height=48,
            font_size=12,
        ).pack(side="left", padx=8)
        RoundedButton(
            row,
            text="NEW letter",
            command=lambda: self._on_letter(False),
            bg=T.ACCENT,
            fg=T.BG_DEEP,
            width=140,
            height=48,
            font_size=12,
        ).pack(side="left", padx=8)

        # Letter timeout → treat as wrong "NEW" guess only if still in letter phase
        self.after(trial.deadline_ms, self._letter_timeout)

    def _letter_timeout(self):
        if not self._alive or self._phase != "letter":
            return
        # Timeout counts as incorrect (didn't answer in time)
        self._finish_letter(said_match=False, timed_out=True)

    def _on_letter(self, said_match: bool):
        if not self._alive or self._phase != "letter":
            return
        self._finish_letter(said_match, timed_out=False)

    def _finish_letter(self, said_match: bool, timed_out: bool = False):
        if self._phase != "letter":
            return
        self.cancel_timers()
        trial = self._trial

        if timed_out:
            # Force a wrong letter outcome on timeout
            expected = False if trial.is_first else trial.letter_match
            # Pick the wrong answer deliberately
            said_match = not expected

        event = self.engine.answer_letter(said_match)
        if timed_out:
            event = dict(event)
            event["message"] = "Too slow on letter"
            event["good"] = False
        self.apply_event(event)

        if trial.probe_digit and trial.previous_digit is not None:
            self._phase = "digit"
            self.after(400, self._show_digit_probe)
        else:
            self._complete_trial()

    def _show_digit_probe(self):
        if not self._alive or self._phase != "digit":
            return
        self.cancel_timers()
        clear_frame(self.play)
        trial = self._trial

        self.update_hud("What was the PREVIOUS gold digit?", T.WARNING)
        Label(
            self.play,
            text="Secondary probe — digit from the last trial (not the one you just saw)",
            size=11,
            color=T.TEXT_DIM,
            wrap=340,
        ).pack(pady=(12, 8))

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=10)

        for i in range(10):
            RoundedButton(
                grid,
                text=str(i),
                command=lambda x=i: self._on_digit(x),
                bg=T.BG_ELEVATED,
                fg=T.TEXT,
                width=52,
                height=44,
                font_size=14,
            ).grid(row=i // 5, column=i % 5, padx=4, pady=4)

        self.after(4000, self._digit_timeout)

    def _digit_timeout(self):
        if not self._alive or self._phase != "digit":
            return
        self._on_digit(None)

    def _on_digit(self, value: int | None):
        if not self._alive or self._phase != "digit":
            return
        self.cancel_timers()
        event = self.engine.answer_digit(value)
        if not event.get("warmup"):
            self.apply_event(event)
        self._complete_trial()

    def _complete_trial(self):
        if self._phase == "done":
            return
        self._phase = "done"
        self.cancel_timers()
        self.engine.commit_trial()
        self.next_or_finish()
