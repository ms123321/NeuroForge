"""
NeuroForge mobile shell (BeeWare Toga).

Desktop uses tkinter (`neuroforge.app`). Mobile packaging uses this module
with Briefcase → iOS / Android.

All scoring & adaptive difficulty come from `neuroforge.logic` (UI-free).
"""

from __future__ import annotations

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from neuroforge import __version__
from neuroforge.logic import ENGINES
from neuroforge.modes import MODE_META
from neuroforge.progress import Progress
from neuroforge.logic.engine import difficulty_label


# Simple two-button / multi-choice templates for mobile v1
SIMPLE_ENGINES = {
    "focus": "go_nogo",
    "flanker": "left_right",
    "simon": "left_right",
    "stroop": "multi",
    "nback": "match",
    "rotate": "same_diff",
    "category": "yes_no",
    "change": "same_diff",
    "sart": "go_nogo",
    "calc": "multi",
    "symdigit": "multi",
    "speed": "multi",
    "odd": "multi_index",
    "posner": "left_right",
    "rulesearch": "multi_index",
    "rsvp": "multi",
    "switch": "multi_index",
}


class NeuroForgeMobile(toga.App):
    def startup(self):
        self.progress = Progress.load()
        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=12, flex=1))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()
        self.show_home()

    def clear(self):
        for child in list(self.main_box.children):
            self.main_box.remove(child)

    def show_home(self):
        self.clear()
        self.progress = Progress.load()
        p = self.progress

        self.main_box.add(
            toga.Label(
                "NEUROFORGE",
                style=Pack(font_size=12, font_weight="bold", color="#8FA6FF", margin_bottom=4),
            )
        )
        self.main_box.add(
            toga.Label(
                "Rewire. Adapt. Grow.",
                style=Pack(font_size=22, font_weight="bold", margin_bottom=8),
            )
        )
        self.main_box.add(
            toga.Label(
                f"{p.growth_title()}  ·  {p.growth_points} GP\n"
                f"Streak {p.current_streak}  ·  {p.total_sessions} sessions\n"
                f"v{__version__} mobile",
                style=Pack(font_size=12, color="#8B9BB8", margin_bottom=16),
            )
        )

        self.main_box.add(
            toga.Button(
                "Train a skill",
                on_press=lambda w: self.show_modes(),
                style=Pack(margin_bottom=8, height=48, background_color="#6C8CFF", color="#0B1020"),
            )
        )
        self.main_box.add(
            toga.Button(
                "Daily Circuit (5 modes)",
                on_press=lambda w: self.start_circuit(
                    ["focus", "memory", "nback", "speed", "flanker"]
                ),
                style=Pack(margin_bottom=8, height=48, background_color="#B794F6", color="#0B1020"),
            )
        )
        self.main_box.add(
            toga.Button(
                "Progress",
                on_press=lambda w: self.show_progress(),
                style=Pack(margin_bottom=8, height=44, background_color="#1C2540", color="#E8EEF9"),
            )
        )
        self.main_box.add(
            toga.Label(
                "Not a medical device. Entertainment & personal training only.",
                style=Pack(font_size=10, color="#5A6A88", margin_top=20),
            )
        )

    def show_modes(self):
        self.clear()
        self.main_box.add(
            toga.Button("← Back", on_press=lambda w: self.show_home(), style=Pack(margin_bottom=8))
        )
        self.main_box.add(
            toga.Label("Choose a skill", style=Pack(font_size=18, font_weight="bold", margin_bottom=8))
        )

        scroll_content = toga.Box(style=Pack(direction=COLUMN))
        for key, meta in MODE_META.items():
            level = self.progress.level_for(key)
            label = f"{meta['title']}  ·  Lv {level} {difficulty_label(level)}"
            scroll_content.add(
                toga.Button(
                    label,
                    on_press=lambda w, k=key: self.start_mode(k),
                    style=Pack(margin_bottom=6, height=44, background_color="#1C2540", color="#E8EEF9"),
                )
            )
        # Toga ScrollContainer
        scroll = toga.ScrollContainer(content=scroll_content, style=Pack(flex=1))
        self.main_box.add(scroll)

    def show_progress(self):
        self.clear()
        self.main_box.add(
            toga.Button("← Back", on_press=lambda w: self.show_home(), style=Pack(margin_bottom=8))
        )
        lines = [
            f"{self.progress.growth_title()} · {self.progress.growth_points} GP",
            f"Streak {self.progress.current_streak} (best {self.progress.best_streak})",
            f"Sessions {self.progress.total_sessions}",
            "",
        ]
        for key, meta in MODE_META.items():
            st = self.progress.modes.get(key)
            if not st:
                continue
            acc = f"{st.accuracy * 100:.0f}%" if st.total_attempts else "—"
            lines.append(f"{meta['title']}: Lv {st.level} · high {st.high_score} · {acc}")
        self.main_box.add(
            toga.MultilineTextInput(
                value="\n".join(lines),
                readonly=True,
                style=Pack(flex=1, font_size=12),
            )
        )

    def start_circuit(self, keys: list[str]):
        self._circuit = list(keys[1:])
        self.start_mode(keys[0])

    def start_mode(self, key: str):
        self._circuit = getattr(self, "_circuit", None)
        level = self.progress.level_for(key)
        if key not in ENGINES:
            self.main_window.info_dialog("Unavailable", f"Mode {key} not found.")
            return
        # Sequence memory needs multi-step UI — use simplified mobile runner
        self._run_mobile_session(key, level)

    def _run_mobile_session(self, key: str, level: int):
        """Generic mobile session runner for engines with simple response APIs."""
        eng_cls = ENGINES[key]
        engine = eng_cls(level)
        meta = MODE_META[key]
        template = SIMPLE_ENGINES.get(key, "generic")

        self.clear()
        title = toga.Label(
            f"{meta['title']}  ·  Lv {level}",
            style=Pack(font_size=16, font_weight="bold", margin_bottom=4),
        )
        status = toga.Label("Ready", style=Pack(font_size=13, color="#8B9BB8", margin_bottom=8))
        stim = toga.Label("—", style=Pack(font_size=28, font_weight="bold", margin_bottom=12, text_align=CENTER))
        btn_box = toga.Box(style=Pack(direction=COLUMN, margin_top=8))

        self.main_box.add(toga.Button("← Quit mode", on_press=lambda w: self._end_early(key, engine), style=Pack(margin_bottom=8)))
        self.main_box.add(title)
        self.main_box.add(status)
        self.main_box.add(stim)
        self.main_box.add(btn_box)

        state = {"trial": None, "busy": False}

        def set_status(msg: str, score: bool = False):
            sc = engine.state
            status.text = f"Score {sc.score}  ·  {sc.correct}/{sc.attempts}  ·  {msg}"

        def finish_session():
            entry = self.progress.record_session(
                mode=key,
                score=engine.state.score,
                correct=engine.state.correct,
                attempts=max(1, engine.state.attempts),
                duration_sec=60.0,
                level=level,
                max_streak=engine.state.max_streak,
            )
            delta = entry.get("level_delta", 0)
            note = "Level up!" if delta > 0 else ("Easier next time" if delta < 0 else "Level holds")
            self.main_window.info_dialog(
                "Session complete",
                f"Score {engine.state.score}\nAccuracy {engine.state.accuracy:.0%}\n{note}",
            )
            circuit = getattr(self, "_circuit", None) or []
            if circuit:
                nxt = circuit[0]
                self._circuit = circuit[1:]
                self.start_mode(nxt)
            else:
                self._circuit = None
                self.show_home()

        def next_trial():
            if engine.done():
                finish_session()
                return
            state["busy"] = False
            trial = engine.next_trial()
            state["trial"] = trial
            # clear buttons
            for c in list(btn_box.children):
                btn_box.remove(c)

            # Render by engine type
            try:
                self._render_trial(key, template, trial, stim, btn_box, engine, set_status, after_answer)
            except Exception as e:
                stim.text = f"(simplified)\n{type(trial).__name__}"
                set_status(str(e)[:80])

                def _skip(_w=None):
                    if state["busy"]:
                        return
                    state["busy"] = True
                    engine.advance()
                    next_trial()

                btn_box.add(
                    toga.Button(
                        "Skip / next",
                        on_press=_skip,
                        style=Pack(margin_bottom=6, height=44),
                    )
                )

        def after_answer(apply_fn):
            if state["busy"]:
                return
            state["busy"] = True
            try:
                event = apply_fn()
                if isinstance(event, dict):
                    set_status(event.get("message", "OK"))
            except Exception as e:
                set_status(f"Error: {e}")
            engine.advance()
            # brief delay via next trial immediately (mobile)
            next_trial()

        # bind helper on self for render
        self._after_answer = after_answer
        next_trial()

    def _end_early(self, key, engine):
        self._circuit = None
        if engine.state.attempts > 0:
            self.progress.record_session(
                mode=key,
                score=engine.state.score,
                correct=engine.state.correct,
                attempts=engine.state.attempts,
                duration_sec=30.0,
                level=engine.level,
                max_streak=engine.state.max_streak,
            )
        self.show_home()

    def _render_trial(self, key, template, trial, stim, btn_box, engine, set_status, after_answer):
        """Map trial fields to simple mobile controls."""
        from neuroforge.logic.simon import COLOR_MAP

        if key == "focus":
            stim.text = "GREEN = TAP\nRED = HOLD" if trial.is_go else "HOLD (no-go)"
            # approximate: show go/nogo
            stim.text = "● GO — tap" if trial.is_go else "■ NO-GO — wait"
            if trial.is_go:
                btn_box.add(toga.Button("TAP", on_press=lambda w: after_answer(lambda: engine.respond(True, False)), style=Pack(height=48, margin_bottom=6, background_color="#3DDCB5")))
            else:
                btn_box.add(toga.Button("I held (correct)", on_press=lambda w: after_answer(lambda: engine.respond(False, True)), style=Pack(height=48, margin_bottom=6)))
                btn_box.add(toga.Button("False alarm", on_press=lambda w: after_answer(lambda: engine.respond(True, False)), style=Pack(height=44, margin_bottom=6)))
            return

        if key == "nback":
            stim.text = f"{trial.letter}\n\n{trial.n}-Back?"
            btn_box.add(toga.Button("MATCH", on_press=lambda w: after_answer(lambda: engine.answer(True)), style=Pack(height=48, margin_bottom=6, background_color="#3DDCB5")))
            btn_box.add(toga.Button("NO MATCH", on_press=lambda w: after_answer(lambda: engine.answer(False)), style=Pack(height=48, margin_bottom=6, background_color="#FF7B72")))
            return

        if key == "flanker":
            stim.text = trial.display
            btn_box.add(toga.Button("← LEFT", on_press=lambda w: after_answer(lambda: engine.answer("<")), style=Pack(height=48, margin_bottom=6)))
            btn_box.add(toga.Button("RIGHT →", on_press=lambda w: after_answer(lambda: engine.answer(">")), style=Pack(height=48, margin_bottom=6)))
            return

        if key == "simon":
            stim.text = f"{trial.color.upper()} on {trial.side.upper()}\nBlue=LEFT Gold=RIGHT"
            btn_box.add(toga.Button("LEFT", on_press=lambda w: after_answer(lambda: engine.answer("left")), style=Pack(height=48, margin_bottom=6, background_color="#6C8CFF")))
            btn_box.add(toga.Button("RIGHT", on_press=lambda w: after_answer(lambda: engine.answer("right")), style=Pack(height=48, margin_bottom=6, background_color="#F5C542")))
            return

        if key == "rotate":
            stim.text = "Same shape rotated\nor different (mirror)?"
            btn_box.add(toga.Button("SAME", on_press=lambda w: after_answer(lambda: engine.answer(True)), style=Pack(height=48, margin_bottom=6, background_color="#3DDCB5")))
            btn_box.add(toga.Button("DIFFERENT", on_press=lambda w: after_answer(lambda: engine.answer(False)), style=Pack(height=48, margin_bottom=6, background_color="#FF7B72")))
            return

        if key == "change":
            stim.text = f"Array of {len(trial.sample)} colors\n(encode then decide)"
            # mobile simplified: skip encode animation, ask immediately on test truth
            btn_box.add(toga.Button("SAME", on_press=lambda w: after_answer(lambda: engine.answer(False)), style=Pack(height=48, margin_bottom=6)))
            btn_box.add(toga.Button("CHANGED", on_press=lambda w: after_answer(lambda: engine.answer(True)), style=Pack(height=48, margin_bottom=6)))
            return

        if key == "category":
            stim.text = f"{trial.rule_prompt}\n\n{trial.word}"
            btn_box.add(toga.Button("YES", on_press=lambda w: after_answer(lambda: engine.answer(True)), style=Pack(height=48, margin_bottom=6, background_color="#3DDCB5")))
            btn_box.add(toga.Button("NO", on_press=lambda w: after_answer(lambda: engine.answer(False)), style=Pack(height=48, margin_bottom=6, background_color="#FF7B72")))
            return

        if key == "sart":
            stim.text = f"{trial.digit}\n\nTAP all except 3"
            btn_box.add(toga.Button("TAP", on_press=lambda w: after_answer(lambda: engine.respond(True)), style=Pack(height=48, margin_bottom=6)))
            btn_box.add(toga.Button("HOLD", on_press=lambda w: after_answer(lambda: engine.respond(False)), style=Pack(height=48, margin_bottom=6)))
            return

        if key == "posner":
            stim.text = f"Cue {trial.cue_side} → find target"
            btn_box.add(toga.Button("LEFT", on_press=lambda w: after_answer(lambda: engine.answer("left")), style=Pack(height=48, margin_bottom=6)))
            btn_box.add(toga.Button("RIGHT", on_press=lambda w: after_answer(lambda: engine.answer("right")), style=Pack(height=48, margin_bottom=6)))
            return

        if key == "calc":
            stim.text = trial.expression
            for opt in trial.options:
                btn_box.add(
                    toga.Button(
                        str(opt),
                        on_press=lambda w, v=opt: after_answer(lambda: engine.choose(v)),
                        style=Pack(height=44, margin_bottom=4),
                    )
                )
            return

        if key == "symdigit":
            legend = "  ".join(f"{s}={d}" for s, d in trial.key_map[:6])
            stim.text = f"{legend}\n\n{trial.probe_symbol} = ?"
            for opt in trial.options:
                btn_box.add(
                    toga.Button(
                        str(opt),
                        on_press=lambda w, v=opt: after_answer(lambda: engine.choose(v)),
                        style=Pack(height=44, margin_bottom=4),
                    )
                )
            return

        if key == "speed":
            stim.text = f"Find: {trial.target}"
            for opt in trial.options:
                btn_box.add(
                    toga.Button(
                        opt,
                        on_press=lambda w, v=opt: after_answer(lambda: engine.choose(v, 0.5)),
                        style=Pack(height=44, margin_bottom=4),
                    )
                )
            return

        if key == "stroop":
            stim.text = f"Ink color of:\n{trial.word}"
            for opt in trial.options:
                btn_box.add(
                    toga.Button(
                        opt,
                        on_press=lambda w, v=opt: after_answer(lambda: engine.choose(v)),
                        style=Pack(height=44, margin_bottom=4),
                    )
                )
            return

        if key == "rsvp":
            stim.text = "Stream done — which digit?"
            for opt in trial.options:
                btn_box.add(
                    toga.Button(
                        str(opt),
                        on_press=lambda w, v=opt: after_answer(lambda: engine.choose(v)),
                        style=Pack(height=44, margin_bottom=4),
                    )
                )
            return

        if key == "odd":
            stim.text = "Find the odd one\n(tap index)"
            for i, sym in enumerate(trial.items[:12]):
                btn_box.add(
                    toga.Button(
                        f"{i}: {sym}",
                        on_press=lambda w, idx=i: after_answer(lambda: engine.choose(idx)),
                        style=Pack(height=40, margin_bottom=3),
                    )
                )
            return

        if key == "switch":
            stim.text = f"Rule: {trial.rule}\nTarget {trial.target_shape} {trial.target_color_name}"
            for i, opt in enumerate(trial.options):
                shape, name, _ = opt
                btn_box.add(
                    toga.Button(
                        f"{shape} {name}",
                        on_press=lambda w, idx=i: after_answer(lambda: engine.choose(idx)),
                        style=Pack(height=44, margin_bottom=4),
                    )
                )
            return

        if key == "rulesearch":
            t = trial.target
            stim.text = f"Target: {t.count}x {t.shape} {t.color_name}\n(hidden rule)"
            for i, card in enumerate(trial.options):
                btn_box.add(
                    toga.Button(
                        f"{card.count}x {card.shape} {card.color_name}",
                        on_press=lambda w, idx=i: after_answer(lambda: engine.choose(idx)),
                        style=Pack(height=44, margin_bottom=4),
                    )
                )
            return

        # Fallback for complex modes (memory, dual, track, etc.)
        stim.text = f"{MODE_META[key]['title']}\n\nDesktop has full UI.\nMobile simplified next update."
        set_status("Use desktop build for full mode")
        btn_box.add(
            toga.Button(
                "Back to menu",
                on_press=lambda w: self.show_home(),
                style=Pack(height=48, margin_bottom=6),
            )
        )


def main():
    return NeuroForgeMobile(
        formal_name="NeuroForge",
        app_id="com.neuroforge.app",
        app_name="NeuroForge",
        description="Adaptive brain training",
    )


if __name__ == "__main__":
    main().main_loop()
