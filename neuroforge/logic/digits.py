"""Backward digit span — verbal working memory (WAIS-inspired)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size, time_ms
from .scoring import ScoreState, apply_hit


@dataclass
class DigitsTrial:
    forward: list[int]
    target: list[int]  # reversed
    flash_ms: int
    mode: str  # "backward"


class DigitsEngine:
    key = "digits"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 6 + self.level // 2
        self.span = set_size(3, 8, self.level)
        self.flash_ms = time_ms(900, 400, self.level)
        self.current: DigitsTrial | None = None
        self.player: list[int] = []

    def next_trial(self) -> DigitsTrial:
        length = min(9, self.span + self.state.round_i // 3)
        # unique digits preferred
        if length <= 10:
            forward = random.sample(range(10), length)
        else:
            forward = [random.randrange(10) for _ in range(length)]
        self.player = []
        flash = max(300, self.flash_ms - self.state.round_i * 20)
        self.current = DigitsTrial(
            forward=forward,
            target=list(reversed(forward)),
            flash_ms=flash,
            mode="backward",
        )
        return self.current

    def tap_digit(self, d: int) -> dict | None:
        assert self.current is not None
        self.player.append(d)
        expected = self.current.target[: len(self.player)]
        pts = points_for_level(14, self.level)
        if self.player != expected:
            return apply_hit(self.state, pts, False, "Wrong order")
        if len(self.player) == len(self.current.target):
            event = apply_hit(
                self.state, pts + len(self.player) * 2, True,
                f"Backward span {len(self.player)}",
            )
            if self.state.correct % 2 == 0:
                self.span = min(9, self.span + 1)
            return event
        return None

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
