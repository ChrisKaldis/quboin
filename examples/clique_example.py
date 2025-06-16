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

User can select between three algorithms, the brute force solution that
calculates the energy of all possible states or simulated annealing,
tabu search. A plot with the solution of graph is also presented.
"""

import logging

from argparse import ArgumentParser
from networkx import Graph
from networkx.drawing import kamada_kawai_layout
from networkx.generators import caveman_graph, barbell_graph

from dimod import BinaryQuadraticModel, ExactSolver
from dwave.samplers import TabuSampler, SimulatedAnnealingSampler

from quboin.clique import build_clique_k
from quboin.utils import plot_graph_coloring


def parse_arguments():
    # Set up argument parser.
    parser = ArgumentParser(
        description = "Arguments for building k-clique problem."
    )
    parser.add_argument(
        "--solver",
        "-s",
        type=str,
        default="ts",
        choices=["sa", "es", "ts"],
        help=(
            "solver must be either sa (Simulated Annealing)"
            ", es (Exact Solver), ts (Tabu Sampler)."
        )
    )
    parser.add_argument(
        "--graph",
        "-g",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help=(
            "Choose type of graph, 0 for a simple graph,"
            "1 for caveman graph and 2 for barbell."
        )
    )
    parser.add_argument(
        "--l",
        "-l",
        type=int,
        default=20,
        help=("Number of cliques, used in caveman graph.")
    )
    parser.add_argument(
        "--k",
        "-k",
        type=int,
        default=10,
        help=("Size of clique.")
    )
    parser.add_argument(
        "--reads",
        "-r",
        type=int,
        default=1000,
        help=("Number of reads for the sampler.")
    )

    return parser.parse_args()


def get_graph(graph_pick, lamda, k):
    if graph_pick == 0:
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
    elif graph_pick == 1:
        graph = caveman_graph(lamda, k)
        nodes_position = kamada_kawai_layout(graph)
    elif graph_pick == 2:
        graph = barbell_graph(k, lamda)
        nodes_position = kamada_kawai_layout(graph)

    return graph, nodes_position


def solve_problem(solver, bqm, reads, logger):
    if solver == "sa":
        sampler = SimulatedAnnealingSampler()
        samples = sampler.sample(bqm, num_reads=reads)
        logger.info("%s", samples.aggregate())
    elif solver == "es":
        sampler = ExactSolver()
        samples = sampler.sample(bqm)
        logger.info("%s", samples)
    elif solver == "ts":
        sampler = TabuSampler()
        samples = sampler.sample(bqm, num_reads=reads)
        logger.info("%s", samples.aggregate())

    return samples


def is_solution_zero(sampleset):
    if sampleset.first.energy == 0.0:
        return True
    else:
        return False


def main():
    logging.basicConfig(level = logging.INFO, format = "%(message)s")
    logger = logging.getLogger(__name__)

    args = parse_arguments()
    graph, pos = get_graph(args.graph, args.l, args.k)
    b = 1
    a = b * args.k + 1
    offset = a*args.k**2 + b*args.k*(args.k-1)*0.5

    clique_qubo = build_clique_k(graph, k=args.k, alpha=a, beta=b)
    clique_bqm = BinaryQuadraticModel.from_qubo(clique_qubo, offset)
    samples = solve_problem(args.solver, clique_bqm, args.reads, logger)

    if is_solution_zero(samples):
        solution = samples.first
        pallete = ["#ffa3a3", "#ff0000"]
        coloring = [(key, pallete[val]) for key, val in solution[0].items()]
        plot_graph_coloring(graph, pos, coloring, (2*args.k, 2*args.k))
        logger.info("An image in graph_plot.png created.")
    else:
        logger.info("Optimal solution wasn't found.")


if __name__ == "__main__":
    main()
