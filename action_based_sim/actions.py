"""Discrete actions (ENHANCE / CHECK / ABSTAIN) and their zero-sum effects.

One rule for every effect: the losing side gives up a fixed fraction
(config.effect_magnitude) of its own current share; the acting actor
receives exactly what was given up.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from action_based_sim.config import SimulationConfig
from action_based_sim.state import State
from action_based_sim.tables import ACTORS, CHECK_MECHANISMS, is_check_legal


class ActionType(Enum):
    ENHANCE = "ENHANCE"
    CHECK = "CHECK"
    ABSTAIN = "ABSTAIN"


@dataclass
class Action:
    type: ActionType
    actor: str
    modality: Optional[str] = None
    target: Optional[str] = None
    mechanism: Optional[str] = None  # filled in on resolve, for logging


def resolve_action(
    action: Action, state: State, config: SimulationConfig, rng: random.Random
) -> Tuple[float, Optional[bool]]:
    """Apply one action to `state`. Returns (share_moved, check_success)."""
    if action.type == ActionType.ABSTAIN:
        return 0.0, None

    if action.type == ActionType.ENHANCE:
        total_moved = 0.0
        for donor in (a for a in ACTORS if a != action.actor):
            amount = config.effect_magnitude * state.P[action.modality][donor]
            total_moved += state.transfer_share(action.modality, donor, action.actor, amount)
        return total_moved, None

    if action.type == ActionType.CHECK:
        if not is_check_legal(action.actor, action.target):
            return 0.0, False

        mechanism = rng.choice(CHECK_MECHANISMS[(action.actor, action.target)])
        action.mechanism = mechanism["name"]
        weight = mechanism["weight"]

        checker_strength = state.effective_strength(action.actor, action.modality)
        target_strength = state.effective_strength(action.target, action.modality)
        denom = checker_strength + target_strength
        success_probability = checker_strength / denom if denom > 0 else 0.5

        if rng.random() < success_probability:
            amount = config.effect_magnitude * weight * state.P[action.modality][action.target]
            moved = state.transfer_share(action.modality, action.target, action.actor, amount)
            return moved, True
        return 0.0, False

    raise ValueError(f"Unknown action type: {action.type}")
