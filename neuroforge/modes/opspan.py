"""Operation span UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.opspan import OspanEngine
from ..ui import Label, RoundedButton, clear_frame, font
from .base import BaseMode


class OpSpan(BaseMode):
    key = "opspan"
    title = "Op Span"

    def start(self):
        self.engine = OspanEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["opspan"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["opspan"])

    def next_round(self):
        if not self._alive:
            return
        self.engine.next_trial()
        self.update_hud("Solve math · remember letters", T.MODE_COLORS["opspan"])
        self._show_math()

    def _show_math(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.current
        item = trial.items[self.engine.item_i]
        self.update_hud(
            f"Math {self.engine.item_i + 1}/{len(trial.items)}",
            T.MODE_COLORS["opspan"],
        )
        Label(self.play, text="Solve quickly", size=11, color=T.TEXT_DIM).pack(pady=(10, 4))
        Label(self.play, text=item.expression, size=28, bold=True, color=T.GOLD).pack(pady=12)

        row = tk.Frame(self.play, bg=T.BG_DEEP)
        row.pack(pady=8)
        self._answered = False

        def pick(v: int | None):
            if self._answered or not self._alive:
                return
            self._answered = True
            self.cancel_timers()
            event = self.engine.answer_math(v)
            color = T.SUCCESS if event["good"] else T.ERROR
            self.update_hud(event["message"], color)
            self.after(250, self._show_letter)

        for v in item.math_options:
            RoundedButton(
                row, text=str(v), command=lambda x=v: pick(x),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=80, height=44, font_size=14,
            ).pack(side="left", padx=6)
        self.after(int(trial.math_time * 1000), lambda: pick(None))

    def _show_letter(self):
        if not self._alive:
            return
        clear_frame(self.play)
        item = self.engine.current.items[self.engine.item_i]
        Label(self.play, text="Remember this letter", size=12, color=T.TEXT_DIM).pack(pady=(20, 8))
        card = tk.Canvas(self.play, width=120, height=120, bg=T.BG_CARD, highlightthickness=0)
        card.pack(pady=10)
        card.create_text(60, 60, text=item.letter, font=font(42, bold=True), fill=T.TEXT)

        def cont():
            self.engine.ack_letter()
            if self.engine.phase == "recall":
                self._show_recall()
            else:
                self._show_math()

        self.after(900, cont)

    def _show_recall(self):
        if not self._alive:
            return
        clear_frame(self.play)
        target = self.engine.current.target_letters
        self._picked: list[str] = []
        self.update_hud(f"Recall {len(target)} letters in order", T.TEAL)
        Label(self.play, text="Tap letters in the order you saw them", size=11, color=T.TEXT_DIM).pack(
            pady=(8, 4)
        )
        self._seq_lbl = Label(self.play, text="(empty)", size=16, bold=True, color=T.GOLD)
        self._seq_lbl.pack(pady=8)

        # unique letter pool = targets + foils
        pool = list(dict.fromkeys(target + list("FHJKLNPQRSTY")))
        random_pool = pool[: max(8, len(target) + 3)]
        import random
        random.shuffle(random_pool)

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(pady=8)

        def tap(let: str):
            if len(self._picked) >= len(target):
                return
            self._picked.append(let)
            self._seq_lbl.configure(text=" ".join(self._picked))
            if len(self._picked) == len(target):
                self.apply_event(self.engine.recall(self._picked))
                self.next_or_finish()

        for i, let in enumerate(random_pool):
            RoundedButton(
                grid, text=let, command=lambda L=let: tap(L),
                bg=T.BG_ELEVATED, fg=T.TEXT, width=48, height=42, font_size=14,
            ).grid(row=i // 4, column=i % 4, padx=4, pady=4)
