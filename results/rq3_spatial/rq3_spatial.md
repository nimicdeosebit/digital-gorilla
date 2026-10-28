# RQ3 — Does it matter where power sits?

## The question

The aggregate models hold one number per kind of power, so two worlds look
identical to them: one where a kind of power is spread thinly and evenly
everywhere, and one where the same total is piled into a few places. Those are
not the same situation. RQ3 asks whether the distinction changes anything.

## Where it is answered

In the NetLogo model, `netlogo/digital_gorilla.nlogo` — 289 localities, each
running the action model's rules on its own power matrix, with power leaking
to neighbouring localities at a rate that depends on the kind of power.
`netlogo/README.md` documents the mechanism and the controls.

The measure is `spread-of`, which is 1 - (standard deviation / mean) across
localities, averaged over actors. 1.0 means that kind of power looks the same
everywhere; lower means it is regionally lumpy.

The control is the `uniform-diffusion?` switch, which sets every rate to 0.17.
The rates are our numbers, so the pattern has to be shown to come from the
differences between them rather than from the mechanism.

## Configuration

BehaviorSpace `spread-by-modality-pinned`, 10 repetitions per switch setting, 50 ticks, all ten controls pinned in the experiment definition (heterogeneity 0.6, diffusion-scale 1.0, check-ratio 1.0, shocks 0.15).

Data: `spread-by-modality-table.csv` 

Table: `python3 questions/rq3_spatial.py`

## Result

| Modality | Rate | Rates differ | Uniform 0.17 | Change |
|---|---|---|---|---|
| Narrative | 0.30 | 0.956 +/- 0.004 | 0.939 | -0.017 |
| Epistemic | 0.30 | 0.941 +/- 0.003 | 0.921 | -0.019 |
| Authoritative | 0.05 | 0.881 +/- 0.006 | 0.940 | +0.059 |
| Economic | 0.15 | 0.856 +/- 0.017 | 0.869 | +0.013 |
| Physical | 0.03 | 0.803 +/- 0.007 | 0.934 | +0.131 |

The gap between the most evenly distributed modalitly and the most regionally concentrated modality: 

Our modality-specific rates: 0.956 − 0.803 = **0.153**
Uniform 0.17 rates: 0.940 − 0.869 = **0.071**

## How fast power travels decides how evenly it spreads

Narrative and epistemic, the two fastest at 0.30, are the most evenly
distributed. Physical, the slowest at 0.03, is the most regionally
concentrated.

The control shows the **rates** cause this. Setting all five to 0.17 more than
halves the spread across modalities: physical gains +0.131, rising from
lumpiest to near the top, while narrative and epistemic both fall once slowed.

**Physical    rate** 0.03 → 0.17   sped up    →  0.803 → 0.934   *MORE* uniform  (+0.131)
**Narrative   rate** 0.30 → 0.17   slowed     →  0.956 → 0.939   *LESS* uniform  (−0.017)

Increasing the rate of the modality makes it more uniform. Reducing the rate makes it less uniform. The effect runs in both directions, which is what separates a result caused by the rates from one the diffusion mechanism would produce regardless of them.

So the distinction RQ3 asks about, i.e., whether it matters that power spread thinly everywhere is different from power piled into a few places, is real and measurable. Different kinds of power end up differently distributed across the grid.

## Why the ordering of the rates is defensible

The ordering comes from the paper's own descriptions of what each kind of power
consists of: knowledge and narrative travel at almost no cost, economic power
moves through institutions, authority stops at a jurisdiction, and force has to
physically be somewhere. The magnitudes are ours — as everywhere else in this
project, the framework supplies none.
