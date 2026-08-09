"""
Symbol–Digit coding (SDMT-inspired)
Symbol Digit Modalities Test — processing speed measure widely used in
neurology (MS, TBI, aging) and NIH cognitive batteries.

Map symbols→digits under time pressure; more pairs + less time at high levels.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

SYMBOLS = ["◆", "●", "▲", "■", "★", "✚", "◇", "○", "□", "△", "◼", "✦", "♦", "♠", "♣", "♥"]


@dataclass
class SymDigitTrial:
    key_map: list[tuple[str, int]]  # symbol → digit 1..n
    probe_symbol: str
    correct_digit: int
    options: list[int]
    deadline_ms: int


class SymDigitEngine:
    key = "symdigit"
    domain = "processing_speed"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="processing_speed")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 14 + self.level * 2
        # build a session key once
        n = self.ad.base.set_size
        n = max(4, min(9, n))
        syms = random.sample(SYMBOLS, n)
        self.key_map = list(zip(syms, range(1, n + 1)))
        self._map = dict(self.key_map)
        self.current: SymDigitTrial | None = None

    def next_trial(self) -> SymDigitTrial:
        p = self.ad.live_profile()
        probe = random.choice(list(self._map.keys()))
        correct = self._map[probe]
        opts = {correct}
        digits = list(self._map.values())
        while len(opts) < min(4, len(digits)):
            opts.add(random.choice(digits))
        options = list(opts)
        random.shuffle(options)
        self.current = SymDigitTrial(
            key_map=self.key_map,
            probe_symbol=probe,
            correct_digit=correct,
            options=options,
            deadline_ms=max(800, p.deadline_ms),
        )
        return self.current

    def choose(self, digit: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(10, self.level)
        if digit is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = digit == self.current.correct_digit
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Coded" if good else f"Was {self.current.correct_digit}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
