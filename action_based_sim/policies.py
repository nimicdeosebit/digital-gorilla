"""Rule-based actor policies encoding Table 4/6 behavior, not learned policies.

Each policy watches a short list of (target, modality) pairs it can legally
check (Table 6); if the most concentrated one crosses the concentration
threshold, it checks it. Otherwise it grows its own priority modality, or abstains.
"""

import random
from typing import List, Optional, Tuple

from action_based_sim.actions import Action, ActionType
from action_based_sim.config import SimulationConfig
from action_based_sim.state import State


def _most_concentrated_above_threshold(
    state: State, candidates: List[Tuple[str, str]], threshold: float
) -> Optional[Tuple[str, str]]:
    """Candidates naming an actor that is not in this run are skipped, so the
    same policies work for the three-actor baseline without rewriting them."""
    best, best_share = None, threshold
    for target, modality in candidates:
        if target not in state.actors:
            continue
        share = state.P[modality][target]
        if share > best_share:
            best, best_share = (target, modality), share
    return best


def _people_policy(state: State, config: SimulationConfig, rng: random.Random) -> Action:
    # Consumer choice vs. Enterprises, protest vs. State overreach, refusal
    # to adopt vs. AI narrative dominance.
    candidates = [("Enterprises", "Economic"), ("State", "Authoritative"), ("AI", "Narrative")]
    hit = _most_concentrated_above_threshold(state, candidates, config.concentration_threshold)
    if hit:
        target, modality = hit
        return Action(ActionType.CHECK, actor="People", modality=modality, target=target)
    if rng.random() < 0.3:
        return Action(ActionType.ENHANCE, actor="People", modality="Narrative")
    return Action(ActionType.ABSTAIN, actor="People")


def _state_policy(state: State, config: SimulationConfig, rng: random.Random) -> Action:
    # Regulation/antitrust vs. Enterprises, legislation vs. AI epistemic dominance.
    candidates = [("Enterprises", "Economic"), ("AI", "Epistemic")]
    hit = _most_concentrated_above_threshold(state, candidates, config.concentration_threshold)
    if hit:
        target, modality = hit
        return Action(ActionType.CHECK, actor="State", modality=modality, target=target)
    if rng.random() < 0.3:
        return Action(ActionType.ENHANCE, actor="State", modality="Authoritative")
    return Action(ActionType.ABSTAIN, actor="State")


def _enterprises_policy(state: State, config: SimulationConfig, rng: random.Random) -> Action:
    # Capability throttling vs. AI economic encroachment; otherwise grow.
    hit = _most_concentrated_above_threshold(
        state, [("AI", "Economic")], config.concentration_threshold
    )
    if hit:
        target, modality = hit
        return Action(ActionType.CHECK, actor="Enterprises", modality=modality, target=target)
    modality = "Economic" if rng.random() < 0.7 else "Epistemic"
    return Action(ActionType.ENHANCE, actor="Enterprises", modality=modality)


def _ai_policy(state: State, config: SimulationConfig, rng: random.Random) -> Action:
    # Automates decisions vs. Enterprises only once AI's own epistemic
    # position is already strong; otherwise grow.
    if state.P["Epistemic"]["AI"] > config.concentration_threshold:
        hit = _most_concentrated_above_threshold(
            state, [("Enterprises", "Economic")], config.concentration_threshold
        )
        if hit:
            target, modality = hit
            return Action(ActionType.CHECK, actor="AI", modality=modality, target=target)
    modality = "Epistemic" if rng.random() < 0.5 else "Narrative"
    return Action(ActionType.ENHANCE, actor="AI", modality=modality)


_POLICIES = {
    "People": _people_policy,
    "State": _state_policy,
    "Enterprises": _enterprises_policy,
    "AI": _ai_policy,
}


def decide(actor_name: str, state: State, config: SimulationConfig, rng: random.Random) -> Action:
    return _POLICIES[actor_name](state, config, rng)
