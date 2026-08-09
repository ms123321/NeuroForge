"""
Antisaccade-style response — inhibit reflexive same-side response.
Used in executive-function / frontal-network research (Hallett; Munoz & Everling).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class AntiTrial:
    flash_side: str  # left | right
    correct_side: str  # opposite
    deadline_ms: int


class AntisaccadeEngine:
    key = "antisaccade"
    domain = "inhibition"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="inhibition")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 14 + self.level * 2
        self.current: AntiTrial | None = None

    def next_trial(self) -> AntiTrial:
        p = self.ad.live_profile()
        side = random.choice(["left", "right"])
        self.current = AntiTrial(
            flash_side=side,
            correct_side="right" if side == "left" else "left",
            deadline_ms=max(700, p.deadline_ms // 2),
        )
        return self.current

    def answer(self, side: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if side is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Too slow")
        good = side == self.current.correct_side
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Opposite correct" if good else f"Look opposite — was {self.current.correct_side}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
