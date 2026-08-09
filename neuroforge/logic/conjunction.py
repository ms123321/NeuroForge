"""
Conjunction visual search (Treisman & Gelade feature integration theory).
Target defined by combination of features (e.g. red AND circle among distractors).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

SHAPES = ["●", "■", "▲"]
COLORS = [("#FF7B72", "red"), ("#6C8CFF", "blue"), ("#3DDCB5", "green")]


@dataclass
class SearchItem:
    shape: str
    color_hex: str
    color_name: str
    is_target: bool


@dataclass
class ConjunctionTrial:
    items: list[SearchItem]
    target_desc: str
    target_index: int
    present: bool  # target present or absent trial
    cols: int
    deadline_ms: int


class ConjunctionEngine:
    key = "conjunction"
    domain = "attention"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="attention")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 12 + self.level
        self.set_n = min(6 + self.level, 16)
        self.current: ConjunctionTrial | None = None

    def next_trial(self) -> ConjunctionTrial:
        p = self.ad.live_profile()
        n = min(20, self.set_n + self.state.round_i // 3)
        t_shape = random.choice(SHAPES)
        t_hex, t_name = random.choice(COLORS)
        present = random.random() < 0.55
        items: list[SearchItem] = []
        target_index = -1
        for i in range(n):
            # distractors share one feature
            if random.random() < 0.5:
                shape, (hx, nm) = t_shape, random.choice([c for c in COLORS if c[1] != t_name] or COLORS)
            else:
                shape = random.choice([s for s in SHAPES if s != t_shape] or SHAPES)
                hx, nm = t_hex, t_name
            items.append(SearchItem(shape, hx, nm, False))
        if present:
            target_index = random.randrange(n)
            items[target_index] = SearchItem(t_shape, t_hex, t_name, True)
        cols = 4 if n > 9 else 3
        self.current = ConjunctionTrial(
            items=items,
            target_desc=f"{t_name.upper()} {t_shape}",
            target_index=target_index,
            present=present,
            cols=cols,
            deadline_ms=max(2000, p.deadline_ms + n * 80),
        )
        return self.current

    def choose(self, index: int | None, said_absent: bool = False) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if said_absent:
            good = not self.current.present
            self.ad.observe(good)
            return apply_hit(self.state, pts, good, "Correct absent" if good else "Target was present")
        if index is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = self.current.present and index == self.current.target_index
        self.ad.observe(good)
        return apply_hit(self.state, pts, good, "Found target" if good else "Not the target")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
