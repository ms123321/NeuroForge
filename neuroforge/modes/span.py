"""Block Span UI — Corsi-style."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.span import SpanEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class BlockSpan(BaseMode):
    key = "span"
    title = "Block Span"

    def start(self):
        self.engine = SpanEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["span"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["span"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._accepting = False
        self.update_hud(f"Watch {len(trial.sequence)} blocks…", T.MODE_COLORS["span"])
        Label(self.play, text="Remember the order, then replay", size=12, color=T.TEXT_DIM).pack(
            pady=(8, 6)
        )

        grid = tk.Frame(self.play, bg=T.BG_DEEP)
        grid.pack(expand=True)
        self._cells: list[tk.Canvas] = []
        size = 72
        for i in range(9):
            r, c = divmod(i, 3)
            cell = tk.Canvas(
                grid, width=size, height=size, bg=T.BG_CARD,
                highlightthickness=2, highlightbackground=T.BG_ELEVATED,
            )
            cell.grid(row=r, column=c, padx=6, pady=6)
            cell.create_rectangle(8, 8, size - 8, size - 8, fill=T.BG_ELEVATED, outline="", tags="blk")
            cell.bind("<Button-1>", lambda e, j=i: self._on_tap(j))
            self._cells.append(cell)

        self._trial = trial
        self.after(500, self._play_seq)

    def _flash(self, idx: int, on: bool):
        c = self._cells[idx]
        if on:
            c.itemconfig("blk", fill=T.ACCENT)
            c.configure(highlightbackground=T.ACCENT)
        else:
            c.itemconfig("blk", fill=T.BG_ELEVATED)
            c.configure(highlightbackground=T.BG_ELEVATED)

    def _play_seq(self, step: int = 0):
        if not self._alive:
            return
        if step >= len(self._trial.sequence):
            self._accepting = True
            self.update_hud("Your turn — tap the blocks", T.TEAL)
            return
        idx = self._trial.sequence[step]
        self._flash(idx, True)
        self.after(self._trial.flash_ms, lambda: self._unflash(idx, step))

    def _unflash(self, idx: int, step: int):
        if not self._alive:
            return
        self._flash(idx, False)
        self.after(150, lambda: self._play_seq(step + 1))

    def _on_tap(self, idx: int):
        if not self._accepting or not self._alive:
            return
        self._flash(idx, True)
        self.after(100, lambda: self._flash(idx, False))
        event = self.engine.tap(idx)
        if event is None:
            return
        self._accepting = False
        self.apply_event(event)
        self.next_or_finish()
