"""QUBO formulation for the graph coloring problem.

This module provides a function to construct a QUBO model to find
whether it is possible to color a graph with k colors in a way
that every node connected with every other node with an edge has
different color.
"""

from networkx import Graph


def build_graph_coloring(
        graph: Graph,
        num_colors: int,
        alpha: int = 1,
        beta: int = 1,
) -> dict[tuple[int, int], int]:
    """Constructs a QUBO for the graph coloring problem.

    This model contains two constraints. The first one applies
    a penalty of size alpha when it is selected more than one color 
    for a vertex (each node has exactly one color).
    The second one applies a penalty size beta when it is selected 
    the same color for two neighboring vertices. Usually there is
    no particular reason for selecting different alpha and beta. 

    Args:
        graph: A `networkx` undirected graph.
        num_colors: Size of the available colors.
        alpha: Penalty coefficient for single color constraint.
        beta: Penalty coefficient for different colors of adjacent nodes.

    Returns:
        A dictionary representing the QUBO matrix, where keys 
        are index pairs and values are the corresponding coefficients.
    """
    qubo: dict[tuple[int, int], int] = {}
    node_to_index = {node: i for i, node in enumerate(sorted(graph.nodes()))}

    for node, idx in node_to_index.items():
        node_start = idx * num_colors
        # Single-color constraint,
        for color in range(num_colors):
            pos = node_start + color
            qubo[(pos,pos)] = -alpha
            for c in range(color+1, num_colors):
                col_pos = node_start + c
                qubo[(pos,col_pos)] = 2 * alpha
        # Adjacency constraint,
        for neighbor in graph.neighbors(node):
            neighbor_idx = node_to_index[neighbor]
            if neighbor_idx > idx:
                for color in range(num_colors):
                    row_pos = node_start + color
                    col_pos = neighbor_idx * num_colors + color
                    qubo[(row_pos, col_pos)] = beta

    return qubo
