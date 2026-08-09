"""Operation span — complex working memory (Turner & Engle, 1989)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .difficulty import clamp_level, points_for_level, set_size, time_sec
from .scoring import ScoreState, apply_hit

LETTERS = list("FHJKLNPQRSTY")


@dataclass
class OspanItem:
    expression: str
    math_answer: int
    math_options: list[int]
    letter: str


@dataclass
class OspanTrial:
    items: list[OspanItem]
    target_letters: list[str]
    math_time: float


class OspanEngine:
    """
    For each item: solve math, then remember a letter.
    At end: recall letters in order.
    """

    key = "opspan"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 5 + self.level // 2
        self.span = set_size(2, 5, self.level)
        self.math_time = time_sec(5.0, 2.2, self.level)
        self.current: OspanTrial | None = None
        self.phase = "math"  # math | letter | recall
        self.item_i = 0
        self.math_ok = 0
        self.player_letters: list[str] = []

    def next_trial(self) -> OspanTrial:
        length = min(6, self.span + self.state.round_i // 3)
        items = []
        letters = []
        for _ in range(length):
            a, b = random.randint(2, 9 + self.level), random.randint(1, 9)
            op = random.choice(["+", "−", "×"] if self.level >= 4 else ["+", "−"])
            if op == "+":
                ans = a + b
                expr = f"{a} + {b}"
            elif op == "−":
                if a < b:
                    a, b = b, a
                ans = a - b
                expr = f"{a} − {b}"
            else:
                ans = a * b
                expr = f"{a} × {b}"
            opts = {ans}
            while len(opts) < 3:
                opts.add(ans + random.choice([-3, -2, -1, 1, 2, 3]))
            opt_list = list(opts)
            random.shuffle(opt_list)
            let = random.choice(LETTERS)
            letters.append(let)
            items.append(OspanItem(expression=expr, math_answer=ans, math_options=opt_list, letter=let))
        self.current = OspanTrial(items=items, target_letters=letters, math_time=self.math_time)
        self.phase = "math"
        self.item_i = 0
        self.math_ok = 0
        self.player_letters = []
        return self.current

    def answer_math(self, value: int | None) -> dict:
        assert self.current is not None
        item = self.current.items[self.item_i]
        good = value is not None and value == item.math_answer
        if good:
            self.math_ok += 1
        self.phase = "letter"
        return {
            "good": good,
            "message": "Math OK" if good else f"Math was {item.math_answer}",
            "letter": item.letter,
        }

    def ack_letter(self) -> None:
        self.item_i += 1
        if self.item_i >= len(self.current.items):
            self.phase = "recall"
        else:
            self.phase = "math"

    def recall(self, letters: list[str]) -> dict:
        assert self.current is not None
        pts = points_for_level(16, self.level)
        target = self.current.target_letters
        good = letters == target
        # also require majority math correct for full credit feel
        math_ratio = self.math_ok / max(1, len(target))
        if good and math_ratio >= 0.5:
            if self.state.correct % 2 == 0:
                self.span = min(6, self.span + 1)
            return apply_hit(self.state, pts + len(target) * 3, True, f"Complex span {len(target)}")
        if good:
            return apply_hit(self.state, pts // 2, True, "Letters OK (math weak)")
        return apply_hit(self.state, pts, False, f"Was {''.join(target)}")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
