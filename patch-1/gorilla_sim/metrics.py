"""Aspiration/Stability metrics and Table 8 quadrant classification.
Normalizations are provisional, they don't retune before validation."""

from statistics import mean

from gorilla_sim.state import State
from gorilla_sim.tables import MODALITIES

_MIN_HHI = 0.25  # perfectly balanced across 4 actors
_MAX_HHI = 1.00  # single actor holds everything


def aspiration(state: State) -> float:
    mean_hhi = mean(state.hhi(m) for m in MODALITIES)
    value = (1.0 - mean_hhi) / (1.0 - _MIN_HHI)
    return max(0.0, min(1.0, value))


def stability(state: State, recent_volatility: float, recent_check_success_rate: float) -> float:
    legitimacy_term = mean(state.L.values())
    raw = legitimacy_term + recent_check_success_rate - recent_volatility
    return max(0.0, min(1.0, raw / 2))


def classify_quadrant(asp: float, stab: float, threshold: float = 0.5) -> str:
    if stab >= threshold and asp < threshold:
        return "I - Surviving not Thriving"
    if stab >= threshold and asp >= threshold:
        return "II - High Potential"
    if stab < threshold and asp >= threshold:
        return "III - Creative Chaos"
    return "IV - Fragile Collapse"
