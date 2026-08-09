"""Stop-signal task — response inhibition (Logan & Cowan, 1984)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, rate, time_ms
from .scoring import ScoreState, apply_hit


@dataclass
class StopTrial:
    direction: str  # "<" or ">"
    is_stop: bool
    go_ms: int  # time before stop signal (if stop)
    respond_window_ms: int


class StopEngine:
    key = "stop"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 16 + self.level * 2
        self.stop_rate = rate(0.2, 0.4, self.level)
        # SSD (stop-signal delay) shorter at high level = harder to inhibit
        self.ssd_ms = time_ms(350, 120, self.level)
        self.respond_window_ms = time_ms(900, 500, self.level)
        self.current: StopTrial | None = None

    def next_trial(self) -> StopTrial:
        direction = random.choice(["<", ">"])
        is_stop = random.random() < self.stop_rate
        ssd = max(80, self.ssd_ms - self.state.round_i * 5)
        self.current = StopTrial(
            direction=direction,
            is_stop=is_stop,
            go_ms=ssd if is_stop else 0,
            respond_window_ms=self.respond_window_ms,
        )
        return self.current

    def respond(self, pressed: bool, direction: str | None = None) -> dict:
        """
        pressed=True means player responded.
        On go trials must press correct direction; on stop must NOT press.
        """
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if self.current.is_stop:
            good = not pressed
            msg = "Stopped!" if good else "Failed stop — should hold"
            return apply_hit(self.state, pts + (5 if good else 0), good, msg)
        # go trial
        if not pressed:
            return apply_hit(self.state, pts, False, "Missed go")
        good = direction == self.current.direction
        return apply_hit(self.state, pts, good, "Go correct" if good else "Wrong direction")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
