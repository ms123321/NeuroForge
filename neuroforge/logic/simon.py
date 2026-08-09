"""Simon task — spatial stimulus-response compatibility (Simon, 1969)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, rate, time_sec
from .scoring import ScoreState, apply_hit


@dataclass
class SimonTrial:
    color: str  # "blue" | "gold" — maps to left/right response
    side: str  # "left" | "right" — where stimulus appears
    congruent: bool  # side matches mapped response side
    time_limit: float


# blue -> press LEFT, gold -> press RIGHT
COLOR_MAP = {"blue": "left", "gold": "right"}
COLOR_HEX = {"blue": "#6C8CFF", "gold": "#F5C542"}


class SimonEngine:
    key = "simon"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 14 + self.level * 2
        self.time_limit = time_sec(2.8, 0.95, self.level)
        self.incongruent_rate = rate(0.35, 0.7, self.level)
        self.current: SimonTrial | None = None

    def next_trial(self) -> SimonTrial:
        color = random.choice(["blue", "gold"])
        correct_side = COLOR_MAP[color]
        incongruent = random.random() < self.incongruent_rate
        if incongruent:
            side = "right" if correct_side == "left" else "left"
        else:
            side = correct_side
        tl = max(0.8, self.time_limit - self.state.round_i * 0.025)
        self.current = SimonTrial(
            color=color,
            side=side,
            congruent=side == correct_side,
            time_limit=tl,
        )
        return self.current

    def answer(self, side: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(11, self.level)
        correct = COLOR_MAP[self.current.color]
        if side is None:
            return apply_hit(self.state, pts, False, "Time's up")
        good = side == correct
        if good:
            tag = "congruent" if self.current.congruent else "Simon conflict OK"
            return apply_hit(self.state, pts + (4 if not self.current.congruent else 0), True, tag)
        return apply_hit(self.state, pts, False, f"Should press {correct.upper()}")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
