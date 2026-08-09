"""Persistent progress, streaks, and adaptive difficulty."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any


def _data_dir() -> Path:
    # Prefer explicit data dir (Railway volume or local)
    override = os.environ.get("NEUROFORGE_DATA") or os.environ.get("DATA_DIR")
    if override:
        path = Path(override)
    elif os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home())
        path = base / "NeuroForge"
    else:
        # Linux / Railway / containers
        path = Path(os.environ.get("HOME") or "/tmp") / ".neuroforge"
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        path = Path("/tmp/neuroforge")
        path.mkdir(parents=True, exist_ok=True)
    return path


DATA_FILE = _data_dir() / "progress.json"


@dataclass
class ModeStats:
    level: int = 1
    high_score: int = 0
    sessions: int = 0
    total_correct: int = 0
    total_attempts: int = 0
    best_streak: int = 0
    last_accuracy: float = 0.0

    @property
    def accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.total_correct / self.total_attempts


@dataclass
class Progress:
    player_name: str = "Trainee"
    total_sessions: int = 0
    total_minutes: float = 0.0
    current_streak: int = 0
    best_streak: int = 0
    last_play_date: str = ""
    growth_points: int = 0  # metaphor for synaptic growth
    sound_enabled: bool = True
    language: str = "en"
    modes: dict[str, ModeStats] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    MODE_KEYS = (
        "focus", "memory", "switch", "speed", "nback",
        "dual", "rotate", "stroop",
        "flanker", "odd", "trail", "span", "calc", "category",
        "simon", "change", "stop", "digits", "pasat", "track", "opspan",
        "sart", "posner", "symdigit", "dualtask", "rulesearch", "rsvp",
        "antisaccade", "running", "tower", "conjunction", "matrix", "backspan",
        "cpt", "partial", "dichotic", "prospective", "loci", "countkeep",
        "serial7", "cancel", "oddball", "choicert", "wordlist",
        "brownpeterson",
    )

    def ensure_modes(self) -> None:
        for key in self.MODE_KEYS:
            if key not in self.modes:
                self.modes[key] = ModeStats()
            elif isinstance(self.modes[key], dict):
                self.modes[key] = ModeStats(**self.modes[key])

    def record_session(
        self,
        mode: str,
        score: int,
        correct: int,
        attempts: int,
        duration_sec: float,
        level: int,
        max_streak: int,
    ) -> dict[str, Any]:
        self.ensure_modes()
        today = date.today().isoformat()
        if self.last_play_date:
            last = date.fromisoformat(self.last_play_date)
            delta = (date.today() - last).days
            if delta == 1:
                self.current_streak += 1
            elif delta > 1:
                self.current_streak = 1
            # same day: keep streak
        else:
            self.current_streak = 1
        self.best_streak = max(self.best_streak, self.current_streak)
        self.last_play_date = today

        self.total_sessions += 1
        self.total_minutes += duration_sec / 60.0

        stats = self.modes[mode]
        stats.sessions += 1
        stats.total_correct += correct
        stats.total_attempts += attempts
        stats.high_score = max(stats.high_score, score)
        stats.best_streak = max(stats.best_streak, max_streak)
        accuracy = (correct / attempts) if attempts else 0.0
        stats.last_accuracy = accuracy

        # Adaptive Difficulty Engine (mismatch model / dual n-back style)
        from .logic.engine import AdaptiveEngine

        ad = AdaptiveEngine(level=level)
        # reconstruct observations from session totals (order unknown → approximate)
        for i in range(attempts):
            ad.observe(i < correct)
        delta = ad.recommend_level_delta()
        # score gate: weak scores can't promote even if accuracy is high on few trials
        min_score = 35 + level * 10
        if delta > 0 and score < min_score:
            delta = 0
        old_level = stats.level
        if delta > 0:
            stats.level = min(10, max(stats.level, level) + 1)
        elif delta < 0:
            stats.level = max(1, min(stats.level, level) - 1)
        else:
            stats.level = max(1, max(stats.level, level))

        # Growth points reward consistency + performance
        gained = max(5, int(score * 0.4) + int(accuracy * 20) + (3 if self.current_streak > 1 else 0))
        self.growth_points += gained

        entry = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "mode": mode,
            "score": score,
            "correct": correct,
            "attempts": attempts,
            "accuracy": round(accuracy, 3),
            "level": level,
            "level_after": stats.level,
            "level_delta": stats.level - old_level,
            "duration_sec": round(duration_sec, 1),
            "growth_gained": gained,
        }
        self.history.append(entry)
        self.history = self.history[-200:]  # cap
        self.save()
        return entry

    def level_for(self, mode: str) -> int:
        self.ensure_modes()
        return self.modes[mode].level

    def growth_title(self) -> str:
        g = self.growth_points
        if g < 50:
            return "Sprouting Dendrite"
        if g < 150:
            return "Forming Synapse"
        if g < 350:
            return "Strengthening Circuit"
        if g < 700:
            return "Myelin Builder"
        if g < 1200:
            return "Plastic Pro"
        return "Neuro Architect"

    def to_dict(self) -> dict[str, Any]:
        self.ensure_modes()
        return {
            "player_name": self.player_name,
            "total_sessions": self.total_sessions,
            "total_minutes": self.total_minutes,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "last_play_date": self.last_play_date,
            "growth_points": self.growth_points,
            "sound_enabled": self.sound_enabled,
            "language": self.language,
            "modes": {k: asdict(v) for k, v in self.modes.items()},
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Progress:
        modes_raw = data.get("modes") or {}
        modes = {}
        for k, v in modes_raw.items():
            modes[k] = ModeStats(**v) if isinstance(v, dict) else v
        p = cls(
            player_name=data.get("player_name", "Trainee"),
            total_sessions=int(data.get("total_sessions", 0)),
            total_minutes=float(data.get("total_minutes", 0.0)),
            current_streak=int(data.get("current_streak", 0)),
            best_streak=int(data.get("best_streak", 0)),
            last_play_date=data.get("last_play_date", ""),
            growth_points=int(data.get("growth_points", 0)),
            sound_enabled=bool(data.get("sound_enabled", True)),
            language=str(data.get("language", "en")),
            modes=modes,
            history=list(data.get("history") or []),
        )
        p.ensure_modes()
        return p

    def save(self) -> None:
        DATA_FILE.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> Progress:
        if not DATA_FILE.exists():
            p = cls()
            p.ensure_modes()
            return p
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except (json.JSONDecodeError, TypeError, ValueError, OSError):
            p = cls()
            p.ensure_modes()
            return p
