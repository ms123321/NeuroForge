"""
Posner spatial cueing task
(Posner, 1980) — attention orienting; used across cognitive neuroscience / NIH aging studies.

Central or peripheral cue predicts target side. Invalid cues cost RT.
Higher levels: shorter SOA, more invalid cues, more noise.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class PosnerTrial:
    cue_side: str  # left | right | neutral
    target_side: str
    valid: bool
    cue_ms: int
    soa_ms: int  # cue→target
    deadline_ms: int


class PosnerEngine:
    key = "posner"
    domain = "attention"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="attention")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 16 + self.level * 2
        self.current: PosnerTrial | None = None

    def next_trial(self) -> PosnerTrial:
        p = self.ad.live_profile()
        # valid cue rate falls with conflict axis
        valid_rate = max(0.55, 0.85 - p.conflict * 0.4)
        target = random.choice(["left", "right"])
        if random.random() < 0.12:
            cue = "neutral"
            valid = True  # neutral isn't invalid; no directional info
        elif random.random() < valid_rate:
            cue = target
            valid = True
        else:
            cue = "right" if target == "left" else "left"
            valid = False
        self.current = PosnerTrial(
            cue_side=cue,
            target_side=target,
            valid=valid if cue != "neutral" else True,
            cue_ms=max(80, p.encode_ms // 6),
            soa_ms=max(100, p.isi_ms // 2),
            deadline_ms=max(500, p.deadline_ms // 2),
        )
        return self.current

    def answer(self, side: str | None) -> dict:
        assert self.current is not None
        pts = points_for_level(11, self.level)
        if side is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Too slow")
        good = side == self.current.target_side
        self.ad.observe(good)
        if good:
            tag = "valid cue" if self.current.valid and self.current.cue_side != "neutral" else (
                "neutral" if self.current.cue_side == "neutral" else "invalid cue overcome"
            )
            return apply_hit(self.state, pts + (4 if not self.current.valid else 0), True, tag)
        return apply_hit(self.state, pts, False, f"Target was {self.current.target_side}")

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
