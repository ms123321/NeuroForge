"""Memory Lattice UI."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.memory import MemoryEngine
from ..ui import Label, clear_frame, font
from .base import BaseMode


class MemoryLattice(BaseMode):
    key = "memory"
    title = "Memory Lattice"

    def start(self):
        self.engine = MemoryEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["memory"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["memory"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._accepting = False
        self.update_hud(f"Memorize {len(trial.sequence)}-step sequence", T.ACCENT_SOFT)
        Label(self.play, text="Watch the pattern…", size=13, color=T.TEXT_DIM).pack(pady=(8, 4))

        self._grid = tk.Frame(self.play, bg=T.BG_DEEP)
        self._grid.pack(expand=True)
        self._canvases: list[tk.Canvas] = []
        cols = 2 if trial.n_tiles <= 4 else 3
        size = 100
        for i, (color, _) in enumerate(trial.tiles):
            c = tk.Canvas(
                self._grid, width=size, height=size, bg=T.BG_CARD,
                highlightthickness=2, highlightbackground=T.BG_ELEVATED,
            )
            r, col = divmod(i, cols)
            c.grid(row=r, column=col, padx=8, pady=8)
            c.create_oval(12, 12, size - 12, size - 12, fill=color, outline="", tags="dot")
            c.create_text(size // 2, size // 2, text=str(i + 1), fill=T.BG_DEEP,
                          font=font(16, bold=True), tags="num")
            c.bind("<Button-1>", lambda e, j=i: self._on_tile(j))
            self._canvases.append(c)

        self._trial = trial
        self.after(600, self._play_sequence)

    def _flash(self, idx: int, on: bool):
        c = self._canvases[idx]
        color = self._trial.tiles[idx][0]
        c.configure(
            bg=color if on else T.BG_CARD,
            highlightbackground=color if on else T.BG_ELEVATED,
        )
        c.itemconfig("dot", fill=T.TEXT if on else color)

    def _play_sequence(self, step: int = 0):
        if not self._alive:
            return
        if step >= len(self._trial.sequence):
            self._accepting = True
            self.update_hud("Your turn — tap the order", T.TEAL)
            return
        idx = self._trial.sequence[step]
        self._flash(idx, True)
        self.after(self._trial.flash_ms, lambda: self._unflash(idx, step))

    def _unflash(self, idx: int, step: int):
        if not self._alive:
            return
        self._flash(idx, False)
        self.after(180, lambda: self._play_sequence(step + 1))

    def _on_tile(self, idx: int):
        if not self._accepting or not self._alive:
            return
        self._flash(idx, True)
        self.after(120, lambda: self._flash(idx, False))
        event = self.engine.tap(idx)
        if event is None:
            return
        self._accepting = False
        self.apply_event(event)
        self.next_or_finish()
