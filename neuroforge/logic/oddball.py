"""
Oddball paradigm — rare target among standards (P300 / clinical ERP research).
Press when the rare stimulus appears.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

STANDARDS = ["●", "○", "■", "□"]
TARGETS = ["★", "▲", "◆"]


@dataclass
class OddballTrial:
    symbol: str
    is_target: bool
    deadline_ms: int


class OddballEngine:
    key = "oddball"
    domain = "attention"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="attention")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 20 + self.level * 2
        # rarer targets at higher levels (harder vigilance)
        self.target_rate = max(0.12, 0.28 - self.level * 0.015)
        self.standard = random.choice(STANDARDS)
        self.target = random.choice(TARGETS)
        self.current: OddballTrial | None = None

    def next_trial(self) -> OddballTrial:
        p = self.ad.live_profile()
        is_target = random.random() < self.target_rate
        symbol = self.target if is_target else self.standard
        self.current = OddballTrial(
            symbol=symbol,
            is_target=is_target,
            deadline_ms=max(400, p.deadline_ms // 4),
        )
        return self.current

    def respond(self, pressed: bool) -> dict:
        assert self.current is not None
        pts = points_for_level(9, self.level)
        if self.current.is_target:
            good = pressed
            msg = "Target hit" if good else "Missed oddball"
        else:
            good = not pressed
            msg = "Correct ignore" if good else "False alarm"
        self.ad.observe(good)
        return apply_hit(self.state, pts + (5 if self.current.is_target and good else 0), good, msg)

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
