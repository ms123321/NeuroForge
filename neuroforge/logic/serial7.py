"""
Serial sevens — subtract 7 repeatedly (MMSE / bedside cognitive exam lineage).
Mental control + working memory + processing speed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class Serial7Trial:
    prompt: str
    answer: int
    options: list[int]
    deadline_ms: int


class Serial7Engine:
    key = "serial7"
    domain = "processing_speed"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="processing_speed")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 10 + self.level
        # classic starts at 100; harder levels start lower or use larger steps
        self.value = 100 if self.level <= 4 else random.choice([100, 93, 86])
        self.step = 7 if self.level < 8 else random.choice([7, 7, 8])
        self.current: Serial7Trial | None = None
        self._started = False

    def next_trial(self) -> Serial7Trial:
        p = self.ad.live_profile()
        if not self._started:
            self._started = True
            prompt = f"Start: {self.value}. Subtract {self.step}."
            answer = self.value - self.step
        else:
            prompt = f"{self.value} − {self.step} = ?"
            answer = self.value - self.step
        self.value = answer
        opts = {answer}
        while len(opts) < 4:
            opts.add(answer + random.choice([-14, -7, -3, -1, 1, 3, 7, 14]))
        options = list(opts)
        random.shuffle(options)
        self.current = Serial7Trial(
            prompt=prompt,
            answer=answer,
            options=options,
            deadline_ms=max(2500, p.deadline_ms + 500 - self.level * 80),
        )
        return self.current

    def choose(self, value: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(11, self.level)
        if value is None:
            self.ad.observe(False)
            # still advance chain so it doesn't desync badly
            return apply_hit(self.state, pts, False, "Time's up")
        good = value == self.current.answer
        if not good:
            # reset value to correct for next step (clinical: continue from correct)
            self.value = self.current.answer
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Correct" if good else f"Was {self.current.answer}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
