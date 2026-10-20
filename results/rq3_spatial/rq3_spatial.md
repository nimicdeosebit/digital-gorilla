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

## Status: not yet run

The experiment has never been run, so this question has no numbers. The model
and the measure are both in place; what is missing is the run.

To produce them: BehaviorSpace experiment `spread-by-modality`, 10 repetitions,
both settings of `uniform-diffusion?`, in NetLogo desktop — NetLogo Web has no
BehaviorSpace. Average each `spread-of` column over the repetitions, separately
for each switch setting, and the result is one uniformity value per modality
with and without the control. Steps are in `NEXT_STEPS.md`.

What it should show, if the claim holds: narrative and epistemic (rate 0.30)
closest to 1.0, physical (0.03) lowest, and the differences between modalities
largely disappearing once every rate is set to 0.17. If the ordering comes out
otherwise, report that — a model that contradicts the prediction is a finding.

If the run does not happen before submission, drop RQ3 to a demonstration: the
model shows the mechanism and the view makes it visible, but no numerical claim
is made.

## Why the ordering of the rates is defensible

The ordering comes from the paper's own descriptions of what each kind of power
consists of: knowledge and narrative travel at almost no cost, economic power
moves through institutions, authority stops at a jurisdiction, and force has to
physically be somewhere. The magnitudes are ours — as everywhere else in this
project, the framework supplies none.
