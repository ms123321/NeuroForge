"""Focus Pulse pure logic — Go/No-Go (response inhibition)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, rate, session_pressure, time_ms
from .scoring import ScoreState, apply_hit


@dataclass
class FocusTrial:
    is_go: bool
    stimulus_ms: int
    isi_ms: int


class FocusEngine:
    key = "focus"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 16 + self.level * 2  # more trials at high level
        # L1: 1200ms / L10: 380ms — real speed pressure
        self.stimulus_ms = time_ms(1200, 380, self.level)
        self.isi_ms = time_ms(750, 280, self.level)
        # More no-go traps at high level (harder inhibition)
        self.no_go_rate = rate(0.18, 0.48, self.level)
        self.current: FocusTrial | None = None

    def next_trial(self) -> FocusTrial:
        pressure = session_pressure(self.state.round_i)
        no_go = min(0.55, self.no_go_rate + pressure * 0.15)
        stim = max(320, int(self.stimulus_ms * (1 - pressure * 0.2)))
        is_go = random.random() > no_go
        self.current = FocusTrial(is_go=is_go, stimulus_ms=stim, isi_ms=self.isi_ms)
        return self.current

    def respond(self, tapped: bool, timed_out: bool = False) -> dict:
        assert self.current is not None
        is_go = self.current.is_go
        pts = points_for_level(10, self.level)
        if timed_out:
            good = not is_go
            msg = "Correct hold" if good else "Too slow"
        else:
            good = is_go
            msg = "Go! +points" if good else "False alarm — should ignore"
        return apply_hit(self.state, pts, good, msg)

    def done(self) -> bool:
        return self.state.round_i >= self.rounds

    def advance(self) -> None:
        self.state.round_i += 1
