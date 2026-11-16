"""Excessive Overkill (EO) style for matplotlib.

    import sys; sys.path.insert(0, "path/to/eo-style-guide/matplotlib")
    import eo_style as eo
    eo.use("dark")          # or "light" for reports and print
    fig, a = plt.subplots()
    a.plot(t, j1, label="J1"); a.plot(t, j3, label="J3")
    eo.label_lines(a)       # direct labels at line ends instead of a legend box
    eo.title(a, "Joint current", "Phase current per joint")
    a.set_xlabel("Time, s"); a.set_ylabel("Phase current, A")   # every axis, quantity then unit
    eo.logo(fig)            # optional: EO mark in the figure corner
    eo.save(fig, "current.png")   # refuses to save if any axis is unlabeled
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import axis as mpl_axis
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
LOGO_DIR = HERE.parent / "assets" / "logo"

# Roboto ships in ../fonts so plots look the same on machines without it installed
for _f in (HERE.parent / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(_f))

PALETTE = {
    "dark": {
        "bg": "#000000", "panel": "#0a0a0a", "ink": "#ffffff", "muted": "#8f8f8f",
        "grid": "#1f1f1f", "accent": "#ffffff",
        "series": ["#2f62e8", "#e03a2f", "#0f9a66", "#a45ee0", "#1a9cc0", "#d9539a"],
        "good": "#4fbf5a", "warning": "#e6c229", "critical": "#ff5a4a", "off": "#5a5c5e",
    },
    "light": {
        "bg": "#ffffff", "panel": "#ffffff", "ink": "#0b0b0b", "muted": "#595959",
        "grid": "#e6e6e6", "accent": "#000000",
        "series": ["#1f4fd8", "#e3241b", "#0f8a5f", "#8a3fd1", "#0e7fa3", "#c2307a"],
        "good": "#1d8a3e", "warning": "#b58900", "critical": "#d42a1c", "off": "#9a9a95",
    },
}

_mode = "dark"
_tick_init = mpl_axis.Tick.__init__


def _mono_tick_init(self, *args, **kwargs):
    # Every tick label matplotlib creates, on any axes (3D and colorbars too), is
    # set to Roboto Mono here, so it holds for savefig, plt.show and notebooks alike.
    _tick_init(self, *args, **kwargs)
    self.label1.set_fontfamily("Roboto Mono")
    self.label2.set_fontfamily("Roboto Mono")


def use(mode="dark"):
    global _mode
    _mode = mode
    plt.style.use(HERE / f"eo-{mode}.mplstyle")
    mpl_axis.Tick.__init__ = _mono_tick_init
    return PALETTE[mode]


def colors():
    return PALETTE[_mode]


def title(ax, text, sub=None):
    """Uppercase title, muted subtitle under it. Left aligned."""
    p = PALETTE[_mode]
    ax.set_title(text.upper(), loc="left", color=p["ink"], fontsize=11, fontweight="bold",
                 fontfamily="Roboto Condensed", pad=22 if sub else 10)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, color=p["muted"], fontsize=8.5, va="bottom")


def label_lines(ax, min_gap=None):
    """Name each line at its right end, nudged apart so labels don't overprint.
    Use this instead of a legend for up to 4 lines."""
    p = PALETTE[_mode]
    lines = [l for l in ax.get_lines() if not l.get_label().startswith("_")]
    if not lines:
        return
    lo, hi = ax.get_ylim()
    gap = min_gap if min_gap is not None else (hi - lo) * 0.05
    ends = sorted(((l.get_ydata()[-1], l) for l in lines), key=lambda e: e[0])
    placed = []
    for y, l in ends:
        if placed and y - placed[-1] < gap:
            y = placed[-1] + gap
        placed.append(y)
        ax.annotate(l.get_label(), xy=(l.get_xdata()[-1], y), xytext=(6, 0), textcoords="offset points",
                    va="center", color=p["ink"], fontsize=8.5, annotation_clip=False)


def bars(ax, labels, values, highlight=None, unit="", xlabel=None, ylabel=None):
    """Horizontal bars, one color, the highlighted bar in series red, values printed at bar ends."""
    p = PALETTE[_mode]
    cols = [p["series"][1] if lab == highlight else p["series"][0] for lab in labels]
    y = range(len(labels))
    ax.barh(y, values, color=cols, height=0.55)
    ax.set_yticks(list(y), labels)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.tick_params(axis="y", colors=p["ink"], length=0)
    ax.spines["bottom"].set_visible(False)
    for i, v in enumerate(values):
        ax.annotate(f"{v}{unit}", xy=(v, i), xytext=(5, 0), textcoords="offset points", va="center",
                    color=p["muted"], fontsize=8.5, fontfamily="Roboto Mono")
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)


def ref_line(ax, value, label, status="warning"):
    """Dashed threshold line in a status color, labeled at the left."""
    p = PALETTE[_mode]
    ax.axhline(value, color=p[status], linestyle=(0, (4, 3)), linewidth=1)
    ax.annotate(label, xy=(0, value), xycoords=("axes fraction", "data"), xytext=(4, 4),
                textcoords="offset points", color=p["muted"], fontsize=8)


_logo_cache = {}


def _logo_array(kind, mode):
    key = (kind, mode)
    if key not in _logo_cache:
        import numpy as np
        from PIL import Image
        name = "eo-wordmark-white.png" if kind == "wordmark" else "eo-mark-white.png"
        im = Image.open(LOGO_DIR / name).convert("RGBA")
        im.thumbnail((1600, 1600))
        arr = np.asarray(im).copy()
        if mode == "light":
            arr[..., :3] = 11  # ink #0b0b0b on white
        _logo_cache[key] = arr
    return _logo_cache[key]


def logo(fig, loc="upper right", height=0.32, pad=0.15, wordmark=False, alpha=0.9):
    """Stamp the EO mark (or the EXCESSIVE OVERKILL wordmark) in a figure corner.
    height and pad are in inches. loc: upper/lower + left/right. Call before save()."""
    arr = _logo_array("wordmark" if wordmark else "mark", _mode)
    fw, fh = fig.get_size_inches()
    h = height / fh
    w = height * arr.shape[1] / arr.shape[0] / fw
    x = pad / fw if "left" in loc else 1 - pad / fw - w
    y = pad / fh if "lower" in loc else 1 - pad / fh - h
    a = fig.add_axes([x, y, w, h], zorder=10)
    a.imshow(arr, alpha=alpha, interpolation="antialiased")
    a.axis("off")
    return a


def _is_3d(a):
    return hasattr(a, "get_zlabel")


def unlabeled(fig):
    """Names of axes in fig that are missing an x or y (or z) label. Colorbars count too."""
    missing = []
    for i, a in enumerate(fig.get_axes()):
        if not a.get_visible() or not a.axison:
            continue
        name = a.get_title(loc="left") or a.get_title() or f"axes {i}"
        need = [("x", a.get_xlabel()), ("y", a.get_ylabel())]
        if _is_3d(a):
            need.append(("z", a.get_zlabel()))
        if a.get_label() == "<colorbar>":  # only the long axis carries a label
            bb = a.get_position()
            need = [need[1]] if bb.height > bb.width else [need[0]]
        missing += [f"{name}: {k}" for k, v in need if not v.strip()]
    return missing


def save(fig, path, **kw):
    """Save after checking every axis is labeled."""
    missing = unlabeled(fig)
    if missing:
        raise ValueError("eo-style: label every axis before saving. Missing: " + ", ".join(missing))
    fig.savefig(path, **kw)
