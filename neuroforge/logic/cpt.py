"""
Continuous Performance Test (CPT-AX style)
Sustained attention / vigilance — used widely in ADHD and neurology assessment
(Rosvold et al.; Conners CPT lineage).
Respond only when A is followed by X; ignore other sequences.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

LETTERS = list("ABCDEFGHJKLMNPRSTUVWZ")


@dataclass
class CptTrial:
    letter: str
    is_target: bool  # AX target (previous was A, current is X)
    deadline_ms: int


class CptEngine:
    key = "cpt"
    domain = "attention"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="attention")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 24 + self.level * 3
        self.prev = ""
        self.target_rate = max(0.12, 0.28 - self.level * 0.012)
        self.current: CptTrial | None = None

    def next_trial(self) -> CptTrial:
        p = self.ad.live_profile()
        # Build AX sequences occasionally
        if self.prev == "A" and random.random() < 0.55:
            letter = "X" if random.random() < 0.7 else random.choice([c for c in LETTERS if c != "X"])
        elif random.random() < self.target_rate:
            letter = "A"
        else:
            letter = random.choice(LETTERS)
            if letter == "A" and random.random() < 0.3:
                letter = random.choice([c for c in LETTERS if c != "A"])
        is_target = self.prev == "A" and letter == "X"
        self.current = CptTrial(
            letter=letter,
            is_target=is_target,
            deadline_ms=max(450, p.deadline_ms // 3),
        )
        return self.current

    def respond(self, pressed: bool) -> dict:
        assert self.current is not None
        pts = points_for_level(8, self.level)
        if self.current.is_target:
            good = pressed
            msg = "Hit AX" if good else "Missed AX target"
        else:
            good = not pressed
            msg = "Correct withhold" if good else "False alarm"
        self.ad.observe(good)
        # update prev after response
        self.prev = self.current.letter
        return apply_hit(self.state, pts + (4 if self.current.is_target and good else 0), good, msg)

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
