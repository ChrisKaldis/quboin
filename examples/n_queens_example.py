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

"""Solving N-queens problem.
"""

from networkx import Graph

from dimod import BinaryQuadraticModel
from dwave.samplers import SimulatedAnnealingSampler

from quboin.n_queens import build_n_queen
from quboin.utils import plot_graph_coloring

QUEENS = 8

def build_queens_graph(n):
    graph = Graph()
    pos = dict()
    for i in range(n):
        for j in range(n):
            graph.add_node(i*n+j)
            pos[i*n+j] = (j+1, i+1)
            #row
            for k in range(n-j-1):
                graph.add_edge(i*n+j, j+k+1+i*n)
            #col
            for m in range(n-i-1):
                graph.add_edge(i*n+j, (m+i+1)*n+j)
            #diag
            for o in range(n-i-j-1):
                graph.add_edge(i*(n+1)+o, (i+j+1)*n+(i+j+1)+o)
            for p in range(n-i-j-2):
                graph.add_edge((i+p+1)*n+i, (i+j+p+2)*n+i+j+1)
            for q in range(n-i-j-1):
                graph.add_edge((i*n+j+q+1), (i+j+1)*n+q)
            for s in range(n-i-j-2):
                graph.add_edge(
                    (i+1)*n+(s+1)*n-i-1,
                    (i+1)*n+(j+1)*n+(s+1)*n-i-1-j-1
                )

    return graph, pos


def calculate_valid_solutions(samples):
    lowest_energy_samples = samples.lowest()
    valid_solutions = lowest_energy_samples.aggregate()

    return len(valid_solutions)


def main():
    graph, pos = build_queens_graph(QUEENS)
    queen_qubo = build_n_queen(graph, QUEENS)
    queen_bqm = BinaryQuadraticModel.from_qubo(queen_qubo, offset=QUEENS**2)
    solver = SimulatedAnnealingSampler()
    samples = solver.sample(queen_bqm, num_reads=300)

    if samples.first.energy == 0.0:
        solution = samples.first
        pallete = ["#DAA765", "#834A00"]
        coloring = [(key, pallete[val]) for key, val in solution[0].items()]
        plot_graph_coloring(graph, pos, coloring, fig_size=(QUEENS+1,QUEENS+1))
        print(calculate_valid_solutions(samples))
    else:
        print("Didn't find any valid solution.")


if __name__ == "__main__":
    main()
