# Results

One folder per experiment. Each folder holds the write-up (`.md`) and the data
it was computed from (`.csv`, `.json`).

| Folder | Question it answers |
|---|---|
| `baseline/` | What does the action model do when nothing is intervened on? |
| `rq1_check_threshold/` | RQ1. How strong does a check have to be before the People end up in High Potential? |
| `rq2_three_vs_four/` | RQ2. Does adding AI as a fourth actor change the outcome? |
| `rq3_levers/` | RQ3. Do the five policy levers help, and can they substitute for raw check strength? |
| `rq4_spatial/` | RQ4. Does it matter where power sits? (NetLogo) |
| `robustness/` | Does the result survive letting legitimacy move? |
| `validation/` | Do the two implementations agree? |

## Regenerating

Run from the repository root. Each script writes into the folder its results
belong in; the sweep scripts cache, so a figure redraws in seconds.

```bash
python3 questions/baseline.py
python3 questions/rq1_check_threshold.py
python3 questions/rq2_three_vs_four.py
python3 questions/rq3_levers.py
python3 questions/rq4_spatial.py   # reduces the NetLogo CSVs to tables
```

Delete a cache file to force a fresh run.

## The one number to check

The action-model baseline reproduces at aspiration 0.261, stability 0.718,
quadrant I in 100 of 100 runs. If that moves, something upstream changed.
