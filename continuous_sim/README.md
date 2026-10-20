# The contest model

Power as arithmetic. No actor ever decides anything here: every round the whole
4x5 matrix is recomputed from scores. This is the simplest thing the paper's
framework can be turned into, and it exists to answer one question — does the
framework settle anywhere on its own, or does it run away?

## The round

```
effort      what an actor puts where. One unit split across the five
            modalities, so each row sums to 1. Fixed per actor.
capability  how effective it is there, independent of what it chose.
score       effort * capability
target      your score divided by everyone's score in that modality
new share   (1 - rate) * old share + rate * target
```

`rate` is 0.16, so each round closes 16% of the remaining gap. That is why a
run settles in about 27 rounds and then sits still: the step size decides how
fast, not where.

Effort comes from `PRIORITIES` in `agents.py` — People act through voice and
consent, the State through law and force, Enterprise through markets, AI
through information. That is a claim about *interests*, read off the paper.
Giving one actor a growing capability advantage would be a claim about
*ability*, which the paper does not support, so capability is flat by default.

## Two update rules, on purpose

| Rule | What it does | Result |
|---|---|---|
| `tullock` | contest success function (Tullock 1980) | converges to one interior point |
| `replicator` | replicator equation (Taylor & Jonker 1978) | runs to a corner; one actor takes everything |

Both are in `contest.py` and both are reported. Same inputs, different
mathematics, opposite conclusions — which is the honest way to show that the
outcome depends on the rule you pick, not only on the framework.

## Knowledge spillover

`mechanisms.py`. Holding data makes an actor more effective elsewhere:

```
capability = 1 + gain * (that actor's epistemic share)
```

Where it lands is genuinely ambiguous in the source. The paper enumerates three
modalities in one sentence (economic, authoritative, physical) and implies a
fourth (narrative) a sentence later. Both readings are in `TARGET_SETS` and the
choice is a parameter, because it changes a headline result. Epistemic never
boosts itself by default.

Off by default (`GAIN = 0.0`), so the flat baseline is what you get unless you
ask for the mechanism.

## Files

| File | What it holds |
|---|---|
| `state.py` | the 4x5 matrix, the initial reading of the paper, `normalise` |
| `agents.py` | effort priorities, capability, score |
| `contest.py` | the two update rules |
| `mechanisms.py` | knowledge spillover and its two target sets |
| `metrics.py` | aspiration, stability, HHI, quadrant |
| `variants.py` | running with a subset of the actors, for the three-actor baseline |
| `config.py` | every tunable number, each marked PLACEHOLDER where it is our choice |
| `plots.py` | figures 1–5 |

## How it keeps the books

Every column must sum to 1. This model breaks that constantly and
**renormalises** every round (`P / P.sum(axis=0)`). The action model instead
never breaks it and asserts it. Two different disciplines, both valid — worth
stating, because it is the kind of thing a reader will ask about.

## What it does not have

No legitimacy. No decisions. No failure — nothing in this model can attempt
something and not get it. Those are exactly what the action model adds, which
is why both exist.

## Worth knowing

The end state does not depend on the starting matrix. Every initial condition
tested — the paper-derived one, an even split, random matrices, AI holding
everything — converges to the same fixed point to within 1e-14. The initial
matrix sets the journey, not the destination. That matters because the initial
matrix is our reading of the paper's qualitative table, and this result means
the headline conclusion does not rest on it.

Run it: `python3 continuous_sim/plots.py` draws figures 1–5.
