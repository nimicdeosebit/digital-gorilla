"""Figure for the policy-lever results.

Two panels:
  (a) who each lever actually moves power to, as a change against the
      no-lever baseline
  (b) the check-strength sweep with and without levers, showing that policy
      does not lower the threshold

Run:  python3 figure_levers.py   (after lever_experiments.py)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from statistics import mean

import matplotlib as mpl
import matplotlib.pyplot as plt

from action_based_sim.levers import ALL_LEVERS, LEVERS, STABILITY_ONLY
from action_based_sim.tables import ACTORS, MODALITIES

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "questions"))
from rq1_check_threshold import run_batch  # noqa: E402

FIGDIR = Path(__file__).resolve().parent.parent / "figures"
FIGDIR.mkdir(exist_ok=True)
RESULTS = Path(__file__).resolve().parent.parent / "results" / "rq4_levers"
RESULTS.mkdir(parents=True, exist_ok=True)
CACHE = RESULTS / "lever_cache.json"
SHARES = RESULTS / "lever_shares.json"

PEOPLE, STATE, ENT, AI = "#2a78d6", "#eb6834", "#1baf7a", "#8c5ec4"
ACTOR_COLOUR = {"People": PEOPLE, "State": STATE, "Enterprises": ENT, "AI": AI}
INK, FAINT, RULE = "#23211c", "#6b665c", "#ddd8cd"

mpl.rcParams.update({
    "font.size": 8.5, "font.family": "DejaVu Sans",
    "axes.edgecolor": RULE, "axes.labelcolor": INK, "axes.labelsize": 8.5,
    "axes.titlesize": 9, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": FAINT, "ytick.color": FAINT,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "text.color": INK, "figure.facecolor": "white", "axes.facecolor": "white",
})


def gather_shares():
    if SHARES.exists():
        return json.loads(SHARES.read_text())

    def shares(levers):
        f = run_batch(n_seeds=200, enhance_magnitude=.10, check_magnitude=.10,
                      enhance_mode="per_capita", levers=list(levers))
        return {a: mean(mean(x["state"]["P"][m][a] for m in MODALITIES)
                        for x in f) for a in ACTORS}

    base = shares([])
    out = {"baseline": base, "levers": {}}
    for lever in ALL_LEVERS:
        s = shares([lever])
        out["levers"][lever] = {a: s[a] - base[a] for a in ACTORS}
    SHARES.write_text(json.dumps(out, indent=1))
    return out


def main():
    data = json.loads(CACHE.read_text())
    sh = gather_shares()

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.6),
                             gridspec_kw={"width_ratios": [1.25, 1]})

    # ---- (a) who gains -----------------------------------------------------
    ax = axes[0]
    order = ["civic_capacity", "antitrust", "data_rights", "ai_liability",
             "audit_transparency"]
    ys = range(len(order))
    width = 0.19
    for k, actor in enumerate(ACTORS):
        offs = [(y + (k - 1.5) * width) for y in ys]
        vals = [sh["levers"][lv][actor] for lv in order]
        ax.barh(offs, vals, height=width, color=ACTOR_COLOUR[actor],
                label=actor, edgecolor="white", linewidth=0.5)
    ax.axvline(0, color=FAINT, lw=1)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([LEVERS[k]["label"].replace(" and ", " &\n")
                        for k in order], fontsize=7.5)
    ax.set_xlabel("change in mean share against no lever")
    ax.set_title("Who each lever moves power to", loc="left", pad=14)
    ax.annotate("a", xy=(0, 1), xycoords="axes fraction",
                xytext=(-78, 12), textcoords="offset points",
                fontsize=10, fontweight="bold", color=INK)
    ax.grid(axis="x", color=RULE, lw=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.legend(frameon=False, fontsize=7.5, ncol=4, loc="lower center",
              bbox_to_anchor=(0.5, -0.42), columnspacing=1.2,
              handlelength=1.1, handletextpad=0.5)

    # ---- (b) threshold -----------------------------------------------------
    ax = axes[1]
    series = (("none", "#9a958a", "^", ":", "no levers"),
              ("antitrust+audit", "#eb6834", "s", "-", "antitrust + audit"),
              ("all five", "#1baf7a", "o", "-", "all five levers"))
    for key, colour, marker, ls, label in series:
        rows = data["b"][key]
        xs = [float(r["label"]) for r in rows]
        ys2 = [r["quadrant_II"] for r in rows]
        ax.plot(xs, ys2, marker + ls, color=colour, lw=2, ms=4.5,
                markeredgecolor="white", markeredgewidth=0.8, label=label)
    ax.axhline(0.5, color=FAINT, lw=0.9, ls="--", dashes=(5, 4))
    ax.set_xlim(1, 6)
    ax.set_ylim(-0.03, 0.9)
    ax.set_yticks([0, 0.25, 0.5, 0.75])
    ax.set_yticklabels(["0%", "25%", "50%", "75%"])
    ax.set_xlabel("check strength / enhance strength")
    ax.set_ylabel("runs reaching High Potential")
    ax.set_title("Policy does not lower the threshold", loc="left", pad=14)
    ax.annotate("b", xy=(0, 1), xycoords="axes fraction",
                xytext=(-44, 12), textcoords="offset points",
                fontsize=10, fontweight="bold", color=INK)
    ax.grid(axis="y", color=RULE, lw=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")

    fig.subplots_adjust(left=0.175, right=0.985, top=0.85, bottom=0.26,
                        wspace=0.42)
    fig.savefig(FIGDIR / "fig9_levers.png", dpi=220)
    plt.close(fig)
    print("wrote figures/fig9_levers.png")


if __name__ == "__main__":
    main()
