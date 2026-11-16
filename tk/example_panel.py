"""Telemetry panel in the EO style, tkinter version of examples/panel.html.

    python tk/example_panel.py            # dark
    python tk/example_panel.py light
    python tk/example_panel.py dark shot.png   # save a screenshot after 3 s and exit (Windows)
"""
import math
import random
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eo_tk as eo

mode = sys.argv[1] if len(sys.argv) > 1 else "dark"
shot = sys.argv[2] if len(sys.argv) > 2 else None

root = tk.Tk()
root.title("Arm bench 02")
root.geometry(f"{eo.px(1180)}x{eo.px(860)}")
eo.apply(root, mode)
C = eo.colors()
mpl_eo = eo.use_matplotlib()

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure

page = tk.Frame(root, bg=C["bg"])
page.pack(fill="both", expand=True, padx=eo.px(28), pady=(eo.px(22), eo.px(14)))

# ── Header ─────────────────────────────────────────────────────────
head = eo.Header(page, "Arm bench 02", ["run 2026-10-15-a", "fw 0.9.4", "rev C"])
head.pack(fill="x")
live = eo.Status(head.meta, "Live", "live"); live.pack(side="left")
start = eo.button(head.controls, "Start run", kind="primary")
eo.button(head.controls, "Export CSV").pack(side="right", padx=(0, eo.px(8)))
start.pack(side="right", padx=(eo.px(8), 0))

# ── Tiles ──────────────────────────────────────────────────────────
tiles = tk.Frame(page, bg=C["bg"]); tiles.pack(fill="x", pady=(eo.px(20), eo.px(8)))
spec = [("Bus voltage", "V", 24.13, 2), ("Loop rate", "Hz", 998, 0), ("Peak motor temp", "°C", 61.4, 1), ("Faults this run", "", 0, 0)]
tile = {}
for i, (name, unit, v, d) in enumerate(spec):
    t = eo.Tile(tiles, name, unit); t.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else eo.px(8), 0))
    t.set(v, d); tile[name] = (t, d)
    tiles.columnconfigure(i, weight=1, uniform="t")
tile["Bus voltage"][0].sub("min 23.80 · max 24.31")
tile["Loop rate"][0].sub("target 1000")
tile["Peak motor temp"][0].sub("J3 above 60", "warning")
tile["Faults this run"][0].sub("Nominal", "good")

# ── Chart + controls ───────────────────────────────────────────────
mid = tk.Frame(page, bg=C["bg"]); mid.pack(fill="both", expand=True, pady=(0, eo.px(8)))
mid.columnconfigure(0, weight=3); mid.columnconfigure(1, weight=1); mid.rowconfigure(0, weight=1)

chart_panel = eo.Panel(mid, "Joint current", "Phase current per joint over the last 60 s")
chart_panel.grid(row=0, column=0, sticky="nsew", padx=(0, eo.px(8)))
fig = Figure(figsize=(6, 2.6), dpi=100)
a = fig.add_subplot(111)
canvas = eo.embed_figure(chart_panel.body, fig)
canvas.get_tk_widget().pack(fill="both", expand=True)
N = 120
data = {f"J{k+1}": [1.2 + k * .55 + math.sin(i / (9 + k * 3) + k) * (.5 + k * .1) + (random.random() - .5) * .25 for i in range(N)] for k in range(4)}


def draw():
    a.clear()
    t = [i / 2 for i in range(N)]
    for name, ys in data.items():
        a.plot(t, ys, label=name)
    a.set_ylim(0, 4); a.set_xlim(0, 60)
    a.set_xlabel("Time, s"); a.set_ylabel("Phase current, A")
    mpl_eo.label_lines(a)
    fig.subplots_adjust(left=0.09, right=0.93, top=0.95, bottom=0.2)
    canvas.draw_idle()


ctl = eo.Panel(mid, "Test setup", "Applies to the next run")
ctl.grid(row=0, column=1, sticky="nsew")
b = ctl.body
eo.label(b, "Profile", "label").pack(anchor="w")
cb = ttk.Combobox(b, values=["Pick and place", "Wave", "Home and stow"], state="readonly"); cb.current(0)
cb.pack(fill="x", pady=(eo.px(4), eo.px(10)))
eo.label(b, "Cycles", "label").pack(anchor="w")
ent = ttk.Entry(b); ent.insert(0, "20"); ent.pack(fill="x", pady=(eo.px(4), eo.px(10)))
eo.label(b, "Speed", "label").pack(anchor="w")
sc = ttk.Scale(b, from_=0, to=100, value=60); sc.pack(fill="x", pady=(eo.px(4), eo.px(10)))
ttk.Checkbutton(b, text="Log to CSV").pack(anchor="w")
ttk.Checkbutton(b, text="Stop on fault").pack(anchor="w", pady=(0, eo.px(10)))
prog = ttk.Progressbar(b, maximum=100, value=0); prog.pack(fill="x", pady=(0, eo.px(6)))
row = tk.Frame(b, bg=C["bg"]); row.pack(fill="x")
spin = eo.Spinner(row); spin.pack(side="left", padx=(0, eo.px(8)))
state = ttk.Label(row, text="Idle", style="Meta.TLabel"); state.pack(side="left")

# ── Event log ──────────────────────────────────────────────────────
log = eo.Panel(page, "Event log", "Most recent first")
log.pack(fill="x")
tbl = eo.Table(log.body, [("time", "Time", 130, "w"), ("src", "Source", 90, "w"), ("evt", "Event", 380, "w"),
                          ("status", "Status", 110, "w"), ("val", "Value", 110, "e")], height=4)
tbl.pack(fill="x")
for r, st in [(("13:42:07.114", "J3", "Winding temp above soft limit", "■ Warning", "61.4 °C"), "warning"),
              (("13:41:52.880", "CAN", "Heartbeat resumed on node 0x12", "■ OK", "3 ms"), "good"),
              (("13:41:52.401", "CAN", "Heartbeat missed on node 0x12", "■ Critical", "480 ms"), "critical"),
              (("13:40:10.002", "Host", "Run started", "■ Idle", "-"), "muted")]:
    tbl.add(r, st)

eo.Footer(page, "bench panel template").pack(fill="x", side="bottom", pady=(eo.px(16), 0))

# ── Behavior ───────────────────────────────────────────────────────
running = {"on": False, "n": 0}


def finish():
    running["on"] = False
    eo.busy(start, False); spin.stop(); state.configure(text="Idle")
    prog.configure(value=0)


def step():
    if not running["on"]:
        return
    running["n"] += 1
    prog.configure(value=running["n"] * 100 / 60)
    if running["n"] >= 60:
        finish()
        return
    root.after(100, step)


def on_start():
    running.update(on=True, n=0)
    eo.busy(start, True, "Running"); spin.start(); state.configure(text="Run in progress")
    step()


start.configure(command=on_start)


def tick():
    for k in data:
        data[k] = data[k][1:] + [data[k][-1] + (random.random() - .5) * .3]
        data[k][-1] = min(3.9, max(0.1, data[k][-1]))
    draw()
    tile["Bus voltage"][0].set(24.1 + random.random() * .1, 2)
    tile["Loop rate"][0].set(996 + random.random() * 4, 0)
    root.after(1500, tick)


draw()
root.after(1500, tick)

if shot:
    def snap():
        from PIL import ImageGrab
        root.update_idletasks(); root.update()
        x, y, w, h = root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height()
        ImageGrab.grab(bbox=(x, y, x + w, y + h), all_screens=True).save(shot)
        root.destroy()
    root.after(300, on_start)
    root.after(2500, snap)

root.mainloop()
