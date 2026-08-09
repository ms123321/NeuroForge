"""
Matrix pattern completion — Raven-like abstract reasoning (simplified).
Fluid intelligence / pattern induction used across cognitive aging research.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

MOTIFS = ["●", "■", "▲", "◆", "★", "○"]


@dataclass
class MatrixTrial:
    grid: list[str]  # 8 cells, 9th is ?
    options: list[str]
    answer: str
    deadline_ms: int


class MatrixEngine:
    key = "matrix"
    domain = "flexibility"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="flexibility")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 10 + self.level
        self.current: MatrixTrial | None = None

    def next_trial(self) -> MatrixTrial:
        p = self.ad.live_profile()
        rule = random.choice(["row_cycle", "col_cycle", "constant_row"])
        a, b, c = random.sample(MOTIFS, 3)

        if rule == "row_cycle":
            # each row is rotation of a,b,c
            rows = [
                [a, b, c],
                [b, c, a],
                [c, a, "?"],  # answer b
            ]
            answer = b
        elif rule == "col_cycle":
            rows = [
                [a, b, c],
                [b, c, a],
                [c, "?", b],  # answer a for col0 cycle... wait
            ]
            # col0: a,b,c → row2 col0 = c already. col1: b,c,? answer a
            rows = [
                [a, b, c],
                [b, c, a],
                [c, a, "?"],
            ]
            answer = b  # row cycle same
        else:
            # each row constant
            rows = [
                [a, a, a],
                [b, b, b],
                [c, c, "?"],
            ]
            answer = c

        grid = [x for row in rows for x in row]
        # blank last
        grid[8] = "?"
        opts = {answer}
        while len(opts) < 4:
            opts.add(random.choice(MOTIFS))
        options = list(opts)
        random.shuffle(options)
        self.current = MatrixTrial(
            grid=grid,
            options=options,
            answer=answer,
            deadline_ms=max(4000, p.deadline_ms + 1000),
        )
        return self.current

    def choose(self, value: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(13, self.level)
        if value is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = value == self.current.answer
        self.ad.observe(good)
        return apply_hit(self.state, pts, good, "Pattern fit" if good else f"Was {self.current.answer}")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
