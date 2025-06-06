"""QUBO formulation for the k-clique problem in an undirected graph.

This module provides a function to construct a QUBO model to determine 
whether a graph contains a clique of a specified size k.
"""

from networkx import Graph


def build_clique_k(
        graph: Graph,
        k : int,
        alpha: int = 1,
        beta: int = 1,
    ) -> dict[tuple[int, int], int]:
    """Construct a QUBO for solving the k-clique problem in a graph.

    The function formulates a QUBO (Quadratic Unconstrained Binary Optimization)
    to determine whether there exists a clique of size `k` in the given graph.
    The variables of qubo are the nodes sorted, we keep the default names, it is
    integer numbers that starts counting from zero.

    For better results you should define A > B * k. Also if you want the ground
    solution of the problem to be equal to zero you have to define an offset
    value alpha*(k^2) + beta*[k*(k-1)/2].

    Args:
        graph: A `networkx` undirected graph
        k: The target clique size.
        alpha: Penalty coefficient for enforcing the size constraint.
        beta: Penalty coefficient for non-complete graph.

    Returns:
        A dictionary representing the QUBO matrix, where keys 
        are index pairs and values are the corresponding coefficients.
    """
    qubo: dict[tuple[int, int], int] = {}
    node_to_index = {node: i for i, node in enumerate(sorted(graph.nodes()))}
    n = graph.number_of_nodes()

    # Size constraint penalty,
    # in case the selected nodes aren't size `k`.
    for i in range(n):
        # linear term
        qubo[(i, i)] = alpha * (1 - 2*k)
        for j in range(i+1, n):
            # quadratic term
            qubo[(i, j)] = 2 * alpha

    # Structure constraint penalty,
    # in case of the selected subgraph is  a non-complete graph.
    for u, v in graph.edges():
        i = node_to_index[u]
        j = node_to_index[v]
        if i > j:
            i, j = j, i
        # decrease value of neighbors.
        qubo[(i, j)] -= beta

    return qubo
