"""
Running memory span — continuously update WM with last N items
(Broadway & Engle; used in WM capacity research).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level, n_back_depth
from .scoring import ScoreState, apply_hit

LETTERS = list("FHJKLNPQRSTY")


@dataclass
class RunningTrial:
    stream: list[str]
    window: int
    target: list[str]
    flash_ms: int


class RunningSpanEngine:
    key = "running"
    domain = "working_memory"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="working_memory")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 6 + self.level // 2
        self.window = max(2, min(5, n_back_depth(self.level) + 1))
        self.current: RunningTrial | None = None
        self.player: list[str] = []

    def next_trial(self) -> RunningTrial:
        p = self.ad.live_profile()
        stream_len = self.window + random.randint(2, 3 + self.level // 3)
        stream = [random.choice(LETTERS) for _ in range(stream_len)]
        target = stream[-self.window :]
        self.player = []
        self.current = RunningTrial(
            stream=stream,
            window=self.window,
            target=target,
            flash_ms=max(350, p.encode_ms // 2),
        )
        return self.current

    def tap(self, letter: str) -> dict | None:
        assert self.current is not None
        self.player.append(letter)
        expected = self.current.target[: len(self.player)]
        pts = points_for_level(14, self.level)
        if self.player != expected:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Wrong letter order")
        if len(self.player) == len(self.current.target):
            self.ad.observe(True)
            if self.state.correct % 2 == 0:
                self.window = min(6, self.window + 1)
            return apply_hit(self.state, pts + self.window * 2, True, f"Last {self.window} correct")
        return None

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
