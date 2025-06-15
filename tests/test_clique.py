"""Test k-clique problem."""

import unittest
import networkx as nx

from dimod import BinaryQuadraticModel

from quboin.clique import build_clique_k


class TestBuildCliqueK(unittest.TestCase):
    """Unittest for the build_clique_k function."""

    def setUp(self):
        """Sets up a test graph and QUBO parameters for use in test cases."""
        self.k = 3
        self.alpha = 4
        self.beta = 1

        # simple graph from  problem's wiki page
        self.graph = nx.Graph()
        self.graph.add_edges_from([
            (1, 2),
            (1, 5),
            (2, 3),
            (2, 5),
            (3, 4),
            (4, 5),
            (4, 6)
        ])

    def test_small_qubo(self):
        """Tests whether build_clique_k produces correct QUBO coefficients.
        
        This test checks the linear and quadratic coefficients of the QUBO
        representation for the k-clique problem using `dimod` library.
        """
        actual_qubo = build_clique_k(self.graph, self.k, self.alpha, self.beta)
        actual_bqm = BinaryQuadraticModel.from_qubo(actual_qubo)

        nodes = sorted(self.graph.nodes())
        node_to_index = {node: idx for idx, node in enumerate(nodes)}
        n = len(nodes)

        expected_linear_terms = dict()
        expected_quadratic_terms = dict()

        for i in range(n):
            expected_linear_terms[i] = self.alpha * (1 - 2 * self.k)

        for i in range(n):
            for j in range(i + 1, n):
                expected_quadratic_terms[(i, j)] = 2 * self.alpha

        for u, v in self.graph.edges():
            i = node_to_index[u]
            j = node_to_index[v]
            if i > j:
                i, j = j, i
            expected_quadratic_terms[(i, j)] -= self.beta

        self.assertEqual(actual_bqm.linear, expected_linear_terms)
        self.assertEqual(actual_bqm.quadratic, expected_quadratic_terms)


if __name__ == "__main__":
    unittest.main()
