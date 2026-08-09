"""
Letter / symbol cancellation — clinical attention & visual search
(star cancellation, letter cancellation used in neglect screening).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

FOILS = list("ABCDEFGHJKLMNPRSTUVXYZ")


@dataclass
class CancelTrial:
    cells: list[str]
    target: str
    target_indices: list[int]
    cols: int
    deadline_ms: int


class CancellationEngine:
    key = "cancel"
    domain = "attention"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="attention")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 8 + self.level // 2
        self.grid_n = min(16 + self.level * 2, 36)
        self.current: CancelTrial | None = None
        self.found: set[int] = set()

    def next_trial(self) -> CancelTrial:
        p = self.ad.live_profile()
        n = min(40, self.grid_n + self.state.round_i)
        target = random.choice(["Q", "O", "X", "★"])
        n_targets = max(3, min(8, 3 + self.level // 2))
        cells = []
        target_indices = []
        for i in range(n):
            if len(target_indices) < n_targets and (
                n - i <= n_targets - len(target_indices) or random.random() < 0.2
            ):
                cells.append(target)
                target_indices.append(i)
            else:
                foil = random.choice(FOILS)
                while foil == target:
                    foil = random.choice(FOILS)
                cells.append(foil)
        # ensure exact count
        while len(target_indices) < n_targets:
            i = random.randrange(n)
            if i not in target_indices:
                cells[i] = target
                target_indices.append(i)
        cols = 6 if n > 24 else 5 if n > 16 else 4
        self.found = set()
        self.current = CancelTrial(
            cells=cells,
            target=target,
            target_indices=sorted(target_indices),
            cols=cols,
            deadline_ms=max(8000, p.deadline_ms * 2 + n * 120),
        )
        return self.current

    def tap(self, index: int) -> dict | None:
        """Returns event when trial ends, else None if still searching."""
        assert self.current is not None
        pts = points_for_level(10, self.level)
        if index in self.found:
            return None
        if index in self.current.target_indices:
            self.found.add(index)
            if len(self.found) >= len(self.current.target_indices):
                self.ad.observe(True)
                return apply_hit(
                    self.state, pts + len(self.found) * 2, True,
                    f"All {len(self.found)} cancelled",
                )
            return None
        # false positive — end trial as miss
        self.ad.observe(False)
        return apply_hit(self.state, pts, False, "Not a target")

    def timeout(self) -> dict:
        assert self.current is not None
        pts = points_for_level(10, self.level)
        found = len(self.found)
        total = len(self.current.target_indices)
        good = found >= total
        self.ad.observe(good)
        if good:
            return apply_hit(self.state, pts, True, "Complete")
        return apply_hit(self.state, pts, False, f"Found {found}/{total}")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
