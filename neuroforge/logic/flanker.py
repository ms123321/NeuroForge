"""Flanker pure logic — Eriksen flanker task."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, rate, set_size, time_sec
from .scoring import ScoreState, apply_hit


@dataclass
class FlankerTrial:
    center: str
    congruent: bool
    display: str
    time_limit: float


class FlankerEngine:
    key = "flanker"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 14 + self.level * 2
        self.time_limit = time_sec(3.0, 1.0, self.level)
        self.incongruent_rate = rate(0.3, 0.75, self.level)
        self.n_flank = set_size(2, 4, self.level)
        self.current: FlankerTrial | None = None

    def next_trial(self) -> FlankerTrial:
        center = random.choice(["<", ">"])
        congruent = random.random() > self.incongruent_rate
        flank = center if congruent else (">" if center == "<" else "<")
        display = flank * self.n_flank + center + flank * self.n_flank
        tl = max(0.85, self.time_limit - self.state.round_i * 0.03)
        self.current = FlankerTrial(
            center=center, congruent=congruent, display=display, time_limit=tl
        )
        return self.current

    def answer(self, direction: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(10, self.level)
        if direction is None:
            return apply_hit(self.state, pts, False, "Time's up")
        good = direction == self.current.center
        if good:
            tag = "congruent" if self.current.congruent else "conflict resolved"
            return apply_hit(self.state, pts + (3 if not self.current.congruent else 0), True, tag)
        return apply_hit(self.state, pts, False, f"Center was {self.current.center}")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
