"""Basic utility functions for the quboin package.

Includes helper functions to:
-Read integer input files,
-Finds the best valid solution of knapsack,
"""

import os
from networkx import Graph

from dimod import SampleSet


def read_integers_from_file(filename: str) -> list[int]:
    """Read integers from a text file where each line contains one integer.

    This function is used in order to read the data used in knapsack example.

    Args:
        filename: Path to the text file containing one integer per line.

    Returns:
        A list of integers parsed from the file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If a line doesn't contain a valid integer.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file '{filename}' was not found.")

    integers: list[int] = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            # Strip in case of whitespaces or empty lines
            stripped_line = line.strip()
            if stripped_line:
                try:
                    integers.append(int(stripped_line))
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid integer found in {filename}: {exc}"
                    ) from exc

    return integers


def find_valid_knapsack_solution(
        samples_set: SampleSet,
        weights: list[int],
        profits: list[int],
        capacity: int,
    ) -> tuple[SampleSet, int, int]:
    """Search in a `SampleSet` for the first valid knapsack solution.

    A `dimod.SampleSet` from a sampler contains samples with "good" 
    solutions. It is necessary to check if some samples don't satisfy
    the capacity penalty and find the best one if there is one.

    Args:
        samples_set: `SampleSet` containing binary solutions.
        weights: List with the weight of each object.
        profits: List with the profit of each object.
        capacity: Capacity of knapsack.

    Returns:
        A tuple with the first valid solution found together with
        its weight and profit.
    """
    n = len(weights)
    for sample in samples_set.data():
        weight = 0
        profit = 0

        for key, val in sample[0].items():
            # in case of encoding with aux bits,
            # stop counting when items end.
            if key == n:
                break
            if val:
                weight += weights[key]
                profit += profits[key]

        # if current weight doesn't exceed the
        # capacity penalty return the solution.
        if weight <= capacity:
            return sample, weight, profit


def read_dimacs_graph(filename: str) -> Graph:
    """Read a graph from a DIMACS file.

    Args:
        filename: Path to the DIMACS-formatted file.

    Returns:
        A Networkx graph created by the edge list in the file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If an edge line is not formatted properly.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file '{filename}' was not found.")

    G = Graph()
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            # check if this line is empty or a comment.
            if not line or line.startswith("c"):
                # Skip comments and empty lines.
                continue

            parts = line.split()
            # check if this line is refered to graph's edge.
            if parts[0] == "e":
                if len(parts) != 3:
                    raise ValueError(f"Malformed edge line: '{line}'")
                try:
                    u, v = map(int, parts[1:3])
                    G.add_edge(u, v)
                except ValueError as e:
                    raise ValueError(f"Invalid edge endpoints in line: '{line}'") from e

    return G
