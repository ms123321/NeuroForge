"""Dual N-Back pure logic — letter + position (Jaeggi-style dual WM)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, n_back_depth, points_for_level, time_ms
from .scoring import ScoreState, apply_hit

LETTERS = list("ABCFGJKLQR")


@dataclass
class DualTrial:
    letter: str
    position: int
    letter_match: bool
    position_match: bool
    n: int
    stim_ms: int


class DualNBackEngine:
    key = "dual"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.n = n_back_depth(self.level)
        self.rounds = 14 + self.level * 2
        self.stim_ms = time_ms(2200, 1100, self.level)
        self.match_rate = 0.22 + self.level * 0.02
        self.letters: list[str] = []
        self.positions: list[int] = []
        self.current: DualTrial | None = None

    def next_trial(self) -> DualTrial:
        force_letter = len(self.letters) >= self.n and random.random() < self.match_rate
        force_pos = len(self.positions) >= self.n and random.random() < self.match_rate

        if force_letter:
            letter = self.letters[-self.n]
        else:
            letter = random.choice(LETTERS)
            if len(self.letters) >= self.n:
                while letter == self.letters[-self.n]:
                    letter = random.choice(LETTERS)

        if force_pos:
            position = self.positions[-self.n]
        else:
            position = random.randrange(9)
            if len(self.positions) >= self.n:
                while position == self.positions[-self.n]:
                    position = random.randrange(9)

        letter_match = len(self.letters) >= self.n and letter == self.letters[-self.n]
        position_match = len(self.positions) >= self.n and position == self.positions[-self.n]

        self.letters.append(letter)
        self.positions.append(position)
        stim = max(900, self.stim_ms - self.state.round_i * 15)
        self.current = DualTrial(
            letter=letter,
            position=position,
            letter_match=letter_match,
            position_match=position_match,
            n=self.n,
            stim_ms=stim,
        )
        return self.current

    def answer(self, said_letter_match: bool, said_pos_match: bool) -> dict:
        assert self.current is not None
        t = self.current
        pts = points_for_level(8, self.level)
        letter_ok = said_letter_match == t.letter_match
        pos_ok = said_pos_match == t.position_match
        apply_hit(self.state, pts, letter_ok, "letter")
        apply_hit(self.state, pts, pos_ok, "position")
        both = letter_ok and pos_ok
        return {
            "good": both,
            "partial": letter_ok or pos_ok,
            "message": f"{'L✓' if letter_ok else 'L✗'} {'P✓' if pos_ok else 'P✗'}"
            + ("  dual hit!" if both else ""),
            "letter_ok": letter_ok,
            "pos_ok": pos_ok,
        }

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
