"""QUBO formulation utilities for the knapsack problem.

This module includes functions to:
- Load knapsack problem data from file inputs.
- Construct a QUBO representation of the knapsack problem.
- Construct a QUBO representation of the problem with auxiliary bits.
"""

from math import log2

from quboin.utils import read_integers_from_file


def load_knapsack_data(
    capacity_file: str,
    weights_file: str,
    profits_file: str,
) -> tuple[int, list[int], list[int]]:
    """Loads knapsack problem data from files.

    Args:
        capacity_file: Path to file with the capacity.
        weights_file: Path to file with weights.
        profits_file: Path to file with profits.

    Returns:
        A tuple with the capacity and the lists of weights and profits.

    Raises:
        ValueError: For various validation errors with clear priorities:
            1. If any of the files don't contain any number (are empty).
            2. If weights and profits have different length
            3. If any weight is non-possitive.
            4. If capacity is negative.
            5. If capacity is smaller than the smallest of weights.
    """
    capacity_list = read_integers_from_file(capacity_file)
    weights = read_integers_from_file(weights_file)
    profits = read_integers_from_file(profits_file)

    # 1.
    if not capacity_list:
        raise ValueError("Capacity file is empty.")
    if not weights:
        raise ValueError("Weights file is empty.")
    if not profits:
        raise ValueError("Profits file is empty.")

    capacity = capacity_list[0]

    # 2.
    if len(weights) != len(profits):
        raise ValueError(
            (
                f"Lists weights and profits have different "
                f"length {len(weights)} != {len(profits)}."
            )
        )

    # 3.
    if any(w <= 0 for w in weights):
        raise ValueError("All weights must be positive integers.")

    # 4.
    if capacity < 0:
        raise ValueError(f"Capacity cannot be negative ({capacity}).")

    # 5.
    min_weight = min(weights)
    if capacity < min_weight:
        raise ValueError(
            (
                f"Capacity: {capacity} is smaller than the "
                f"minimum weight: {min_weight}. No items can be selected."
            )
        )

    return capacity, weights, profits


def build_knapsack(
    weights: list[int],
    profits: list[int],
    capacity: int,
    alpha: int,
    beta: int,
) -> dict[tuple[int, int], int]:
    """Knapsack problem as a simplified QUBO.

    It's the simple case without auxiliary bits. Generally alpha
    should be greater or equal to max(profit) * beta in order to
    avoid weakly violated our constraint but every alpha >= beta
    is a good first assumption. The constraint that we use is
    actually from the subset sum problem, as a result we have good
    results only when the optimal solution is near the capacity.

    Args:
        weights: List with the weight of each object.
        profits: List with the profit of each object.
        capacity: Capacity of knapsack.
        alpha: Penalty coefficient for the constraint.
        beta: Coefficient of optimization term.

    Returns:
        A dictionary representing the QUBO matrix, where keys 
        are index pairs and values are the corresponding coefficients. 
    """
    qubo: dict[tuple[int, int], int] = {}

    n = len(weights)
    for i in range(n):
        qubo[(i, i)] = (
            - beta * profits[i]
            + alpha * weights[i] ** 2
            - 2 * alpha * capacity * weights[i]
        )
        for j in range(i+1, n):
            qubo[(i, j)] = 2 * alpha * weights[i] * weights[j]

    return qubo


def build_knapsack_with_aux(
        weights: list[int],
        profits: list[int],
        capacity: int,
        alpha: int = 1,
        beta: int = 1,
) -> dict[tuple[int, int], int]:
    """Constructs QUBO matrix for knapsack problem using auxiliary bits.

    Uses a binary encoding of the knapsack capacity constraint via 
    auxiliary bits.

    Args:
        weights: List with the weight of each item.
        profits: List with the profit of each item. 
        capacity: Capacity of knapsack.
        alpha: Penalty coefficient for the constraint.
        beta: Coefficient of optimization term.

    Returns:
        A dictionary representing the QUBO matrix like the 
        `build_knapsack_qubo` function but with additional
        auxiliary bits.
    """
    qubo: dict[tuple[int, int], int] = {}
    n = len(weights)

    # Number of auxiliary bits
    m = int(log2(capacity))
    remainder = capacity - (2**m - 1)

    # Items coefficients
    for i in range(n):
        # Diagonal terms
        qubo[(i, i)] = -beta * profits[i] + alpha * weights[i]**2

        # Off-diagonal terms
        # Item-item interactions
        for j in range(i+1, n):
            qubo[(i, j)] = 2 * alpha * weights[i] * weights[j]

        # Item-auxiliary bit interactions
        for k in range(m):
            qubo[(i, k + n)] = -alpha * weights[i] * (2 ** (k + 1))

        qubo[(i, n + m)] = -2 * alpha * weights[i] * remainder

    # Auxiliary bit coefficients
    for i in range(m):
        # Diagonal terms
        qubo[(i + n, i + n)] = alpha * (2 ** (2 * i))

        # Off-diagonal terms
        for j in range(i + 1, m):
            qubo[(i + n, j + n)] = alpha * (2 ** (i + j + 1))

        qubo[(i + n, n + m)] = alpha * (2 ** (i + 1)) * remainder

    qubo[(n + m, n + m)] = alpha * remainder ** 2

    return qubo
