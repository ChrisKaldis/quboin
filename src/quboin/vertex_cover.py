"""QUBO formulation for the min vertex cover problem.

This module provides a function to construct a QUBO model to find
the minimum number of vertices such that every edge is incident to 
at least one selected node.
"""

from networkx import Graph


def build_min_vertex_cover(
        graph: Graph,
        alpha: int = 2,
        beta: int = 1,
    ) -> dict[tuple[int, int], int]:
    """Constructs a QUBO for the min vertex cover optimization problem.

    We want to minimize the selected nodes subject to every edge has
    at least one of the selected nodes. B < A in order to find valid
    solution.

    Args:
        graph: A `networkx` undirected graph
        alpha: Penalty coefficient for the constraint
        beta: Coefficient of the optimization term.

    Returns:
        A dictionary representing the QUBO matrix, where keys 
        are index pairs and values are the corresponding coefficients.
    """
    qubo: dict[tuple[int, int], int] = {}
    node_to_index = {node: idx for idx, node in enumerate(sorted(graph.nodes()))}

    for node, i in node_to_index.items():
        node_degree = graph.degree(node)
        qubo[(i, i)] = beta - alpha * node_degree

    for u, v in graph.edges():
        i = node_to_index[u]
        j = node_to_index[v]
        if i > j:
            i, j = j, i
        qubo[(i, j)] = alpha

    return qubo
