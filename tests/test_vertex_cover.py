"""Test min vertex cover."""

import unittest
import networkx as nx

from dimod import BinaryQuadraticModel

from quboin.vertex_cover import build_min_vertex_cover


class TestBuildMinVertexCover(unittest.TestCase):
    """Unit test for the min_vertex_cover function."""

    def setUp(self):
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
        """
        """
        # we use the default A = 2, B = 1 for simplicity
        actual_qubo = build_min_vertex_cover(self.graph)
        actual_bqm = BinaryQuadraticModel.from_qubo(actual_qubo)

        nodes = sorted(self.graph.nodes())
        node_to_index = {node: idx for idx, node in enumerate(nodes)}

        expected_linear_terms = dict()
        expected_quadratic_terms = dict()

        for node in nodes:
            i = node_to_index[node]
            deg = self.graph.degree(node)
            expected_linear_terms[i] = 1 - 2 * deg

        for u, v in self.graph.edges():
            i = node_to_index[u]
            j = node_to_index[v]
            if i > j:
                i, j = j, i
            expected_quadratic_terms[(i, j)] = 2

        self.assertEqual(actual_bqm.linear, expected_linear_terms)
        self.assertEqual(actual_bqm.quadratic, expected_quadratic_terms)


if __name__ == "__main__":
    unittest.main()
