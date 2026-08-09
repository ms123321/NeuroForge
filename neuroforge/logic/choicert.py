"""
Choice reaction time — classic psychomotor / processing-speed measure
(clinical neuropsych batteries; simple vs choice RT).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class ChoiceRtTrial:
    side: str  # left | right
    n_choices: int  # 2 or 4
    options: list[str]
    deadline_ms: int
    isi_ms: int


class ChoiceRtEngine:
    key = "choicert"
    domain = "processing_speed"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="processing_speed")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 16 + self.level * 2
        self.n_choices = 2 if self.level < 5 else 4
        self.current: ChoiceRtTrial | None = None
        self._t0 = 0.0

    def next_trial(self) -> ChoiceRtTrial:
        p = self.ad.live_profile()
        if self.n_choices == 2:
            options = ["LEFT", "RIGHT"]
            side = random.choice(["left", "right"])
        else:
            options = ["TL", "TR", "BL", "BR"]
            side = random.choice(["tl", "tr", "bl", "br"])
        self.current = ChoiceRtTrial(
            side=side,
            n_choices=self.n_choices,
            options=options,
            deadline_ms=max(600, p.deadline_ms // 3),
            isi_ms=max(200, p.isi_ms // 2),
        )
        self._t0 = time.perf_counter()
        return self.current

    def answer(self, choice: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(10, self.level)
        elapsed_ms = int((time.perf_counter() - self._t0) * 1000)
        if choice is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Too slow")
        # normalize
        c = choice.lower().replace(" ", "")
        target = self.current.side
        mapping = {
            "left": "left", "right": "right",
            "tl": "tl", "tr": "tr", "bl": "bl", "br": "br",
            "topleft": "tl", "topright": "tr", "bottomleft": "bl", "bottomright": "br",
        }
        got = mapping.get(c, c)
        good = got == target
        self.ad.observe(good)
        if good:
            bonus = max(0, 15 - elapsed_ms // 50)
            return apply_hit(self.state, pts + bonus, True, f"RT {elapsed_ms} ms")
        return apply_hit(self.state, pts, False, f"Was {target.upper()}")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
