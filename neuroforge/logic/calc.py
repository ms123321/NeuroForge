"""Quick Calc pure logic — mental arithmetic / processing speed."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size, time_sec
from .scoring import ScoreState, apply_hit


@dataclass
class CalcTrial:
    expression: str
    answer: int
    options: list[int]
    time_limit: float


class CalcEngine:
    key = "calc"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 12 + self.level * 2
        self.time_limit = time_sec(5.5, 1.8, self.level)
        self.n_options = set_size(3, 6, self.level)
        self.current: CalcTrial | None = None

    def _make_problem(self) -> tuple[str, int]:
        lv = self.level
        if lv <= 2:
            a, b = random.randint(1, 12), random.randint(1, 12)
            op = random.choice(["+", "-"])
            if op == "-" and a < b:
                a, b = b, a
            return f"{a} {op} {b}", a + b if op == "+" else a - b
        if lv <= 4:
            op = random.choice(["+", "-", "×"])
            if op == "×":
                a, b = random.randint(2, 9), random.randint(2, 9)
                return f"{a} × {b}", a * b
            a, b = random.randint(8, 45), random.randint(2, 30)
            if op == "-" and a < b:
                a, b = b, a
            return f"{a} {op} {b}", a + b if op == "+" else a - b
        if lv <= 7:
            if random.random() < 0.5:
                a, b, c = random.randint(3, 20), random.randint(2, 15), random.randint(1, 12)
                return f"{a} + {b} − {c}", a + b - c
            a, b = random.randint(4, 14), random.randint(4, 14)
            return f"{a} × {b}", a * b
        # elite: multi-step
        if random.random() < 0.4:
            a, b = random.randint(12, 40), random.randint(2, 9)
            return f"{a} × {b}", a * b
        a, b, c = random.randint(5, 25), random.randint(3, 15), random.randint(2, 12)
        return f"({a} + {b}) × {c}" if False else f"{a} + {b} × {c}", a + b * c  # order of ops

    def next_trial(self) -> CalcTrial:
        expr, ans = self._make_problem()
        opts = {ans}
        spread = 3 + self.level
        while len(opts) < self.n_options:
            jitter = random.randint(-spread, spread)
            if jitter == 0:
                jitter = random.choice([-2, -1, 1, 2])
            opts.add(ans + jitter)
        options = list(opts)
        random.shuffle(options)
        tl = max(1.5, self.time_limit - self.state.round_i * 0.04)
        self.current = CalcTrial(expression=expr, answer=ans, options=options, time_limit=tl)
        return self.current

    def choose(self, value: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(10, self.level)
        if value is None:
            return apply_hit(self.state, pts, False, "Time's up")
        good = value == self.current.answer
        return apply_hit(
            self.state, pts, good,
            "Correct" if good else f"Answer was {self.current.answer}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
