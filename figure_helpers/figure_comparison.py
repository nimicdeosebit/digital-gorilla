"""The three-panel figure for the three-against-four-actor comparison.

Run:  python3 figure_comparison.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib as mpl
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "questions"))
from rq2_three_vs_four import CONDITIONS, action_batch, run_continuous  # noqa: E402

FIGDIR = Path(__file__).resolve().parent.parent / "figures"
FIGDIR.mkdir(exist_ok=True)
RESULTS = Path(__file__).resolve().parent.parent / "results" / "rq2_three_vs_four"
RESULTS.mkdir(parents=True, exist_ok=True)
CACHE = RESULTS / "comparison_cache.json"

# 4A and 3A-merged are the two conditions being compared; 3A-dropped is the
# control that shows what an unfair merge does, so it is drawn recessive.
STYLE = {
    "4A":          dict(colour="#8c5ec4", marker="o", ls="-",  lw=2.2,
                        label="four actors"),
    "3A-merged":   dict(colour="#1baf7a", marker="s", ls="-",  lw=2.2,
                        label="three, fair merge"),
    "3A-dropped":  dict(colour="#9a958a", marker="^", ls=":",  lw=1.6,
                        label="three, AI deleted (control)"),
}
INK, FAINT, RULE = "#23211c", "#6b665c", "#ddd8cd"
GAINS = [0, 1, 2, 3, 4, 6, 8, 10]
RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]
SEEDS = 150

mpl.rcParams.update({
    "font.size": 8.5,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": RULE,
    "axes.labelcolor": INK,
    "axes.labelsize": 8.5,
    "axes.titlesize": 9,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": FAINT,
    "ytick.color": FAINT,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "text.color": INK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def gather():
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    data = {"continuous": {}, "action_people": {}, "action_q2": {}}
    for cond in CONDITIONS:
        data["continuous"][cond] = [
            run_continuous(cond, gain=g)["people_vs_even"] for g in GAINS
        ]
        people, q2 = [], []
        for r in RATIOS:
            batch = action_batch(cond, n_seeds=SEEDS, check_magnitude=0.10 * r)
            people.append([batch["people_vs_even"], batch["people_vs_even_ci"]])
            q2.append(batch["quadrant_II"])
        data["action_people"][cond] = people
        data["action_q2"][cond] = q2
    CACHE.write_text(json.dumps(data, indent=1))
    return data


def tidy(ax, ylabel, xlabel, title, letter):
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", pad=16)
    ax.annotate(letter, xy=(0, 1), xycoords="axes fraction",
                xytext=(-30, 14), textcoords="offset points",
                fontsize=10, fontweight="bold", color=INK, va="center")
    ax.grid(axis="y", color=RULE, lw=0.7, alpha=0.9)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def main():
    data = gather()
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.5))

    # ---- (a) continuous ---------------------------------------------------
    ax = axes[0]
    for cond in CONDITIONS:
        s = STYLE[cond]
        ax.plot(GAINS, data["continuous"][cond], s["marker"] + s["ls"],
                color=s["colour"], lw=s["lw"], ms=4.5,
                markeredgecolor="white", markeredgewidth=0.8, label=s["label"])
    ax.axhline(1.0, color=FAINT, lw=0.9, ls="--", dashes=(5, 4))
    ax.annotate("an even share", xy=(10, 1.0), xytext=(-4, 5),
                textcoords="offset points", ha="right", fontsize=7.5,
                color=FAINT)
    ax.set_ylim(0.82, 1.02)
    ax.set_yticks([0.85, 0.90, 0.95, 1.00])
    ax.set_yticklabels(["0.85", "0.90", "0.95", "1.00"])
    tidy(ax, "People's share / even share", "epistemic spillover gain",
         "Contest only", "a")

    # ---- (b) action, People ----------------------------------------------
    ax = axes[1]
    for cond in CONDITIONS:
        s = STYLE[cond]
        ys = [p[0] for p in data["action_people"][cond]]
        es = [p[1] for p in data["action_people"][cond]]
        ax.errorbar(RATIOS, ys, yerr=es, fmt=s["marker"] + s["ls"],
                    color=s["colour"], lw=s["lw"], ms=4.5, capsize=2.5,
                    elinewidth=1, markeredgecolor="white",
                    markeredgewidth=0.8, label=s["label"])
    ax.axhline(1.0, color=FAINT, lw=0.9, ls="--", dashes=(5, 4))
    ax.annotate("an even share", xy=(1.0, 1.0), xytext=(2, 5),
                textcoords="offset points", ha="left", fontsize=7.5,
                color=FAINT)
    ax.set_ylim(0.6, 1.19)
    ax.set_yticks([0.6, 0.7, 0.8, 0.9, 1.0, 1.1])
    tidy(ax, "People's share / even share", "check strength / enhance strength",
         "With checks", "b")

    # ---- (c) action, quadrant II -----------------------------------------
    ax = axes[2]
    for cond in CONDITIONS:
        s = STYLE[cond]
        ax.plot(RATIOS, data["action_q2"][cond], s["marker"] + s["ls"],
                color=s["colour"], lw=s["lw"], ms=4.5,
                markeredgecolor="white", markeredgewidth=0.8, label=s["label"])
    ax.axhline(0.5, color=FAINT, lw=0.9, ls="--", dashes=(5, 4))
    ax.set_ylim(-0.03, 1.0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    tidy(ax, "runs reaching High Potential",
         "check strength / enhance strength", "Governance outcome", "c")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
               fontsize=8.5, bbox_to_anchor=(0.5, -0.015),
               handlelength=2.4, columnspacing=2.4)

    fig.subplots_adjust(left=0.065, right=0.99, top=0.84, bottom=0.26,
                        wspace=0.32)
    fig.savefig(FIGDIR / "fig8_three_vs_four.png", dpi=220)
    plt.close(fig)
    print("wrote figures/fig8_three_vs_four.png")


if __name__ == "__main__":
    main()
