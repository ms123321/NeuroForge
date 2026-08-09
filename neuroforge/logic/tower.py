"""
Tower planning (Tower of London–inspired)
Shallice (1982) / executive planning — used in neuropsych & frontal studies.
Simplified: rearrange peg disks to match goal in fewest moves (or choose next move).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .engine import AdaptiveEngine, points_for_level
from .scoring import ScoreState, apply_hit


@dataclass
class TowerTrial:
    # 3 pegs, each a list of disk sizes (bottom→top), disks 1..n larger = bigger
    start: list[list[int]]
    goal: list[list[int]]
    legal_moves: list[tuple[int, int]]  # (from_peg, to_peg)
    best_from: int
    best_to: int
    deadline_ms: int


def _clone(pegs):
    return [list(p) for p in pegs]


def _legal(pegs) -> list[tuple[int, int]]:
    moves = []
    for i in range(3):
        if not pegs[i]:
            continue
        disk = pegs[i][-1]
        for j in range(3):
            if i == j:
                continue
            if not pegs[j] or pegs[j][-1] > disk:
                moves.append((i, j))
    return moves


def _apply(pegs, fr, to):
    p = _clone(pegs)
    p[to].append(p[fr].pop())
    return p


def _heuristic(pegs, goal) -> int:
    # disks not in goal position
    score = 0
    for i in range(3):
        for d in pegs[i]:
            if d not in goal[i]:
                score += 1
            elif pegs[i].index(d) != goal[i].index(d) if d in goal[i] else True:
                score += 1
    return score


class TowerEngine:
    key = "tower"
    domain = "flexibility"

    def __init__(self, level: int = 1):
        self.ad = AdaptiveEngine(level=level, domain="flexibility")
        self.level = self.ad.level
        self.state = ScoreState(level=self.level)
        self.rounds = 8 + self.level // 2
        self.n_disks = min(2 + self.level // 3, 4)
        self.current: TowerTrial | None = None

    def next_trial(self) -> TowerTrial:
        p = self.ad.live_profile()
        n = self.n_disks
        # goal: all on peg 2
        goal = [[], [], list(range(n, 0, -1))]
        # start: all on peg 0, or shuffled via random legal moves
        start = [list(range(n, 0, -1)), [], []]
        for _ in range(2 + self.level // 2):
            moves = _legal(start)
            if not moves:
                break
            fr, to = random.choice(moves)
            start = _apply(start, fr, to)
        # if already goal, scramble once more
        if start == goal:
            start = [list(range(n, 0, -1)), [], []]
            start = _apply(start, 0, 1)

        legal = _legal(start)
        # best move = minimizes heuristic to goal
        best = legal[0]
        best_h = 999
        for m in legal:
            h = _heuristic(_apply(start, m[0], m[1]), goal)
            if h < best_h:
                best_h = h
                best = m

        self.current = TowerTrial(
            start=start,
            goal=goal,
            legal_moves=legal,
            best_from=best[0],
            best_to=best[1],
            deadline_ms=max(4000, p.deadline_ms + 1500),
        )
        return self.current

    def choose(self, fr: int | None, to: int | None) -> dict:
        assert self.current is not None
        pts = points_for_level(14, self.level)
        if fr is None or to is None:
            self.ad.observe(False)
            return apply_hit(self.state, pts, False, "Time's up")
        good = (fr, to) == (self.current.best_from, self.current.best_to)
        # also accept any legal that matches best heuristic
        if not good and (fr, to) in self.current.legal_moves:
            h = _heuristic(_apply(self.current.start, fr, to), self.current.goal)
            h_best = _heuristic(
                _apply(self.current.start, self.current.best_from, self.current.best_to),
                self.current.goal,
            )
            good = h <= h_best
        self.ad.observe(good)
        return apply_hit(
            self.state, pts, good,
            "Good plan" if good else f"Better: peg {self.current.best_from+1}→{self.current.best_to+1}",
        )

    def advance(self) -> None:
        self.state.round_i += 1

    def done(self) -> bool:
        return self.state.round_i >= self.rounds
