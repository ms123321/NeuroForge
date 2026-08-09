"""
Dichotic-style selective attention (visual analogue)
Attend LEFT or RIGHT stream; ignore the other (Hugdahl dichotic listening lineage).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

WORDS = [
    "CAT", "DOG", "SUN", "MOON", "TREE", "FISH", "BIRD", "ROCK",
    "LAKE", "WIND", "FIRE", "STAR", "BOOK", "DOOR", "SHIP", "ROAD",
]


@dataclass
class DichoticTrial:
    attend: str  # left | right
    left_word: str
    right_word: str
    options: list[str]
    answer: str
    switched: bool
    deadline_ms: int


class DichoticEngine:
    key = "dichotic"
    domain = "attention"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="attention")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 14 + self.level * 2
        self.attend = random.choice(["left", "right"])
        self.switch_every = max(2, 6 - self.level // 2)
        self.since = 0
        self.current: DichoticTrial | None = None

    def next_trial(self) -> DichoticTrial:
        p = self.ad.live_profile()
        self.since += 1
        switched = False
        if self.since >= self.switch_every:
            self.attend = "right" if self.attend == "left" else "left"
            self.since = 0
            switched = True
        left, right = random.sample(WORDS, 2)
        answer = left if self.attend == "left" else right
        opts = {answer}
        while len(opts) < 4:
            opts.add(random.choice(WORDS))
        options = list(opts)
        random.shuffle(options)
        self.current = DichoticTrial(
            attend=self.attend,
            left_word=left,
            right_word=right,
            options=options,
            answer=answer,
            switched=switched,
            deadline_ms=max(1800, p.deadline_ms),
        )
        return self.current

    def choose(self, word: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(11, self.level)
        if word is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = word == self.current.answer
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            f"Attended {self.current.attend}" if good else f"Was {self.current.answer}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
