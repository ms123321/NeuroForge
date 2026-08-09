"""
Backward Corsi — spatial span reversed (neuropsych battery variant).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class BackSpanTrial:
    sequence: list[int]
    target: list[int]  # reversed
    flash_ms: int


class BackwardSpanEngine:
    key = "backspan"
    domain = "working_memory"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="working_memory")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 6 + self.level // 2
        self.span = min(2 + self.level // 2, 7)
        self.current: BackSpanTrial | None = None
        self.player: list[int] = []

    def next_trial(self) -> BackSpanTrial:
        p = self.ad.live_profile()
        length = min(8, self.span + self.state.round_i // 3)
        seq = random.sample(range(9), min(length, 9)) if length <= 9 else [
            random.randrange(9) for _ in range(length)
        ]
        self.player = []
        self.current = BackSpanTrial(
            sequence=seq,
            target=list(reversed(seq)),
            flash_ms=max(280, p.encode_ms // 2),
        )
        return self.current

    def tap(self, idx: int) -> dict | None:
        assert self.current is not None
        self.player.append(idx)
        expected = self.current.target[: len(self.player)]
        pts = points_for_level(14, self.level)
        if self.player != expected:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Wrong reverse order")
        if len(self.player) == len(self.current.target):
            self.ad.observe(True)
            if self.state.correct % 2 == 0:
                self.span = min(8, self.span + 1)
            return apply_hit(self.state, pts + len(self.player) * 2, True, "Backward span OK")
        return None

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
