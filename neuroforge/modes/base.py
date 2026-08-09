"""Shared base for training modes (UI layer over pure logic engines)."""

from __future__ import annotations

import time
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Any, Callable

from .. import feedback
from .. import theme as T
from ..logic.difficulty import difficulty_label
from ..ui import HeaderBar, Label, ProgressBar, clear_frame


class ModeResult:
    def __init__(
        self,
        mode_key: str,
        score: int,
        correct: int,
        attempts: int,
        duration_sec: float,
        level: int,
        max_streak: int,
    ):
        self.mode_key = mode_key
        self.score = score
        self.correct = correct
        self.attempts = attempts
        self.duration_sec = duration_sec
        self.level = level
        self.max_streak = max_streak


class BaseMode(ABC):
    key: str = "base"
    title: str = "Mode"
    rounds: int = 20

    def __init__(
        self,
        root: tk.Widget,
        container: tk.Frame,
        level: int,
        on_complete: Callable[[ModeResult], None],
        on_abort: Callable[[], None],
    ):
        self.root = root
        self.container = container
        self.level = max(1, min(10, level))
        self.on_complete = on_complete
        self.on_abort = on_abort

        self.score = 0
        self.correct = 0
        self.attempts = 0
        self.streak = 0
        self.max_streak = 0
        self.round_i = 0
        self.started_at = time.time()
        self._alive = True
        self._after_ids: list[str] = []
        self.engine: Any = None

        self.hud: tk.Frame | None = None
        self.play: tk.Frame | None = None
        self.score_lbl: Label | None = None
        self.round_lbl: Label | None = None
        self.feedback_lbl: Label | None = None
        self.progress: ProgressBar | None = None

    def after(self, ms: int, fn: Callable):
        if not self._alive:
            return
        aid = self.root.after(ms, fn)
        self._after_ids.append(aid)

    def cancel_timers(self):
        for aid in self._after_ids:
            try:
                self.root.after_cancel(aid)
            except tk.TclError:
                pass
        self._after_ids.clear()

    def destroy(self):
        self._alive = False
        self.cancel_timers()
        clear_frame(self.container)

    def build_shell(self, color: str = T.ACCENT):
        clear_frame(self.container)
        self.container.configure(bg=T.BG_DEEP)

        HeaderBar(self.container, self.title, on_back=self._abort).pack(
            fill="x", padx=T.PAD, pady=(12, 4)
        )

        self.hud = tk.Frame(self.container, bg=T.BG_DEEP)
        self.hud.pack(fill="x", padx=T.PAD, pady=(4, 8))

        top = tk.Frame(self.hud, bg=T.BG_DEEP)
        top.pack(fill="x")
        self.score_lbl = Label(top, text="Score  0", size=13, bold=True, color=T.GOLD)
        self.score_lbl.pack(side="left")
        diff = difficulty_label(self.level)
        self.level_lbl = Label(
            top, text=f"Lv {self.level} · {diff}", size=11, bold=True, color=color
        )
        self.level_lbl.pack(side="left", padx=(12, 0))
        self.round_lbl = Label(top, text=f"1 / {self.rounds}", size=12, color=T.TEXT_DIM)
        self.round_lbl.pack(side="right")

        self.progress = ProgressBar(self.hud, width=380, height=8)
        self.progress.pack(pady=(8, 4))
        self.progress.set(0, color)

        self.feedback_lbl = Label(self.hud, text=" ", size=12, color=T.TEXT_DIM)
        self.feedback_lbl.pack(pady=(2, 0))

        self.play = tk.Frame(self.container, bg=T.BG_DEEP)
        self.play.pack(fill="both", expand=True, padx=T.PAD, pady=8)

    def sync_from_engine(self):
        if self.engine is None:
            return
        st = self.engine.state
        self.score = st.score
        self.correct = st.correct
        self.attempts = st.attempts
        self.streak = st.streak
        self.max_streak = st.max_streak
        self.round_i = st.round_i
        self.rounds = getattr(self.engine, "rounds", self.rounds)

    def update_hud(self, feedback_text: str = "", feedback_color: str = T.TEXT_DIM):
        self.sync_from_engine()
        if self.score_lbl:
            self.score_lbl.configure(text=f"Score  {self.score}")
        if self.round_lbl:
            self.round_lbl.configure(text=f"{min(self.round_i + 1, self.rounds)} / {self.rounds}")
        if self.progress:
            self.progress.set(self.round_i / max(1, self.rounds))
        if self.feedback_lbl and feedback_text:
            self.feedback_lbl.configure(text=feedback_text, fg=feedback_color)

    def apply_event(self, event: dict):
        """Apply logic engine event → HUD + sound/haptic."""
        self.sync_from_engine()
        good = event.get("good", False)
        msg = event.get("message", "")
        color = T.SUCCESS if good else T.ERROR
        if event.get("partial") and not good:
            color = T.WARNING
        self.update_hud(msg, color)
        feedback.feedback_hit(self.play or self.container, good=good, root=self.root)

    def register_hit(self, points: int, good: bool, message: str = ""):
        """Legacy path when engine not used."""
        self.attempts += 1
        if good:
            self.correct += 1
            self.streak += 1
            self.max_streak = max(self.max_streak, self.streak)
            bonus = min(15, self.streak * 2)
            self.score += points + bonus
            self.update_hud(message or "Correct ✓", T.SUCCESS)
            feedback.feedback_hit(self.play or self.container, True, self.root)
        else:
            self.streak = 0
            self.score = max(0, self.score - max(2, points // 4))
            self.update_hud(message or "Miss ✗", T.ERROR)
            feedback.feedback_hit(self.play or self.container, False, self.root)

    def next_or_finish(self):
        if self.engine is not None:
            self.engine.advance()
            self.sync_from_engine()
            if self.engine.done():
                self.finish()
            else:
                self.update_hud()
                self.after(350, self.next_round)
            return
        self.round_i += 1
        if self.round_i >= self.rounds:
            self.finish()
        else:
            self.update_hud()
            self.after(350, self.next_round)

    def finish(self):
        if not self._alive:
            return
        self._alive = False
        self.cancel_timers()
        self.sync_from_engine()
        feedback.play_level()
        result = ModeResult(
            mode_key=self.key,
            score=self.score,
            correct=self.correct,
            attempts=self.attempts,
            duration_sec=time.time() - self.started_at,
            level=self.level,
            max_streak=self.max_streak,
        )
        self.on_complete(result)

    def _abort(self):
        self.destroy()
        self.on_abort()

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def next_round(self):
        ...

    def countdown_then(self, seconds: int, then: Callable, color: str = T.ACCENT):
        clear_frame(self.play)
        lbl = Label(self.play, text=str(seconds), size=48, bold=True, color=color)
        lbl.pack(expand=True)

        def tick(n: int):
            if not self._alive:
                return
            if n <= 0:
                feedback.play_go()
                then()
                return
            lbl.configure(text=str(n))
            feedback.play_tick()
            self.after(700, lambda: tick(n - 1))

        tick(seconds)
