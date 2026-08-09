"""
Prospective memory embedded in an ongoing task
Remember to act when a cue appears while doing a primary task
(Einstein & McDaniel PM research; aging/neurology literature).
Primary: parity judgment; PM cue: press special when number is multiple of 5.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class PmTrial:
    number: int
    is_pm_cue: bool  # multiple of 5
    is_odd: bool
    deadline_ms: int


class ProspectiveEngine:
    key = "prospective"
    domain = "attention"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="attention")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 16 + self.level * 2
        # PM cue rate
        self.pm_rate = max(0.12, 0.25 - self.level * 0.01)
        self.current: PmTrial | None = None

    def next_trial(self) -> PmTrial:
        p = self.ad.live_profile()
        if random.random() < self.pm_rate:
            number = random.choice([5, 10, 15, 20, 25, 30, 35, 40])
        else:
            number = random.randint(1, 49)
            while number % 5 == 0:
                number = random.randint(1, 49)
        self.current = PmTrial(
            number=number,
            is_pm_cue=(number % 5 == 0),
            is_odd=(number % 2 == 1),
            deadline_ms=max(1200, p.deadline_ms // 2),
        )
        return self.current

    def answer(self, choice: str | None) -> dict:
        """choice: 'odd' | 'even' | 'pm' | None timeout"""
        assert self.current is not None
        pts = points_for_level(11, self.level)
        if choice is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Too slow")
        if self.current.is_pm_cue:
            good = choice == "pm"
            msg = "PM cue caught!" if good else "Missed PM cue (×5)"
        else:
            if choice == "pm":
                good = False
                msg = "False PM — not a cue"
            else:
                want = "odd" if self.current.is_odd else "even"
                good = choice == want
                msg = "Parity OK" if good else f"Was {want}"
        self.ad.observe(good)
        return apply_hit(self.state, pts + (5 if self.current.is_pm_cue and good else 0), good, msg)

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
