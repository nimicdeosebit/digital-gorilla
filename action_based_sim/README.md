# The action model

This is what makes the continuous model an actual agent simulation.
The action model lets the actors pick an action out of three (ENHANCE, CHECK, ABSTAIN) every tick.
Thus, every tick four actions happen.
This is the project's main model: RQ1, RQ2 and RQ3 are all answered here.

## The state

Same 4×5 power table as the continuous model, but it carries two things the continuous model doesn’t need.

- `P` — the 4x5 power matrix. Every modality's four shares sum to 1.
- `L` — one legitimacy value per actor.

and guarantees one invariant: **every column sums to 1, asserted every tick**.
A mechanism that leaked power would crash the run rather than quietly produce
wrong numbers.

Starting values are in `tables.py`, read off the paper's qualitative tables.
Enterprises lead economic and epistemic; the State leads authoritative and
physical; AI starts low everywhere. The magnitudes are ours — the source gives
examples per cell, not numbers.

### What it carries that the contest model does not

| | contest model | action model |
|---|---|---|
| **Power `P`** | 4x5 numpy array, every column sums to 1 | 4x5 nested dicts keyed by name, every column sums to 1 |
| **Starting values** | its own reading of Table 4 | a different reading — the one NetLogo copies |
| **Legitimacy `L`** | none | one per actor: People 0.65, State 0.70, Enterprises 0.55, AI 0.35 |
| **Capability** | the spillover multiplier; 1 unless `GAIN` > 0 | the policy-lever multiplier; 1 unless a lever is on |
| **How power moves** | the whole table is recomputed from scores | handed over actor to actor by `transfer_share`, clamped, strictly zero-sum |
| **Can a move fail?** | no | yes — a CHECK is a contest you can lose |
| **The invariant** | broken every round, then renormalised | never broken by construction, and asserted every tick |
| **Actor count** | 3 or 4, via `variants.py` | 3 or 4, via the `actors` list in `config.py` |
| **Also carried per run** | nothing but the matrix | RNG, full history, volatility window, check-success window (`environment.py`) |

The row that explains the rest is **can a move fail?** Once an action can fail,
something has to decide whether it does — that is legitimacy. Power has to move
a specific amount from one named actor to another — that is `transfer_share`.
And the run has to remember what happened — that is the history and the two
windows in `environment.py`. None of it is needed in a model where the table is
simply recalculated every round.

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

Checking is a trigger, not a comparison: an actor never weighs a check against
abstaining. If something on its watchlist is over the threshold it checks,
full stop. The roll only decides what happens when nothing triggered.

| Actor | Watches | If nothing is over 0.45 |
|---|---|---|
| People | Enterprises/economic, State/authoritative, AI/narrative | ENHANCE narrative with p = 0.3, else ABSTAIN |
| State | Enterprises/economic, AI/epistemic | ENHANCE authoritative with p = 0.3, else ABSTAIN |
| Enterprises | AI/economic | always ENHANCE — economic at p = 0.7, else epistemic |
| AI | Enterprises/economic, but only once AI's own epistemic share is above 0.45 | always ENHANCE — epistemic or narrative, 50/50 |

So abstaining is never chosen on its merits; it is what is left when nothing
crossed the threshold and the growth roll failed. Enterprises and AI cannot
abstain at all, which is why they are the two that run away.

**ENHANCE** takes a fraction of every other actor's share, and always works. This is motivated by the paper which says that actors attempt to maintain their power across modalities. It's a way of growth not aimed at anyone in particular.

**CHECK** is a contest that can fail. The odds are

```
own power * own legitimacy * own capability
-------------------------------------------------------
the same for you  +  the same for the target
```

Win and share moves from target to checker; lose and nothing happens. Checks
are aimed and fallible because the paper's Table 6 lists them as directional —
a named actor checking a named actor — and because legitimacy would have
nothing to do if a check always worked.

**ABSTAIN** does nothing. It is not neutral, though: while one actor sits out,
the others are still enhancing, and ENHANCE draws from everybody — so an
abstaining actor's share falls. People and the State abstain on roughly seven
ticks in ten whenever nothing is concentrated enough to check, which is most
of a run.

That asymmetry is where the model's central result comes from. Enhancing always
lands and checking only sometimes, so a check has to be about **three times** as
strong before the People end up in the good quadrant. The two magnitudes used to
be a single shared number, which made enhancing roughly three times the stronger
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
legitimacy. They are measured against the no-lever baseline in RQ3; the result
is that two do nothing, antitrust works but the State collects the gains, and
none of them lower the check-strength threshold.

## Limitations to declare

**People are never checked.** No actor's watchlist names People as a target, so
they can lose power only as collateral. Since aspiration *is* People's share,
this biases the headline metric. The paper does list mechanisms running against
People and they sit unused in `tables.py`. See `NEXT_STEPS.md`.

**ENHANCE cannot fail.** A check is a contest, a grab is a certainty. Nothing in
the paper says expansion is frictionless, and that one difference is most of why
the baseline ends in quadrant I every time. Letting growth be contested too is
the obvious next version of this model.

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
