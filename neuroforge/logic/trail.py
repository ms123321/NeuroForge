"""Number Path pure logic — trail making (Reitan TMT-inspired)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size, time_sec
from .scoring import ScoreState, apply_hit


@dataclass
class TrailTrial:
    labels: list[str]
    order: list[str]
    cols: int
    time_limit: float
    mode: str


class TrailEngine:
    key = "trail"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 5 + self.level // 2
        self.count = set_size(5, 14, self.level)
        self.time_limit = time_sec(22.0, 9.0, self.level)
        self.alternate = self.level >= 4  # earlier alternate for more challenge
        self.current: TrailTrial | None = None
        self._next_i = 0
        self._errors = 0

    def next_trial(self) -> TrailTrial:
        self._next_i = 0
        self._errors = 0
        if self.alternate and self.level >= 4:
            n = min(self.count, 12)
            order = []
            for i in range(n):
                if i % 2 == 0:
                    order.append(str(i // 2 + 1))
                else:
                    order.append(chr(ord("A") + i // 2))
            mode = "alternate"
        else:
            order = [str(i) for i in range(1, self.count + 1)]
            mode = "numbers"
        labels = list(order)
        random.shuffle(labels)
        cols = 3 if len(labels) <= 9 else 4
        tl = max(8.0, self.time_limit - self.state.round_i * 0.5)
        self.current = TrailTrial(
            labels=labels, order=order, cols=cols, time_limit=tl, mode=mode
        )
        return self.current

    def tap(self, label: str) -> dict | None:
        assert self.current is not None
        expected = self.current.order[self._next_i]
        # fewer free errors at high level
        max_err = 3 if self.level < 5 else (2 if self.level < 8 else 1)
        if label != expected:
            self._errors += 1
            if self._errors >= max_err:
                return apply_hit(
                    self.state, points_for_level(15, self.level), False,
                    f"Trail broken (wanted {expected})",
                )
            return {"good": False, "partial": True, "message": f"Next is {expected}", "continue": True}
        self._next_i += 1
        if self._next_i >= len(self.current.order):
            bonus = max(0, 5 - self._errors) * 2
            return apply_hit(
                self.state, points_for_level(15, self.level) + bonus, True,
                f"Path complete · {len(self.current.order)} steps",
            )
        return None

    def timeout(self) -> dict:
        return apply_hit(self.state, points_for_level(15, self.level), False, "Time's up on trail")

    def advance(self) -> None:
        self.state.round_i += 1
        if self.state.correct > 0 and self.state.correct % 2 == 0:
            self.count = min(16, self.count + 1)

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
