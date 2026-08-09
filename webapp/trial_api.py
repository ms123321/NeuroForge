"""Serialize engine trials / apply answers for the web UI."""

from __future__ import annotations

from typing import Any


def trial_to_json(mode_key: str, trial: Any) -> dict[str, Any]:
    """Convert a trial dataclass into a JSON-friendly UI payload."""
    base = {"mode": mode_key, "type": type(trial).__name__}

    if mode_key == "focus":
        return {
            **base,
            "ui": "go_nogo",
            "mode": "focus",
            "is_go": trial.is_go,
            "prompt": "TAP green · HOLD on red",
            "stimulus_ms": trial.stimulus_ms,
            "isi_ms": trial.isi_ms,
            "actions": [
                {"id": "tap", "label": "TAP"},
                {"id": "hold", "label": "HOLD"},
            ],
        }
    if mode_key == "nback":
        return {
            **base,
            "ui": "match",
            "mode": "nback",
            "prompt": f"{trial.n}-Back · same as {trial.n} ago?",
            "display": trial.letter,
            "letter": trial.letter,
            "n": trial.n,
            "stim_ms": trial.stim_ms,
            "history": list(trial.history) if getattr(trial, "history", None) else [],
            "actions": [
                {"id": "match", "label": "MATCH"},
                {"id": "nomatch", "label": "NO MATCH"},
            ],
        }
    if mode_key == "flanker":
        return {
            **base,
            "ui": "left_right",
            "prompt": "Center arrow only",
            "display": trial.display,
            "actions": [
                {"id": "left", "label": "← LEFT"},
                {"id": "right", "label": "RIGHT →"},
            ],
        }
    if mode_key == "simon":
        return {
            **base,
            "ui": "left_right",
            "prompt": f"{trial.color.upper()} appears on {trial.side.upper()} — respond by COLOR",
            "display": trial.color.upper(),
            "color": trial.color,
            "actions": [
                {"id": "left", "label": "LEFT (blue)"},
                {"id": "right", "label": "RIGHT (gold)"},
            ],
        }
    if mode_key == "calc":
        return {
            **base,
            "ui": "multi",
            "prompt": "Solve",
            "display": trial.expression,
            "actions": [{"id": str(o), "label": str(o)} for o in trial.options],
        }
    if mode_key == "speed":
        return {
            **base,
            "ui": "speed",
            "mode": "speed",
            "prompt": f"Match the target · {trial.time_limit:.1f}s",
            "display": trial.target,
            "target": trial.target,
            "options": list(trial.options),
            "time_limit": trial.time_limit,
            "actions": [{"id": o, "label": o} for o in trial.options],
        }
    if mode_key == "stroop":
        return {
            **base,
            "ui": "stroop",
            "prompt": "Name the INK color",
            "display": trial.word,
            "ink": trial.ink_hex,
            "actions": [{"id": o, "label": o} for o in trial.options],
        }
    if mode_key == "category":
        return {
            **base,
            "ui": "yes_no",
            "prompt": trial.rule_prompt + (" ⚡ CHANGED" if trial.switched else ""),
            "display": trial.word,
            "actions": [
                {"id": "yes", "label": "YES"},
                {"id": "no", "label": "NO"},
            ],
        }
    if mode_key == "rotate":
        return {
            **base,
            "ui": "same_diff",
            "prompt": "Same shape rotated, or different (mirror)?",
            "display": f"shape {trial.shape_name} · {trial.rotation_deg}°",
            "actions": [
                {"id": "same", "label": "SAME"},
                {"id": "diff", "label": "DIFFERENT"},
            ],
        }
    if mode_key == "change":
        return {
            **base,
            "ui": "same_diff",
            "prompt": f"Memorize {len(trial.sample)} colors — same or changed?",
            "display": "Array encoded",
            "sample": [{"x": x, "y": y, "c": c} for x, y, c in trial.sample],
            "test": [{"x": x, "y": y, "c": c} for x, y, c in trial.test],
            "encode_ms": trial.encode_ms,
            "actions": [
                {"id": "same", "label": "SAME"},
                {"id": "changed", "label": "CHANGED"},
            ],
        }
    if mode_key == "sart":
        return {
            **base,
            "ui": "go_nogo",
            "prompt": "TAP every digit except 3",
            "display": str(trial.digit),
            "actions": [
                {"id": "tap", "label": "TAP"},
                {"id": "hold", "label": "HOLD"},
            ],
        }
    if mode_key == "oddball":
        return {
            **base,
            "ui": "go_nogo",
            "prompt": "TAP rare targets only",
            "display": trial.symbol,
            "actions": [
                {"id": "tap", "label": "TAP"},
                {"id": "hold", "label": "HOLD"},
            ],
        }
    if mode_key == "serial7":
        return {
            **base,
            "ui": "multi",
            "prompt": trial.prompt,
            "display": trial.prompt,
            "actions": [{"id": str(o), "label": str(o)} for o in trial.options],
        }
    if mode_key == "symdigit":
        legend = "  ".join(f"{s}={d}" for s, d in trial.key_map)
        return {
            **base,
            "ui": "multi",
            "prompt": legend,
            "display": trial.probe_symbol,
            "actions": [{"id": str(o), "label": str(o)} for o in trial.options],
        }
    if mode_key == "rsvp":
        return {
            **base,
            "ui": "rsvp",
            "prompt": "Watch stream, then pick the digit",
            "stream": trial.stream,
            "soa_ms": trial.soa_ms,
            "actions": [{"id": str(o), "label": str(o)} for o in trial.options],
        }
    if mode_key == "switch":
        rule_text = f"RULE: match {trial.rule.upper()}"
        if trial.switched:
            rule_text = f"⚡ RULE CHANGED → match {trial.rule.upper()}"
        return {
            **base,
            "ui": "switch",
            "mode": "switch",
            "prompt": rule_text,
            "display": f"{trial.target_shape} {trial.target_color_name}",
            "target_shape": trial.target_shape,
            "target_color_name": trial.target_color_name,
            "target_color": trial.target_color,
            "options_rich": [
                {"shape": o[0], "name": o[1], "color": o[2]} for o in trial.options
            ],
            "actions": [
                {"id": str(i), "label": f"{o[0]} {o[1]}"}
                for i, o in enumerate(trial.options)
            ],
        }
    if mode_key == "rulesearch":
        t = trial.target
        return {
            **base,
            "ui": "multi",
            "prompt": "Match hidden rule (color/shape/count)",
            "display": f"{t.count}× {t.shape} {t.color_name}",
            "actions": [
                {
                    "id": str(i),
                    "label": f"{c.count}× {c.shape} {c.color_name}",
                }
                for i, c in enumerate(trial.options)
            ],
        }
    if mode_key == "dichotic":
        return {
            **base,
            "ui": "multi",
            "prompt": f"Attend {trial.attend.upper()}"
            + (" ⚡ CHANGED" if trial.switched else ""),
            "display": f"L:{trial.left_word}  R:{trial.right_word}",
            "actions": [{"id": o, "label": o} for o in trial.options],
        }
    if mode_key == "prospective":
        return {
            **base,
            "ui": "multi",
            "prompt": "Odd/Even — if multiple of 5 press PM CUE",
            "display": str(trial.number),
            "actions": [
                {"id": "odd", "label": "ODD"},
                {"id": "even", "label": "EVEN"},
                {"id": "pm", "label": "PM CUE"},
            ],
        }
    if mode_key == "matrix":
        return {
            **base,
            "ui": "matrix",
            "prompt": "Complete the pattern",
            "grid": trial.grid,
            "actions": [{"id": o, "label": o} for o in trial.options],
        }
    if mode_key == "loci":
        pairs = [f"{a} → {b}" for a, b in trial.pairs]
        return {
            **base,
            "ui": "loci",
            "prompt": "Study pairs, then recall",
            "pairs": pairs,
            "study_ms": trial.study_ms,
            "cue": trial.cue_place,
            "actions": [{"id": o, "label": o} for o in trial.options],
        }
    if mode_key == "posner":
        return {
            **base,
            "ui": "left_right",
            "prompt": f"Cue {trial.cue_side} → find target",
            "display": f"target {trial.target_side}",
            "cue_side": trial.cue_side,
            "target_side": trial.target_side,
            "actions": [
                {"id": "left", "label": "LEFT"},
                {"id": "right", "label": "RIGHT"},
            ],
        }
    if mode_key == "antisaccade":
        return {
            **base,
            "ui": "left_right",
            "prompt": "Flash — tap OPPOSITE side",
            "display": f"flash {trial.flash_side.upper()}",
            "flash_side": trial.flash_side,
            "actions": [
                {"id": "left", "label": "LEFT"},
                {"id": "right", "label": "RIGHT"},
            ],
        }
    if mode_key == "stop":
        return {
            **base,
            "ui": "stop",
            "prompt": "Arrow = GO · red STOP = hold",
            "display": trial.direction,
            "is_stop": trial.is_stop,
            "go_ms": trial.go_ms,
            "window_ms": trial.respond_window_ms,
            "actions": [
                {"id": "left", "label": "←"},
                {"id": "right", "label": "→"},
                {"id": "hold", "label": "HOLD"},
            ],
        }
    if mode_key == "cpt":
        return {
            **base,
            "ui": "go_nogo",
            "prompt": "TAP only on A then X",
            "display": trial.letter,
            "actions": [
                {"id": "tap", "label": "TAP"},
                {"id": "hold", "label": "HOLD"},
            ],
        }
    if mode_key == "choicert":
        return {
            **base,
            "ui": "left_right",
            "prompt": "React FAST",
            "display": trial.side.upper(),
            "actions": (
                [
                    {"id": "left", "label": "LEFT"},
                    {"id": "right", "label": "RIGHT"},
                ]
                if trial.n_choices == 2
                else [
                    {"id": "tl", "label": "TL"},
                    {"id": "tr", "label": "TR"},
                    {"id": "bl", "label": "BL"},
                    {"id": "br", "label": "BR"},
                ]
            ),
        }
    if mode_key == "odd":
        return {
            **base,
            "ui": "grid",
            "prompt": "Find the odd one",
            "items": trial.items,
            "cols": trial.cols,
            "actions": [{"id": str(i), "label": s} for i, s in enumerate(trial.items)],
        }
    if mode_key == "cancel":
        return {
            **base,
            "ui": "cancel",
            "prompt": f"Cancel every {trial.target}",
            "items": trial.cells,
            "cols": trial.cols,
            "target": trial.target,
            "target_indices": trial.target_indices,
        }
    if mode_key == "memory":
        return {
            **base,
            "ui": "sequence",
            "prompt": "Watch then replay sequence",
            "sequence": trial.sequence,
            "n_tiles": trial.n_tiles,
            "tiles": [{"color": c, "label": lab} for c, lab in trial.tiles],
            "flash_ms": trial.flash_ms,
        }
    if mode_key == "span" or mode_key == "backspan":
        seq = trial.sequence if mode_key == "span" else trial.sequence
        return {
            **base,
            "ui": "blocks",
            "prompt": "Replay order" if mode_key == "span" else "Replay REVERSE order",
            "sequence": seq,
            "target": getattr(trial, "target", seq),
            "flash_ms": trial.flash_ms,
            "reverse": mode_key == "backspan",
        }
    if mode_key == "digits":
        return {
            **base,
            "ui": "digits",
            "prompt": "Watch digits, enter BACKWARDS",
            "forward": trial.forward,
            "flash_ms": trial.flash_ms,
        }
    if mode_key == "running":
        return {
            **base,
            "ui": "running",
            "prompt": f"Recall last {trial.window}",
            "stream": trial.stream,
            "target": trial.target,
            "flash_ms": trial.flash_ms,
        }
    if mode_key == "wordlist":
        return {
            **base,
            "ui": "wordlist",
            "prompt": "Study then free-recall",
            "study": trial.study,
            "pool": trial.pool,
            "study_ms": trial.study_ms,
        }
    if mode_key == "partial":
        return {
            **base,
            "ui": "partial",
            "prompt": "Memorize grid, report cued row",
            "grid": trial.grid,
            "rows": trial.rows,
            "cols": trial.cols,
            "cue_row": trial.cue_row,
            "target": trial.target,
            "encode_ms": trial.encode_ms,
        }
    if mode_key == "brownpeterson":
        return {
            **base,
            "ui": "brownpeterson",
            "prompt": "Remember trigram through distractors",
            "trigram": trial.trigram,
            "distractors": trial.distractors,
            "options": trial.options,
            "encode_ms": trial.encode_ms,
            "distract_ms": trial.distract_ms,
        }
    if mode_key == "pasat":
        return {
            **base,
            "ui": "pasat",
            "prompt": "Add this + previous" if trial.correct_sum is not None else "Remember this number",
            "display": str(trial.number),
            "warmup": trial.correct_sum is None,
            "actions": (
                [{"id": "ok", "label": "Got it"}]
                if trial.correct_sum is None
                else [{"id": str(o), "label": str(o)} for o in trial.options]
            ),
        }
    if mode_key == "countkeep":
        return {
            **base,
            "ui": "countkeep",
            "prompt": trial.display,
            "ask": trial.ask,
            "actions": (
                [{"id": str(o), "label": str(o)} for o in trial.options]
                if trial.ask
                else [{"id": "ok", "label": "Got it →"}]
            ),
        }
    if mode_key == "tower":
        return {
            **base,
            "ui": "tower",
            "prompt": "Best next move toward GOAL",
            "start": trial.start,
            "goal": trial.goal,
            "legal": trial.legal_moves,
        }
    if mode_key == "track":
        return {
            **base,
            "ui": "track",
            "prompt": f"Track {len(trial.targets)} target(s)",
            "n_objects": trial.n_objects,
            "targets": trial.targets,
            "paths": trial.path_steps,
            "flash_ms": trial.flash_ms,
            "step_ms": trial.step_ms,
            "move_steps": trial.move_steps,
        }
    if mode_key == "trail":
        return {
            **base,
            "ui": "trail",
            "prompt": f"Tap in order ({trial.mode})",
            "labels": trial.labels,
            "order": trial.order,
            "cols": trial.cols,
        }
    if mode_key == "opspan":
        return {
            **base,
            "ui": "opspan",
            "prompt": "Math + remember letters",
            "items": [
                {
                    "expression": it.expression,
                    "options": it.math_options,
                    "letter": it.letter,
                    "answer": it.math_answer,
                }
                for it in trial.items
            ],
            "target_letters": trial.target_letters,
            "math_time": trial.math_time,
        }
    if mode_key == "dual":
        return {
            **base,
            "ui": "dual",
            "prompt": f"Dual {trial.n}-back · letter + position",
            "letter": trial.letter,
            "position": trial.position,
            "n": trial.n,
        }
    if mode_key == "dualtask":
        return {
            **base,
            "ui": "dualtask",
            "prompt": "Letter match? + remember digit",
            "letter": trial.letter,
            "digit": trial.digit,
            "is_first": trial.is_first,
            "probe": trial.probe_digit,
            "previous_digit": trial.previous_digit,
        }
    if mode_key == "conjunction":
        return {
            **base,
            "ui": "conjunction",
            "prompt": f"Find {trial.target_desc}",
            "items": [
                {
                    "shape": it.shape,
                    "color": it.color_hex,
                    "name": it.color_name,
                }
                for it in trial.items
            ],
            "cols": trial.cols,
            "present": trial.present,
        }
    if mode_key == "flanker":
        pass  # handled above

    # Generic fallback
    return {
        **base,
        "ui": "generic",
        "prompt": f"Mode {mode_key}",
        "display": str(trial),
        "actions": [{"id": "ok", "label": "Continue"}],
    }


def apply_answer(mode_key: str, engine: Any, trial: Any, payload: dict) -> dict:
    """Apply client answer; return event dict (+ optional done/partial flags)."""
    action = str(payload.get("action", ""))
    data = payload.get("data")

    if mode_key == "focus":
        if action == "tap":
            return engine.respond(True, False)
        if action == "false":
            return engine.respond(True, False)
        # hold / timeout = no tap
        return engine.respond(False, True)
    if mode_key == "nback":
        if action == "timeout":
            return engine.answer(False, timed_out=True)
        return engine.answer(action == "match")
    if mode_key == "flanker":
        return engine.answer("<" if action == "left" else ">" if action == "right" else None)
    if mode_key == "simon":
        return engine.answer(action if action in ("left", "right") else None)
    if mode_key == "calc":
        try:
            return engine.choose(int(action))
        except ValueError:
            return engine.choose(None)
    if mode_key == "speed":
        return engine.choose(action if action else None, float(payload.get("elapsed", 0.5)))
    if mode_key == "stroop":
        return engine.choose(action or None)
    if mode_key == "category":
        if action == "yes":
            return engine.answer(True)
        if action == "no":
            return engine.answer(False)
        return engine.answer(None)
    if mode_key == "rotate":
        if action == "same":
            return engine.answer(True)
        if action == "diff":
            return engine.answer(False)
        return engine.answer(False, True)
    if mode_key == "change":
        if action == "same":
            return engine.answer(False)
        if action == "changed":
            return engine.answer(True)
        return engine.answer(None)
    if mode_key in ("sart", "oddball", "cpt"):
        return engine.respond(action == "tap")
    if mode_key == "serial7":
        try:
            return engine.choose(int(action))
        except ValueError:
            return engine.choose(None)
    if mode_key == "symdigit":
        try:
            return engine.choose(int(action))
        except ValueError:
            return engine.choose(None)
    if mode_key == "rsvp":
        return engine.choose(action or None)
    if mode_key in ("switch", "rulesearch", "odd", "jlo"):
        try:
            return engine.choose(int(action))
        except ValueError:
            return engine.choose(None)
    if mode_key == "dichotic":
        return engine.choose(action or None)
    if mode_key == "prospective":
        return engine.answer(action if action in ("odd", "even", "pm") else None)
    if mode_key == "matrix":
        return engine.choose(action or None)
    if mode_key == "loci":
        return engine.choose(action or None)
    if mode_key == "posner":
        return engine.answer(action if action in ("left", "right") else None)
    if mode_key == "antisaccade":
        return engine.answer(action if action in ("left", "right") else None)
    if mode_key == "stop":
        if action == "hold":
            return engine.respond(False)
        if action in ("left", "right", "<", ">"):
            d = "<" if action in ("left", "<") else ">"
            return engine.respond(True, d)
        return engine.respond(False)
    if mode_key == "choicert":
        return engine.answer(action or None)
    if mode_key == "cancel":
        if action == "timeout":
            return engine.timeout()
        try:
            ev = engine.tap(int(action))
            return ev if ev is not None else {"good": True, "partial": True, "message": "Keep going"}
        except ValueError:
            return engine.timeout()
    if mode_key == "memory":
        try:
            ev = engine.tap(int(action))
            return ev if ev is not None else {"good": True, "partial": True, "message": "…"}
        except ValueError:
            return {"good": False, "message": "bad"}
    if mode_key in ("span", "backspan"):
        try:
            ev = engine.tap(int(action))
            return ev if ev is not None else {"good": True, "partial": True, "message": "…"}
        except ValueError:
            return {"good": False, "message": "bad"}
    if mode_key == "digits":
        try:
            ev = engine.tap_digit(int(action))
            return ev if ev is not None else {"good": True, "partial": True, "message": "…"}
        except ValueError:
            return {"good": False, "message": "bad"}
    if mode_key == "running":
        ev = engine.tap(action)
        return ev if ev is not None else {"good": True, "partial": True, "message": "…"}
    if mode_key == "wordlist":
        if action == "done":
            return engine.finish_early()
        ev = engine.tap(action)
        return ev if ev is not None else {"good": True, "partial": True, "message": "…"}
    if mode_key == "partial":
        ev = engine.tap(action)
        return ev if ev is not None else {"good": True, "partial": True, "message": "…"}
    if mode_key == "brownpeterson":
        return engine.choose(action or None)
    if mode_key == "pasat":
        if action == "ok":
            return engine.choose(None)
        try:
            return engine.choose(int(action))
        except ValueError:
            return engine.choose(None)
    if mode_key == "countkeep":
        if action == "ok":
            return engine.choose(None)
        try:
            return engine.choose(int(action))
        except ValueError:
            return engine.choose(None)
    if mode_key == "tower":
        fr = payload.get("from")
        to = payload.get("to")
        try:
            return engine.choose(int(fr) if fr is not None else None, int(to) if to is not None else None)
        except (TypeError, ValueError):
            return engine.choose(None, None)
    if mode_key == "track":
        sel = data if isinstance(data, list) else payload.get("selected") or []
        return engine.choose([int(x) for x in sel])
    if mode_key == "trail":
        ev = engine.tap(action)
        if ev is None:
            return {"good": True, "partial": True, "message": "Next…"}
        if ev.get("continue"):
            return {"good": False, "partial": True, "message": ev.get("message", "")}
        return ev
    if mode_key == "opspan":
        phase = payload.get("phase")
        if phase == "math":
            try:
                return engine.answer_math(int(action) if action not in ("", "timeout") else None)
            except ValueError:
                return engine.answer_math(None)
        if phase == "letter":
            engine.ack_letter()
            return {"good": True, "message": "Letter stored", "partial": True}
        if phase == "recall":
            letters = data if isinstance(data, list) else []
            return engine.recall(letters)
        return {"good": False, "message": "bad phase"}
    if mode_key == "dual":
        return engine.answer(bool(payload.get("letter")), bool(payload.get("position")))
    if mode_key == "dualtask":
        if payload.get("phase") == "digit":
            try:
                return engine.answer_digit(int(action) if action not in ("", "timeout") else None)
            except ValueError:
                return engine.answer_digit(None)
        # letter
        said = action == "same"
        ev = engine.answer_letter(said)
        return ev
    if mode_key == "conjunction":
        if action == "absent":
            return engine.choose(None, True)
        try:
            return engine.choose(int(action), False)
        except ValueError:
            return engine.choose(None, False)

    return {"good": True, "message": "OK"}
