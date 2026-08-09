"""
Word-list learning — RAVLT / CVLT–inspired free recall
(clinical verbal memory assessment).
Study a list, then free-recall by tapping words from a pool.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit

WORD_BANK = [
    "DRUM", "CURTAIN", "BELL", "COFFEE", "SCHOOL", "PARENT", "MOON", "GARDEN",
    "HAT", "FARMER", "NOSE", "TURKEY", "COLOR", "HOUSE", "RIVER", "APPLE",
    "TABLE", "WINDOW", "CANDLE", "FOREST", "MIRROR", "PENCIL", "CASTLE", "ORANGE",
]


@dataclass
class WordListTrial:
    study: list[str]
    pool: list[str]
    study_ms: int
    deadline_ms: int


class WordListEngine:
    key = "wordlist"
    domain = "working_memory"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="working_memory")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 5 + self.level // 2
        self.list_len = min(4 + self.level // 2, 10)
        self.current: WordListTrial | None = None
        self.recalled: set[str] = set()

    def next_trial(self) -> WordListTrial:
        p = self.ad.live_profile()
        n = min(12, self.list_len + self.state.round_i // 2)
        study = random.sample(WORD_BANK, n)
        foils = [w for w in WORD_BANK if w not in study]
        pool = study + random.sample(foils, min(n, len(foils)))
        random.shuffle(pool)
        self.recalled = set()
        self.current = WordListTrial(
            study=study,
            pool=pool,
            study_ms=max(2500, p.encode_ms * n // 3),
            deadline_ms=max(10000, p.deadline_ms * 2 + n * 400),
        )
        return self.current

    def tap(self, word: str) -> dict | None:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        if word in self.recalled:
            return None
        if word not in self.current.study:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Intrusion (not on list)")
        self.recalled.add(word)
        if len(self.recalled) >= len(self.current.study):
            self.ad.observe(True)
            return apply_hit(
                self.state, pts + len(self.recalled) * 2, True,
                f"Full recall {len(self.recalled)}",
            )
        return None

    def finish_early(self) -> dict:
        assert self.current is not None
        pts = points_for_level(12, self.level)
        n = len(self.recalled)
        total = len(self.current.study)
        ratio = n / max(1, total)
        good = ratio >= 0.7
        self.ad.observe(good)
        return apply_hit(
            self.state, pts + n * 2, good,
            f"Recalled {n}/{total}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
