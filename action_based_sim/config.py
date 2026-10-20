"""Simulation config.

The magnitudes used to be a single number (`effect_magnitude`) shared by
ENHANCE, CHECK and shocks alike. That was a hidden modelling decision, not a
neutral default: because ENHANCE draws from every other actor while CHECK
draws from one, equal magnitudes make enhancing roughly three times stronger
than checking, and the model's outcome follows from that coincidence rather
than from anything in the paper.

They are three separate parameters now, defaulting to the old shared value so
that previously reported runs still reproduce exactly.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from action_based_sim import levers as levers_module
from action_based_sim.tables import ACTORS as ALL_ACTORS

# How ENHANCE draws from the other actors.
#
#   "per_donor"   every other actor gives up `enhance_magnitude` of its own
#                 share, so the total taken is magnitude x (1 - own share) and
#                 scales with the NUMBER of opponents. Original behaviour, and
#                 the reason enhancing beats checking.
#
#   "per_capita"  the same total divided by the number of donors, so one
#                 ENHANCE is worth one CHECK against an average opponent.
#                 Makes the two action types comparable, and makes a
#                 three-actor run comparable with a four-actor one.
ENHANCE_MODES = ("per_donor", "per_capita")


@dataclass
class SimulationConfig:
    ticks: int = 50
    seed: int = 42

    # Which actors exist in this run. Dropping "AI" gives the pre-AI baseline
    # that the four-actor result needs to be compared against.
    actors: List[str] = field(default_factory=lambda: list(ALL_ACTORS))

    # Default share-shift fraction. Kept so old calls that set only this
    # behave exactly as before.
    effect_magnitude: float = 0.10

    # Per-action magnitudes. None means "fall back to effect_magnitude".
    enhance_magnitude: Optional[float] = None
    check_magnitude: Optional[float] = None
    shock_magnitude: Optional[float] = None

    enhance_mode: str = "per_donor"

    shock_probability: float = 0.15
    concentration_threshold: float = 0.45
    volatility_window: int = 5

    # Legitimacy dynamics. At 0.0 legitimacy stays frozen at its Table 5
    # value, which is the original behaviour.
    legitimacy_rate: float = 0.0
    legitimacy_floor: float = 0.05
    legitimacy_ceiling: float = 0.95

    # Policy levers from Table 7's intervention column. Empty means no
    # intervention, which is the baseline every lever run is measured against.
    levers: List[str] = field(default_factory=list)
    lever_strength: float = 1.0

    environment_id: str = "default"

    def __post_init__(self):
        if self.enhance_magnitude is None:
            self.enhance_magnitude = self.effect_magnitude
        if self.check_magnitude is None:
            self.check_magnitude = self.effect_magnitude
        if self.shock_magnitude is None:
            self.shock_magnitude = self.effect_magnitude

        if self.enhance_mode not in ENHANCE_MODES:
            raise ValueError(
                f"enhance_mode must be one of {ENHANCE_MODES}, got {self.enhance_mode!r}"
            )
        unknown = [a for a in self.actors if a not in ALL_ACTORS]
        if unknown:
            raise ValueError(f"unknown actors: {unknown}")
        if len(self.actors) < 2:
            raise ValueError("need at least two actors for a contest")

        # Resolved once, so the per-tick code does no lookup work.
        self.check_gain, self.capability, self.legitimacy_repair = \
            levers_module.resolve(self.levers, self.actors, self.lever_strength)

    @property
    def check_ratio(self) -> float:
        """Check strength as a multiple of enhance strength.

        This is the experimental variable. 1.0 means a CHECK and an ENHANCE
        move the same fraction of the targeted actor's share.
        """
        return self.check_magnitude / self.enhance_magnitude
