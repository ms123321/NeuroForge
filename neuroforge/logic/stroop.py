"""Stroop pure logic — interference control (Stroop, 1935)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, rate, set_size, time_sec
from .scoring import ScoreState, apply_hit

COLOR_WORDS = [
    ("RED", "#FF7B72"),
    ("BLUE", "#6C8CFF"),
    ("GREEN", "#3DDCB5"),
    ("GOLD", "#F5C542"),
    ("PINK", "#F687B3"),
    ("PURPLE", "#B794F6"),
]


@dataclass
class StroopTrial:
    word: str
    ink_hex: str
    ink_name: str
    congruent: bool
    options: list[str]
    correct_ink: str
    time_limit: float


class StroopEngine:
    key = "stroop"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 12 + self.level * 2
        self.time_limit = time_sec(3.8, 1.4, self.level)
        self.incongruent_rate = rate(0.35, 0.88, self.level)
        self.n_options = set_size(3, 6, self.level)
        self.palette = COLOR_WORDS[: set_size(4, 6, self.level)]
        self.current: StroopTrial | None = None

    def next_trial(self) -> StroopTrial:
        word_name, word_hex = random.choice(self.palette)
        congruent = random.random() > self.incongruent_rate
        if congruent:
            ink_name, ink_hex = word_name, word_hex
        else:
            others = [c for c in self.palette if c[0] != word_name]
            ink_name, ink_hex = random.choice(others)

        names = [c[0] for c in self.palette]
        options = [ink_name]
        while len(options) < min(self.n_options, len(names)):
            pick = random.choice(names)
            if pick not in options:
                options.append(pick)
        random.shuffle(options)
        tl = max(1.2, self.time_limit - self.state.round_i * 0.03)
        self.current = StroopTrial(
            word=word_name,
            ink_hex=ink_hex,
            ink_name=ink_name,
            congruent=congruent,
            options=options,
            correct_ink=ink_name,
            time_limit=tl,
        )
        return self.current

    def choose(self, ink_name: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(10, self.level)
        if ink_name is None:
            return apply_hit(self.state, pts, False, "Time's up")
        good = ink_name == self.current.correct_ink
        if good:
            kind = "congruent" if self.current.congruent else "conflict resolved"
            return apply_hit(self.state, pts + (4 if not self.current.congruent else 0), True, kind)
        return apply_hit(self.state, pts, False, f"Ink was {self.current.correct_ink}")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
