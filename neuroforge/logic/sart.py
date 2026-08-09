"""
SART — Sustained Attention to Response Task
(Robertson et al., 1997; widely used in attention / mind-wandering research).

Go on most digits; withhold on a rare target (e.g. 3).
Harder levels: faster pace + rarer no-go = more commission errors.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class SartTrial:
    digit: int
    is_nogo: bool  # True if should WITHHOLD
    stim_ms: int
    isi_ms: int


class SartEngine:
    key = "sart"
    domain = "inhibition"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="inhibition")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 20 + self.level * 3
        self.nogo_digit = 3
        self.current: SartTrial | None = None

    def next_trial(self) -> SartTrial:
        p = self.ad.live_profile()
        # SART: ~11% no-go classic; we scale 8%→18%
        nogo_rate = 0.08 + p.conflict * 0.18
        is_nogo = random.random() < nogo_rate
        digit = self.nogo_digit if is_nogo else random.choice([d for d in range(1, 10) if d != self.nogo_digit])
        if not is_nogo and random.random() < 0.05:
            digit = self.nogo_digit  # rare accidental — still no-go truth
            is_nogo = True
        self.current = SartTrial(
            digit=digit,
            is_nogo=is_nogo,
            stim_ms=max(250, p.encode_ms // 2),
            isi_ms=max(200, p.isi_ms),
        )
        return self.current

    def respond(self, pressed: bool) -> dict:
        assert self.current is not None
        pts = points_for_level(10, self.level)
        if self.current.is_nogo:
            good = not pressed
            msg = "Correct withhold" if good else "Commission error (should hold)"
        else:
            good = pressed
            msg = "Go" if good else "Omission (should tap)"
        self.ad.observe(good)
        return apply_hit(self.state, pts, good, msg)

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
