---
name: eo-style
description: Excessive Overkill (EO) house style for anything with a chart, graph, plot, dashboard, control panel, demo panel, 3D viewer, image gallery or collage, status page, bench report, HTML artifact, or web UI for a tool. Use it every time you build or restyle one of these, in any language or library (plain HTML/SVG, matplotlib, three.js, uPlot, Chart.js, React), even if the user doesn't mention style. It overrides the dataviz skill's palette and mark defaults and any generic "clean modern" look.
---

# eo-style

Black instrument-panel UI: white text and highlights, dark gray rules, and saturated Swiss-poster chart colors as the only hue. Roboto type, square corners, flat surfaces, white as the accent on live readouts and the one main action, dark gray for separation. The interface feels alive: things that are working show a spinner, the main control reacts when the mouse comes near it, and numbers flash when they change.

Everything lives in this skill's folder, the directory that holds this SKILL.md (call it `<skill>` below):

| File | Use it for |
|---|---|
| `tokens.json` | Source of truth for every color, font, and size |
| `web/tokens.css` | CSS variables (`--ax-*`) and classes: `.ax-panel`, `.ax-tile`, `.ax-btn`, `.ax-spin`, `.ax-status`, viewport and collage styles |
| `web/ax-fx.js` | `axBusy()` spinners, `data-fx` hover effects, `axSet()` value flash |
| `web/ax-charts.js` | Dependency-free SVG line and bar charts with axis titles, tooltips, direct labels |
| `web/ax-three.js` | `axScene()`: styled three.js viewport with orbit, hover picking, tooltips, STL/GLB loading |
| `web/ax-collage.js` | `axCollage()`: tilted 3D photo wall with hover lift and lightbox |
| `examples/panel.html` | Telemetry control panel. Start here for dashboards. |
| `examples/arm-3d.html` | 3D robot arm with joint sliders, live trace, loaded STL. Start here for 3D. |
| `examples/collage.html` | Image collage. Start here for galleries and project walls. |
| `examples/fx.html` | Every hover effect and spinner on one page |
| `matplotlib/eo_style.py` | `use()`, `title()`, `label_lines()`, `bars()`, `ref_line()`, `logo()`, `save()` |
| `assets/logo/` | EO mark (white SVG/PNG, black-disc SVG for light backgrounds, black PNG) and the EXCESSIVE OVERKILL wordmark (white PNG) |
| `tk/eo_tk.py` | tkinter/ttk theme and widgets: `apply()`, `Header`, `Panel`, `Tile`, `Status`, `Spinner`, `Table`, `Footer`, `button()`, `busy()`, `embed_figure()` |
| `tk/example_panel.py` | Telemetry panel in Tk. Start here for Python desktop GUIs. |
| `fonts/` | Roboto TTFs, registered automatically by `eo_style.py` |

## Branding

Brand is Excessive Overkill: the circular **EO** stencil mark and the **EXCESSIVE OVERKILL** stencil wordmark, both in `assets/logo/`.

- Every page and every saved figure carries the brand, quietly. Web: the mark leads the `<h1>` (automatic) and a `.ax-foot` footer holds the wordmark. matplotlib: call `eo.logo(fig)` before `eo.save()`.
- On dark backgrounds use the white files. On light backgrounds use `eo-mark-on-light.svg` or the black PNG; the CSS wordmark inverts itself in `data-mode="light"`.
- Use `.ax-logo` (accent) or `.ax-logo.ink` for the mark at other sizes. It is a CSS mask, so it takes any color. Don't recolor it with series colors, don't add a shadow or outline, don't stretch it.
- The logo is the only place stencil letterforms appear. UI type stays Roboto.
- Keep clear space around the mark of at least half its height.

## Pick the mode

Dark for anything people look at on a screen: control panels, live dashboards, demos, tool UIs. Light (`data-mode="light"` on `<html>`, or `use("light")`) for PDFs, printed bench notes, and slides. Pick by the output; don't ask.

## How to apply it

HTML: start from the closest file in `examples/`. Link the files in `web/` with relative paths, or inline them when the output must be one file. Put `class="ax"` on `<body>` and load the fonts:

```html
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Roboto+Condensed:wght@500;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

React or an existing app: map the `--ax-*` variables into the app's theme and port the behaviors in `ax-fx.js`. Keep the rules below even if class names change.

tkinter (the default for Python test and demo GUIs):

```python
import sys; sys.path.insert(0, "<skill>/tk")
import eo_tk as eo
eo.apply(root, "dark")   # then Header, Panel, Tile, Footer; plain ttk widgets are themed automatically
```

Use `eo_tk` widgets rather than ad-hoc colors: no hardcoded hex, no default gray Tk look, no `tk.Button` where `eo.button` fits. Charts in Tk are matplotlib via `eo.use_matplotlib()` and `eo.embed_figure()`. Tk can't letter-space or draw row rules, so titles are uppercase only and tables rely on row hover.

matplotlib:

```python
import sys; sys.path.insert(0, "<skill>/matplotlib")
import eo_style as eo
eo.use("dark")                       # "light" for reports
...
a.set_xlabel("Time, s"); a.set_ylabel("Phase current, A")
eo.label_lines(a); eo.title(a, "Joint current", "Phase current per joint")
eo.save(fig, "current.png")          # raises if any axis is unlabeled
```

## Rules

Type
- Roboto Condensed (500/700) for titles: uppercase, 0.06 to 0.1 em tracking.
- Roboto Mono for numbers, readouts, tick labels, tables, timestamps, buttons, and small uppercase labels.
- Roboto for prose, captions, and axis titles. No Inter, no JetBrains Mono, no serif.
- Every number a reader compares is in Roboto Mono: readouts, ticks, table values, timestamps, coordinates. `ax-fx.js` adds class `ax-n` to numeric table cells automatically; `eo_style.use()` makes every matplotlib tick label mono. Numbers inside sentences stay in Roboto with tabular figures.
- Numbers use tabular figures. Units sit after the value in smaller muted text: `24.12 V`.

Shape
- Corner radius 0 everywhere. The spinner is the one round thing.
- 1 px borders. No drop shadows on panels, no gradients on surfaces, no glassmorphism.
- Panels and tiles get the 8 px white corner bracket on the top-left (`.ax-panel` does this).
- Page title starts with the EO mark in the accent color (`.ax h1::before` does this).

Color
- Brand colors are black, white, and dark gray. Dark mode: `bg #000000`, `panel #0a0a0a`, separators `#2b2b2b` (strong `#3d3d3d`), text `#ffffff`, secondary text `#8f8f8f`. The `accent` is white (`#ffffff`; black `#000000` in light mode) and goes on live readout values, the main action button (white fill, black text), focus rings, spinners, brackets, and hover glows. Not in charts.
- No hue outside charts and status. Separation comes from dark gray 1 px lines, never from tinted fills.
- Categorical series use this order and never cycle. Dark: `#2f62e8 #e03a2f #0f9a66 #a45ee0 #1a9cc0 #d9539a`. Light: `#1f4fd8 #e3241b #0f8a5f #8a3fd1 #0e7fa3 #c2307a`. A 7th series folds into "Other" or a second chart.
- A series keeps its color when filters hide other series.
- Status colors (`good`, `warning`, `critical`, `off`) only mean state. Always pair the square with a word: `■ Warning`.
- Text is `ink` or `muted`, never a series color.
- Adding a new color? Run the dataviz skill's `scripts/validate_palette.js` against `#0a0a0a` (dark) or `#ffffff` (light) and fix any FAIL.

Charts
- Every axis on every chart has a title: the quantity, then the unit after a comma. `Phase current, A`. `Time before now, s`. Category axes too (`Test`). 3D scenes label their X/Y/Z triad with units. `ax-charts.js` draws a red warning if a label is missing; `eo_style.save()` refuses to save.
- Lines 2.5 px (2.0 in matplotlib), round joins, no area fill, no markers unless points are sparse.
- Bars are flat, square, one color (`s1` blue). Color one bar `s2` red only to call it out, and say why in the caption.
- Horizontal bars when labels are words. Value printed at the bar end.
- Gridlines dashed `2 4`, y-only for line charts, x-only for horizontal bars. Baseline axis solid.
- Label up to 4 lines directly at their right end, and keep the square-swatch legend above the plot.
- Threshold lines are dashed in a status color with a short label: `soft limit 60°`.
- Every HTML chart gets a hover tooltip (crosshair for lines, per-bar for bars).
- One y-axis per chart. Two units means two charts.
- A single number is a tile (`.ax-tile` + `.ax-value`), not a chart.

Layout
- Header: title and run metadata (run id, firmware, rev, live status) on the left, controls on the right, one rule under it.
- A row of tiles, then charts or a 3D view in a grid with 8 px gaps, then tables, then notes.
- Each chart has an uppercase title, then a one-line muted caption.
- Tables: uppercase mono headers, 1 px row rules, numbers right-aligned, timestamps muted with milliseconds, a faint white row hover.

## Personality defaults (always on, no one has to ask)

- Spinner wherever something is running or loading. Buttons that start work swap to `◌ Running` and disable until done (`axBusy(btn, true, 'Homing')`). Panels waiting on data dim and show the large spinner with a one-word label (`data-busy="Fetching cycles"`). 3D models show it while they load (`axScene().load()` does this). Never leave a blank panel or a frozen button.
- The main feature on each screen gets a hover effect via `data-fx`. There are three. Pick the one that matches what it does: `sparks` for start, run, launch, enable motor, power; `ripple` for connect, scan, capture, sync; `orbit` for record, stream, auto. One per screen, two at most. Secondary buttons get only the border-color change.
- Live readouts tween when they change and flash a faint white highlight (`axSet(el, value, { digits })`).
- A live data stream shows a breathing green square: `<span class="ax-status live">Live</span>`.
- Buttons press down 1 px on click. Table rows tint on hover. Clicking an object in a 3D view jumps to its control.
- Empty states say what's missing in one muted line ("No runs yet. Start one above."), never a blank box.
- Everything honors `prefers-reduced-motion` (the helpers already do).

## 3D and collage

Use `axScene()` for any 3D view: robot poses, CAD previews, sensor point clouds, workspace layouts. It gives flat dark solids with thin ink edges like a CAD drawing, a dashed floor grid, a labeled XYZ triad, idle auto-rotate that stops when touched, a camera dolly-in on load, and a white glow plus tooltip on hover. Build parts with `v.solid(geometry)`, make them interactive with `v.pickable(mesh, infoFnOrHtml, onClick)`, load real CAD with `await v.load('part.stl', { size, parent })`. Connect 3D objects to the panel both ways: sliders move the model, clicking the model focuses the slider. See `examples/arm-3d.html`.

Use `axCollage()` for project galleries, build logs, and photo walls. Photos sit desaturated on a tilted wall that leans toward the mouse; the hovered photo lifts out in full color with its caption and corner bracket; click opens a lightbox. Give big hero shots `span: [2, 2]`. See `examples/collage.html`.

Both need a page served over HTTP (`python3 -m http.server`) because they load modules and assets.

## Words

- Plain, specific prose: first person for bench notes ("I swapped the board"), real numbers instead of adjectives, no em dashes.
- No emoji in UI or reports. Buttons say the action: "Start run", "Enable motor", "Export CSV".

## Things that make it look AI-made (avoid)

Rounded cards with soft shadows, purple or indigo gradients, cream backgrounds, Inter everywhere, emoji section headers, "Overview / Insights / Summary" headings, pill badges, a rainbow of colors on single-series bars, donut charts for close values, unlabeled axes, a centered hero number with a sparkline under it on every card, and glossy 3D with default blue-gray materials and no edges.

## Library snippets

uPlot:

```js
const css = v => getComputedStyle(document.documentElement).getPropertyValue('--ax-' + v).trim();
const axis = label => ({ label, labelFont: "11px Roboto", font: "11px 'Roboto Mono'", stroke: css('muted'),
  grid: { stroke: css('grid'), dash: [2, 4], width: 1 }, ticks: { show: false } });
const opts = { axes: [axis('Time, s'), axis('Phase current, A')],
  series: [{}, ...names.map((label, i) => ({ label, stroke: css('s' + (i + 1)), width: 2.5 }))] };
```

Chart.js:

```js
Chart.defaults.font.family = "'Roboto Mono', monospace";
Chart.defaults.color = css('muted');
Chart.defaults.borderColor = css('grid');
Chart.defaults.elements.line.borderWidth = 2.5;
Chart.defaults.elements.line.tension = 0;
Chart.defaults.elements.point.radius = 0;
Chart.defaults.elements.bar.borderRadius = 0;
Chart.defaults.plugins.legend.labels.boxWidth = 10;
// and on every chart: scales.x.title = { display: true, text: 'Time, s' }, same for y
```
