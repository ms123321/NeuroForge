"""
Rule discovery (WCST-lite)
Wisconsin Card Sorting Test–inspired set shifting / abstract rule search.
Used in executive function assessment; related to frontal network flexibility
studied across NIH aging and clinical neuropsychology.

Sort by color OR shape OR count; rule changes without warning after streaks.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

COLORS = [("Red", "#FF7B72"), ("Blue", "#6C8CFF"), ("Green", "#3DDCB5"), ("Gold", "#F5C542")]
SHAPES = ["●", "▲", "■", "◆"]


@dataclass
class Card:
    color_name: str
    color_hex: str
    shape: str
    count: int


@dataclass
class RuleTrial:
    rule: str  # color | shape | count
    target: Card
    options: list[Card]
    correct_index: int
    rule_changed: bool
    deadline_ms: int


def _random_card() -> Card:
    cn, ch = random.choice(COLORS)
    return Card(cn, ch, random.choice(SHAPES), random.randint(1, 4))


def _matches(rule: str, a: Card, b: Card) -> bool:
    if rule == "color":
        return a.color_name == b.color_name
    if rule == "shape":
        return a.shape == b.shape
    return a.count == b.count


class RuleSearchEngine:
    key = "rulesearch"
    domain = "flexibility"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="flexibility")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 14 + self.level * 2
        self.rules = ["color", "shape", "count"]
        self.rule = random.choice(self.rules)
        self.streak = 0
        self.switch_after = self.ad.base.switch_every
        self.current: RuleTrial | None = None

    def next_trial(self) -> RuleTrial:
        p = self.ad.live_profile()
        changed = False
        if self.streak >= p.switch_every:
            old = self.rule
            self.rule = random.choice([r for r in self.rules if r != old])
            self.streak = 0
            changed = True

        target = _random_card()
        # one correct match under current rule
        correct = _random_card()
        if self.rule == "color":
            correct.color_name, correct.color_hex = target.color_name, target.color_hex
            # ensure not also matching other rules accidentally only — ok if multi-match
        elif self.rule == "shape":
            correct.shape = target.shape
        else:
            correct.count = target.count

        options = [correct]
        while len(options) < 3:
            foil = _random_card()
            if not _matches(self.rule, target, foil):
                options.append(foil)
        random.shuffle(options)
        # re-find correct index
        correct_index = next(i for i, c in enumerate(options) if _matches(self.rule, target, c))

        self.current = RuleTrial(
            rule=self.rule,
            target=target,
            options=options,
            correct_index=correct_index,
            rule_changed=changed,
            deadline_ms=max(1200, p.deadline_ms),
        )
        return self.current

    def choose(self, index: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if index is None:
            self.ad.observe(False)
            self.streak = 0
            return apply_hit(self.state, pts, False, "Time's up")
        good = index == self.current.correct_index
        self.ad.observe(good)
        if good:
            self.streak += 1
            msg = "Rule shift!" if self.current.rule_changed else "Sorted"
            return apply_hit(self.state, pts, True, msg)
        self.streak = 0
        return apply_hit(self.state, pts, False, "Doesn't match the hidden rule")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
