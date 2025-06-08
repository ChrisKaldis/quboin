# Copyright 2025 Christos Kaldis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example how to use quboin for solving 0/1 Knapsack problem.

Data:
https://people.sc.fsu.edu/~jburkardt/datasets/knapsack_01/knapsack_01.html
"""

from argparse import ArgumentParser
from pathlib import Path

from dimod import BinaryQuadraticModel
from dwave.samplers import SimulatedAnnealingSampler

from quboin.knapsack import (
    load_knapsack_data, build_knapsack, build_knapsack_with_aux
) 
from quboin.utils import (
    read_integers_from_file, find_valid_knapsack_solution
)


def parse_arguments():
    # Set up argument parser.
    parser = ArgumentParser(
        description = "Argument for the Knapsack problem."
    )
    parser.add_argument(
        "--aux",
        "-aux",
        type=int,
        default=1,
        help=(
            "There are two formulation, the one with auxiliary bits,"
            " and one that is simplified."
        )
    )
    parser.add_argument(
        "--filename",
        "-f",
        type=str,
        default="p01",
        choices=["p01","p02","p03","p04","p05","p06","p07","p08"],
        help=("Available files of knapsack small examples.")
    )

    return parser.parse_args()


def get_files(file):
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "datasets" / "knapsack"
    capacity_path = data_dir / (file + "_c.txt")
    weights_path = data_dir / (file + "_w.txt")
    profits_path = data_dir / (file + "_p.txt")
    solution_path = data_dir / (file + "_s.txt")

    return capacity_path, weights_path, profits_path, solution_path


def create_qubo(aux, weights, profits, cap):
    if aux == 1:
        a = max(profits)+1
        b = 1
        qubo = build_knapsack_with_aux(weights, profits, cap, a, b)
        offset = cap
    else:
        a = max(profits)
        qubo = build_knapsack(weights, profits, cap, a, 1)
        offset = a*cap**2

    return BinaryQuadraticModel.from_qubo(qubo, offset)


def solve_qubo(bqm, samples):
    sampler = SimulatedAnnealingSampler()
    samples = sampler.sample(bqm, num_reads=samples)

    return samples.aggregate()


def optimal(solution, solution_file):
    optimal_solution = read_integers_from_file(solution_file)
    n = len(optimal_solution)
    for key, val in solution.items():
        # stop before aux variables
        if key == n:
            break
        if val != optimal_solution[key]:
            return False

    return True


def main():
    args = parse_arguments()
    c_file, w_file, p_file, s_file = get_files(args.filename)
    c, w, p = load_knapsack_data(c_file, w_file, p_file)
    knapsack_bqm = create_qubo(args.aux, w, p, c)
    samples = solve_qubo(knapsack_bqm, 1000)
    print(samples.aggregate())

    solution, s_w, s_p = find_valid_knapsack_solution(samples, w, p, c)
    if solution is None:
        print("No valid solution found")
    elif optimal(solution[0], s_file):
        print("The solution is optimal.")

    var = [int(val) for _, val in solution[0].items()]
    print(f"{var} with weight:{s_w} and profit:{s_p}\n"
          f"{solution[2]} samples with {solution[1]} energy were found.")


if __name__ == "__main__":
    main()
