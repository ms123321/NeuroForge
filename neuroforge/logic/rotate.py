"""Mental Rotation pure logic — visuospatial (Shepard & Metzler)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, rate, time_sec
from .scoring import ScoreState, apply_hit

SHAPES = {
    "L": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "T": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "J": [(1, 0), (1, 1), (1, 2), (0, 2)],
    "U": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)],
    "P": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)],
}


def rotate_cells(cells: list[tuple[int, int]], times: int) -> list[tuple[int, int]]:
    out = list(cells)
    for _ in range(times % 4):
        out = [(y, -x) for x, y in out]
    min_x = min(x for x, _ in out)
    min_y = min(y for _, y in out)
    return sorted((x - min_x, y - min_y) for x, y in out)


def mirror_cells(cells: list[tuple[int, int]]) -> list[tuple[int, int]]:
    out = [(-x, y) for x, y in cells]
    min_x = min(x for x, _ in out)
    min_y = min(y for _, y in out)
    return sorted((x - min_x, y - min_y) for x, y in out)


@dataclass
class RotateTrial:
    shape_name: str
    base_cells: list[tuple[int, int]]
    option_a: list[tuple[int, int]]
    option_b: list[tuple[int, int]]
    correct: str
    probe_cells: list[tuple[int, int]]
    is_same: bool
    rotation_deg: int
    time_limit: float


class RotateEngine:
    key = "rotate"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 10 + self.level
        self.time_limit = time_sec(7.0, 2.2, self.level)
        self.mirror_rate = rate(0.3, 0.6, self.level)
        # higher levels use more complex shapes
        self.shape_keys = list(SHAPES.keys())[: max(3, min(7, 3 + self.level // 2))]
        self.current: RotateTrial | None = None

    def next_trial(self) -> RotateTrial:
        name = random.choice(self.shape_keys)
        base = rotate_cells(SHAPES[name], random.randrange(4))
        # larger angular disparity at high level is harder for some people;
        # use 90/180/270 always; at high level prefer non-trivial
        rot = random.choice([1, 2, 3] if self.level < 6 else [1, 3, 2, 1, 3])
        same = rotate_cells(base, rot)
        use_mirror = random.random() < self.mirror_rate
        if use_mirror:
            probe = rotate_cells(mirror_cells(same), random.randrange(4))
            is_same = False
        else:
            probe = same
            is_same = True
        tl = max(1.8, self.time_limit - self.state.round_i * 0.08)
        self.current = RotateTrial(
            shape_name=name,
            base_cells=base,
            option_a=base,
            option_b=probe,
            correct="same" if is_same else "mirror",
            probe_cells=probe,
            is_same=is_same,
            rotation_deg=rot * 90,
            time_limit=tl,
        )
        return self.current

    def answer(self, said_same: bool, timed_out: bool = False) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if timed_out:
            return apply_hit(self.state, pts, False, "Time's up")
        good = said_same == self.current.is_same
        if good:
            msg = "Same shape (rotated)" if said_same else "Correct — it's a mirror"
        else:
            msg = "Actually same (rotation)" if self.current.is_same else "Actually a mirror/foil"
        return apply_hit(self.state, pts, good, msg)

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
