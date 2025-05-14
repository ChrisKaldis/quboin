"""
An example how to use quboin in order to create and solve a 0/1 Knapsack problem.

With a large amount of samples (e.g. 1000) it can find the optimal solution
for the first 6 datasets.

Data:
https://people.sc.fsu.edu/~jburkardt/datasets/knapsack_01/knapsack_01.html
"""

from pathlib import Path
from dwave.samplers import PathIntegralAnnealingSampler
from dimod import BinaryQuadraticModel

from quboin.knapsack import load_knapsack_data, build_knapsack_qubo
from quboin.utils import read_integers_from_file, find_valid_knapsack_solution


def get_files(capacity_file, weights_file, profits_file, solution_file):
    """Data path of files."""
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "datasets" / "knapsack"
    capacity_path = data_dir / capacity_file
    weights_path = data_dir / weights_file
    profits_path = data_dir / profits_file
    solution_path = data_dir / solution_file

    return capacity_path, weights_path, profits_path, solution_path


def solve_qubo(qubo, samples):
    """Sampling a given qubo."""
    sampler = PathIntegralAnnealingSampler()
    knapsack_bqm = BinaryQuadraticModel.from_qubo(qubo)
    samples = sampler.sample(knapsack_bqm, num_reads=samples)

    return samples.aggregate()


def optimal(solution, solution_file):
    """Check if the solution is the best."""
    optimal_solution = read_integers_from_file(solution_file)
    n = len(optimal_solution)
    for key, val in solution.items():
        if key == n:
            break
        if val != optimal_solution[key]:
            return False

    return True


def solve_problem():
    """A simple way to solve knapsack problem using quboin."""
    # get the path of the data.
    c_file, w_file, p_file, s_file = get_files(
        "p06_c.txt", "p06_w.txt", "p06_p.txt", "p06_s.txt")
    # get the lists with the data.
    c, w, p = load_knapsack_data(c_file, w_file, p_file)
    # create QUBO formulation.
    k_qubo = build_knapsack_qubo(w, p, c)
    # use a sampler.
    samples = solve_qubo(k_qubo, 1000)
    # find the valid solution with the smallest energy.
    solution, weight, profit = find_valid_knapsack_solution(
        samples, w, p, c)
    # check if there is a valid one and if it is the best.
    if solution is None:
        print("No valid solution found")
        return
    elif optimal(solution[0], s_file):
        print("The solution is optimal.")
    # show the sample that is found with its data.
    print(f"{solution}, with weight:{weight} and profit:{profit}")


def main():
    solve_problem()


if __name__ == "__main__":
    main()
