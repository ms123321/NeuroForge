"""
Backward-compatible difficulty helpers.

All adaptive logic now lives in ``neuroforge.logic.engine``.
This module re-exports the public API so existing modes keep working.
"""

from __future__ import annotations

from .engine import (
    AdaptiveEngine,
    DifficultyProfile,
    LEVEL_MAX,
    LEVEL_MIN,
    build_profile,
    clamp_level,
    difficulty_label,
    level_t,
    lerp,
    lerp_int,
    n_back_depth,
    points_for_level,
    rate,
    session_pressure,
    set_size,
    time_ms,
    time_sec,
)

__all__ = [
    "AdaptiveEngine",
    "DifficultyProfile",
    "LEVEL_MAX",
    "LEVEL_MIN",
    "build_profile",
    "clamp_level",
    "difficulty_label",
    "level_t",
    "lerp",
    "lerp_int",
    "n_back_depth",
    "points_for_level",
    "rate",
    "session_pressure",
    "set_size",
    "time_ms",
    "time_sec",
]
