"""
Partial report (Sperling-inspired)
Iconic / visual short-term memory — brief array, cued subset to report.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

LETTERS = list("BCDFGHJKLMNPRSTVWXZ")


@dataclass
class PartialTrial:
    grid: list[str]  # 3x3 or 3x4
    rows: int
    cols: int
    cue_row: int
    target: list[str]  # letters in cued row
    encode_ms: int
    deadline_ms: int


class PartialReportEngine:
    key = "partial"
    domain = "working_memory"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="working_memory")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 8 + self.level // 2
        self.cols = min(3 + self.level // 4, 5)
        self.rows = 3
        self.current: PartialTrial | None = None
        self.player: list[str] = []

    def next_trial(self) -> PartialTrial:
        p = self.ad.live_profile()
        n = self.rows * self.cols
        grid = random.sample(LETTERS, n) if n <= len(LETTERS) else [
            random.choice(LETTERS) for _ in range(n)
        ]
        cue = random.randrange(self.rows)
        target = grid[cue * self.cols : (cue + 1) * self.cols]
        self.player = []
        self.current = PartialTrial(
            grid=grid,
            rows=self.rows,
            cols=self.cols,
            cue_row=cue,
            target=target,
            encode_ms=max(120, p.encode_ms // 5),
            deadline_ms=max(4000, p.deadline_ms + 1000),
        )
        return self.current

    def tap(self, letter: str) -> dict | None:
        assert self.current is not None
        self.player.append(letter)
        expected = self.current.target[: len(self.player)]
        pts = points_for_level(12, self.level)
        if self.player != expected:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Wrong letter in row")
        if len(self.player) == len(self.current.target):
            self.ad.observe(True)
            return apply_hit(self.state, pts + len(self.player) * 2, True, "Row reported")
        return None

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
