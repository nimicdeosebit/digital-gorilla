"""Do the Table 7 policy levers change anything, and can they substitute for
raw check strength?

Three experiments:

  A. Each lever on its own, the pair the earlier prototype found did most of
     the work, and all five together -- all at the baseline check ratio of 1.0,
     where nothing reaches High Potential without intervention. This asks
     whether policy alone can fix the baseline.

  B. The check-strength sweep repeated with no levers, with the pair, and with
     all five. This asks whether policy LOWERS the threshold -- which is the
     research question, so it is the experiment that matters most.

  C. Lever strength swept continuously, to see whether the effect is
     proportional or has a floor.

Run:  python3 lever_experiments.py
"""

import csv
import json
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from action_based_sim.levers import ALL_LEVERS, LEVERS, STABILITY_ONLY
from action_based_sim.tables import MODALITIES
from rq1_check_threshold import ci95, crossing_point, run_batch, summarise

N_SEEDS = 200
ENHANCE = 0.10
RATIOS = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0)
RESULTS = Path(__file__).resolve().parent.parent / "results" / "rq4_levers"
RESULTS.mkdir(parents=True, exist_ok=True)
CACHE = RESULTS / "lever_cache.json"

CONDITIONS = [
    ("none", ()),
    *[(name, (name,)) for name in ALL_LEVERS],
    ("antitrust+audit", STABILITY_ONLY),
    ("all five", ALL_LEVERS),
]


def batch(lever_names, ratio=1.0, n_seeds=N_SEEDS, **kw):
    finals = run_batch(
        n_seeds=n_seeds,
        enhance_magnitude=ENHANCE,
        check_magnitude=ENHANCE * ratio,
        enhance_mode="per_capita",
        levers=list(lever_names),
        **kw,
    )
    row = summarise(finals, "")
    people = [
        mean(f["state"]["P"][m]["People"] for m in MODALITIES) for f in finals
    ]
    row["people"] = mean(people)
    row["people_ci"] = ci95(people)
    row["people_vs_even"] = row["people"] * len(finals[0]["state"]["P"]["Economic"])
    return row


def header(first="condition"):
    h = (f"{first:<18}{'aspiration':>18}{'People/even':>16}"
         f"{'High Potential':>16}{'quadrant':>8}")
    print(h)
    print("-" * len(h))


def line(label, r):
    print(f"{label:<18}"
          f"{r['aspiration']:>11.3f} +/-{r['aspiration_ci']:.3f}"
          f"{r['people_vs_even']:>16.3f}"
          f"{r['quadrant_II']:>15.0%}"
          f"{r['modal_quadrant'].split()[0]:>8}")


# ---------------------------------------------------------------- experiment A
def experiment_a():
    print("=" * 76)
    print("A -- each lever at the baseline check ratio of 1.0")
    print(f"({N_SEEDS} seeds; without levers nothing reaches High Potential here)")
    print("=" * 76)
    header()
    rows = {}
    for label, names in CONDITIONS:
        r = batch(names, ratio=1.0)
        rows[label] = r
        line(label, r)
    base = rows["none"]["people_vs_even"]
    print("\n  change in People's position against the no-lever baseline:")
    for label, _ in CONDITIONS[1:]:
        d = rows[label]["people_vs_even"] - base
        print(f"    {label:<18}{d:+.3f}")
    return rows


# ---------------------------------------------------------------- experiment B
def experiment_b():
    print()
    print("=" * 76)
    print("B -- does policy lower the check-strength threshold?")
    print("=" * 76)
    out = {}
    for label, names in (("none", ()),
                         ("antitrust+audit", STABILITY_ONLY),
                         ("all five", ALL_LEVERS)):
        rows = []
        for ratio in RATIOS:
            r = batch(names, ratio=ratio)
            r["label"] = f"{ratio:g}"
            rows.append(r)
        out[label] = rows
        print(f"\n{label}")
        header("ratio")
        for r in rows:
            line(r["label"], r)
        x = crossing_point(rows)
        print(f"  -> High Potential becomes the majority at ratio "
              + (f"~{x:.2f}" if x else "never in this range"))
    return out


# ---------------------------------------------------------------- experiment C
def experiment_c():
    print()
    print("=" * 76)
    print("C -- how hard does policy have to push? (all five, ratio 1.0)")
    print("=" * 76)
    header("strength")
    rows = []
    for strength in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0):
        r = batch(ALL_LEVERS, ratio=1.0, lever_strength=strength)
        r["label"] = f"{strength:g}"
        rows.append(r)
        line(r["label"], r)
    return rows


def save(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1))
    print(f"wrote {path}")


def main():
    a = experiment_a()
    b = experiment_b()
    c = experiment_c()

    CACHE.write_text(json.dumps({
        "a": {k: {kk: vv for kk, vv in v.items() if kk != "label"}
              for k, v in a.items()},
        "b": b,
        "c": c,
    }, indent=1))
    print(f"\nwrote {CACHE.name}")

    with open(RESULTS / "lever_results.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(next(iter(a.values())).keys()))
        w.writeheader()
        for label, row in a.items():
            row = dict(row)
            row["label"] = label
            w.writerow(row)
    print("wrote results/rq4_levers/lever_results.csv")


if __name__ == "__main__":
    main()
