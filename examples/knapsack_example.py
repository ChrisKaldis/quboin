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

"""Small example of 0/1 Knapsack problem using quboin.

This is a very simple example that shows the better solution of the
knapsack problem with aux variables. The case is that the best solution
is not near the capacity of the knapsack but instead quite smaller.
"""

from argparse import ArgumentParser

from dimod import BinaryQuadraticModel
from dwave.samplers import SimulatedAnnealingSampler

from quboin.knapsack import build_knapsack_with_aux, build_knapsack


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

    return parser.parse_args()


def get_problem_data():
    weights = [12, 1, 1, 2, 4]
    profits = [4, 2, 1, 2, 10]
    # p/w = [0.3, 2, 1, 1, 2.5], pick up oder -> 4, 2, 3, 1, 0  
    capacity = 15

    return weights, profits, capacity


def select_qubo(auxilliary, weights, profits, capacity):
    if auxilliary == 1:
        qubo = build_knapsack_with_aux(
            weights, profits, capacity, max(profits)
        )
    else:
        qubo = build_knapsack(
            weights, profits, capacity, max(profits), 1
        )

    return qubo


def main():
    args = parse_arguments()
    w, p, c = get_problem_data()
    qubo = select_qubo(args.aux, w, p, c)
    bqm = BinaryQuadraticModel.from_qubo(qubo)
    sampler = SimulatedAnnealingSampler()
    samples = sampler.sample(bqm, num_reads=100)
    print(samples.aggregate())


if __name__ == "__main__":
    main()
