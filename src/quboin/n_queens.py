"""QUBO formulation for the N-Queen problem.
"""

from networkx import Graph


def build_n_queen(
        graph: Graph,
        n: int = 8,
        alpha: int = 1,
    ) -> dict[tuple[int, int], int]:
    """Constructs a QUBO for n queens problem.

    This model contains two constraints. The first one applies
    a penalty when it is selected more than n queens on the board. 
    The second one applies a penalty when two nodes re selected
    that are connected through an edge. 

    Args:
        graph: A `networkx` undirected graph.
        n: Number of queens.
        alpha: Penalty coefficient for the constraints.

    Returns:
        A dictionary representing the QUBO matrix, where keys 
        are index pairs and values are the corresponding coefficients.
    """
    qubo: dict[tuple[int, int], int] = {}
    node_to_index = {node: idx for idx, node in enumerate(sorted(graph.nodes()))}
    node_number = graph.number_of_nodes()

    for i in range(node_number):
        qubo[(i, i)] = alpha * (1 - 2*n)
        for j in range(i+1, node_number):
            qubo[(i, j)] = 2 * alpha

    for u, v in graph.edges():
        i = node_to_index[u]
        j = node_to_index[v]
        if i > j:
            i, j = j, i
        qubo[(i, j)] += alpha

    return qubo
