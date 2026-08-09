"""Audio + haptic-style visual feedback (desktop stand-in for iOS haptics)."""

from __future__ import annotations

import struct
import threading
import wave
from pathlib import Path
from typing import TYPE_CHECKING

from . import theme as T

if TYPE_CHECKING:
    import tkinter as tk

_ASSETS = Path(__file__).resolve().parent.parent / "assets" / "sounds"
_sounds_ready = False
_enabled = True


def set_enabled(on: bool) -> None:
    global _enabled
    _enabled = on


def is_enabled() -> bool:
    return _enabled


def _ensure_sounds() -> None:
    global _sounds_ready
    if _sounds_ready:
        return
    _ASSETS.mkdir(parents=True, exist_ok=True)
    specs = {
        "correct.wav": [(880, 0.06), (1175, 0.08)],
        "wrong.wav": [(220, 0.12), (165, 0.14)],
        "tick.wav": [(660, 0.04)],
        "go.wav": [(523, 0.05), (784, 0.09)],
        "level.wav": [(523, 0.05), (659, 0.05), (784, 0.05), (1047, 0.12)],
        "tap.wav": [(900, 0.025)],
    }
    for name, notes in specs.items():
        path = _ASSETS / name
        if not path.exists():
            _write_tone_sequence(path, notes)
    _sounds_ready = True


def _write_tone_sequence(path: Path, notes: list[tuple[float, float]], rate: int = 22050) -> None:
    frames = bytearray()
    for freq, dur in notes:
        n = int(rate * dur)
        for i in range(n):
            t = i / rate
            # soft envelope to avoid clicks
            env = 1.0
            attack = int(0.008 * rate)
            release = int(0.02 * rate)
            if i < attack:
                env = i / max(1, attack)
            elif i > n - release:
                env = max(0.0, (n - i) / max(1, release))
            import math
            sample = int(16000 * env * math.sin(2 * math.pi * freq * t))
            frames += struct.pack("<h", max(-32767, min(32767, sample)))
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


def _play_file(name: str) -> None:
    if not _enabled:
        return
    _ensure_sounds()
    path = _ASSETS / name
    if not path.exists():
        return

    def _run():
        try:
            if __import__("sys").platform == "win32":
                import winsound
                winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                # best-effort non-Windows
                import subprocess
                subprocess.Popen(
                    ["afplay" if __import__("sys").platform == "darwin" else "aplay", str(path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


def play_correct() -> None:
    _play_file("correct.wav")


def play_wrong() -> None:
    _play_file("wrong.wav")


def play_tick() -> None:
    _play_file("tick.wav")


def play_go() -> None:
    _play_file("go.wav")


def play_level() -> None:
    _play_file("level.wav")


def play_tap() -> None:
    _play_file("tap.wav")


def haptic_flash(widget: "tk.Misc", good: bool = True, root: "tk.Misc | None" = None) -> None:
    """Brief border/background flash — desktop stand-in for phone vibration."""
    if not _enabled or widget is None:
        return
    try:
        import tkinter as tk

        color = T.SUCCESS if good else T.ERROR
        target = root or widget
        # overlay flash frame if possible
        top = target.winfo_toplevel()
        flash = tk.Frame(top, bg=color, height=4)
        flash.place(relx=0, rely=0, relwidth=1, height=5)
        try:
            old = widget.cget("highlightbackground")
        except Exception:
            old = None
        try:
            widget.configure(highlightthickness=3, highlightbackground=color)
        except Exception:
            pass

        def clear():
            try:
                flash.destroy()
            except Exception:
                pass
            try:
                if old is not None:
                    widget.configure(highlightthickness=0, highlightbackground=old)
                else:
                    widget.configure(highlightthickness=0)
            except Exception:
                pass

        top.after(120, clear)
    except Exception:
        pass


def feedback_hit(widget: "tk.Misc | None", good: bool, root: "tk.Misc | None" = None) -> None:
    if good:
        play_correct()
    else:
        play_wrong()
    if widget is not None:
        haptic_flash(widget, good=good, root=root)
