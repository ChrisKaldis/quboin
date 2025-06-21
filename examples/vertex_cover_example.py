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

"""Solve Min vertex cover problem for two small graphs.

User can select between two algorithms, the brute force solution that
calculates the energy of all possible states or simulated annealing. 
A plot with the solution of graph is also presented.
"""

import logging

from argparse import ArgumentParser
from networkx import Graph

from dimod import BinaryQuadraticModel, ExactSolver
from neal import SimulatedAnnealingSampler

from quboin.vertex_cover import build_min_vertex_cover
from quboin.utils import plot_graph_coloring


def parse_arguments():
    # Set up argument parser.
    parser = ArgumentParser(
        description = "Arguments for building min vertex cover problem."
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
    parser.add_argument(
        "--graph",
        "-g",
        type=str,
        default="2",
        choices=["1", "2"],
        help=(
            "you can select between 2 graphs with 6 nodes."
        )
    )

    return parser.parse_args()


def get_first_graph():
    graph = Graph()
    graph.add_edges_from([
        (0, 1),
        (0, 2),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1)
    ])
    pos = {
        0: (1.2, 3.5),
        1: (2, 4),
        2: (1.8, 2.5),
        3: (3.5, 4.5),
        4: (3.3, 3.5),
        5: (3, 2.5)
    }

    return graph, pos


def get_second_graph():
    graph = Graph()
    graph.add_edges_from([
        (0, 1),
        (0, 2),
        (1, 3),
        (2, 1),
        (2, 4),
        (3, 4),
        (3, 5)
    ])
    pos = {
        0: (1, 2.5),
        1: (2.1, 3.1),
        2: (1.9, 2.1),
        3: (3.2, 3.2),
        4: (2.8, 2),
        5: (4, 3.5)
    }

    return graph, pos


def select_graph(graph_choice):
    if graph_choice == "1":
        graph, pos = get_first_graph()
    else:
        graph, pos = get_second_graph()

    return graph, pos


def solve_problem(solver_choice, bqm):
    if solver_choice == "sa":
        solver = SimulatedAnnealingSampler()
        samples = solver.sample(bqm, num_reads=100)
        samples = samples.aggregate()
    else:
        solver = ExactSolver()
        samples = solver.sample(bqm)

    return samples


def main():
    logging.basicConfig(
        filename="vertex_cover.log",
        filemode="w",
        level=logging.INFO,
        format="%(message)s"
    )
    logging.StreamHandler.terminator = ""
    logger = logging.getLogger(__name__)

    args = parse_arguments()
    graph, pos = select_graph(args.graph)
    o = 2 * graph.number_of_edges()
    qubo = build_min_vertex_cover(graph)
    bqm = BinaryQuadraticModel.from_qubo(qubo, offset=o)
    samples = solve_problem(args.solver, bqm)
    logger.info("%s",samples)
    solution = samples.first
    pallete = ["#ffa3a3", "#ff0000"]
    coloring = [(key, pallete[val]) for key, val in solution[0].items()]
    plot_graph_coloring(graph, pos, coloring, node_size=1000)


if __name__ == "__main__":
    main()
