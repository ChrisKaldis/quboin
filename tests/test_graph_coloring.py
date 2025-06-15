"""Test graph coloring problem."""

import unittest
import networkx as nx

from dimod import BinaryQuadraticModel

from quboin.graph_coloring import build_graph_coloring


class TestBuildGraphColoring(unittest.TestCase):
    """Unittest for the build_graph_coloring function."""

    def setUp(self):
        self.graph = nx.Graph()
        self.graph.add_edges_from([
            (1, 2),
            (2, 3),
            (2, 4),
            (4, 3)
        ])
        self.colors = 3

    def test_small_qubo(self):
        """Tests whether build_graph_coloring produces correct QUBO coefficients.
        
        This test checks the linear and quadratic coefficients of the QUBO
        representation for the coloring problem using `dimod` library.
        """

        actual_qubo = build_graph_coloring(self.graph, self.colors)
        actual_bqm = BinaryQuadraticModel.from_qubo(actual_qubo)

        nodes = sorted(self.graph.nodes())
        node_to_index = {node: idx for idx, node in enumerate(nodes)}

        expected_linear_terms = dict()
        expected_quadratic_terms = dict()

        for i in range(self.graph.number_of_nodes()*self.colors):
            expected_linear_terms[i] = -1.0

        for node in nodes:
            node_idx = node_to_index[node]*self.colors
            for color in range(self.colors):
                i = node_idx + color
                for c in range(color+1, self.colors):
                    j = node_idx + c
                    expected_quadratic_terms[(j, i)] = 2

        for u, v in self.graph.edges():
            i = node_to_index[u] * self.colors
            j = node_to_index[v] * self.colors
            for c in range(self.colors):
                expected_quadratic_terms[(j+c, i+c)] = 1

        self.assertEqual(actual_bqm.linear, expected_linear_terms)
        self.assertEqual(actual_bqm.quadratic, expected_quadratic_terms)


if __name__ == "__main__":
    unittest.main()
