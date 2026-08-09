"""
Paired-associate / loci-style memory
Method of loci & paired associates used in memory training research
(often compared with dual n-back in transfer studies).
Learn word–location pairs, then cued recall.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

PLACES = ["Kitchen", "Garden", "Bridge", "Tower", "Lake", "Market", "Library", "Gate", "Hill", "Cave"]
ITEMS = ["Key", "Lamp", "Coin", "Book", "Cup", "Map", "Ring", "Bell", "Hat", "Rope", "Pen", "Shoe"]


@dataclass
class LociTrial:
    pairs: list[tuple[str, str]]  # place, item
    cue_place: str
    answer: str
    options: list[str]
    study_ms: int
    deadline_ms: int
    phase: str  # study shown once per "block" — each trial is one cue after study


class LociEngine:
    """Each round: study N pairs, then one cued recall (simplified per-trial study)."""

    key = "loci"
    domain = "working_memory"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="working_memory")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 8 + self.level // 2
        self.n_pairs = min(2 + self.level // 2, 6)
        self.current: LociTrial | None = None

    def next_trial(self) -> LociTrial:
        p = self.ad.live_profile()
        n = min(self.n_pairs + self.state.round_i // 4, 6)
        places = random.sample(PLACES, n)
        items = random.sample(ITEMS, n)
        pairs = list(zip(places, items))
        cue, answer = random.choice(pairs)
        opts = {answer}
        while len(opts) < min(4, len(ITEMS)):
            opts.add(random.choice(ITEMS))
        options = list(opts)
        random.shuffle(options)
        self.current = LociTrial(
            pairs=pairs,
            cue_place=cue,
            answer=answer,
            options=options,
            study_ms=max(1800, p.encode_ms * n // 2),
            deadline_ms=max(3000, p.deadline_ms + 500),
            phase="study",
        )
        return self.current

    def choose(self, item: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(13, self.level)
        if item is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = item == self.current.answer
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Loci recall OK" if good else f"Was {self.current.answer}",
        )

    def advance(self) -> None:
        self.state.round_i += 1
        if self.state.correct > 0 and self.state.correct % 3 == 0:
            self.n_pairs = min(7, self.n_pairs + 1)

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
