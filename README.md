# The Digital Gorilla: an agent-based model

An agent-based operationalisation of Parra-Orlandoni, Schnyder and Mallet,
*The Digital Gorilla: Rebalancing Power in the Age of AI*. The framework
describes power held across five modalities by four societal actors, and
argues that checks and balances restrain whoever grows too strong, but it
gives no numbers. These models supply them and measure the result.

Every experiment has its own folder under `results/`, holding the write-up and
the data it was computed from. [`EXPERIMENTS.md`](EXPERIMENTS.md) lists every
experiment and links to its write-up; [`results/README.md`](results/README.md)
is the index to the folders themselves.

## What is here

| Folder | What it is |
|---|---|
| `continuous_sim/` | The contest model: power moves every round by arithmetic, nobody decides anything. Two update rules compared. See its README. |
| `action_based_sim/` | The action model: each tick every actor chooses ENHANCE, CHECK or ABSTAIN. Holds the five policy levers and `single_run.py`. See its README. |
| `netlogo/` | The spatial model: the action model on a 17x17 grid, with power diffusing between localities. See `netlogo/README.md`. |
| `questions/` | These are the research questions for our experiment; each writes into its `results/` folder. |
| `figure_helpers/` | The scripts that draw the figures from those results. |
| `results/` | One folder per experiment: write-up plus its CSV/JSON data. |
| `figures/` | Every figure in the report. |

Three files at the root carry the written record: [`EXPERIMENTS.md`](EXPERIMENTS.md) (what was run and what it showed), [`NEXT_STEPS.md`](NEXT_STEPS.md) (what is still open) and this file.

## Running it

Python 3.10 or newer.

```bash
pip install -r requirements.txt

python3 questions/baseline.py             # -> results/baseline/
python3 questions/rq1_check_threshold.py  # -> results/rq1_check_threshold/
python3 questions/rq2_three_vs_four.py    # prints; cached by the figure script
python3 questions/rq3_levers.py           # -> results/rq3_levers/
python3 questions/rq4_spatial.py          # reads the BehaviorSpace CSVs in results/rq4_spatial/

python3 continuous_sim/plots.py              # figures 1-5
python3 figure_helpers/make_figures.py       # figures 6, 7 and 10
python3 figure_helpers/figure_comparison.py  # figure 8
python3 figure_helpers/figure_levers.py      # figure 9
```

The spatial model is run by hand: open `netlogo/digital_gorilla.nlogox` in
NetLogo 7, press `setup` then `go`. The seven BehaviorSpace experiments are
defined inside the model file, and their output CSVs are already in
`results/rq4_spatial/`, so `questions/rq4_spatial.py` reproduces the tables
without re-running NetLogo.

Scripts that sweep parameters cache their results (`*_cache.json`, now inside
the matching results folder), so a figure redraws in seconds rather than
re-running thousands of simulations. Delete the cache to force a fresh run.

## The one invariant

Every modality's four shares sum to 1, in every model, at every tick. It is
asserted rather than assumed, so a mechanism that leaked power would fail
loudly.

## Reproducibility

All runs are seeded. The defaults reproduce the baseline reported throughout:
aspiration 0.261, stability 0.718, quadrant I in 100 of 100 runs.
