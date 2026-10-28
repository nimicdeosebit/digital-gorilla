# Questions

One script per question. Each writes its output into the matching folder under
`results/`. Note that the 3rd RQ uses the Netlogo model, that's why you don't see it here. 

Run them from the repository root:

```bash
python3 questions/baseline.py             # -> results/baseline/
python3 questions/rq1_check_threshold.py  # -> results/rq1_check_threshold/
                                          #    + results/rq2_three_vs_four/
python3 questions/rq2_three_vs_four.py    # prints; cached by figure_helpers/
python3 questions/rq3_levers.py           # -> results/rq3_levers/
python3 questions/rq4_spatial.py          # reads the NetLogo CSVs -> tables
```

| Script | Question |
|---|---|
| `baseline.py` | — Baseline. What does the action model do with no intervention? |
| `rq1_check_threshold.py` | RQ1. How strong must a check be before the People reach High Potential? |
| `rq2_three_vs_four.py` | RQ2. Does adding AI as a fourth actor change the outcome? |
| `rq3_levers.py` | RQ3. Do the five policy levers help, and can they replace check strength? |
| `rq4_spatial.py` | RQ4. Does it matter where power sits? Reduces the NetLogo BehaviorSpace output to tables. |

One wrinkle worth knowing: `rq1_check_threshold.py` sweeps BOTH the check
ratio and the actor count, because the two sweeps share the same batch runner.
So it also writes `sweep_actor_count.csv` and `sweep_threshold_by_actors.csv`
into `results/rq2_three_vs_four/`. The name says rq1 because the threshold is
what it is for.

The figure scripts live in `figure_helpers/`: they draw results rather than
produce them, and they read the caches these scripts leave behind.
