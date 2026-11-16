"""Renders example-dark.png and example-light.png to check the styles."""
import math, random
import matplotlib.pyplot as plt
import eo_style as eo

random.seed(7)
t = [i / 2 for i in range(120)]
joints = {f"J{k+1}": [1.2 + k * .55 + math.sin(i / (9 + k * 3) + k) * (.5 + k * .1) + (random.random() - .5) * .25
                      + (.02 * (i - 80) if k == 2 and i > 80 else 0) for i in range(120)] for k in range(4)}

for mode in ("dark", "light"):
    eo.use(mode)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1.6, 1]})
    for name, v in joints.items():
        a.plot(t, v, label=name)
    a.set_ylim(0, 4)
    a.set_xlabel("Time, s")
    a.set_ylabel("Phase current, A")
    eo.label_lines(a)
    eo.title(a, "Joint current", "Phase current per joint")
    eo.bars(b, ["Pick", "Place", "Home", "Wave", "Reach", "Stow"], [412, 388, 205, 296, 451, 174],
            highlight="Reach", xlabel="Cycle time, ms", ylabel="Test")
    eo.title(b, "Cycle time by test", "Median of 20 cycles")
    fig.tight_layout()
    eo.logo(fig, "upper right")
    eo.save(fig, f"example-{mode}.png")

# The label check in action
fig, a = plt.subplots()
a.plot([0, 1], [0, 1])
try:
    eo.save(fig, "/tmp/should-not-exist.png")
except ValueError as e:
    print(e)
