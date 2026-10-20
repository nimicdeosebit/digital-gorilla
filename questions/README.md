# Questions

One script per question. Each writes its output into the matching folder under
`results/`. Note that the 3rd RQ uses the Netlogo model, that's why you don't see it here. 

Run them from the repository root:

```bash
python3 questions/baseline.py             # -> results/baseline/
python3 questions/rq1_check_threshold.py  # -> results/rq1_check_threshold/
                                          #    + results/rq2_three_vs_four/
python3 questions/rq2_three_vs_four.py    # prints; cached by figure_helpers/
python3 questions/rq4_levers.py           # -> results/rq4_levers/
```

| Script | Question |
|---|---|
| `baseline.py` | — Baseline. What does the action model do with no intervention? |
| (none) | RQ3. Does it matter WHERE power sits? Answered by the NetLogo model in `netlogo/`. |
| `rq1_check_threshold.py` | RQ1. How strong must a check be before the People reach High Potential? |
| `rq2_three_vs_four.py` | RQ2. Does adding AI as a fourth actor change the outcome? |
| `rq4_levers.py` | RQ4. Do the five policy levers help, and can they replace check strength? |

One wrinkle worth knowing: `rq1_check_threshold.py` sweeps BOTH the check
ratio and the actor count, because the two sweeps share the same batch runner.
So it also writes `sweep_actor_count.csv` and `sweep_threshold_by_actors.csv`
into `results/rq2_three_vs_four/`. The name says rq1 because the threshold is
what it is for.

The figure scripts live in `figure_helpers/`: they draw results rather than
produce them, and they read the caches these scripts leave behind.
