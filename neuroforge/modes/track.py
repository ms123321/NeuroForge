"""Multiple object tracking UI (simplified)."""

from __future__ import annotations

import tkinter as tk

from .. import theme as T
from ..logic.track import TrackEngine
from ..ui import Label, RoundedButton, clear_frame
from .base import BaseMode


class ObjectTrack(BaseMode):
    key = "track"
    title = "Object Track"

    def start(self):
        self.engine = TrackEngine(self.level)
        self.rounds = self.engine.rounds
        self.build_shell(T.MODE_COLORS["track"])
        self.countdown_then(3, self.next_round, T.MODE_COLORS["track"])

    def next_round(self):
        if not self._alive:
            return
        clear_frame(self.play)
        trial = self.engine.next_trial()
        self._selected: set[int] = set()
        self._phase = "flash"
        n_t = len(trial.targets)
        self.update_hud(f"Targets glow — track {n_t} object(s)", T.MODE_COLORS["track"])
        Label(self.play, text="Watch them move, then tap the targets", size=11, color=T.TEXT_DIM).pack(
            pady=(6, 4)
        )

        self._w, self._h = 320, 280
        self._canvas = tk.Canvas(
            self.play, width=self._w, height=self._h, bg=T.BG_CARD, highlightthickness=0
        )
        self._canvas.pack(pady=6)
        self._trial = trial
        self._dots = []
        for i in range(trial.n_objects):
            x, y = trial.path_steps[i][0]
            px, py = x * self._w, y * self._h
            is_t = i in trial.targets
            color = T.GOLD if is_t else T.ACCENT_SOFT
            d = self._canvas.create_oval(px - 12, py - 12, px + 12, py + 12, fill=color, outline="")
            self._dots.append(d)

        self.after(trial.flash_ms, self._start_move)

    def _start_move(self):
        if not self._alive:
            return
        # unhighlight
        for d in self._dots:
            self._canvas.itemconfig(d, fill=T.ACCENT_SOFT)
        self.update_hud("Tracking…", T.TEXT_DIM)
        self._step = 1
        self._animate()

    def _animate(self):
        if not self._alive:
            return
        trial = self._trial
        if self._step > trial.move_steps:
            self._pick_phase()
            return
        for i, d in enumerate(self._dots):
            x, y = trial.path_steps[i][min(self._step, len(trial.path_steps[i]) - 1)]
            px, py = x * self._w, y * self._h
            self._canvas.coords(d, px - 12, py - 12, px + 12, py + 12)
        self._step += 1
        self.after(trial.step_ms, self._animate)

    def _pick_phase(self):
        self._phase = "pick"
        n_t = len(self._trial.targets)
        self.update_hud(f"Tap the {n_t} target(s), then Submit", T.TEAL)
        for i, d in enumerate(self._dots):
            self._canvas.tag_bind(d, "<Button-1>", lambda e, idx=i: self._toggle(idx))

        RoundedButton(
            self.play, text="Submit", command=self._submit,
            bg=T.MODE_COLORS["track"], fg=T.BG_DEEP, width=160, height=44,
        ).pack(pady=8)

    def _toggle(self, idx: int):
        if self._phase != "pick" or not self._alive:
            return
        if idx in self._selected:
            self._selected.remove(idx)
            self._canvas.itemconfig(self._dots[idx], fill=T.ACCENT_SOFT)
        else:
            if len(self._selected) >= len(self._trial.targets):
                return
            self._selected.add(idx)
            self._canvas.itemconfig(self._dots[idx], fill=T.GOLD)

    def _submit(self):
        if self._phase != "pick" or not self._alive:
            return
        self._phase = "done"
        self.apply_event(self.engine.choose(list(self._selected)))
        self.next_or_finish()
