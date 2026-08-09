"""In-memory play sessions for the web API."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlaySession:
    id: str
    mode_key: str
    level: int
    engine: Any
    created: float = field(default_factory=time.time)
    finished: bool = False
    last_trial: Any = None


class SessionStore:
    def __init__(self, ttl_sec: int = 3600):
        self._sessions: dict[str, PlaySession] = {}
        self.ttl = ttl_sec

    def create(self, mode_key: str, level: int, engine: Any) -> PlaySession:
        self._purge()
        sid = uuid.uuid4().hex
        sess = PlaySession(id=sid, mode_key=mode_key, level=level, engine=engine)
        self._sessions[sid] = sess
        return sess

    def get(self, sid: str) -> PlaySession | None:
        self._purge()
        return self._sessions.get(sid)

    def delete(self, sid: str) -> None:
        self._sessions.pop(sid, None)

    def _purge(self) -> None:
        now = time.time()
        dead = [k for k, v in self._sessions.items() if now - v.created > self.ttl]
        for k in dead:
            del self._sessions[k]


STORE = SessionStore()
