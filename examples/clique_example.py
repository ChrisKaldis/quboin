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

"""Solve k-clique problem for a small graph.

User can select between two algorithms, the brute force solution that
calculates the energy of all possible states or simulated annealing.
A plot with the solution of graph is also presented.
"""

import argparse
from networkx import Graph

from dimod import BinaryQuadraticModel, ExactSolver
from neal import SimulatedAnnealingSampler

from quboin.clique import build_clique_k
from quboin.utils import plot_graph_coloring


def parse_arguments():
    # Set up argument parser.
    parser = argparse.ArgumentParser(
        description = "Arguments for building k-clique problem."
    )
    parser.add_argument(
        "--solver",
        "-s",
        type=str,
        default="sa",
        choices=["sa", "es"],
        help=(
            "solver must be either sa (Simulated Annealing)"
            "which is the default or es (Exact Solver)."
        )
    )

    return parser.parse_args()


def get_graph():
    graph = Graph()
    graph.add_edges_from([
            (1, 2), (1, 5),
            (2, 3), (2, 5),
            (3, 4),
            (4, 5), (4, 6)
        ])
    # used for drawing the graph.
    nodes_position = {
        1: (4, 3),
        2: (3.2, 2.1),
        3: (1.2, 1.8),
        4: (1.5, 4.2),
        5: (3.2, 4.3),
        6: (0.5, 4.5)
    }

    return graph, nodes_position


def solve_problem(solver, bqm):
    if solver == "sa":
        sampler = SimulatedAnnealingSampler()
        samples = sampler.sample(bqm, num_reads=100)
        print(samples.aggregate())
    elif solver == "es":
        sampler = ExactSolver()
        samples = sampler.sample(bqm)
        print(samples)

    return samples


def is_solution_zero(sampleset):
    if sampleset.first.energy == 0.0:
        return True
    else:
        return False


def main():
    args = parse_arguments()
    graph, pos = get_graph()
    k = 3
    b = 1
    a = b * k
    o = a*k**2 + b*k*(k-1)/2

    qubo = build_clique_k(graph, k=k, alpha=a, beta=b)
    clique_bqm = BinaryQuadraticModel.from_qubo(qubo, offset=o)
    samples = solve_problem(args.solver, clique_bqm)

    if is_solution_zero(samples):
        solution = samples.first
        pallete = ["#ffa3a3", "#ff0000"]
        coloring = [(key, pallete[val]) for key, val in solution[0].items()]
        plot_graph_coloring(graph, pos, coloring)
    else:
        print("Optimal solution wasn't found.")


if __name__ == "__main__":
    main()
