import csv
from collections import Counter
from statistics import mean, stdev

from action_based_sim.config import SimulationConfig
from action_based_sim.environment import Environment
from action_based_sim.tables import ACTORS, MODALITIES


N_RUNS = 100
OUTPUT_FILE = "experiment_results.csv"


def run_one(seed):
    """Run one complete simulation and return the results."""

    config = SimulationConfig(seed=seed)
    env = Environment(config)

    history = env.run()
    final = history[-1]

    result = {
        "seed": seed,
        "aspiration": final["aspiration"],
        "stability": final["stability"],
        "quadrant": final["quadrant"],
        "number_of_shocks": sum(
            1 for record in history if record["shock"] is not None
        ),
    }

    # Save every actor's final share in every modality.
    for modality in MODALITIES:
        for actor in ACTORS:
            column_name = f"{actor}_{modality}"
            result[column_name] = final["state"]["P"][modality][actor]

    return result


def check_reproducibility():
    """The same seed should produce exactly the same simulation."""

    first = run_one(42)
    second = run_one(42)

    assert first == second, "Same seed produced different results."

    print("Reproducibility check passed: seed 42 gives identical results.")


def run_many(n_runs):
    """Run the simulation with seeds 0, 1, 2, ..., n_runs - 1."""

    results = []

    for seed in range(n_runs):
        result = run_one(seed)
        results.append(result)

    return results


def save_results(results, filename):
    """Save all individual simulation results to a CSV file."""

    fieldnames = list(results[0].keys())

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def print_summary(results):
    """Print a simple summary across all runs."""

    aspirations = [result["aspiration"] for result in results]
    stabilities = [result["stability"] for result in results]

    quadrant_counts = Counter(result["quadrant"] for result in results)

    print("\n----- EXPERIMENT SUMMARY -----")
    print(f"Number of runs: {len(results)}")

    print(
        f"\nAspiration: mean={mean(aspirations):.3f}, "
        f"std={stdev(aspirations):.3f}"
    )

    print(
        f"Stability:  mean={mean(stabilities):.3f}, "
        f"std={stdev(stabilities):.3f}"
    )

    print("\nFinal quadrant frequencies:")

    for quadrant, count in quadrant_counts.items():
        percentage = count / len(results) * 100
        print(f"{quadrant}: {count} ({percentage:.1f}%)")

    print("\nMean final power shares:")

    for modality in MODALITIES:
        print(f"\n{modality}")

        for actor in ACTORS:
            column_name = f"{actor}_{modality}"

            values = [
                result[column_name]
                for result in results
            ]

            print(
                f"  {actor:<12} "
                f"mean={mean(values):.3f}, "
                f"std={stdev(values):.3f}"
            )    

def main():
    check_reproducibility()
    results = run_many(N_RUNS)
    save_results(results, OUTPUT_FILE)
    print_summary(results)
    print(f"\nFull results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()