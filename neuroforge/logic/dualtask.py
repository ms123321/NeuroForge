"""
Cognitive dual-task — letter 1-back + digit store/probe.

Primary: is the letter the same as the previous trial?
Secondary: remember the digit; occasionally report the previous digit.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

LETTERS = list("ABCFGJKL")


@dataclass
class DualTaskTrial:
    letter: str
    letter_match: bool  # True if same as previous letter
    digit: int  # digit to store this trial
    probe_digit: bool  # ask for previous digit after letter response
    previous_digit: int | None  # correct answer for probe (None = skip probe)
    is_first: bool
    deadline_ms: int


class DualTaskEngine:
    key = "dualtask"
    domain = "working_memory"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="working_memory")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 12 + self.level * 2
        self.prev_letter: str | None = None
        self.stored_digit: int | None = None  # digit from last committed trial
        # probe every 2–4 trials depending on level
        self.ask_every = max(2, 5 - self.level // 3)
        self._since_probe = 0
        self.current: DualTaskTrial | None = None

    def next_trial(self) -> DualTaskTrial:
        p = self.ad.live_profile()
        is_first = self.prev_letter is None

        if is_first:
            letter = random.choice(LETTERS)
            letter_match = False
        elif random.random() < 0.32:
            letter = self.prev_letter  # type: ignore[assignment]
            letter_match = True
        else:
            letter = random.choice(LETTERS)
            while letter == self.prev_letter:
                letter = random.choice(LETTERS)
            letter_match = False

        digit = random.randint(0, 9)

        # Probe the digit from the *previous* committed trial
        self._since_probe += 1
        probe = (
            not is_first
            and self.stored_digit is not None
            and self._since_probe >= self.ask_every
        )
        if probe:
            self._since_probe = 0

        self.current = DualTaskTrial(
            letter=letter,
            letter_match=letter_match,
            digit=digit,
            probe_digit=probe,
            previous_digit=self.stored_digit if probe else None,
            is_first=is_first,
            deadline_ms=max(2000, min(4500, p.deadline_ms)),
        )
        return self.current

    def answer_letter(self, said_match: bool) -> dict:
        assert self.current is not None
        pts = points_for_level(8, self.level)
        # First trial: only "NEW" (not same) is correct
        expected = False if self.current.is_first else self.current.letter_match
        good = said_match == expected
        self.ad.observe(good)
        if self.current.is_first:
            msg = "First letter — NEW is correct" if good else "First trial: choose NEW"
        else:
            msg = "Letter OK" if good else (
                "Was SAME" if expected else "Was NEW"
            )
        return apply_hit(self.state, pts, good, msg)

    def answer_digit(self, value: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(10, self.level)
        target = self.current.previous_digit
        if target is None:
            return {"good": True, "message": "No probe", "warmup": True, "points": 0}
        if value is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, f"Digit timeout (was {target})")
        good = value == target
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Digit OK" if good else f"Previous digit was {target}",
        )

    def commit_trial(self) -> None:
        """Advance memory streams after the trial is fully resolved."""
        assert self.current is not None
        self.prev_letter = self.current.letter
        self.stored_digit = self.current.digit

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
