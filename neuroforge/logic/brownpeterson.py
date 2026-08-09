"""
Brown–Peterson paradigm — distractor-filled retention interval
(classic short-term memory decay / interference research; clinical memory).
Encode 3 consonants → distractor math → recall trigram.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

CONS = list("BCDFGHJKLMNPRSTVWXYZ")


@dataclass
class BPTrial:
    trigram: str
    distractors: list[str]  # math prompts
    distractor_answers: list[int]
    options: list[str]
    encode_ms: int
    distract_ms: int
    deadline_ms: int


class BrownPetersonEngine:
    key = "brownpeterson"
    domain = "working_memory"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="working_memory")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 6 + self.level // 2
        self.n_distract = min(1 + self.level // 3, 4)
        self.current: BPTrial | None = None

    def next_trial(self) -> BPTrial:
        p = self.ad.live_profile()
        tri = "".join(random.sample(CONS, 3))
        distractors = []
        answers = []
        for _ in range(self.n_distract):
            a, b = random.randint(2, 12), random.randint(2, 12)
            distractors.append(f"{a} + {b}")
            answers.append(a + b)
        opts = {tri}
        while len(opts) < 4:
            opts.add("".join(random.sample(CONS, 3)))
        options = list(opts)
        random.shuffle(options)
        self.current = BPTrial(
            trigram=tri,
            distractors=distractors,
            distractor_answers=answers,
            options=options,
            encode_ms=max(800, p.encode_ms // 2),
            distract_ms=max(1500, 1200 + self.level * 100),
            deadline_ms=max(4000, p.deadline_ms + 500),
        )
        return self.current

    def choose(self, value: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(14, self.level)
        if value is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = value == self.current.trigram
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Trigram recalled" if good else f"Was {self.current.trigram}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
