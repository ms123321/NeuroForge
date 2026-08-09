"""
Running count / mental updating
Keep a mental total while ignoring distractor operations
(WM updating — related to PASAT and executive updating).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class CountTrial:
    display: str
    is_update: bool
    correct_total: int
    options: list[int]
    deadline_ms: int
    ask: bool


class CountKeepEngine:
    key = "countkeep"
    domain = "working_memory"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="working_memory")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 14 + self.level * 2
        self.total = 0
        self.since_ask = 0
        self.ask_every = max(2, 4 - self.level // 4)
        self.current: CountTrial | None = None

    def next_trial(self) -> CountTrial:
        p = self.ad.live_profile()
        self.since_ask += 1
        ask = self.since_ask >= self.ask_every and self.state.round_i > 0
        if ask:
            self.since_ask = 0
            opts = {self.total}
            while len(opts) < 4:
                opts.add(self.total + random.randint(-5, 5))
            options = list(opts)
            random.shuffle(options)
            self.current = CountTrial(
                display="What is your running total?",
                is_update=False,
                correct_total=self.total,
                options=options,
                deadline_ms=max(2500, p.deadline_ms),
                ask=True,
            )
            return self.current

        # update or distractor
        if random.random() < 0.7:
            delta = random.randint(1, 3 + self.level // 3)
            if random.random() < 0.5:
                delta = -delta
            self.total += delta
            sign = "+" if delta > 0 else ""
            display = f"Add {sign}{delta}"
            is_update = True
        else:
            # distractor — do NOT add
            junk = random.randint(1, 9)
            display = f"Ignore {junk}"
            is_update = False
        self.current = CountTrial(
            display=display,
            is_update=is_update,
            correct_total=self.total,
            options=[],
            deadline_ms=max(1200, p.deadline_ms // 2),
            ask=False,
        )
        return self.current

    def acknowledge(self) -> dict:
        """Non-ask trial: player just continues (always 'ok')."""
        return {"good": True, "message": "Updated" if self.current and self.current.is_update else "Ignored", "warmup": True}

    def choose(self, value: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if not self.current.ask:
            return self.acknowledge()
        if value is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = value == self.current.correct_total
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Total correct" if good else f"Total was {self.current.correct_total}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
