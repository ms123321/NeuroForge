"""Change detection — visual working memory capacity (Luck & Vogel, 1997)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size, time_ms, time_sec
from .scoring import ScoreState, apply_hit

COLORS = ["#6C8CFF", "#3DDCB5", "#F5C542", "#F687B3", "#B794F6", "#FF7B72", "#63B3ED", "#F6AD55"]


@dataclass
class ChangeTrial:
    sample: list[tuple[float, float, str]]  # x,y fraction, color
    test: list[tuple[float, float, str]]
    changed: bool
    encode_ms: int
    time_limit: float


class ChangeEngine:
    key = "change"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 10 + self.level
        self.set_n = set_size(2, 6, self.level)  # VWM set size
        self.encode_ms = time_ms(1200, 400, self.level)
        self.time_limit = time_sec(3.5, 1.5, self.level)
        self.current: ChangeTrial | None = None

    def next_trial(self) -> ChangeTrial:
        n = min(8, self.set_n + self.state.round_i // 4)
        # place items with jitter
        sample = []
        used = set()
        for _ in range(n):
            while True:
                x = random.uniform(0.15, 0.85)
                y = random.uniform(0.15, 0.85)
                key = (round(x, 1), round(y, 1))
                if key not in used:
                    used.add(key)
                    break
            sample.append((x, y, random.choice(COLORS)))
        changed = random.random() < 0.5
        test = [(x, y, c) for x, y, c in sample]
        if changed and test:
            i = random.randrange(len(test))
            x, y, c = test[i]
            new_c = random.choice([col for col in COLORS if col != c])
            test[i] = (x, y, new_c)
        self.current = ChangeTrial(
            sample=sample,
            test=test,
            changed=changed,
            encode_ms=max(300, self.encode_ms - self.state.round_i * 20),
            time_limit=self.time_limit,
        )
        return self.current

    def answer(self, said_changed: bool | None) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if said_changed is None:
            return apply_hit(self.state, pts, False, "Time's up")
        good = said_changed == self.current.changed
        if good:
            return apply_hit(self.state, pts, True, "Changed" if said_changed else "Same array")
        return apply_hit(
            self.state, pts, False,
            "Was changed" if self.current.changed else "Was the same",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
