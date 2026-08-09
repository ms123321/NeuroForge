"""
RSVP / attentional selection
Rapid Serial Visual Presentation — attention research (attentional blink literature).

Stream of letters; report the target digit that appeared.
Higher levels: faster SOA, more distractors, optional second target (T2).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

LETTERS = list("ABCDEFGHJKLMNPQRSTUVWXYZ")


@dataclass
class RsvpTrial:
    stream: list[str]  # items shown in order
    target: str  # the digit character
    soa_ms: int
    options: list[str]
    deadline_ms: int


class RsvpEngine:
    key = "rsvp"
    domain = "attention"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="attention")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 10 + self.level
        self.current: RsvpTrial | None = None

    def next_trial(self) -> RsvpTrial:
        p = self.ad.live_profile()
        stream_len = max(6, min(14, p.set_size + 4))
        target = str(random.randint(0, 9))
        # place target not first/last
        pos = random.randint(2, stream_len - 2)
        stream = [random.choice(LETTERS) for _ in range(stream_len)]
        stream[pos] = target
        opts = {target}
        while len(opts) < 4:
            opts.add(str(random.randint(0, 9)))
        options = list(opts)
        random.shuffle(options)
        soa = max(60, p.encode_ms // 8)
        self.current = RsvpTrial(
            stream=stream,
            target=target,
            soa_ms=soa,
            options=options,
            deadline_ms=max(1500, p.deadline_ms),
        )
        return self.current

    def choose(self, value: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if value is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = value == self.current.target
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Caught it" if good else f"Was {self.current.target}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
