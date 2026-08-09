"""
Full regression suite for all NeuroForge modes.
Run:  python tests/test_all_modes.py
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def perfect_play(key, eng, trial):
    if key == "focus":
        eng.respond(True, False) if trial.is_go else eng.respond(False, True)
    elif key == "memory":
        for idx in trial.sequence:
            eng.tap(idx)
    elif key == "switch":
        eng.choose(trial.correct_index)
    elif key == "speed":
        eng.choose(trial.target, 0.1)
    elif key == "nback":
        eng.answer(trial.is_match)
    elif key == "dual":
        eng.answer(trial.letter_match, trial.position_match)
    elif key == "rotate":
        eng.answer(trial.is_same)
    elif key == "stroop":
        eng.choose(trial.correct_ink)
    elif key == "flanker":
        eng.answer(trial.center)
    elif key == "odd":
        eng.choose(trial.odd_index)
    elif key == "trail":
        for lab in trial.order:
            eng.tap(lab)
    elif key == "span":
        for idx in trial.sequence:
            eng.tap(idx)
    elif key == "calc":
        eng.choose(trial.answer)
    elif key == "category":
        eng.answer(trial.is_yes)
    elif key == "simon":
        from neuroforge.logic.simon import COLOR_MAP
        eng.answer(COLOR_MAP[trial.color])
    elif key == "change":
        eng.answer(trial.changed)
    elif key == "stop":
        eng.respond(False) if trial.is_stop else eng.respond(True, trial.direction)
    elif key == "digits":
        for d in trial.target:
            eng.tap_digit(d)
    elif key == "pasat":
        eng.choose(trial.correct_sum)
    elif key == "track":
        eng.choose(list(trial.targets))
    elif key == "opspan":
        for item in trial.items:
            eng.answer_math(item.math_answer)
            eng.ack_letter()
        eng.recall(trial.target_letters)
    elif key == "sart":
        eng.respond(not trial.is_nogo)
    elif key == "posner":
        eng.answer(trial.target_side)
    elif key == "symdigit":
        eng.choose(trial.correct_digit)
    elif key == "dualtask":
        eng.answer_letter(False if trial.is_first else trial.letter_match)
        if trial.probe_digit and trial.previous_digit is not None:
            eng.answer_digit(trial.previous_digit)
        eng.commit_trial()
    elif key == "rulesearch":
        eng.choose(trial.correct_index)
    elif key == "rsvp":
        eng.choose(trial.target)
    else:
        raise RuntimeError(f"No perfect_play handler for {key}")


def main() -> int:
    from neuroforge.modes import MODES, MODE_META
    from neuroforge.logic import ENGINES
    from neuroforge.progress import Progress
    from neuroforge import theme as T

    errors: list[str] = []

    # Registry
    if set(MODES) != set(ENGINES):
        errors.append(f"MODE/ENGINE mismatch {set(MODES) ^ set(ENGINES)}")
    if set(MODES) != set(MODE_META):
        errors.append(f"MODE/META mismatch {set(MODES) ^ set(MODE_META)}")
    for k in MODES:
        if k not in T.MODE_COLORS:
            errors.append(f"Missing color: {k}")
        if k not in Progress.MODE_KEYS:
            errors.append(f"Missing progress key: {k}")

    # Full perfect sessions
    for key, cls in sorted(ENGINES.items()):
        try:
            eng = cls(2)
            safety = 0
            while not eng.done() and safety < 300:
                safety += 1
                trial = eng.next_trial()
                perfect_play(key, eng, trial)
                eng.advance()
            assert eng.done() and eng.state.attempts > 0
            assert eng.state.accuracy >= 0.9, f"acc={eng.state.accuracy}"
            print(f"OK  session {key}")
        except Exception as e:
            errors.append(f"session {key}: {e}")
            print(f"FAIL session {key}: {e}")
            traceback.print_exc()

    # UI smoke
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    for key, ModeCls in sorted(MODES.items()):
        try:
            box = tk.Frame(root)
            mode = ModeCls(
                root, box, level=2,
                on_complete=lambda r: None,
                on_abort=lambda: None,
            )
            mode.start()
            root.update()
            mode.cancel_timers()
            mode.next_round()
            root.update()
            mode.destroy()
            box.destroy()
            print(f"OK  UI {key}")
        except Exception as e:
            errors.append(f"UI {key}: {e}")
            print(f"FAIL UI {key}: {e}")
            traceback.print_exc()
    root.destroy()

    # Progress
    p = Progress()
    p.ensure_modes()
    for key in MODES:
        p.record_session(key, 50, 8, 10, 20.0, 2, 2)

    print()
    if errors:
        print(f"FAILED ({len(errors)}):")
        for e in errors:
            print(" -", e)
        return 1
    print(f"ALL CLEAR — {len(MODES)} modes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
