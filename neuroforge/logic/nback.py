"""N-Back Lite pure logic — continuous working memory update."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, n_back_depth, points_for_level, time_ms
from .scoring import ScoreState, apply_hit

LETTERS = list("ABCFGJKLMPQRSXYZ")


@dataclass
class NBackTrial:
    letter: str
    is_match: bool
    n: int
    stim_ms: int
    history: list[str]


class NBackEngine:
    key = "nback"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.n = n_back_depth(self.level)
        self.rounds = 18 + self.level * 2
        self.stim_ms = time_ms(1800, 850, self.level)
        # higher match lure rate at high levels (harder)
        self.match_rate = 0.28 + self.level * 0.015
        self.history: list[str] = []
        self.current: NBackTrial | None = None

    def next_trial(self) -> NBackTrial:
        if len(self.history) >= self.n and random.random() < self.match_rate:
            letter = self.history[-self.n]
            is_match = True
        else:
            letter = random.choice(LETTERS)
            # lure: match n+1 or n-1 sometimes at high level
            if self.level >= 6 and len(self.history) >= self.n + 1 and random.random() < 0.2:
                letter = self.history[-(self.n + 1)]
            is_match = len(self.history) >= self.n and letter == self.history[-self.n]
            if len(self.history) >= self.n and not is_match:
                while letter == self.history[-self.n]:
                    letter = random.choice(LETTERS)
                is_match = False

        self.history.append(letter)
        stim = max(700, self.stim_ms - self.state.round_i * 12)
        self.current = NBackTrial(
            letter=letter,
            is_match=is_match,
            n=self.n,
            stim_ms=stim,
            history=list(self.history),
        )
        return self.current

    def answer(self, said_match: bool, timed_out: bool = False) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if timed_out:
            good = not self.current.is_match
            return apply_hit(self.state, pts, good, "Timeout (counted as no match)")
        good = said_match == self.current.is_match
        if good:
            msg = "Match correct" if said_match else "Correct reject"
        else:
            msg = "Was a match" if self.current.is_match else "Was NOT a match"
        return apply_hit(self.state, pts, good, msg)

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
