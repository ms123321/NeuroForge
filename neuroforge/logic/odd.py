"""Odd Spot pure logic — visual search."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size, time_sec
from .scoring import ScoreState, apply_hit

SYMBOLS = ["●", "■", "▲", "◆", "★", "✚", "○", "□", "△", "◇", "◼", "✦", "♦", "♠"]


@dataclass
class OddTrial:
    items: list[str]
    odd_index: int
    cols: int
    time_limit: float


class OddEngine:
    key = "odd"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 10 + self.level
        self.grid = set_size(3, 6, self.level)  # 3x3 → 6x6
        self.time_limit = time_sec(5.5, 1.8, self.level)
        self.current: OddTrial | None = None

    def next_trial(self) -> OddTrial:
        n = self.grid * self.grid
        common, odd = random.sample(SYMBOLS, 2)
        # at high level, odd is more subtle: same family pairs
        if self.level >= 7:
            pairs = [("●", "○"), ("■", "□"), ("▲", "△"), ("◆", "◇")]
            common, odd = random.choice(pairs)
            if random.random() < 0.5:
                common, odd = odd, common
        items = [common] * n
        odd_index = random.randrange(n)
        items[odd_index] = odd
        tl = max(1.5, self.time_limit - self.state.round_i * 0.05)
        self.current = OddTrial(items=items, odd_index=odd_index, cols=self.grid, time_limit=tl)
        return self.current

    def choose(self, index: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if index is None:
            return apply_hit(self.state, pts, False, "Time's up")
        good = index == self.current.odd_index
        return apply_hit(self.state, pts, good, "Found it!" if good else "That wasn't the odd one")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
