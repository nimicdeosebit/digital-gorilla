"""Discrete actions (ENHANCE / CHECK / ABSTAIN) and their zero-sum effects.

The losing side gives up a fraction of its own current share and the acting
actor receives exactly what was given up, so every modality still sums to 1.

ENHANCE and CHECK no longer share one magnitude. They are asymmetric moves --
ENHANCE draws from every other actor, CHECK from one -- so a single shared
magnitude silently makes enhancing the stronger move. See config.py.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from action_based_sim.config import SimulationConfig
from action_based_sim.state import State
from action_based_sim.tables import CHECK_MECHANISMS, is_check_legal


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
        donors = [a for a in state.actors if a != action.actor]
        if not donors:
            return 0.0, None
        # per_donor : each donor gives up `enhance_magnitude` of its own share
        # per_capita: the same total shared out, so one ENHANCE is worth one
        #             CHECK against an average opponent
        scale = 1.0 if config.enhance_mode == "per_donor" else 1.0 / len(donors)
        total_moved = 0.0
        for donor in donors:
            amount = config.enhance_magnitude * scale * state.P[action.modality][donor]
            total_moved += state.transfer_share(
                action.modality, donor, action.actor, amount
            )
        return total_moved, None

    if action.type == ActionType.CHECK:
        if action.target not in state.actors or not is_check_legal(
            action.actor, action.target
        ):
            return 0.0, False

        mechanism = rng.choice(CHECK_MECHANISMS[(action.actor, action.target)])
        action.mechanism = mechanism["name"]
        weight = mechanism["weight"]

        cap = getattr(config, "capability", None)
        checker_strength = state.effective_strength(
            action.actor, action.modality, cap)
        target_strength = state.effective_strength(
            action.target, action.modality, cap)
        denom = checker_strength + target_strength
        success_probability = checker_strength / denom if denom > 0 else 0.5

        if rng.random() < success_probability:
            # A lever may make checks in this modality bite harder.
            gain = getattr(config, "check_gain", {}).get(action.modality, 1.0)
            amount = (
                config.check_magnitude * weight * gain
                * state.P[action.modality][action.target]
            )
            moved = state.transfer_share(
                action.modality, action.target, action.actor, amount
            )
            return moved, True
        return 0.0, False

    raise ValueError(f"Unknown action type: {action.type}")
