"""Pure-logic unit tests (no GUI)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from neuroforge.logic import ENGINES
from neuroforge.logic.difficulty import clamp_level, difficulty_label, n_back_depth, time_ms
from neuroforge.logic.scoring import ScoreState, apply_hit
from neuroforge.logic.focus import FocusEngine
from neuroforge.logic.memory import MemoryEngine
from neuroforge.logic.switch import SwitchEngine
from neuroforge.logic.speed import SpeedEngine
from neuroforge.logic.nback import NBackEngine
from neuroforge.logic.dual import DualNBackEngine
from neuroforge.logic.rotate import RotateEngine
from neuroforge.logic.stroop import StroopEngine
from neuroforge.logic.flanker import FlankerEngine
from neuroforge.logic.odd import OddEngine
from neuroforge.logic.trail import TrailEngine
from neuroforge.logic.span import SpanEngine
from neuroforge.logic.calc import CalcEngine
from neuroforge.logic.category import CategoryEngine
from neuroforge.logic.simon import SimonEngine, COLOR_MAP
from neuroforge.logic.change import ChangeEngine
from neuroforge.logic.stop import StopEngine
from neuroforge.logic.digits import DigitsEngine
from neuroforge.logic.pasat import PasatEngine
from neuroforge.logic.track import TrackEngine
from neuroforge.logic.opspan import OspanEngine


def test_scoring():
    s = ScoreState()
    e = apply_hit(s, 10, True)
    assert e["good"] and s.correct == 1 and s.score > 0
    e2 = apply_hit(s, 10, False)
    assert not e2["good"] and s.streak == 0


def test_difficulty_curves():
    assert clamp_level(0) == 1 and clamp_level(99) == 10
    assert time_ms(1000, 400, 1) > time_ms(1000, 400, 10)
    assert n_back_depth(1) == 1 and n_back_depth(10) == 4
    assert difficulty_label(1) == "Easy" and difficulty_label(10) == "Elite"
    # high level must be strictly harder on key params
    f1, f10 = FocusEngine(1), FocusEngine(10)
    assert f1.stimulus_ms > f10.stimulus_ms
    assert f1.no_go_rate < f10.no_go_rate
    m1, m10 = MemoryEngine(1), MemoryEngine(10)
    assert m1.seq_len < m10.seq_len
    n1, n10 = NBackEngine(1), NBackEngine(10)
    assert n1.n < n10.n


def test_focus():
    e = FocusEngine(3)
    t = e.next_trial()
    e.respond(tapped=t.is_go, timed_out=False)
    assert e.state.attempts == 1


def test_memory():
    e = MemoryEngine(2)
    t = e.next_trial()
    event = None
    for idx in t.sequence:
        event = e.tap(idx)
    assert event is not None and event["good"]


def test_switch():
    e = SwitchEngine(8)
    t = e.next_trial()
    assert len(t.options) >= 2
    assert e.choose(t.correct_index)["good"]


def test_speed():
    e = SpeedEngine(2)
    t = e.next_trial()
    assert e.choose(t.target, 0.5)["good"]


def test_nback():
    e = NBackEngine(1)
    e.next_trial()
    e.answer(False)


def test_dual():
    e = DualNBackEngine(2)
    e.next_trial()
    e.answer(False, False)
    assert e.state.attempts == 2


def test_rotate():
    e = RotateEngine(3)
    t = e.next_trial()
    assert e.answer(t.is_same)["good"]


def test_stroop():
    e = StroopEngine(5)
    t = e.next_trial()
    assert e.choose(t.correct_ink)["good"]


def test_flanker():
    e = FlankerEngine(3)
    t = e.next_trial()
    assert e.answer(t.center)["good"]


def test_odd():
    e = OddEngine(2)
    t = e.next_trial()
    assert e.choose(t.odd_index)["good"]


def test_trail():
    e = TrailEngine(2)
    t = e.next_trial()
    event = None
    for lab in t.order:
        event = e.tap(lab)
    assert event is not None and event["good"]


def test_span():
    e = SpanEngine(2)
    t = e.next_trial()
    event = None
    for idx in t.sequence:
        event = e.tap(idx)
    assert event is not None and event["good"]


def test_calc():
    e = CalcEngine(3)
    t = e.next_trial()
    assert e.choose(t.answer)["good"]


def test_category():
    e = CategoryEngine(2)
    t = e.next_trial()
    assert e.answer(t.is_yes)["good"]


def test_simon():
    e = SimonEngine(4)
    t = e.next_trial()
    assert e.answer(COLOR_MAP[t.color])["good"]


def test_change():
    e = ChangeEngine(3)
    t = e.next_trial()
    assert e.answer(t.changed)["good"]


def test_stop():
    e = StopEngine(3)
    t = e.next_trial()
    if t.is_stop:
        assert e.respond(False)["good"]
    else:
        assert e.respond(True, t.direction)["good"]


def test_digits():
    e = DigitsEngine(2)
    t = e.next_trial()
    event = None
    for d in t.target:
        event = e.tap_digit(d)
    assert event is not None and event["good"]


def test_pasat():
    e = PasatEngine(2)
    e.next_trial()
    e.choose(None)  # warmup
    t2 = e.next_trial()
    assert t2.correct_sum is not None
    assert e.choose(t2.correct_sum)["good"]


def test_track():
    e = TrackEngine(2)
    t = e.next_trial()
    assert e.choose(list(t.targets))["good"]


def test_opspan():
    e = OspanEngine(2)
    t = e.next_trial()
    for item in t.items:
        e.answer_math(item.math_answer)
        e.ack_letter()
    assert e.recall(t.target_letters)["good"]


def test_adaptive_engine():
    from neuroforge.logic.engine import AdaptiveEngine, build_profile
    p1 = build_profile(1, "working_memory")
    p10 = build_profile(10, "working_memory")
    assert p1.deadline_ms > p10.deadline_ms
    assert p1.set_size < p10.set_size
    assert p1.n_depth < p10.n_depth
    ad = AdaptiveEngine(level=3, domain="attention")
    for _ in range(12):
        ad.observe(True)
    assert ad.recommend_level_delta() == 1
    ad2 = AdaptiveEngine(level=5, domain="attention")
    for _ in range(12):
        ad2.observe(False)
    assert ad2.recommend_level_delta() == -1
    live = ad.live_profile()
    assert live.deadline_ms <= ad.base.deadline_ms


def test_new_research_modes():
    from neuroforge.logic.sart import SartEngine
    from neuroforge.logic.posner import PosnerEngine
    from neuroforge.logic.symdigit import SymDigitEngine
    from neuroforge.logic.dualtask import DualTaskEngine
    from neuroforge.logic.rulesearch import RuleSearchEngine
    from neuroforge.logic.rsvp import RsvpEngine

    s = SartEngine(3)
    t = s.next_trial()
    s.respond(not t.is_nogo)

    p = PosnerEngine(3)
    pt = p.next_trial()
    assert p.answer(pt.target_side)["good"]

    sd = SymDigitEngine(3)
    st = sd.next_trial()
    assert sd.choose(st.correct_digit)["good"]

    d = DualTaskEngine(2)
    dt = d.next_trial()
    d.answer_letter(dt.letter_match)
    d.commit_trial()

    r = RuleSearchEngine(3)
    rt = r.next_trial()
    assert r.choose(rt.correct_index)["good"]

    rv = RsvpEngine(3)
    rvt = rv.next_trial()
    assert rv.choose(rvt.target)["good"]


def test_engines_registry():
    assert len(ENGINES) >= 27
    from neuroforge.modes import MODES
    assert set(MODES.keys()) == set(ENGINES.keys())



if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"OK  {fn.__name__}")
    print(f"\n{len(tests)} tests passed")
