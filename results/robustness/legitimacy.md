# Legitimacy robustness check

### Purpose

Legitimacy was initialised from Table 5 and never updated, while silently
weighting every CHECK through `effective_strength`. `legitimacy_rate` now
relaxes each actor's legitimacy toward `1 - (its mean share)`: concentrated
power is decreasingly seen as rightfully held. Off by default.

### Result

Over rates 0.0, 0.05, 0.10, 0.20, 0.40 the legitimacy values move a long way
(AI rises from 0.35 to about 0.80) but aspiration changes from 0.393 to 0.389
and stability from 0.839 to 0.841, both inside the confidence intervals, and
the quadrant stays I in 100% of runs.

The frozen-legitimacy simplification therefore does not drive any reported
result. It should still be described as a simplification, not defended as
neutral.
