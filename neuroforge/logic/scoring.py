"""Shared scoring helpers (UI-free)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScoreState:
    score: int = 0
    correct: int = 0
    attempts: int = 0
    streak: int = 0
    max_streak: int = 0
    round_i: int = 0
    level: int = 1
    history: list[dict] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        if self.attempts == 0:
            return 0.0
        return self.correct / self.attempts


def apply_hit(state: ScoreState, points: int, good: bool, message: str = "") -> dict:
    """Apply a trial result; returns event dict for UI feedback."""
    state.attempts += 1
    if good:
        state.correct += 1
        state.streak += 1
        state.max_streak = max(state.max_streak, state.streak)
        bonus = min(15, state.streak * 2)
        gained = points + bonus
        state.score += gained
        event = {"good": True, "points": gained, "message": message or "Correct", "streak": state.streak}
    else:
        state.streak = 0
        penalty = max(2, points // 4)
        state.score = max(0, state.score - penalty)
        event = {"good": False, "points": -penalty, "message": message or "Miss", "streak": 0}
    state.history.append(event)
    return event


def level_params(level: int) -> int:
    return max(1, min(10, int(level)))
