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

"""Graph coloring of a small graph with 4 nodes.

User can decide the color of one node. This is useful in order to
understand how the implementation of sudoku works.
"""

from argparse import ArgumentParser
from networkx import Graph

from dimod import BinaryQuadraticModel
from dwave.samplers import SimulatedAnnealingSampler

from quboin.graph_coloring import build_graph_coloring
from quboin.utils import plot_graph_coloring


def parse_arguments():
    # Set up argument parser.
    parser = ArgumentParser(
        description = "Arguments for building min vertex cover problem."
    )
    parser.add_argument(
        "--node",
        "-n",
        type=str,
        default="-1",
        choices=["-1", "0", "1", "2", "3"],
        help=(
            "Select which of the 4 nodes of the graph "
            "you want to give a certain color."
        )
    )
    parser.add_argument(
        "--color",
        "-c",
        type=str,
        default="0",
        choices=["0", "1", "2"],
        help=(
            "you can select between 3 colors."
        )
    )

    return parser.parse_args()


def get_graph():
    graph = Graph()
    graph.add_edges_from([
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 2)
    ])
    pos = {
        1: (1, 2.5),
        2: (2, 2.6),
        3: (3, 5),
        4: (3, 1)
    }

    return graph, pos


def fix_variables(bqm, node, color):
    num_colors = 3
    if int(node) >= 0:
        idx = int(node) * num_colors
        for i in range(num_colors):
            if i == int(color):
                bqm.fix_variable(idx+i, 1)
            else:
                bqm.fix_variable(idx+i, 0)


def find_colors(solution, node, color):
    pallete = ["#ff0000", "#1dfc00", "#0084ff"]
    node_colors = list()
    num_colors = 3
    # solution it's a SampleSet with only one item.
    for i, value in solution.samples()[0].items():
        if value == 1:
            node_idx = i // num_colors
            color_idx = i % num_colors
            node_colors.append((node_idx, pallete[color_idx]))

    if int(node) >= 0:
        node_colors.insert(int(node),(int(node), pallete[int(color)]))

    return node_colors


def main():
    args = parse_arguments()
    graph, pos = get_graph()
    qubo = build_graph_coloring(graph, 3)
    bqm = BinaryQuadraticModel.from_qubo(qubo, offset=graph.number_of_nodes())
    fix_variables(bqm, args.node, args.color)
    sampler = SimulatedAnnealingSampler()
    samples = sampler.sample(bqm, num_reads=100)
    print(samples.aggregate())
    node_colors = find_colors(samples, args.node, args.color)
    plot_graph_coloring(graph, pos, node_colors, node_size=1000)


if __name__ == "__main__":
    main()
