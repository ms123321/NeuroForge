"""Object Track — simplified multiple-object tracking (Pylyshyn & Storm, 1988)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size, time_ms
from .scoring import ScoreState, apply_hit


@dataclass
class TrackTrial:
    n_objects: int
    targets: list[int]  # indices that were targets
    path_steps: list[list[tuple[float, float]]]  # per object list of (x,y) 0-1
    flash_ms: int
    move_steps: int
    step_ms: int


class TrackEngine:
    key = "track"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 6 + self.level // 2
        self.n_objects = set_size(4, 8, self.level)
        self.n_targets = set_size(1, 3, self.level)
        self.move_steps = set_size(4, 10, self.level)
        self.step_ms = time_ms(280, 140, self.level)
        self.flash_ms = time_ms(900, 450, self.level)
        self.current: TrackTrial | None = None

    def next_trial(self) -> TrackTrial:
        n = self.n_objects
        n_t = min(self.n_targets, n - 1)
        targets = random.sample(range(n), n_t)
        # random walk paths for each object
        positions = [(random.uniform(0.15, 0.85), random.uniform(0.15, 0.85)) for _ in range(n)]
        paths: list[list[tuple[float, float]]] = [[p] for p in positions]
        steps = self.move_steps + self.state.round_i // 2
        for _ in range(steps):
            for i in range(n):
                x, y = paths[i][-1]
                x = min(0.9, max(0.1, x + random.uniform(-0.18, 0.18)))
                y = min(0.9, max(0.1, y + random.uniform(-0.18, 0.18)))
                paths[i].append((x, y))
        self.current = TrackTrial(
            n_objects=n,
            targets=sorted(targets),
            path_steps=paths,
            flash_ms=self.flash_ms,
            move_steps=steps,
            step_ms=self.step_ms,
        )
        return self.current

    def choose(self, selected: list[int]) -> dict:
        assert self.current is not None
        pts = points_for_level(15, self.level)
        sel = sorted(selected)
        good = sel == self.current.targets
        if good:
            return apply_hit(self.state, pts + len(self.current.targets) * 3, True, "Tracked!")
        return apply_hit(
            self.state, pts, False,
            f"Targets were {self.current.targets}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
