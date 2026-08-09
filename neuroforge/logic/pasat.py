"""PASAT-lite — paced serial addition (Gronwall, 1977) visual variant."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, time_ms
from .scoring import ScoreState, apply_hit


@dataclass
class PasatTrial:
    number: int
    previous: int | None
    correct_sum: int | None  # None on first trial (no answer)
    stim_ms: int
    options: list[int]


class PasatEngine:
    """Each trial shows a digit; answer = current + previous (skip first)."""

    key = "pasat"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 12 + self.level * 2  # includes first warm-up
        self.stim_ms = time_ms(2800, 1200, self.level)
        self.prev: int | None = None
        self.current: PasatTrial | None = None
        self._digit_max = 9 if self.level < 6 else 12

    def next_trial(self) -> PasatTrial:
        num = random.randint(1, min(9, self._digit_max))
        if self.prev is None:
            correct = None
            options = []
        else:
            correct = self.prev + num
            opts = {correct}
            while len(opts) < 4:
                opts.add(correct + random.randint(-4, 4) or correct + 1)
            options = list(opts)
            random.shuffle(options)
        stim = max(900, self.stim_ms - self.state.round_i * 30)
        self.current = PasatTrial(
            number=num,
            previous=self.prev,
            correct_sum=correct,
            stim_ms=stim,
            options=options,
        )
        return self.current

    def choose(self, value: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(11, self.level)
        # first trial: no score, just store
        if self.current.correct_sum is None:
            self.prev = self.current.number
            return {"good": True, "points": 0, "message": "Remember this number…", "streak": self.state.streak, "warmup": True}

        if value is None:
            event = apply_hit(self.state, pts, False, "Too slow")
        else:
            good = value == self.current.correct_sum
            event = apply_hit(
                self.state, pts, good,
                "Sum correct" if good else f"Was {self.current.correct_sum}",
            )
        self.prev = self.current.number
        return event

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
