# The action model

Power as a sequence of choices. Four actors, five modalities, and every tick
each actor picks one of three things to do. This is the project's main model:
RQ1, RQ2 and RQ4 are all answered here.

## The state

`state.py` holds two things:

- `P` — the 4x5 power matrix. Every modality's four shares sum to 1.
- `L` — one legitimacy value per actor.

and guarantees one invariant: **every column sums to 1, asserted every tick**.
A mechanism that leaked power would crash the run rather than quietly produce
wrong numbers.

Starting values are in `tables.py`, read off the paper's qualitative tables.
Enterprises lead economic and epistemic; the State leads authoritative and
physical; AI starts low everywhere. The magnitudes are ours — the source gives
examples per cell, not numbers.

## One tick

```
decide    each actor scans its own short list of rivals it may check.
          Most concentrated one above 0.45 -> CHECK it.
          Otherwise ENHANCE (p = 0.3) or ABSTAIN.
resolve   actions applied in sequence
shock     with probability 0.15, one external event moves share
          from a disfavoured to a favoured actor
update    legitimacy relaxes (off by default), invariant asserted
```

**ENHANCE** takes a fraction of every other actor's share, and always works.

**CHECK** is a contest that can fail. The odds are

```
own power * own legitimacy * own capability
-------------------------------------------------------
the same for you  +  the same for the target
```

Win and share moves from target to checker; lose and nothing happens.

That asymmetry is the model's central finding. Enhancing always lands and
checking only sometimes, so a check has to be about **three times** as strong
before the People end up in the good quadrant. The two magnitudes used to be a
single shared number, which made enhancing roughly three times the stronger
move by accident; they are separate parameters now, and the ratio between them
is the experimental variable.

## What is measured

`metrics.py`:

- **aspiration** — People's mean share, normalised so an even split is 0.5
- **stability** — per-modality HHI, rescaled so an even split is 1, then
  averaged across modalities
- **volatility** — recent movement plus recent check failures. Recorded but
  deliberately NOT part of the quadrant; it used to be folded into stability,
  which meant stability was not measuring balance of power at all.
- **quadrant** — the two axes cut at 0.5, giving the paper's four cells

## Files

| File | What it holds |
|---|---|
| `state.py` | the matrix, legitimacy, transfers, HHI, the invariant |
| `tables.py` | all paper-derived data: initial power, legitimacy, mechanisms, shocks |
| `policies.py` | who may check whom, and when — the decision rules |
| `actions.py` | ENHANCE / CHECK / ABSTAIN and their effects |
| `events.py` | the shock engine |
| `levers.py` | the five policy interventions |
| `environment.py` | one self-contained simulation: state, actors, RNG, history |
| `config.py` | every parameter, with the levers resolved once at construction |
| `metrics.py` | aspiration, stability, volatility, quadrant |
| `single_run.py` | one run printed tick by tick, for inspecting a trajectory |

## The levers

`levers.py` implements five interventions. Each can raise how hard checks bite
in a modality, raise or lower an actor's capability, or repair the State's
legitimacy. They are measured against the no-lever baseline in RQ4; the result
is that two do nothing, antitrust works but the State collects the gains, and
none of them lower the check-strength threshold.

## Limitations to declare

**People are never checked.** No actor's watchlist names People as a target, so
they can lose power only as collateral. Since aspiration *is* People's share,
this biases the headline metric. The paper does list mechanisms running against
People and they sit unused in `tables.py`. See `NEXT_STEPS.md`.

**All mechanism weights are 1.0.** A check draws a named mechanism from the
catalogue and logs it, but every weight is the same, so the draw has no
numerical consequence. The catalogue is faithful as a catalogue; it does not
yet do any work.

**Aspiration is a proxy.** The paper means more by it than "how much do the
People hold".

## Running it

```bash
python3 action_based_sim/single_run.py     # watch one run
python3 questions/baseline.py              # 100 seeds -> results/baseline/
```

The baseline reproduces at aspiration 0.261, stability 0.718, quadrant I in
100 of 100 runs. If that moves, something upstream changed.
