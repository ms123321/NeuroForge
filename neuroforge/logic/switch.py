"""Switch Path pure logic — rule switching (cognitive flexibility)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .difficulty import clamp_level, points_for_level, set_size
from .scoring import ScoreState, apply_hit

SHAPES = ["●", "▲", "■", "◆", "★", "✚"]
COLORS = [
    ("Blue", "#6C8CFF"),
    ("Teal", "#3DDCB5"),
    ("Gold", "#F5C542"),
    ("Pink", "#F687B3"),
    ("Purple", "#B794F6"),
    ("Coral", "#FF7B72"),
]


@dataclass
class SwitchTrial:
    rule: str
    switched: bool
    target_shape: str
    target_color_name: str
    target_color: str
    options: list[tuple[str, str, str]]
    correct_index: int


class SwitchEngine:
    key = "switch"

    def __init__(self, level: int = 1):
        self.level = clamp_level(level)
        self.state = ScoreState(level=self.level)
        self.rounds = 14 + self.level * 2
        # Switch more often at high level (every 5 → every 2)
        self.switch_every = max(2, 6 - self.level // 2)
        self.n_options = set_size(2, 4, self.level)  # more choices at high level
        self.n_shapes = set_size(4, 6, self.level)
        self.n_colors = set_size(4, 6, self.level)
        self.rule = "color"
        self.since_switch = 0
        self.current: SwitchTrial | None = None

    def _maybe_switch(self) -> bool:
        self.since_switch += 1
        # occasional random switch at high level
        if self.since_switch >= self.switch_every or (
            self.level >= 7 and random.random() < 0.12
        ):
            self.rule = "shape" if self.rule == "color" else "color"
            self.since_switch = 0
            return True
        return False

    def next_trial(self) -> SwitchTrial:
        switched = self._maybe_switch()
        shapes = SHAPES[: self.n_shapes]
        colors = COLORS[: self.n_colors]
        target_shape = random.choice(shapes)
        target_color_name, target_color = random.choice(colors)

        if self.rule == "color":
            correct = (random.choice(shapes), target_color_name, target_color)
        else:
            correct = (target_shape, *random.choice(colors))

        options = [correct]
        while len(options) < self.n_options:
            shape = random.choice(shapes)
            cname, chex = random.choice(colors)
            foil = (shape, cname, chex)
            # foil must not also satisfy the rule
            if self.rule == "color" and cname == target_color_name:
                continue
            if self.rule == "shape" and shape == target_shape:
                continue
            if foil not in options:
                options.append(foil)

        random.shuffle(options)
        correct_index = options.index(correct)
        self.current = SwitchTrial(
            rule=self.rule,
            switched=switched,
            target_shape=target_shape,
            target_color_name=target_color_name,
            target_color=target_color,
            options=options,
            correct_index=correct_index,
        )
        return self.current

    def choose(self, index: int) -> dict:
        assert self.current is not None
        good = index == self.current.correct_index
        msg = f"Matched by {self.current.rule}" if good else f"Wrong — rule is {self.current.rule}"
        return apply_hit(self.state, points_for_level(12, self.level), good, msg)

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
