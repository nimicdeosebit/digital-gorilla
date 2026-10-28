# Policy levers

### Purpose

Every shock in Table 7 comes with an `intervention` sentence saying what should
be done about it. `action_based_sim/levers.py` turns those five sentences into
things the model can run with. The framework gives no magnitudes, so the
magnitudes are ours, taken from the June prototype. They do not depend on that
prototype's discarded AI growth curve -- they are capability and
check-strength edits -- so they port across unchanged.

Only two channels exist in this model, and every lever uses one or both:
`check_gain` multiplies the magnitude of a CHECK in one modality, and
`capability` multiplies an actor's effective strength in one modality, which
changes both its odds of checking successfully and its odds of resisting a
check. Transparency also adds legitimacy repair, to the State only.

| lever | channel |
|---|---|
| Antitrust | checks in Economic x1.90 |
| Audit and transparency | checks in Epistemic x1.50; State legitimacy +0.04/tick |
| Data rights | People +0.45 epistemic capability; AI -0.18 |
| AI liability | AI -0.22 authoritative and physical capability |
| Civic capacity | People +0.40 narrative, +0.20 authoritative; AI -0.12 narrative |

Defaults are unchanged: with no levers the baseline still reproduces at
aspiration 0.261, stability 0.718, quadrant I in 100 of 100 runs.

### Result 1: two of the five levers do nothing at all

At the baseline check ratio of 1.0, over 200 seeds, the change in each actor's
mean share against the no-lever run:

| lever | People | State | Enterprises | AI |
|---|---|---|---|---|
| Civic capacity | **+0.0071** | -0.0037 | -0.0013 | -0.0021 |
| Antitrust | +0.0025 | +0.0088 | **-0.0117** | +0.0003 |
| Data rights | -0.0002 | +0.0012 | -0.0007 | -0.0003 |
| AI liability | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| Audit and transparency | **-0.0106** | **+0.0144** | -0.0034 | -0.0003 |

AI liability and data rights do nothing measurable, and the reason is
structural rather than a question of magnitude. A capability edit only matters
where some policy in Table 6 actually uses that (actor, modality) pair. AI
liability drags AI in authoritative and physical power, which no actor ever
checks AI on. Data rights boost People's epistemic capability, and People never
check anyone in the epistemic modality. The levers act on channels the
implemented policy set does not use.

### Result 2: antitrust works, but the State collects

Antitrust is the only lever that moves a large amount of power: Enterprises
lose 0.0117. But People gain only 0.0025 of it and the State takes 0.0088.
Cutting one actor down does not hand the proceeds to People; it hands them to
whoever does the cutting.

### Result 3: transparency leaves People worse off

The audit lever is the largest single effect in the table and it runs the wrong
way for People: -0.0106 for People, +0.0144 for the State. The lever
strengthens the regulator, in both of its channels -- stronger epistemic checks
are exercised by the State against AI, and legitimacy repair makes the State
harder to check in turn. In a four-actor framework the regulator is not the
people, so a policy that empowers it moves power away from them.

Civic capacity is the only lever that leaves People better off, and it is the
only one whose channel points at People directly rather than at an actor People
are supposed to be protected from.

### Result 4: policy does not lower the check-strength threshold

The ratio at which High Potential becomes the majority outcome:

| condition | threshold |
|---|---|
| No levers | ~3.03 |
| All five levers | ~3.32 |
| Antitrust + audit | ~3.78 |

Levers do not substitute for check strength, and the two State-empowering ones
push the threshold up. Sweeping lever strength from 0 to 3 at ratio 1.0 raises
People from 0.787 to 0.892 of an even share and High Potential from 0% to 16%,
so the effect is monotone but never reaches the quadrant on its own.

Figure: `figures/fig9_levers.png`. Code: `action_based_sim/levers.py`,
`questions/rq3_levers.py`, `figure_helpers/figure_levers.py`.

### A bug found by reading the result

The first run had the audit lever applying legitimacy repair to every actor,
which raised the legitimacy of the actors being audited and made them harder to
check. The documented intent was the State only. Fixed; the direction of the
result did not change, which is worth saying, but the magnitude did.

### Limitations

Results 1 and 2 both depend on which (target, modality) pairs the Table 6
policies cover, and that coverage is incomplete: nothing checks People at all,
and nothing checks the State on physical power. A lever aimed at an uncovered
pair cannot do anything, so the finding is about this policy set rather than
about the intervention in the world.
