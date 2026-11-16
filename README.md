<p align="center"><img src="assets/logo/eo-mark-on-light.svg" alt="EO" width="96"></p>

# eo-style-guide

The Excessive Overkill visual style for test and demo tooling: control panels, charts, 3D viewers, and bench reports. Dark instrument-panel layout, Roboto type, a terracotta accent, saturated blue/red/green chart colors, the EO mark on every page, and a few small motion touches (a spinner on anything running, a hover effect on each screen's main control, readouts that flash when they change).

It is packaged as a skill so AI coding agents apply it without being reminded, and as plain files you can use with no agent at all.

![Telemetry control panel](docs/panel.png)

| 3D arm with live joint control | Photo collage |
|---|---|
| ![3D arm](docs/arm-3d.png) | ![Collage](docs/collage.png) |

matplotlib output, dark mode:

![matplotlib example](matplotlib/example-dark.png)

## What's in it

| Path | What it is |
|---|---|
| `SKILL.md` | The rules an agent reads. Start here if you want to know what the style is. |
| `tokens.json` | Every color, font, size, and logo path in one place |
| `assets/logo/` | EO mark (white and on-light variants, SVG and PNG) and the EXCESSIVE OVERKILL wordmark |
| `web/` | `tokens.css` plus four small scripts: spinners and hover effects, SVG charts, a three.js viewport, an image collage |
| `examples/` | A telemetry panel, a 3D robot arm, a motion demo, and a photo collage |
| `matplotlib/` | Dark and light style sheets and `eo_style.py` |
| `fonts/` | Roboto, Roboto Condensed, and Roboto Mono (OFL), so matplotlib needs no font install |

To see the examples, serve the folder and open the panel page. The 3D and collage pages load ES modules, so opening the files directly won't work.

```sh
python -m http.server 8791
# then open http://localhost:8791/examples/panel.html
```

## Use it

### Claude Code

Clone it into your skills folder:

```sh
git clone https://github.com/ExcessiveOverkill/eo-style-guide.git ~/.claude/skills/eo-style
```

To make it apply every time, add this to `~/.claude/CLAUDE.md`:

```markdown
## Visual style

Before building or restyling any chart, plot, dashboard, control panel, status page, report, or tool UI, read `~/.claude/skills/eo-style/SKILL.md` and follow it. It overrides any default palette or generic look. If a project already has its own established theme, keep that theme.
```

On Windows the folder is `%USERPROFILE%\.claude\skills\eo-style`.

### Other agents (Codex, Cursor, anything that reads AGENTS.md)

Clone the repo anywhere and point your `AGENTS.md` at it:

```markdown
## Visual style

Before building or restyling any chart, plot, dashboard, control panel, report, or tool UI, read `~/eo-style-guide/SKILL.md` and follow it. Copy files from `~/eo-style-guide/web/` and start from the closest page in `~/eo-style-guide/examples/`.
```

For Cursor, the same text works as a rule in `.cursor/rules/eo-style.mdc` with `alwaysApply: true`.

### No agent

Web: link `web/tokens.css` and `web/ax-fx.js`, put `class="ax"` on `<body>`, and copy pieces from `examples/`. The CSS and JS keep the short `ax` prefix.

Python:

```python
import sys; sys.path.insert(0, "path/to/eo-style-guide/matplotlib")
import eo_style as eo
eo.use("dark")              # or "light" for reports and print
# ... plot, label every axis ...
eo.logo(fig)                # EO mark in the corner; wordmark=True for the full name
eo.save(fig, "out.png")     # refuses to save if any axis is unlabeled
```

## Branding

- The EO mark leads every page title (`h1`), drawn as a CSS mask in the accent color. `<span class="ax-logo"></span>` places it anywhere; add `ink` for the text color.
- The wordmark goes in the footer: `<footer class="ax-foot"><img class="ax-wordmark" src="assets/logo/eo-wordmark-white.png" alt="Excessive Overkill"></footer>`. Light mode inverts it automatically.
- matplotlib figures get the mark with `eo.logo(fig)`.

The logos are monochrome. The terracotta accent (`#e2683c` dark, `#c4532a` light) and the chart series colors are inherited defaults, not brand colors. To change them, edit `tokens.json` first, then copy the values into `web/tokens.css`, `matplotlib/eo_style.py`, and both `.mplstyle` files. Check new chart colors for colorblind separation before you commit to them (Anthropic's dataviz skill ships a `validate_palette.js` for this).

## Credits and license

Based on [alexchunlin/alex-style-guide](https://github.com/alexchunlin/alex-style-guide) (MIT). Code and docs are MIT, with both copyright lines kept in `LICENSE`. Fonts are under the SIL Open Font License (`fonts/OFL.txt`). The gripper mesh in `examples/assets/` is from Robotiq's ROS description package (BSD 3-Clause); see `examples/assets/ATTRIBUTION.md`. The EO logos and wordmark are not covered by the MIT license; all rights reserved by Excessive Overkill.
