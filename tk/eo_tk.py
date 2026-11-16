"""Excessive Overkill (EO) style for tkinter / ttk.

    import sys; sys.path.insert(0, "path/to/eo-style-guide/tk")
    import eo_tk as eo

    root = tk.Tk()
    eo.apply(root, "dark")                       # theme, fonts, window icon, dark title bar
    head = eo.Header(root, "Arm bench 02", ["run 2026-10-15-a", "fw 0.9.4"])
    head.pack(fill="x", padx=eo.px(24), pady=(eo.px(20), 0))
    eo.button(head.controls, "Start run", cmd, kind="primary").pack(side="left")
    tile = eo.Tile(root, "Bus voltage", unit="V"); tile.set(24.13, digits=2)
    eo.Footer(root, "bench panel").pack(fill="x", side="bottom")

Rules mirrored from SKILL.md: black surface, white text and highlights, 1 px dark
gray separators, square corners, white 8 px corner bracket on panels and tiles,
Roboto Condensed titles, Roboto Mono for every number, a spinner on anything
running, readouts that tween and flash when they change. Call apply() once at
startup; to change mode, restart the window.
"""

import ctypes
import sys
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import ttk

HERE = Path(__file__).resolve().parent
ROOT_DIR = HERE.parent
FONT_DIR = ROOT_DIR / "fonts"
LOGO_DIR = ROOT_DIR / "assets" / "logo" / "tk"

# Mirrors tokens.json. Tk uses one surface (bg) for frames and labels; `panel` is
# for input fields, tables and text areas so they read as slightly inset.
PALETTE = {
    "dark": {
        "bg": "#000000", "panel": "#0a0a0a", "border": "#2b2b2b", "border_strong": "#3d3d3d",
        "rule": "#1c1c1c", "grid": "#1f1f1f", "axis": "#4d4d4d", "ink": "#ffffff", "muted": "#8f8f8f",
        "accent": "#ffffff", "on_accent": "#000000", "accent_hover": "#d9d9d9", "hover_row": "#161616",
        "flash": "#2b2b2b", "select": "#262626",
        "series": ["#2f62e8", "#e03a2f", "#0f9a66", "#a45ee0", "#1a9cc0", "#d9539a"],
        "good": "#4fbf5a", "warning": "#e6c229", "critical": "#ff5a4a", "off": "#5a5c5e",
    },
    "light": {
        "bg": "#ffffff", "panel": "#ffffff", "border": "#d0d0d0", "border_strong": "#000000",
        "rule": "#e6e6e6", "grid": "#e6e6e6", "axis": "#000000", "ink": "#0b0b0b", "muted": "#595959",
        "accent": "#000000", "on_accent": "#ffffff", "accent_hover": "#333333", "hover_row": "#f2f2f2",
        "flash": "#e6e6e6", "select": "#e6e6e6",
        "series": ["#1f4fd8", "#e3241b", "#0f8a5f", "#8a3fd1", "#0e7fa3", "#c2307a"],
        "good": "#1d8a3e", "warning": "#b58900", "critical": "#d42a1c", "off": "#9a9a95",
    },
}

C = dict(PALETTE["dark"])  # active palette, updated by apply()
F = {}                     # active fonts, filled by apply()
_mode = "dark"
_scale = 1.0
_images = []               # keep PhotoImage references alive


def px(n):
    """Scale a 96-dpi pixel size to this display."""
    return int(round(n * _scale))


def colors():
    return C


# ── Fonts ──────────────────────────────────────────────────────────


def _register_fonts():
    """Make the bundled Roboto TTFs usable by Tk for this process (Windows only;
    on other systems install them or Tk falls back to the system fonts)."""
    if sys.platform != "win32":
        return
    for f in FONT_DIR.glob("*.ttf"):
        try:
            ctypes.windll.gdi32.AddFontResourceExW(str(f), 0x10, 0)  # FR_PRIVATE
        except Exception:
            pass


def _family(root, wanted, fallbacks):
    have = {n.lower() for n in tkfont.families(root)}
    for name in (wanted, *fallbacks):
        if name.lower() in have:
            return name
    return fallbacks[-1]


def _make_fonts(root):
    sans = _family(root, "Roboto", ("Segoe UI", "Helvetica", "Arial"))
    cond = _family(root, "Roboto Condensed", ("Arial Narrow", sans))
    mono = _family(root, "Roboto Mono", ("Consolas", "Menlo", "Courier New"))
    mk = lambda fam, size, weight="normal": tkfont.Font(root=root, family=fam, size=size, weight=weight)
    F.update(
        sans=sans, cond=cond, mono=mono,
        body=mk(sans, 10), caption=mk(sans, 9), mono_=mk(mono, 10), mono_s=mk(mono, 9),
        label=mk(mono, 8, "bold"), button=mk(mono, 9, "bold"),
        title=mk(cond, 20, "bold"), h2=mk(cond, 11, "bold"), value=mk(mono, 24), value_s=mk(mono, 11),
    )


# ── Theme ──────────────────────────────────────────────────────────


def apply(root, mode="dark", icon=True):
    """Theme the whole app. Call once, right after creating the root window."""
    global _mode, _scale
    _mode = mode
    C.clear(); C.update(PALETTE[mode])
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    _register_fonts()
    try:
        _scale = root.winfo_fpixels("1i") / 96.0
    except tk.TclError:
        _scale = 1.0
    _make_fonts(root)
    root.configure(bg=C["bg"])
    _tk_defaults(root)
    _ttk_styles(root)
    if icon:
        set_icon(root)
    if mode == "dark":
        _dark_titlebar(root)
    return C


def _tk_defaults(root):
    o = root.option_add
    o("*Background", C["bg"]); o("*Foreground", C["ink"])
    # Per-class fonts only: a global *Font would override the ttk style fonts.
    for w in ("Label", "Button", "Checkbutton", "Radiobutton", "Labelframe", "Message"):
        o(f"*{w}.font", F["body"])
    o("*highlightThickness", 0); o("*borderWidth", 0)
    for w in ("Text", "Listbox", "Entry", "Spinbox"):
        o(f"*{w}.background", C["panel"]); o(f"*{w}.foreground", C["ink"])
        o(f"*{w}.insertBackground", C["accent"]); o(f"*{w}.selectBackground", C["accent"])
        o(f"*{w}.selectForeground", C["on_accent"])
        o(f"*{w}.highlightThickness", 1); o(f"*{w}.highlightBackground", C["border"])
        o(f"*{w}.highlightColor", C["accent"]); o(f"*{w}.font", F["mono_"])
    o("*Menu.background", C["panel"]); o("*Menu.foreground", C["ink"])
    o("*Menu.activeBackground", C["accent"]); o("*Menu.activeForeground", C["on_accent"])
    o("*Menu.font", F["body"]); o("*Menu.borderWidth", 1); o("*Menu.relief", "solid")
    o("*TCombobox*Listbox.background", C["panel"]); o("*TCombobox*Listbox.foreground", C["ink"])
    o("*TCombobox*Listbox.selectBackground", C["accent"]); o("*TCombobox*Listbox.selectForeground", C["on_accent"])
    o("*TCombobox*Listbox.font", F["mono_"])


def _ttk_styles(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    bg, panel, ink, muted, acc = C["bg"], C["panel"], C["ink"], C["muted"], C["accent"]
    bd, bds = C["border"], C["border_strong"]

    s.configure(".", background=bg, foreground=ink, bordercolor=bd, darkcolor=bg, lightcolor=bg,
                troughcolor=C["border"], focuscolor=acc, selectbackground=acc, selectforeground=C["on_accent"],
                insertcolor=acc, font=F["body"], relief="flat")
    s.configure("TFrame", background=bg)
    s.configure("TSeparator", background=bd)

    # Labels
    s.configure("TLabel", background=bg, foreground=ink, font=F["body"])
    s.configure("Title.TLabel", font=F["title"])
    s.configure("H2.TLabel", font=F["h2"])
    s.configure("Caption.TLabel", foreground=muted, font=F["caption"])
    s.configure("Muted.TLabel", foreground=muted)
    s.configure("Meta.TLabel", foreground=muted, font=F["mono_s"])
    s.configure("Label.TLabel", foreground=muted, font=F["label"])   # small uppercase mono
    s.configure("Mono.TLabel", font=F["mono_"])
    s.configure("Value.TLabel", foreground=acc, font=F["value"])
    s.configure("Unit.TLabel", foreground=muted, font=F["value_s"])

    # Buttons: square, 1 px border, border goes to the accent on hover
    pad = (px(12), px(7))
    s.configure("TButton", background=bg, foreground=ink, bordercolor=bds, darkcolor=bg, lightcolor=bg,
                borderwidth=1, focusthickness=1, focuscolor=acc, padding=pad, font=F["button"], anchor="center")
    s.map("TButton", bordercolor=[("disabled", bd), ("pressed", acc), ("active", acc)],
          background=[("pressed", C["rule"]), ("active", bg)], foreground=[("disabled", C["off"])])
    s.configure("Primary.TButton", background=acc, foreground=C["on_accent"], bordercolor=acc,
                darkcolor=acc, lightcolor=acc)
    s.map("Primary.TButton", background=[("disabled", bd), ("pressed", C["accent_hover"]), ("active", C["accent_hover"])],
          bordercolor=[("disabled", bd), ("active", C["accent_hover"])],
          foreground=[("disabled", C["off"])], darkcolor=[("active", C["accent_hover"])], lightcolor=[("active", C["accent_hover"])])
    s.configure("Danger.TButton", foreground=C["critical"], bordercolor=C["critical"])
    s.map("Danger.TButton", bordercolor=[("disabled", bd), ("active", C["critical"])])

    # Inputs
    for w in ("TEntry", "TSpinbox", "TCombobox"):
        s.configure(w, fieldbackground=panel, foreground=ink, bordercolor=bd, darkcolor=bd, lightcolor=bd,
                    insertcolor=acc, padding=(px(6), px(5)), arrowcolor=ink, font=F["mono_"], borderwidth=1)
        s.map(w, bordercolor=[("focus", acc), ("hover", bds)], lightcolor=[("focus", acc)], darkcolor=[("focus", acc)],
              fieldbackground=[("readonly", panel), ("disabled", bg)], foreground=[("disabled", C["off"])],
              selectbackground=[("readonly", panel)], selectforeground=[("readonly", ink)])
    s.configure("TCombobox", background=bg)
    s.configure("TSpinbox", background=bg, arrowsize=px(12))

    # Toggles
    for w in ("TCheckbutton", "TRadiobutton"):
        s.configure(w, background=bg, foreground=ink, indicatorbackground=panel, indicatorforeground=C["on_accent"],
                    indicatorcolor=panel, upperbordercolor=bds, lowerbordercolor=bds, font=F["body"], padding=px(2))
        s.map(w, indicatorbackground=[("selected", acc), ("pressed", bd), ("!selected", panel)],
              indicatorcolor=[("selected", acc), ("pressed", bd), ("!selected", panel)],
              upperbordercolor=[("active", acc)], lowerbordercolor=[("active", acc)],
              indicatorforeground=[("selected", C["on_accent"])],
              background=[("active", bg)], foreground=[("disabled", C["off"])])

    # Slider and progress
    s.configure("Horizontal.TScale", background=ink, troughcolor=bd, bordercolor=bg, lightcolor=ink, darkcolor=ink)
    s.configure("Vertical.TScale", background=ink, troughcolor=bd, bordercolor=bg, lightcolor=ink, darkcolor=ink)
    s.map("Horizontal.TScale", background=[("active", acc)], lightcolor=[("active", acc)], darkcolor=[("active", acc)])
    s.configure("Horizontal.TProgressbar", background=acc, troughcolor=bd, bordercolor=bg, lightcolor=acc,
                darkcolor=acc, thickness=px(6))

    # Scrollbars
    for o in ("Vertical", "Horizontal"):
        s.configure(f"{o}.TScrollbar", background=bds, troughcolor=bg, bordercolor=bg, darkcolor=bds, lightcolor=bds,
                    arrowcolor=muted, gripcount=0, arrowsize=px(12))
        s.map(f"{o}.TScrollbar", background=[("active", C["axis"])])

    # Tabs
    s.configure("TNotebook", background=bg, bordercolor=bd, tabmargins=(0, 0, 0, 0))
    s.configure("TNotebook.Tab", background=bg, foreground=muted, bordercolor=bd, lightcolor=bg, darkcolor=bg,
                padding=(px(14), px(7)), font=F["button"])
    s.map("TNotebook.Tab", foreground=[("selected", ink)], background=[("selected", panel)],
          bordercolor=[("selected", acc)], lightcolor=[("selected", acc)])

    # Table
    s.configure("Treeview", background=panel, fieldbackground=panel, foreground=ink, bordercolor=bd,
                lightcolor=panel, darkcolor=panel, rowheight=px(28), font=F["mono_s"], borderwidth=0)
    s.map("Treeview", background=[("selected", C["select"])], foreground=[("selected", ink)])
    s.configure("Treeview.Heading", background=bg, foreground=muted, font=F["label"], bordercolor=bds,
                lightcolor=bg, darkcolor=bg, relief="flat", padding=(px(8), px(6)))
    s.map("Treeview.Heading", background=[("active", bg)], foreground=[("active", ink)])
    s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    # Groups and panes
    s.configure("TLabelframe", background=bg, bordercolor=bd, borderwidth=1, relief="solid")
    s.configure("TLabelframe.Label", background=bg, foreground=muted, font=F["label"])
    s.configure("TPanedwindow", background=bg)
    s.configure("Sash", sashthickness=px(5), background=bd, bordercolor=bg, gripcount=0)
    s.configure("TMenubutton", background=bg, foreground=ink, bordercolor=bds, arrowcolor=ink, padding=pad, font=F["button"])
    s.map("TMenubutton", bordercolor=[("active", acc)])


def set_icon(root, size=64):
    img = tk.PhotoImage(master=root, file=str(LOGO_DIR / f"eo-mark-white-{size}.png"))
    _images.append(img)
    try:
        root.iconphoto(True, img)
    except tk.TclError:
        pass


def _dark_titlebar(root):
    """Windows 10/11: use the dark title bar so the window frame matches."""
    if sys.platform != "win32":
        return
    try:
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        one = ctypes.c_int(1)
        for attr in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE (new / old id)
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(one), 4) == 0:
                break
    except Exception:
        pass


# ── Logo ───────────────────────────────────────────────────────────


def logo_image(kind="mark", size=None, master=None):
    """PhotoImage of the EO mark (size 24/32/64/128) or wordmark (height 12/16/24),
    white on dark mode and black on light mode."""
    tone = "white" if _mode == "dark" else "black"
    if kind == "wordmark":
        name = f"eo-wordmark-{tone}-{size or 16}.png"
    else:
        name = f"eo-mark-{tone}-{size or 32}.png"
    img = tk.PhotoImage(master=master, file=str(LOGO_DIR / name))
    _images.append(img)
    return img


# ── Widgets ────────────────────────────────────────────────────────


def button(parent, text, cmd=None, kind="", **kw):
    """kind: '' (secondary), 'primary' (the one main action), 'danger'."""
    style = {"primary": "Primary.TButton", "danger": "Danger.TButton"}.get(kind, "TButton")
    b = ttk.Button(parent, text=text.upper(), command=cmd, style=style, cursor="hand2", **kw)
    return b


def label(parent, text, kind="", **kw):
    """kind: '', title, h2, caption, muted, meta, label (small uppercase), mono."""
    style = {"": "TLabel"}.get(kind, f"{kind.capitalize()}.TLabel")
    if kind in ("title", "h2", "label"):
        text = text.upper()
    return ttk.Label(parent, text=text, style=style, **kw)


class Rule(tk.Frame):
    """1 px dark gray separator."""

    def __init__(self, parent, vertical=False):
        super().__init__(parent, bg=C["border"], width=1 if vertical else 0, height=1 if not vertical else 0)


def _bracket(frame):
    """White 8 px corner bracket on the top-left, drawn over the 1 px border."""
    n, t = px(8), 2
    tk.Frame(frame, bg=C["accent"], width=n, height=t).place(x=-1, y=-1)
    tk.Frame(frame, bg=C["accent"], width=t, height=n).place(x=-1, y=-1)


class Panel(tk.Frame):
    """Bordered surface with the corner bracket. Put content in `.body`.
    Panel(parent, "Joint current", "Phase current per joint over the last 60 s")"""

    def __init__(self, parent, title=None, caption=None, pad=16, bracket=True):
        super().__init__(parent, bg=C["bg"], highlightthickness=1, highlightbackground=C["border"], bd=0)
        inner = tk.Frame(self, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=px(pad), pady=px(pad - 2))
        if title:
            label(inner, title, "h2").pack(anchor="w")
        if caption:
            label(inner, caption, "caption").pack(anchor="w", pady=(0, px(8)))
        self.body = tk.Frame(inner, bg=C["bg"])
        self.body.pack(fill="both", expand=True)
        if bracket:
            _bracket(self)


class Tile(Panel):
    """One number: small label, big mono readout, unit, optional sub line.
    set() tweens the value and flashes it. Use a Tile, not a chart, for a single number."""

    def __init__(self, parent, name, unit="", sub=""):
        super().__init__(parent, pad=14)
        b = self.body
        label(b, name, "label").pack(anchor="w")
        row = tk.Frame(b, bg=C["bg"]); row.pack(anchor="w", pady=(px(6), 0))
        self._val = tk.Label(row, text="--", font=F["value"], fg=C["accent"], bg=C["bg"], padx=px(2))
        self._val.pack(side="left")
        self._unit = ttk.Label(row, text=unit, style="Unit.TLabel"); self._unit.pack(side="left", anchor="s", pady=(0, px(4)), padx=(px(4), 0))
        self._sub = ttk.Label(b, text=sub, style="Meta.TLabel"); self._sub.pack(anchor="w", pady=(px(4), 0))
        self._cur = None; self._job = None

    def sub(self, text, state=None):
        """Sub line. Pass a state (good/warning/critical/off) to prefix a status square."""
        self._sub.configure(text=("■ " if state else "") + text, foreground=C[state] if state else C["muted"])

    def set(self, value, digits=0, ms=400):
        start = self._cur if self._cur is not None else value
        self._cur = value
        if self._job:
            self.after_cancel(self._job)
        self._val.configure(bg=C["flash"])
        self.after(140, lambda: self._val.configure(bg=C["bg"]))
        t0 = [0]
        steps = max(1, ms // 16)

        def tick():
            t0[0] += 1
            k = min(1.0, t0[0] / steps); e = 1 - (1 - k) ** 3
            self._val.configure(text=f"{start + (value - start) * e:.{digits}f}")
            self._job = self.after(16, tick) if k < 1 else None
        tick()


class Status(tk.Frame):
    """Square + word, never color alone. state: good, warning, critical, off, live (breathing green)."""

    def __init__(self, parent, text="", state="off"):
        super().__init__(parent, bg=C["bg"])
        n = px(8)
        self._sq = tk.Canvas(self, width=n, height=n, bg=C["bg"], highlightthickness=0, bd=0)
        self._sq.pack(side="left", padx=(0, px(6)))
        self._rect = self._sq.create_rectangle(0, 0, n, n, width=0)
        self._txt = ttk.Label(self, text=text, style="Meta.TLabel"); self._txt.pack(side="left")
        self._live = False; self._phase = 0; self._job = None
        self.set(text, state)

    def set(self, text, state="off"):
        self._txt.configure(text=text)
        self._live = state == "live"
        self._sq.itemconfigure(self._rect, fill=C["good" if self._live else state])
        if self._live and not self._job:
            self._breathe()

    def _breathe(self):
        if not self._live:
            self._job = None
            return
        self._phase = (self._phase + 1) % 100
        k = abs(50 - self._phase) / 50          # 0..1..0 over ~3 s
        a, b = _hex(C["good"]), _hex(C["bg"])
        mix = tuple(int(x * (0.35 + 0.65 * k) + y * (0.65 - 0.65 * k)) for x, y in zip(a, b))
        self._sq.itemconfigure(self._rect, fill="#%02x%02x%02x" % mix)
        self._job = self.after(30, self._breathe)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Spinner(tk.Canvas):
    """Accent arc chasing around a gray track, with a small dot orbiting the other way.
    Show one wherever something is running or loading."""

    def __init__(self, parent, size=16, bg=None):
        n = px(size)
        super().__init__(parent, width=n, height=n, bg=bg or C["bg"], highlightthickness=0, bd=0)
        w = max(2, n // 8); pad = w // 2 + 1
        self._n = n; self._a = 0; self._job = None
        self.create_oval(pad, pad, n - pad, n - pad, outline=C["border_strong"], width=w)
        self._arc = self.create_arc(pad, pad, n - pad, n - pad, start=0, extent=100, style="arc", outline=C["accent"], width=w)
        self._dot = self.create_oval(0, 0, 0, 0, fill=C["ink"], width=0)

    def start(self):
        if not self._job:
            self._tick()
        return self

    def stop(self):
        if self._job:
            self.after_cancel(self._job); self._job = None
        self.itemconfigure(self._arc, extent=0)
        self.coords(self._dot, 0, 0, 0, 0)

    def _tick(self):
        import math
        self._a = (self._a - 14) % 360
        self.itemconfigure(self._arc, start=self._a, extent=100)
        c, r, d = self._n / 2, self._n * 0.22, max(1, self._n // 8)
        ang = math.radians(-self._a * 1.6)
        x, y = c + r * math.cos(ang), c - r * math.sin(ang)
        self.coords(self._dot, x - d, y - d, x + d, y + d)
        self._job = self.after(30, self._tick)


_busy_state = {}


def busy(btn, on=True, text="Running"):
    """Swap a button to a spinning 'RUNNING' state and disable it, or restore it.
        eo.busy(btn, True, "Homing") ... eo.busy(btn, False)"""
    if on:
        if btn in _busy_state:
            return
        _busy_state[btn] = [btn.cget("text"), None, 0]
        btn.state(["disabled"])
        frames = "|/-\\"

        def spin():
            st = _busy_state.get(btn)
            if not st:
                return
            st[2] = (st[2] + 1) % 4
            btn.configure(text=f"{frames[st[2]]} {text.upper()}")
            st[1] = btn.after(110, spin)
        spin()
    else:
        st = _busy_state.pop(btn, None)
        if st:
            btn.after_cancel(st[1]) if st[1] else None
            btn.configure(text=st[0]); btn.state(["!disabled"])


class Header(tk.Frame):
    """Mast: EO mark + uppercase title and mono meta line on the left, `.controls` on the right,
    one rule underneath."""

    def __init__(self, parent, title, meta=()):
        super().__init__(parent, bg=C["bg"])
        row = tk.Frame(self, bg=C["bg"]); row.pack(fill="x")
        left = tk.Frame(row, bg=C["bg"]); left.pack(side="left")
        mark = tk.Label(left, image=logo_image("mark", 32, self), bg=C["bg"], bd=0)
        mark.pack(side="left", padx=(0, px(10)), anchor="n", pady=(px(2), 0))
        text = tk.Frame(left, bg=C["bg"]); text.pack(side="left")
        self.title = label(text, title, "title"); self.title.pack(anchor="w")
        self.meta = tk.Frame(text, bg=C["bg"]); self.meta.pack(anchor="w", pady=(px(2), 0))
        for m in meta:
            ttk.Label(self.meta, text=m, style="Meta.TLabel").pack(side="left", padx=(0, px(14)))
        self.controls = tk.Frame(row, bg=C["bg"]); self.controls.pack(side="right", anchor="s")
        Rule(self).pack(fill="x", pady=(px(14), 0))


class Footer(tk.Frame):
    """Rule, EXCESSIVE OVERKILL wordmark on the left, small mono note on the right."""

    def __init__(self, parent, note=""):
        super().__init__(parent, bg=C["bg"])
        Rule(self).pack(fill="x")
        row = tk.Frame(self, bg=C["bg"]); row.pack(fill="x", pady=(px(10), 0))
        tk.Label(row, image=logo_image("wordmark", 12, self), bg=C["bg"], bd=0).pack(side="left")
        ttk.Label(row, text=note, style="Meta.TLabel").pack(side="right")


class Table(ttk.Treeview):
    """Event-log style table. columns: [(id, "HEADING", width_px, "w"|"e"), ...]. Numbers go in
    right-aligned ("e") columns. Rows tint on hover; add(values, state=...) colors the row text
    muted/warning/critical."""

    def __init__(self, parent, columns, height=6):
        super().__init__(parent, columns=[c[0] for c in columns], show="headings", height=height, selectmode="browse")
        for cid, head, w, anchor in columns:
            self.heading(cid, text=head.upper(), anchor=anchor)
            self.column(cid, width=px(w), anchor=anchor, stretch=(w >= 160))
        self.tag_configure("hover", background=C["hover_row"])
        self.tag_configure("muted", foreground=C["muted"])
        for st in ("good", "warning", "critical"):
            self.tag_configure(st, foreground=C[st])
        self._hov = None
        self.bind("<Motion>", self._move); self.bind("<Leave>", lambda e: self._unhover())

    def add(self, values, state=None, at="end"):
        return self.insert("", at, values=values, tags=(state,) if state else ())

    def empty_message(self, text="No runs yet. Start one above."):
        self.insert("", "end", values=(text,), tags=("muted",))

    def _unhover(self):
        if self._hov and self.exists(self._hov):
            self.item(self._hov, tags=tuple(t for t in self.item(self._hov, "tags") if t != "hover"))
        self._hov = None

    def _move(self, e):
        row = self.identify_row(e.y)
        if row == self._hov:
            return
        self._unhover()
        if row:
            self.item(row, tags=tuple(self.item(row, "tags")) + ("hover",)); self._hov = row


def use_matplotlib():
    """Theme matplotlib to the active mode and return the eo_style module (for label_lines, title, save...).
    Call before creating figures you plan to embed."""
    sys.path.insert(0, str(ROOT_DIR / "matplotlib"))
    import eo_style
    eo_style.use(_mode)
    return eo_style


def embed_figure(parent, fig):
    """Embed a matplotlib Figure in a Tk parent (call use_matplotlib() first so the figure is themed).
    Returns the canvas widget; call .draw() / .draw_idle() after updating data."""
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().configure(bg=C["bg"], highlightthickness=0, bd=0)
    return canvas
