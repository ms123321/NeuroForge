"""Block Span pure logic — Corsi block tapping."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size, time_ms
from .scoring import ScoreState, apply_hit


@dataclass
class SpanTrial:
    sequence: list[int]
    flash_ms: int
    grid: int


class SpanEngine:
    key = "span"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 7 + self.level // 2
        self.seq_len = set_size(2, 8, self.level)
        self.flash_ms = time_ms(700, 280, self.level)
        self.grid = 3
        self.n_cells = 9
        self.current: SpanTrial | None = None
        self.player: list[int] = []

    def next_trial(self) -> SpanTrial:
        length = min(9, self.seq_len + self.state.round_i // 2)
        if length <= self.n_cells:
            seq = random.sample(range(self.n_cells), length)
        else:
            seq = [random.randrange(self.n_cells) for _ in range(length)]
        self.player = []
        flash = max(220, self.flash_ms - self.state.round_i * 12)
        self.current = SpanTrial(sequence=seq, flash_ms=flash, grid=self.grid)
        return self.current

    def tap(self, idx: int) -> dict | None:
        assert self.current is not None
        self.player.append(idx)
        expected = self.current.sequence[: len(self.player)]
        pts = points_for_level(14, self.level)
        if self.player != expected:
            return apply_hit(self.state, pts, False, "Wrong block")
        if len(self.player) == len(self.current.sequence):
            event = apply_hit(
                self.state, pts + len(self.current.sequence) * 3, True,
                f"Span {len(self.current.sequence)}",
            )
            if self.state.correct % 2 == 0:
                self.seq_len = min(9, self.seq_len + 1)
            return event
        return None

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
