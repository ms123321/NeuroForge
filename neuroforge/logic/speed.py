"""Speed Mirror pure logic — processing speed."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size, time_sec
from .scoring import ScoreState, apply_hit

SYMBOLS = ["◆", "●", "▲", "■", "★", "✚", "◇", "○", "□", "△", "◼", "✦"]


@dataclass
class SpeedTrial:
    target: str
    options: list[str]
    time_limit: float


class SpeedEngine:
    key = "speed"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 12 + self.level * 2
        self.time_limit = time_sec(3.5, 1.1, self.level)
        self.n_options = set_size(3, 8, self.level)
        self.current: SpeedTrial | None = None

    def next_trial(self) -> SpeedTrial:
        # tighten time mid-session
        tl = max(0.9, self.time_limit - self.state.round_i * 0.04)
        pool = random.sample(SYMBOLS, k=min(len(SYMBOLS), self.n_options + 2))
        target = pool[0]
        options = pool[: self.n_options]
        if target not in options:
            options[-1] = target
        random.shuffle(options)
        self.current = SpeedTrial(target=target, options=options, time_limit=tl)
        return self.current

    def choose(self, symbol: str | None, elapsed: float) -> dict:
        assert self.current is not None
        pts = points_for_level(8, self.level)
        if symbol is None:
            return apply_hit(self.state, pts, False, "Time's up")
        if symbol == self.current.target:
            speed_bonus = max(0, int((self.current.time_limit - elapsed) * 10))
            return apply_hit(self.state, pts + speed_bonus, True, f"Hit in {elapsed:.2f}s")
        return apply_hit(self.state, pts, False, "Wrong symbol")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
