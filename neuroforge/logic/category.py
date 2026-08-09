"""Category Flex pure logic — semantic set shifting."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, time_sec
from .scoring import ScoreState, apply_hit

ITEMS: dict[str, set[str]] = {
    "Apple": {"fruit", "food", "living"},
    "Banana": {"fruit", "food", "living"},
    "Carrot": {"veg", "food", "living"},
    "Dog": {"animal", "living"},
    "Eagle": {"animal", "living", "bird"},
    "Shark": {"animal", "living"},
    "Rose": {"plant", "living"},
    "Oak": {"plant", "living"},
    "Chair": {"furniture", "object"},
    "Table": {"furniture", "object"},
    "Car": {"vehicle", "object"},
    "Bike": {"vehicle", "object"},
    "Hammer": {"tool", "object"},
    "Phone": {"tech", "object"},
    "Laptop": {"tech", "object"},
    "Shirt": {"clothing", "object"},
    "Soccer": {"sport"},
    "Piano": {"music", "object"},
    "Rain": {"weather"},
    "Moon": {"space"},
    "Whale": {"animal", "living"},
    "Mango": {"fruit", "food", "living"},
    "Truck": {"vehicle", "object"},
    "Violin": {"music", "object"},
}

RULES = [
    ("fruit", "Is it a fruit?"),
    ("animal", "Is it an animal?"),
    ("living", "Is it living?"),
    ("object", "Is it a man-made object?"),
    ("vehicle", "Is it a vehicle?"),
    ("food", "Is it food?"),
    ("plant", "Is it a plant?"),
    ("tech", "Is it technology?"),
    ("music", "Is it related to music?"),
]


@dataclass
class CategoryTrial:
    word: str
    rule_key: str
    rule_prompt: str
    is_yes: bool
    switched: bool
    time_limit: float


class CategoryEngine:
    key = "category"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 12 + self.level * 2
        self.switch_every = max(2, 6 - self.level // 2)
        self.time_limit = time_sec(4.0, 1.5, self.level)
        self.rule_key, self.rule_prompt = random.choice(RULES)
        self.since_switch = 0
        self.current: CategoryTrial | None = None

    def _maybe_switch(self) -> bool:
        self.since_switch += 1
        if self.since_switch >= self.switch_every or (
            self.level >= 7 and random.random() < 0.15
        ):
            options = [r for r in RULES if r[0] != self.rule_key]
            self.rule_key, self.rule_prompt = random.choice(options)
            self.since_switch = 0
            return True
        return False

    def next_trial(self) -> CategoryTrial:
        switched = self._maybe_switch()
        want_yes = random.random() < 0.5
        pool_yes = [w for w, tags in ITEMS.items() if self.rule_key in tags]
        pool_no = [w for w, tags in ITEMS.items() if self.rule_key not in tags]
        if want_yes and pool_yes:
            word = random.choice(pool_yes)
            is_yes = True
        elif pool_no:
            word = random.choice(pool_no)
            is_yes = False
        else:
            word = random.choice(list(ITEMS.keys()))
            is_yes = self.rule_key in ITEMS[word]
        tl = max(1.2, self.time_limit - self.state.round_i * 0.03)
        self.current = CategoryTrial(
            word=word,
            rule_key=self.rule_key,
            rule_prompt=self.rule_prompt,
            is_yes=is_yes,
            switched=switched,
            time_limit=tl,
        )
        return self.current

    def answer(self, said_yes: bool | None) -> dict:
        assert self.current is not None
        pts = points_for_level(11, self.level)
        if said_yes is None:
            return apply_hit(self.state, pts, False, "Time's up")
        good = said_yes == self.current.is_yes
        if good:
            return apply_hit(self.state, pts, True, "Fits rule" if said_yes else "Correct reject")
        return apply_hit(
            self.state, pts, False,
            "Does fit" if self.current.is_yes else "Does NOT fit",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
