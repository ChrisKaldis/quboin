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

"""An extended clique script to solve larger problems.

Evaluates the quality of solution of the `build_clique_k` function.
User can select between two samplers, `TabuSampler` from `dwave.samplers`
and `SimulatedAnnealingSampler` from `neal` library. You can select any
of the DIMACS graph files that works with `read_dimacs_graph` function
as long as it is in the ../datasets/graphs/ path.
"""

import argparse

from pathlib import Path
from networkx.drawing import random_layout

from dimod import BinaryQuadraticModel
from neal import SimulatedAnnealingSampler
from dwave.samplers import TabuSampler

from quboin.utils import read_dimacs_graph, plot_graph_coloring
from quboin.clique import build_clique_k


def parse_arguments():
    # Set up argument parser.
    parser = argparse.ArgumentParser(
        description = "Arguments for building k-clique problem."
    )
    parser.add_argument(
        "--filename",
        "-f",
        type=str,
        default="le450_5a.col",
        help=("The name of a file located in datasets/graphs folder.")
    )
    parser.add_argument(
        "--solver",
        "-s",
        type=str,
        default="sa",
        choices=["sa", "ts"],
        help=(
            "solver must be either sa (Simulated Annealing)"
            "which is the default or ts (Tabu Sampler)."
        )
    )
    parser.add_argument(
        "--kappa",
        "-k",
        type=int,
        default=5,
        help=("Size of clique.")
    )
    parser.add_argument(
        "--alpha",
        "-a",
        type=int,
        default=6,
        help=("Alpha constant in QUBO, check build_clique_k.")
    )
    parser.add_argument(
        "--beta",
        "-b",
        type=int,
        default=1,
        help=("Beta constant in QUBO, check build_clique_k.")
    )
    parser.add_argument(
        "--reads",
        "-r",
        type=int,
        default=100,
        help=("Number of reads for the Sampler.")
    )

    return parser.parse_args()


def get_file(filename):
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "datasets" / "graphs"
    graph_path = data_dir / filename

    return graph_path


def solve_problem(solver, bqm, reads):
    if solver == "sa":
        solver = SimulatedAnnealingSampler()
        samples = solver.sample(bqm, num_reads=reads)
    elif solver == "ts":
        solver = TabuSampler()
        samples = solver.sample(bqm, num_reads=reads)
    print(samples.aggregate())

    return samples


def show_best_solution(samples, pos):
    solution = samples.first
    pallete = ["#ffa3a3", "#ff0000"]
    coloring = [(key, pallete[val]) for key, val in solution[0].items()]
    plot_graph_coloring(graph, pos, coloring, (100, 100))


if __name__ == "__main__":
    args = parse_arguments()
    file = get_file(args.filename)
    graph = read_dimacs_graph(file)
    clique_qubo = build_clique_k(graph, args.kappa, args.alpha, args.beta)
    clique_bqm = BinaryQuadraticModel.from_qubo(
        clique_qubo,
        offset=(
            args.alpha*(args.kappa**2)
            + (args.beta*args.kappa*(args.kappa-1))/2
            )
    )
    samples = solve_problem(args.solver, clique_bqm, args.reads)
    show_best_solution(samples, random_layout(graph))
