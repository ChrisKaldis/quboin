"""Unit tests for the utils."""

import unittest
import os
from tempfile import NamedTemporaryFile
from networkx import Graph, is_isomorphic

from dimod import SampleSet

from quboin.utils import (
    read_integers_from_file, find_valid_knapsack_solution, read_dimacs_graph
)
class TestReadIntegersFromFile(unittest.TestCase):
    """Test cases for the read_integers_from_file function."""
    
    def setUp(self):
        """Create temporary files to check all possible cases."""
        # Create a normal file with integers
        self.normal_file = NamedTemporaryFile(mode='w+', delete=False)
        self.normal_file.write("1\n2\n5\n10\n")
        self.normal_file.close()
        
        # Create a file with empty lines and spaces
        self.spaced_file = NamedTemporaryFile(mode='w+', delete=False)
        self.spaced_file.write("\t 5 \n\n \t \n15\n 155  \n")
        self.spaced_file.close()
        
        # Create an empty file
        self.empty_file = NamedTemporaryFile(mode='w+', delete=False)
        self.empty_file.close()
        
        # Create a file with invalid content
        self.invalid_file = NamedTemporaryFile(mode='w+', delete=False)
        self.invalid_file.write("10\nabc\n20\n")
        self.invalid_file.close()

    def tearDown(self):
        """Clean up temporary files."""
        for filepath in [self.normal_file.name, self.spaced_file.name, 
                        self.empty_file.name, self.invalid_file.name]:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_normal_file(self):
        values = read_integers_from_file(self.normal_file.name)
        self.assertEqual(values, [1, 2, 5, 10])

    def test_spaced_file(self):
        values = read_integers_from_file(self.spaced_file.name)
        self.assertEqual(values, [5, 15, 155])

    def test_empty_file(self):
        values = read_integers_from_file(self.empty_file.name)
        self.assertEqual(values, [])

    def test_invalid_file(self):
        with self.assertRaises(ValueError):
            read_integers_from_file(self.invalid_file.name)

    def test_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            read_integers_from_file("wrong_path.txt")


class TestFindValidKnapsackSolution(unittest.TestCase):
    """Test case for find_valid_knapsack_solution."""
    def test_find_valid_knapsack_solution(self):
        weights = [2, 3]
        profits = [5, 6]
        capacity = 5
        sampleset = SampleSet.from_samples(
            [{0: 1, 1: 1}, {0: 1, 1: 0}], vartype="BINARY", energy=[-11, -5])

        sample, weight, profit = find_valid_knapsack_solution(
            sampleset, weights, profits, capacity)

        self.assertEqual(weight, 5)
        self.assertEqual(profit, 11)


class TestReadDimacsGraph(unittest.TestCase):
    def setUp(self):
        # Create a valid DIMACS graph file
        self.valid_graph_data = "\n".join([
            "c Sample DIMACS file",
            "p edge 4 3",
            "e 1 2",
            "e 2 3",
            "e 3 4"
        ])
        self.temp_file = NamedTemporaryFile(delete=False, mode="w+", suffix=".txt")
        self.temp_file.write(self.valid_graph_data)
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_valid_graph(self):
        G = read_dimacs_graph(self.temp_file.name)

        expected = Graph()
        expected.add_edges_from([(1, 2), (2, 3), (3, 4)])

        self.assertTrue(is_isomorphic(G, expected), "The parsed graph does not match the expected structure.")

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_dimacs_graph("nonexistent_file.txt")

    def test_invalid_edge_line(self):
        invalid_data = "e 1\n"
        with NamedTemporaryFile(delete=False, mode="w+", suffix=".txt") as temp_file:
            temp_file.write(invalid_data)
            temp_file_path = temp_file.name

        with self.assertRaises(ValueError):
            read_dimacs_graph(temp_file_path)

        os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main()
