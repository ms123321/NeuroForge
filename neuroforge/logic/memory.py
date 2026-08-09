"""Memory Lattice pure logic — sequence recall (working memory)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .difficulty import clamp_level, points_for_level, set_size, time_ms
from .scoring import ScoreState, apply_hit

TILE_COLORS = [
    ("#6C8CFF", "A"),
    ("#3DDCB5", "B"),
    ("#F5C542", "C"),
    ("#F687B3", "D"),
    ("#B794F6", "E"),
    ("#FF7B72", "F"),
    ("#63B3ED", "G"),
    ("#F6AD55", "H"),
]


@dataclass
class MemoryTrial:
    sequence: list[int]
    n_tiles: int
    flash_ms: int
    tiles: list[tuple[str, str]] = field(default_factory=list)


class MemoryEngine:
    key = "memory"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 7 + self.level // 2
        # L1: length 2, 4 tiles; L10: length 8, 8 tiles, fast flash
        self.seq_len = set_size(2, 8, self.level)
        self.n_tiles = set_size(4, 8, self.level)
        self.flash_ms = time_ms(750, 280, self.level)
        self.current: MemoryTrial | None = None
        self.player: list[int] = []

    def next_trial(self) -> MemoryTrial:
        # Within session growth
        length = min(9, self.seq_len + self.state.round_i // 2)
        tiles = TILE_COLORS[: self.n_tiles]
        seq = [random.randrange(self.n_tiles) for _ in range(length)]
        self.player = []
        flash = max(250, self.flash_ms - self.state.round_i * 15)
        self.current = MemoryTrial(
            sequence=seq, n_tiles=self.n_tiles, flash_ms=flash, tiles=tiles
        )
        return self.current

    def tap(self, idx: int) -> dict | None:
        assert self.current is not None
        self.player.append(idx)
        expected = self.current.sequence[: len(self.player)]
        if self.player != expected:
            return apply_hit(self.state, points_for_level(15, self.level), False, "Sequence broken")
        if len(self.player) == len(self.current.sequence):
            pts = points_for_level(10, self.level) + len(self.current.sequence) * 3
            event = apply_hit(self.state, pts, True, f"Perfect · {len(self.current.sequence)} steps")
            if self.state.correct % 2 == 0:
                self.seq_len = min(9, self.seq_len + 1)
            return event
        return None

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
