"""Parameter sweeps for the action-based model.

Two experiments:

  1. CHECK STRENGTH.  How strong does checking have to be, relative to
     enhancing, before the system stops ending in quadrant I?

     In the original model ENHANCE and CHECK shared one magnitude. They are
     not symmetric moves -- ENHANCE draws from every other actor, CHECK from
     one -- so that shared magnitude made enhancing about three times the
     stronger move, and the 100%-quadrant-I result followed from it. Here the
     ratio is swept instead of assumed.

  2. ACTOR COUNT.  Does adding AI as a fourth actor change where the system
     ends up, compared with a People / State / Enterprises baseline?

Run:  python3 sweeps.py
"""

import csv
import math
import sys
from pathlib import Path
from collections import Counter
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from action_based_sim.config import SimulationConfig
from action_based_sim.environment import Environment
from action_based_sim.tables import ACTORS, MODALITIES

RESULTS = Path(__file__).resolve().parent.parent / "results"
RQ1 = RESULTS / "rq1_check_threshold"
RQ2 = RESULTS / "rq2_three_vs_four"

N_SEEDS = 200
ENHANCE_MAGNITUDE = 0.10
RATIOS = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0)
THREE_ACTORS = ["People", "State", "Enterprises"]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def ci95(values):
    """Half-width of a 95% confidence interval for the mean.

    Normal approximation, which is fine at n = 200.
    """
    if len(values) < 2:
        return 0.0
    return 1.96 * stdev(values) / math.sqrt(len(values))


def run_batch(n_seeds=N_SEEDS, **config_kwargs):
    """Run n_seeds simulations and return the final record of each."""
    finals = []
    for seed in range(n_seeds):
        config = SimulationConfig(seed=seed, **config_kwargs)
        final = Environment(config).run()[-1]
        finals.append(final)
    return finals


def summarise(finals, label):
    asp = [f["aspiration"] for f in finals]
    stab = [f["stability"] for f in finals]
    quads = Counter(f["quadrant"] for f in finals)
    top_quadrant, top_count = quads.most_common(1)[0]
    return {
        "label": label,
        "n": len(finals),
        "aspiration": mean(asp),
        "aspiration_ci": ci95(asp),
        "stability": mean(stab),
        "stability_ci": ci95(stab),
        "quadrant_I": quads.get("I - Surviving not Thriving", 0) / len(finals),
        "quadrant_II": quads.get("II - High Potential", 0) / len(finals),
        "quadrant_III": quads.get("III - Creative Chaos", 0) / len(finals),
        "quadrant_IV": quads.get("IV - Fragile Collapse", 0) / len(finals),
        "modal_quadrant": top_quadrant,
        "modal_share": top_count / len(finals),
    }


def print_table(rows, first_col="ratio"):
    header = (
        f"{first_col:>10}  {'aspiration':>18}  {'stability':>18}  "
        f"{'I':>6}{'II':>6}{'III':>6}{'IV':>6}"
    )
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['label']:>10}  "
            f"{r['aspiration']:.3f} +/- {r['aspiration_ci']:.3f}  "
            f"{r['stability']:.3f} +/- {r['stability_ci']:.3f}  "
            f"{r['quadrant_I']:>6.0%}{r['quadrant_II']:>6.0%}"
            f"{r['quadrant_III']:>6.0%}{r['quadrant_IV']:>6.0%}"
        )


def crossing_point(rows, key="quadrant_II", level=0.5):
    """Linearly interpolate the ratio at which `key` first crosses `level`."""
    for prev, cur in zip(rows, rows[1:]):
        if prev[key] < level <= cur[key]:
            x0, y0 = float(prev["label"]), prev[key]
            x1, y1 = float(cur["label"]), cur[key]
            if y1 == y0:
                return x1
            return x0 + (level - y0) * (x1 - x0) / (y1 - y0)
    return None


# ---------------------------------------------------------------------------
# experiment 1: check strength
# ---------------------------------------------------------------------------
def sweep_check_strength(enhance_mode="per_donor"):
    rows = []
    for ratio in RATIOS:
        finals = run_batch(
            enhance_magnitude=ENHANCE_MAGNITUDE,
            check_magnitude=ENHANCE_MAGNITUDE * ratio,
            enhance_mode=enhance_mode,
        )
        rows.append(summarise(finals, f"{ratio:g}"))
    return rows


# ---------------------------------------------------------------------------
# experiment 2: actor count
# ---------------------------------------------------------------------------
def compare_actor_counts(enhance_mode="per_capita", check_ratio=1.0):
    rows = []
    for label, actors in (("3 actors", THREE_ACTORS), ("4 actors", list(ACTORS))):
        finals = run_batch(
            actors=actors,
            enhance_magnitude=ENHANCE_MAGNITUDE,
            check_magnitude=ENHANCE_MAGNITUDE * check_ratio,
            enhance_mode=enhance_mode,
        )
        row = summarise(finals, label)
        row["people_share"] = mean(
            mean(f["state"]["P"][m]["People"] for m in MODALITIES) for f in finals
        )
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# experiment 3: does AI move the threshold itself?
# ---------------------------------------------------------------------------
def threshold_by_actor_count(enhance_mode="per_capita"):
    """Sweep check strength separately for three and four actors.

    Comparing the two crossing points asks the project's original question in
    a form the model can actually answer: not "does AI change the end state"
    (the normalised aspiration metric is not comparable across actor counts)
    but "does AI change how strong the checks have to be".
    """
    out = {}
    for label, actors in (("3 actors", THREE_ACTORS), ("4 actors", list(ACTORS))):
        rows = []
        for ratio in RATIOS:
            finals = run_batch(
                actors=actors,
                enhance_magnitude=ENHANCE_MAGNITUDE,
                check_magnitude=ENHANCE_MAGNITUDE * ratio,
                enhance_mode=enhance_mode,
            )
            row = summarise(finals, f"{ratio:g}")
            shares = [
                mean(f["state"]["P"][m]["People"] for m in MODALITIES) for f in finals
            ]
            row["people_share"] = mean(shares)
            row["people_share_ci"] = ci95(shares)
            rows.append(row)
        out[label] = rows
    return out


def save_rows(rows, filename):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {filename}")


def main():
    print("=" * 78)
    print("EXPERIMENT 1a -- check strength, ENHANCE drawing from every actor")
    print(f"({N_SEEDS} seeds per point; ratio = check magnitude / enhance magnitude)")
    print("=" * 78)
    per_donor = sweep_check_strength("per_donor")
    print_table(per_donor)
    x = crossing_point(per_donor)
    print(
        f"\nquadrant II becomes the majority outcome at ratio ~ {x:.2f}"
        if x
        else "\nquadrant II never becomes the majority outcome in this range"
    )

    print()
    print("=" * 78)
    print("EXPERIMENT 1b -- check strength, ENHANCE worth one average opponent")
    print("=" * 78)
    per_capita = sweep_check_strength("per_capita")
    print_table(per_capita)
    x = crossing_point(per_capita)
    print(
        f"\nquadrant II becomes the majority outcome at ratio ~ {x:.2f}"
        if x
        else "\nquadrant II never becomes the majority outcome in this range"
    )

    print()
    print("=" * 78)
    print("EXPERIMENT 2 -- does AI as a fourth actor change the outcome?")
    print("=" * 78)
    counts = compare_actor_counts()
    print_table(counts, first_col="run")
    for r in counts:
        print(f"  {r['label']}: People hold {r['people_share']:.3f} on average")

    print()
    print("=" * 78)
    print("EXPERIMENT 3 -- does AI change how strong the checks have to be?")
    print("=" * 78)
    by_count = threshold_by_actor_count()
    thresholds = {}
    for label, rows in by_count.items():
        print(f"\n{label}")
        print_table(rows)
        for r in rows:
            r["actors"] = label
        thresholds[label] = crossing_point(rows)
    print()
    for label, x in thresholds.items():
        print(
            f"  {label}: quadrant II becomes the majority at ratio ~ "
            + (f"{x:.2f}" if x else "never in this range")
        )

    save_rows(per_donor, RQ1 / "sweep_check_per_donor.csv")
    save_rows(per_capita, RQ1 / "sweep_check_per_capita.csv")
    save_rows(counts, RQ2 / "sweep_actor_count.csv")
    save_rows(
        [r for rows in by_count.values() for r in rows],
        RQ2 / "sweep_threshold_by_actors.csv",
    )


if __name__ == "__main__":
    main()
