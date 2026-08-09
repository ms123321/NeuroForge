"""Reusable UI widgets for a touch-friendly, mobile-style layout."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from . import theme as T


def font(size: int = 14, bold: bool = False, mono: bool = False) -> tuple:
    family = "Consolas" if mono else T.FONT_FAMILY
    weight = "bold" if bold else "normal"
    return (family, size, weight)


class RoundedButton(tk.Canvas):
    """Large touch-friendly button drawn on a canvas."""

    def __init__(
        self,
        parent,
        text: str,
        command: Callable | None = None,
        bg: str = T.ACCENT,
        fg: str = T.BG_DEEP,
        width: int = 320,
        height: int = T.BTN_H,
        radius: int = T.RADIUS,
        font_size: int = 15,
        **kwargs,
    ):
        parent_bg = T.BG_DEEP
        try:
            parent_bg = parent.cget("bg")
        except Exception:
            pass
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )
        self._command = command
        self._bg = bg
        self._fg = fg
        self._text = text
        # Never use _w / _h — those are reserved by tkinter Widget for the Tcl path
        self._bw = width
        self._bh = height
        self._r = radius
        self._font_size = font_size
        self._enabled = True
        self._draw()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kw)

    def _draw(self, hover: bool = False):
        self.delete("all")
        color = self._lighten(self._bg) if hover and self._enabled else self._bg
        if not self._enabled:
            color = T.BG_ELEVATED
        self._round_rect(2, 2, self._bw - 2, self._bh - 2, self._r, fill=color, outline="")
        fg = self._fg if self._enabled else T.TEXT_MUTED
        self.create_text(
            self._bw // 2,
            self._bh // 2,
            text=self._text,
            fill=fg,
            font=font(self._font_size, bold=True),
        )

    def _lighten(self, hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, int(r * 1.12))
        g = min(255, int(g * 1.12))
        b = min(255, int(b * 1.12))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _hover(self, on: bool):
        self._draw(hover=on)

    def _on_click(self, _event=None):
        if self._enabled and self._command:
            self._command()

    def set_text(self, text: str):
        self._text = text
        self._draw()

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self._draw()

    def set_colors(self, bg: str, fg: str = T.BG_DEEP):
        self._bg = bg
        self._fg = fg
        self._draw()


class Card(tk.Frame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", T.BG_CARD)
        kwargs.setdefault("padx", 14)
        kwargs.setdefault("pady", 12)
        super().__init__(parent, **kwargs)


class Label(tk.Label):
    def __init__(self, parent, text: str = "", size: int = 14, bold: bool = False,
                 color: str = T.TEXT, wrap: int | None = None, **kwargs):
        bg = kwargs.pop("bg", None)
        if bg is None:
            try:
                bg = parent.cget("bg")
            except Exception:
                bg = T.BG_DEEP
        justify = kwargs.pop("justify", "left")
        super().__init__(
            parent,
            text=text,
            font=font(size, bold),
            fg=color,
            bg=bg,
            wraplength=wrap or 0,
            justify=justify,
            **kwargs,
        )


class HeaderBar(tk.Frame):
    def __init__(self, parent, title: str, on_back: Callable | None = None, **kwargs):
        super().__init__(parent, bg=T.BG_DEEP, **kwargs)
        if on_back:
            btn = tk.Label(
                self, text="← Back", font=font(12, bold=True),
                fg=T.ACCENT_SOFT, bg=T.BG_DEEP, cursor="hand2",
            )
            btn.pack(side="left", padx=(4, 8))
            btn.bind("<Button-1>", lambda e: on_back())
        Label(self, text=title, size=18, bold=True, color=T.TEXT).pack(side="left")


class ProgressBar(tk.Canvas):
    def __init__(self, parent, width: int = 320, height: int = 10, **kwargs):
        super().__init__(
            parent, width=width, height=height,
            bg=T.BG_PANEL, highlightthickness=0, bd=0, **kwargs,
        )
        # Never use _w / _h — reserved by tkinter for the Tcl widget path
        self._bw = width
        self._bh = height
        self._value = 0.0
        self._color = T.TEAL
        self._draw()

    def _draw(self):
        self.delete("all")
        self.create_rectangle(0, 0, self._bw, self._bh, fill=T.BG_ELEVATED, outline="")
        fill_w = max(0, int(self._bw * min(1.0, max(0.0, self._value))))
        if fill_w > 0:
            self.create_rectangle(0, 0, fill_w, self._bh, fill=self._color, outline="")

    def set(self, value: float, color: str | None = None):
        self._value = value
        if color:
            self._color = color
        self._draw()


def clear_frame(frame: tk.Widget):
    for child in frame.winfo_children():
        child.destroy()
