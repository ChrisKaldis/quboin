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

"""This script represents how to solve sudoku like graph coloring problem.
"""

from pathlib import Path
from networkx import Graph

from dimod import BinaryQuadraticModel
from dwave.samplers import TabuSampler

from quboin.graph_coloring import build_graph_coloring
from quboin.utils import plot_graph_coloring

SUDOKU_SIZE = 9

def get_sudoku_path(filename):
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "datasets" / "sudoku"
    sudoku_path = data_dir / filename

    return sudoku_path


def read_sudoku(filename):
    sudoku = list()
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            # Strip in case of whitespaces or empty lines
            stripped_line = line.strip()
            if stripped_line:
                sudoku_line = stripped_line.split()
                sudoku.append([int(i) for i in sudoku_line])

    return sudoku


def build_sudoku_graph():
    graph = Graph()
    for r in range(SUDOKU_SIZE):
        for c in range(SUDOKU_SIZE):
            graph.add_node(r*SUDOKU_SIZE+c)

    for r1 in range(SUDOKU_SIZE):
        for c1 in range(SUDOKU_SIZE):
            for r2 in range(SUDOKU_SIZE):
                for c2 in range(SUDOKU_SIZE):
                    if (r1, c1) == (r2, c2):
                        continue
                    same_row = r1 == r2
                    same_col = c1 == c2
                    same_box = (r1 // 3, c1 // 3) == (r2 // 3, c2 // 3)
                    if same_row or same_col or same_box:
                        graph.add_edge(r1*SUDOKU_SIZE+c1, r2*SUDOKU_SIZE+c2)

    return graph


def get_sudoku_pos():
    position = dict()
    for i in range(SUDOKU_SIZE):
        for j in range(SUDOKU_SIZE):
            position[i*SUDOKU_SIZE+j] = (j+1, i+1)

    return position


def apply_initial_values(sudoku_bqm, sudoku_array):
    for i in range(SUDOKU_SIZE):
        for j in range(SUDOKU_SIZE):
            # check if it is given the value of the cell.
            if sudoku_array[i][j] > 0:
                cell_idx = (i*SUDOKU_SIZE+j)
                for k in range(SUDOKU_SIZE):
                    if sudoku_array[i][j] == k+1:
                        sudoku_bqm.fix_variable(cell_idx*SUDOKU_SIZE+k, 1)
                    else:
                        sudoku_bqm.fix_variable(cell_idx*SUDOKU_SIZE+k, 0)


def translate_solution(solution, sudoku_array):
    node_colors = list()
    # We translate every variable that is true into a cell 
    # with a certain color.
    for i, value in solution.samples()[0].items():
        if value == 1:
            node_idx = i // SUDOKU_SIZE
            color_idx = i % SUDOKU_SIZE
            node_colors.append((node_idx, color_idx+1))
    # Insert the initial values to the solution.
    for i in range(SUDOKU_SIZE):
        for j in range(SUDOKU_SIZE):
            if sudoku_array[i][j] > 0:
                node_colors.insert(
                    i*SUDOKU_SIZE+j, (i*SUDOKU_SIZE+j, sudoku_array[i][j])
                )

    return node_colors


def print_sudoku(sudoku):
    for i in range(SUDOKU_SIZE*SUDOKU_SIZE):
        print(f"{sudoku[i][1]}", end=" ")
        if (i + 1) % (SUDOKU_SIZE) == 0:
            print("")


def main():
    file = get_sudoku_path("first.txt")
    sudoku_array = read_sudoku(file)
    sudoku_graph = build_sudoku_graph()
    sudoku_qubo = build_graph_coloring(sudoku_graph, 9)
    sudoku_bqm = BinaryQuadraticModel.from_qubo(
        sudoku_qubo, sudoku_graph.number_of_nodes()
    )
    apply_initial_values(sudoku_bqm, sudoku_array)

    sampler = TabuSampler()
    samples = sampler.sample(sudoku_bqm, num_reads=100)
    print(samples.aggregate())

    if samples.first.energy == 0:
        sudoku_color = translate_solution(samples, sudoku_array)
        print_sudoku(sudoku_color)
        plot_graph_coloring(
            sudoku_graph, get_sudoku_pos(), sudoku_color, fig_size=(10,10)
        )
    else:
        print("Optimal solution was not found.")


if __name__ == "__main__":
    main()
