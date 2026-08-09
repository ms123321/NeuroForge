"""
NeuroForge Adaptive Difficulty Engine
=====================================

Implements progressive challenge for neuroplasticity-oriented training,
aligned with the *mismatch model of cognitive plasticity*: keep demand
slightly above current ability so circuits reorganize under load
(see dual n-back adaptive protocols used in NIH-funded WM research).

Design principles
-----------------
1. **Challenge zone** — target ~72–85% accuracy (not too easy, not chaotic).
2. **Multi-axis load** — difficulty is a vector, not a single number:
   speed, set size, conflict rate, dual load, distractors, n-depth.
3. **Between-session levels** — persistent level 1–10 from progress save.
4. **Within-session adaptation** — rolling accuracy tightens/loosens load live.
5. **Promote / demote** — after a session, recommend level change.

Engines call ``profile = AdaptiveEngine(level).profile`` then scale params,
and optionally ``engine.observe(correct)`` each trial for live pressure.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


# ── Level scale ──────────────────────────────────────────────────────────

LEVEL_MIN = 1
LEVEL_MAX = 10

# Target accuracy band for the plasticity "sweet spot"
TARGET_ACC_LOW = 0.72
TARGET_ACC_HIGH = 0.85

# Session promote / demote thresholds (stricter promote at higher levels)
PROMOTE_ACC = 0.82
DEMOTE_ACC = 0.52
MIN_ATTEMPTS = 8


def clamp_level(level: int) -> int:
    return max(LEVEL_MIN, min(LEVEL_MAX, int(level)))


def level_t(level: int) -> float:
    """Normalized difficulty 0.0 (L1) → 1.0 (L10)."""
    return (clamp_level(level) - 1) / (LEVEL_MAX - 1)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_int(a: int, b: int, t: float) -> int:
    return int(round(lerp(a, b, t)))


# ── Multi-axis profile ───────────────────────────────────────────────────

@dataclass(frozen=True)
class DifficultyProfile:
    """
    Full load vector for one session/round.

    Axes (all increase hardness except times which decrease):
      speed_t        0–1  how rushed (1 = fastest deadlines)
      set_size       int  items to hold / search / sequence length
      conflict       0–1  incongruent / no-go / stop probability
      dual_load      0–1  second-stream demand
      distractors    int  foil count
      n_depth        int  n-back depth
      encode_ms      int  encoding / stimulus duration
      deadline_ms    int  response window
      isi_ms         int  inter-stimulus interval
      switch_every   int  trials between rule switches (lower = harder)
    """

    level: int
    label: str
    speed_t: float
    set_size: int
    conflict: float
    dual_load: float
    distractors: int
    n_depth: int
    encode_ms: int
    deadline_ms: int
    isi_ms: int
    switch_every: int
    within_pressure: float = 0.0  # live session tightening 0–0.35

    def describe(self) -> str:
        return (
            f"Lv{self.level} {self.label} · set {self.set_size} · "
            f"N={self.n_depth} · conflict {self.conflict:.0%} · "
            f"{self.deadline_ms}ms"
        )

    def with_pressure(self, pressure: float) -> DifficultyProfile:
        """Return a copy tightened by within-session pressure (0–0.35)."""
        p = max(0.0, min(0.35, pressure))
        return DifficultyProfile(
            level=self.level,
            label=self.label,
            speed_t=min(1.0, self.speed_t + p * 0.5),
            set_size=self.set_size + (1 if p > 0.2 else 0),
            conflict=min(0.85, self.conflict + p * 0.25),
            dual_load=min(1.0, self.dual_load + p * 0.2),
            distractors=self.distractors + (1 if p > 0.15 else 0),
            n_depth=self.n_depth,
            encode_ms=max(200, int(self.encode_ms * (1 - p * 0.35))),
            deadline_ms=max(350, int(self.deadline_ms * (1 - p * 0.35))),
            isi_ms=max(150, int(self.isi_ms * (1 - p * 0.3))),
            switch_every=max(2, self.switch_every - (1 if p > 0.2 else 0)),
            within_pressure=p,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def difficulty_label(level: int) -> str:
    lv = clamp_level(level)
    if lv <= 2:
        return "Easy"
    if lv <= 4:
        return "Moderate"
    if lv <= 6:
        return "Challenging"
    if lv <= 8:
        return "Hard"
    return "Elite"


# Domain templates: easy→hard endpoints for each axis
# Values chosen so L1 is learnable and L10 is demanding.
_DOMAIN_AXES: dict[str, dict[str, tuple]] = {
    # (easy, hard) for continuous; ints for discrete
    "default": {
        "set_size": (2, 8),
        "conflict": (0.2, 0.55),
        "dual_load": (0.0, 0.7),
        "distractors": (1, 6),
        "n_depth": (1, 4),
        "encode_ms": (1200, 400),
        "deadline_ms": (2800, 900),
        "isi_ms": (700, 250),
        "switch_every": (6, 2),
    },
    "working_memory": {
        "set_size": (2, 9),
        "conflict": (0.15, 0.4),
        "dual_load": (0.0, 0.9),
        "distractors": (0, 4),
        "n_depth": (1, 4),
        "encode_ms": (1000, 350),
        "deadline_ms": (3000, 1000),
        "isi_ms": (600, 200),
        "switch_every": (8, 3),
    },
    "attention": {
        "set_size": (3, 8),
        "conflict": (0.25, 0.7),
        "dual_load": (0.0, 0.5),
        "distractors": (2, 8),
        "n_depth": (1, 2),
        "encode_ms": (1100, 350),
        "deadline_ms": (2500, 800),
        "isi_ms": (650, 220),
        "switch_every": (5, 2),
    },
    "inhibition": {
        "set_size": (1, 3),
        "conflict": (0.22, 0.55),  # stop/no-go rate
        "dual_load": (0.0, 0.3),
        "distractors": (0, 2),
        "n_depth": (1, 2),
        "encode_ms": (1000, 380),
        "deadline_ms": (1200, 450),
        "isi_ms": (700, 280),
        "switch_every": (6, 3),
    },
    "flexibility": {
        "set_size": (2, 5),
        "conflict": (0.3, 0.65),
        "dual_load": (0.1, 0.6),
        "distractors": (1, 4),
        "n_depth": (1, 2),
        "encode_ms": (900, 400),
        "deadline_ms": (3500, 1400),
        "isi_ms": (500, 200),
        "switch_every": (5, 2),
    },
    "processing_speed": {
        "set_size": (3, 9),
        "conflict": (0.1, 0.3),
        "dual_load": (0.0, 0.4),
        "distractors": (2, 7),
        "n_depth": (1, 2),
        "encode_ms": (800, 300),
        "deadline_ms": (3500, 1000),
        "isi_ms": (400, 150),
        "switch_every": (8, 4),
    },
    "visuospatial": {
        "set_size": (2, 7),
        "conflict": (0.3, 0.6),
        "dual_load": (0.0, 0.5),
        "distractors": (1, 5),
        "n_depth": (1, 3),
        "encode_ms": (1400, 450),
        "deadline_ms": (6000, 2000),
        "isi_ms": (500, 200),
        "switch_every": (6, 3),
    },
}


def build_profile(level: int, domain: str = "default") -> DifficultyProfile:
    """Build a static profile for a between-session level + domain."""
    lv = clamp_level(level)
    tt = level_t(lv)
    axes = _DOMAIN_AXES.get(domain, _DOMAIN_AXES["default"])
    # mild ease-in curve so early levels stay approachable
    tt_eased = tt ** 0.9

    def ax_int(key: str) -> int:
        a, b = axes[key]
        return lerp_int(int(a), int(b), tt_eased)

    def ax_float(key: str) -> float:
        a, b = axes[key]
        return lerp(float(a), float(b), tt_eased)

    # n_depth stepwise (research protocols step n, not lerp)
    n = ax_int("n_depth")
    if domain in ("working_memory", "default"):
        if lv <= 2:
            n = 1
        elif lv <= 5:
            n = 2
        elif lv <= 8:
            n = 3
        else:
            n = 4

    return DifficultyProfile(
        level=lv,
        label=difficulty_label(lv),
        speed_t=tt_eased,
        set_size=ax_int("set_size"),
        conflict=ax_float("conflict"),
        dual_load=ax_float("dual_load"),
        distractors=ax_int("distractors"),
        n_depth=n,
        encode_ms=ax_int("encode_ms"),
        deadline_ms=ax_int("deadline_ms"),
        isi_ms=ax_int("isi_ms"),
        switch_every=ax_int("switch_every"),
        within_pressure=0.0,
    )


# ── Live adaptive engine ─────────────────────────────────────────────────

@dataclass
class AdaptiveEngine:
    """
    Session-scoped adaptive difficulty controller.

    Usage::

        ad = AdaptiveEngine(level=3, domain="working_memory")
        profile = ad.live_profile()   # use for next trial
        ad.observe(correct=True)
        rec = ad.recommend_level_delta()  # after session: -1, 0, or +1
    """

    level: int = 1
    domain: str = "default"
    window: int = 8  # rolling accuracy window
    history: list[bool] = field(default_factory=list)
    base: DifficultyProfile = field(init=False)

    def __post_init__(self) -> None:
        self.level = clamp_level(self.level)
        self.base = build_profile(self.level, self.domain)
        self.history = list(self.history)

    def observe(self, correct: bool) -> None:
        self.history.append(bool(correct))

    @property
    def attempts(self) -> int:
        return len(self.history)

    @property
    def accuracy(self) -> float:
        if not self.history:
            return 1.0
        return sum(self.history) / len(self.history)

    @property
    def rolling_accuracy(self) -> float:
        w = self.history[-self.window :]
        if not w:
            return 1.0
        return sum(w) / len(w)

    def within_pressure(self) -> float:
        """
        Live pressure from rolling accuracy + trial count.
        High accuracy → tighten; low accuracy → ease.
        """
        if self.attempts < 3:
            return 0.0
        acc = self.rolling_accuracy
        # map accuracy to pressure: 100% → +0.3, 50% → -0.1 (eased)
        if acc >= TARGET_ACC_HIGH:
            p = 0.12 + (acc - TARGET_ACC_HIGH) * 1.2  # up to ~0.3
        elif acc <= TARGET_ACC_LOW:
            p = -0.08 - (TARGET_ACC_LOW - acc) * 0.4  # ease slightly
        else:
            p = 0.04  # mild climb in the sweet spot
        # session length ramp
        p += min(0.12, self.attempts * 0.008)
        return max(-0.1, min(0.35, p))

    def live_profile(self) -> DifficultyProfile:
        p = self.within_pressure()
        if p <= 0:
            # ease: slightly longer deadlines
            return DifficultyProfile(
                level=self.base.level,
                label=self.base.label,
                speed_t=max(0.0, self.base.speed_t + p * 0.3),
                set_size=max(1, self.base.set_size + (0 if p > -0.05 else -1)),
                conflict=max(0.1, self.base.conflict + p * 0.2),
                dual_load=max(0.0, self.base.dual_load + p * 0.15),
                distractors=max(0, self.base.distractors),
                n_depth=self.base.n_depth,
                encode_ms=int(self.base.encode_ms * (1 - p * 0.25)),
                deadline_ms=int(self.base.deadline_ms * (1 - p * 0.25)),
                isi_ms=int(self.base.isi_ms * (1 - p * 0.2)),
                switch_every=self.base.switch_every,
                within_pressure=p,
            )
        return self.base.with_pressure(p)

    def recommend_level_delta(self) -> int:
        """
        After session: +1 promote, -1 demote, 0 hold.
        Mirrors adaptive dual n-back protocols (~85% to increase n).
        """
        if self.attempts < MIN_ATTEMPTS:
            return 0
        acc = self.accuracy
        # higher levels need slightly better accuracy to promote
        promote_bar = PROMOTE_ACC + (self.level - 1) * 0.008
        if acc >= promote_bar and self.level < LEVEL_MAX:
            return 1
        if acc < DEMOTE_ACC and self.level > LEVEL_MIN:
            return -1
        return 0

    def apply_recommendation(self) -> int:
        """Return new level after applying recommendation."""
        return clamp_level(self.level + self.recommend_level_delta())


# ── Helpers used by task engines ─────────────────────────────────────────

def points_for_level(base: int, level: int) -> int:
    return base + (clamp_level(level) - 1)


def time_ms(easy_ms: int, hard_ms: int, level: int) -> int:
    return max(hard_ms, lerp_int(easy_ms, hard_ms, level_t(level)))


def time_sec(easy_s: float, hard_s: float, level: int) -> float:
    return max(hard_s, lerp(easy_s, hard_s, level_t(level)))


def rate(easy: float, hard: float, level: int) -> float:
    return min(hard, lerp(easy, hard, level_t(level)))


def set_size(easy: int, hard: int, level: int) -> int:
    return max(easy, lerp_int(easy, hard, level_t(level)))


def n_back_depth(level: int) -> int:
    return build_profile(level, "working_memory").n_depth


def session_pressure(round_i: int, every: int = 4) -> float:
    return min(0.25, (round_i // every) * 0.04)
