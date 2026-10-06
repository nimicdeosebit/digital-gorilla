"""Aspiration and stability, and the Table 8 quadrant.

The paper puts these two on separate axes: the matrix is for "preserving both
human flourishing (aspiration) and balanced power (stability)" (Sec. 5.1(b)).
Balanced power is STABILITY, so the concentration measure belongs there and
aspiration has to be about People.

These definitions match the ones used in continuous_sim, so the two simulations
can be compared.
"""

from statistics import mean

from action_based_sim.state import State
from action_based_sim.tables import MODALITIES


def aspiration(state: State) -> float:
    """People's mean share across the five modalities, normalised so that an
    even split between n actors gives 0.5 and People holding twice an even
    share gives 1.0.

    This is a PROXY for one part of what the paper means by aspiration. Sec. 4.3
    describes it more widely than "how much do People hold", so it should be
    reported as a proxy rather than as the thing itself.
    """
    n = len(state.P[MODALITIES[0]])
    peoples_share = mean(state.P[m]["People"] for m in MODALITIES)
    return max(0.0, min(1.0, peoples_share / (2.0 / n)))


def stability(state: State) -> float:
    """How unconcentrated power is: 1 means an even split, 0 means a single
    actor holds everything.

    Computed per modality from the HHI and then averaged, so an actor owning
    two modalities outright still registers even when its overall position
    looks moderate. The paper itself suggests market concentration indices as
    the measure here (Sec. 4.4).
    """
    n = len(state.P[MODALITIES[0]])
    even = 1.0 / n
    per_modality = [1.0 - (state.hhi(m) - even) / (1.0 - even) for m in MODALITIES]
    return max(0.0, min(1.0, mean(per_modality)))


def volatility(recent_volatility: float, recent_check_success_rate: float) -> float:
    """How turbulent the last few rounds were, kept SEPARATE from stability.

    It used to be folded into stability, which meant stability was not
    measuring balance of power at all. It is recorded alongside the two axes
    so it can still be looked at, but it does not decide the quadrant.
    """
    return max(0.0, min(1.0, recent_volatility + (1.0 - recent_check_success_rate)))


def classify_quadrant(asp: float, stab: float, threshold: float = 0.5) -> str:
    if stab >= threshold and asp < threshold:
        return "I - Surviving not Thriving"
    if stab >= threshold and asp >= threshold:
        return "II - High Potential"
    if stab < threshold and asp >= threshold:
        return "III - Creative Chaos"
    return "IV - Fragile Collapse"
