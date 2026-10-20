"""Figures for the two new experiments.

Style follows continuous_sim/plots.py so all figures in the report match:
same palette, same size, same spines. Series are distinguished by marker
shape as well as colour, so they stay readable in greyscale print and for
colour-blind readers.

Run `python3 sweeps.py` first -- this reads the CSVs it writes.

Run:  python3 make_figures.py
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "continuous_sim"))

FIGDIR = Path(__file__).resolve().parent.parent / "figures"
FIGDIR.mkdir(exist_ok=True)
RQ1 = Path(__file__).resolve().parent.parent / "results" / "rq1_check_threshold"

BLUE, ORANGE = "#2a78d6", "#eb6834"
GREY = "#cccccc"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})


def save(fig, fname):
    fig.tight_layout()
    fig.savefig(FIGDIR / fname, dpi=200)
    plt.close(fig)
    print("wrote figures/" + fname)


def read(filename):
    path = Path(filename)
    if not path.is_absolute():
        path = RQ1 / path.name
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fig_check_threshold(fname="fig6_check_threshold.png"):
    """How strong must checking be before High Potential is the usual outcome?"""
    series = (
        (BLUE, "o", "sweep_check_per_donor.csv", "ENHANCE drains every actor"),
        (ORANGE, "s", "sweep_check_per_capita.csv", "ENHANCE worth one opponent"),
    )
    fig, ax = plt.subplots(figsize=(5, 3))
    for colour, marker, path, label in series:
        rows = read(path)
        xs = [float(r["label"]) for r in rows]
        ys = [float(r["quadrant_II"]) for r in rows]
        ax.plot(xs, ys, marker + "-", ms=4, color=colour, lw=2, label=label)
    ax.axhline(0.5, color=GREY, ls="--", lw=1)
    ax.axvline(1.0, color=GREY, ls=":", lw=1)
    ax.annotate("equal magnitudes\n(the original model)", xy=(1.1, 0.12),
                fontsize=7, color="#666666", va="center")
    ax.set(xlim=(0.5, 6), ylim=(0, 1),
           xlabel="check strength / enhance strength",
           ylabel="runs ending in High Potential")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    save(fig, fname)


def fig_actor_count(fname="fig7_actor_count.png"):
    """Does AI's presence change where People end up, as spillover strengthens?"""
    from variants import report, THREE, FOUR  # noqa: E402

    gains = [0, 1, 2, 3, 4, 6, 8, 10]
    fig, ax = plt.subplots(figsize=(5, 3))
    for colour, marker, actors, label in (
        (BLUE, "o", THREE, "without AI (3 actors)"),
        (ORANGE, "s", FOUR, "with AI (4 actors)"),
    ):
        ys = [report(actors, gain=g)["people_vs_even"] for g in gains]
        ax.plot(gains, ys, marker + "-", ms=4, color=colour, lw=2, label=label)
    ax.axhline(1.0, color=GREY, ls="--", lw=1)
    ax.set(xlabel="epistemic spillover gain",
           ylabel="People's share / even share")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    save(fig, fname)


if __name__ == "__main__":
    fig_check_threshold()
    fig_actor_count()
