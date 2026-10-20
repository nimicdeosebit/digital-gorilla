"""Policy levers: the interventions the framework's Table 7 proposes, as
things the model can actually be run with.

HOW A LEVER ACTS
----------------
Only two channels exist in this model, and every lever uses one or both.

  check_gain    multiplies the magnitude of a CHECK in one modality. A lever
                that makes an existing accountability mechanism bite harder
                acts here: antitrust enforcement, mandatory audit.

  capability    multiplies an actor's effective strength in one modality,
                which changes both how likely its own checks are to succeed
                and how likely it is to resist being checked. A lever that
                moves what an actor is able to do acts here: data rights,
                liability regimes, civic funding.

  legitimacy_repair
                added to an actor's legitimacy each tick. Only transparency
                does this, and only for the State, on the argument that being
                seen to audit is what rebuilds standing.

"""

from typing import Dict, Iterable, List, Tuple

from action_based_sim.tables import ACTORS, MODALITIES

# name -> (check_gain, capability_boost, capability_drag, legitimacy_repair)
#   check_gain        {modality: multiplier added to 1.0}
#   capability_boost  {(actor, modality): amount added to 1.0}
#   capability_drag   {(actor, modality): amount subtracted from 1.0}
LEVERS: Dict[str, dict] = {
    "antitrust": {
        "label": "Antitrust enforcement",
        "table7": "Market shocks and automation crises concentrate resource "
                  "control in corporate actors.",
        "check_gain": {"Economic": 0.90},
        "boost": {},
        "drag": {},
        "legitimacy_repair": 0.0,
    },
    "audit_transparency": {
        "label": "Audit and transparency duties",
        "table7": "Establish epistemic oversight councils to prevent "
                  "information monopoly.",
        "check_gain": {"Epistemic": 0.50},
        "boost": {},
        "drag": {},
        "legitimacy_repair": 0.04,
    },
    "data_rights": {
        "label": "Data rights and data dividends",
        "table7": "Redistributes epistemic capability toward People.",
        "check_gain": {},
        "boost": {("People", "Epistemic"): 0.45},
        "drag": {("AI", "Epistemic"): 0.18},
        "legitimacy_repair": 0.0,
    },
    "ai_liability": {
        "label": "Liability and human-in-the-loop requirements",
        "table7": "Drags AI capability where its authority is delegated "
                  "rather than held.",
        "check_gain": {},
        "boost": {},
        "drag": {("AI", "Authoritative"): 0.22, ("AI", "Physical"): 0.22},
        "legitimacy_repair": 0.0,
    },
    "civic_capacity": {
        "label": "Public-interest media and civic capacity",
        "table7": "Strengthen public media literacy and disclosure norms.",
        "check_gain": {},
        "boost": {("People", "Narrative"): 0.40, ("People", "Authoritative"): 0.20},
        "drag": {("AI", "Narrative"): 0.12},
        "legitimacy_repair": 0.0,
    },
}

ALL_LEVERS: Tuple[str, ...] = tuple(LEVERS)

# The two the prototype found did most of the work, kept as a named set so the
# comparison is reproducible rather than ad hoc.
STABILITY_ONLY: Tuple[str, ...] = ("antitrust", "audit_transparency")

MIN_CAPABILITY = 0.05   # a lever may weaken an actor but never erase it


def validate(names: Iterable[str]) -> List[str]:
    names = list(names)
    unknown = [n for n in names if n not in LEVERS]
    if unknown:
        raise ValueError(f"unknown lever(s): {unknown}; known: {ALL_LEVERS}")
    return names


def resolve(names: Iterable[str], actors: Iterable[str], strength: float = 1.0):
    """Turn a list of lever names into the three things the model consumes.

    `strength` scales every lever's magnitude at once, so a sweep can ask how
    hard policy has to push rather than only whether it is on or off.

    Returns (check_gain, capability, legitimacy_repair) where

      check_gain  {modality: multiplier}, 1.0 when no lever touches it
      capability  {actor: {modality: multiplier}}, 1.0 by default
      legitimacy_repair  float added to legitimacy each tick
    """
    names = validate(names)
    actors = list(actors)

    check_gain = {m: 1.0 for m in MODALITIES}
    capability = {a: {m: 1.0 for m in MODALITIES} for a in actors}
    repair = 0.0

    for name in names:
        lever = LEVERS[name]
        for modality, amount in lever["check_gain"].items():
            check_gain[modality] += strength * amount
        for (actor, modality), amount in lever["boost"].items():
            if actor in capability:
                capability[actor][modality] += strength * amount
        for (actor, modality), amount in lever["drag"].items():
            if actor in capability:
                capability[actor][modality] -= strength * amount
        repair += strength * lever["legitimacy_repair"]

    for actor in capability:
        for modality in capability[actor]:
            capability[actor][modality] = max(
                MIN_CAPABILITY, capability[actor][modality]
            )

    return check_gain, capability, repair


if __name__ == "__main__":
    print(f"{'lever':<22}{'channel':<34}{'effect'}")
    print("-" * 84)
    for name, lever in LEVERS.items():
        bits = []
        for m, v in lever["check_gain"].items():
            bits.append(f"check x{1 + v:.2f} in {m}")
        for (a, m), v in lever["boost"].items():
            bits.append(f"{a} +{v:.2f} in {m}")
        for (a, m), v in lever["drag"].items():
            bits.append(f"{a} -{v:.2f} in {m}")
        if lever["legitimacy_repair"]:
            bits.append(f"legitimacy +{lever['legitimacy_repair']:.2f}/tick")
        print(f"{name:<22}{lever['label']:<34}{'; '.join(bits)}")

    cg, cap, rep = resolve(ALL_LEVERS, ACTORS)
    print("\nall five together:")
    print("  check gain:", {m: round(v, 2) for m, v in cg.items() if v != 1.0})
    print("  capability:", {a: {m: round(v, 2) for m, v in d.items() if v != 1.0}
                            for a, d in cap.items()
                            if any(v != 1.0 for v in d.values())})
    print(f"  legitimacy repair: {rep:.3f}/tick")
