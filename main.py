"""This is a baseline run. Unvalidated, therefore should be treated as provisional."""

from action_based_sim.config import SimulationConfig
from action_based_sim.environment import Environment


def main():
    config = SimulationConfig()
    env = Environment(config)
    history = env.run()

    print(f"{'tick':>4}  {'aspiration':>10}  {'stability':>9}  quadrant")
    for record in history:
        print(
            f"{record['tick']:>4}  {record['aspiration']:>10.3f}  "
            f"{record['stability']:>9.3f}  {record['quadrant']}"
        )

    final = history[-1]
    print("\nFinal quadrant:", final["quadrant"])
    print("Final power shares:")
    for modality, shares in final["state"]["P"].items():
        row = ", ".join(f"{actor}={share:.2f}" for actor, share in shares.items())
        print(f"  {modality:<14} {row}")


if __name__ == "__main__":
    main()
