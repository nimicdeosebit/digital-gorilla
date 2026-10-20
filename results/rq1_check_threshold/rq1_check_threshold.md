# Check strength sweep

### Purpose

The original model used one magnitude (`effect_magnitude = 0.10`) for ENHANCE,
CHECK and shocks alike. Those are not symmetric moves: ENHANCE draws from every
other actor, CHECK draws from one, and only on success. At equal magnitudes
enhancing is therefore about three times the stronger move, and the
100%-quadrant-I result reported above follows from that rather than from
anything in the paper.

`action_based_sim/config.py` now carries `enhance_magnitude`, `check_magnitude` and
`shock_magnitude` separately, all defaulting to `effect_magnitude` so earlier
runs reproduce exactly. The experimental variable is the ratio
`check_magnitude / enhance_magnitude`.

`enhance_mode` controls the other half of the asymmetry:

- `per_donor` (default, original): every other actor gives up
  `enhance_magnitude` of its own share, so ENHANCE scales with the number of
  opponents.
- `per_capita`: the same total divided by the number of donors, so one ENHANCE
  is worth one CHECK against an average opponent. Also what makes a three-actor
  run comparable with a four-actor one.

### Configuration

- Seeds: 0-199 (200 runs per point), verified against an independent block 5000-5299
- Ratios: 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0
- Everything else at defaults

### Result

High Potential (quadrant II) does not become the majority outcome until checks
are roughly **three times** stronger than enhancement. The crossing sits between
2.8 and 3.4 depending on the seed block, and the two `enhance_mode` settings
agree (3.4 per_donor, 3.0 per_capita), so the threshold is a property of the
contest rather than of how ENHANCE is shared out.

At the original setting (ratio 1.0) the outcome is quadrant I in 100% of runs.

Figure: `figures/fig6_check_threshold.png`. Data: `sweep_check_per_donor.csv`,
`sweep_check_per_capita.csv`.
