"""
An example how to use quboin in order to create and solve a 0/1 Knapsack problem.

Data:
https://people.sc.fsu.edu/~jburkardt/datasets/knapsack_01/knapsack_01.html
"""

from pathlib import Path
from dwave.samplers import PathIntegralAnnealingSampler
from dimod import BinaryQuadraticModel
from neal import SimulatedAnnealingSampler

from quboin.knapsack import load_knapsack_data
from quboin.utils import read_integers_from_file
from quboin.knapsack import build_knapsack_qubo, build_knapsack_qubo_aux


def get_files(capacity_file, weights_file, profits_file, solution_file):
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "datasets" / "knapsack"
    capacity_path = data_dir / capacity_file
    weights_path = data_dir / weights_file
    profits_path = data_dir / profits_file
    solution_path = data_dir / solution_file

    return capacity_path, weights_path, profits_path, solution_path


def solve_qubo(qubo, samples, choose):
    if choose == 1:
        sampler = SimulatedAnnealingSampler()
    elif choose == 2:
        sampler = PathIntegralAnnealingSampler()
    knapsack_bqm = BinaryQuadraticModel.from_qubo(qubo)
    samples = sampler.sample(knapsack_bqm, num_reads=samples)

    return samples.aggregate()


def find_valid_solution(samples_set, capacity, weights, profits):
    for sample in samples_set.data():
        weight = 0
        profit = 0
        n = len(weights)
        for key, val in sample[0].items():
            if key == n:
                break
            if val:
                weight += weights[key]
                profit += profits[key]
        if weight <= capacity:
            return sample, weight, profit


def optimal(solution, solution_file):
    optimal_solution = read_integers_from_file(solution_file)
    n = len(optimal_solution)
    for key, val in solution.items():
        if key == n:
            break
        if val != optimal_solution[key]:
            return False

    return True


def solve_problem(with_aux = 0):
    # get the path of the data.
    c_file, w_file, p_file, s_file = get_files(
        "p01_c.txt", "p01_w.txt", "p01_p.txt", "p01_s.txt")
    # create lists with the data.
    c, w, p = load_knapsack_data(c_file, w_file, p_file)
    # choose QUBO formulation.
    if with_aux:
        k_qubo = build_knapsack_qubo_aux(w, p, c, 2*max(p), max(p))
    else:
        k_qubo = build_knapsack_qubo(w, p, c)
    # use a sampler.
    samples = solve_qubo(k_qubo, 1000, 2)
    #print(samples)
    # find the valid solution with the smallest energy. 
    solution, weight, profit = find_valid_solution(samples, c, w, p)
    
    if optimal(solution[0], s_file):
        print("The solution is optimal.")
    
    print(solution, weight, profit)


def main():
    solve_problem(1)


if __name__ == "__main__":
    main()
