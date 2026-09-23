"""Simulation config. Defaults are frozen(fixed), so they don't retune casually."""

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    ticks: int = 50
    seed: int = 42

    # Frozen share-shift fraction, reused by enhance, check, and shocks alike.
    effect_magnitude: float = 0.10

    shock_probability: float = 0.15
    concentration_threshold: float = 0.45
    volatility_window: int = 5

    # Unused by a single run; present so multi-instance runs later are a
    # config changes, not a refactors.
    environment_id: str = "default"
