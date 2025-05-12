"""Unit tests for the knapsack module in the quboin package."""

import unittest

from pathlib import Path
from tempfile import NamedTemporaryFile
from os import unlink
from math import log2

from dimod import BinaryQuadraticModel

import quboin.knapsack as kp


class TestLoadKnapsackData(unittest.TestCase):
    """Test suite for loading knapsack data from files."""
    def setUp(self):
        """Set up file paths for valid knapsack dataset inputs."""
        self.test_dir = Path(__file__).parent.resolve()
        self.dataset_dir = self.test_dir.parent / "datasets" / "knapsack"
        
        self.valid_capacity = self.dataset_dir / "p01_c.txt"
        self.valid_weights = self.dataset_dir / "p01_w.txt"
        self.valid_profits = self.dataset_dir / "p01_p.txt"

    def test_valid_input(self):
        """Test loading data from valid knapsack input files."""
        capacity, weights, profits = kp.load_knapsack_data(
            self.valid_capacity,
            self.valid_weights,
            self.valid_profits
        )
        self.assertEqual(capacity, 165)
        self.assertEqual(
            weights,
            [23, 31, 29, 44, 53, 38, 63, 85, 89, 82]
        )
        self.assertEqual(
            profits,
            [92, 57, 49, 68, 60, 43, 67, 84, 87, 72]
        )

    def _test_with_empty_file(self, file_to_empty, expected_error):
        """Helper for testing error raised when input files are empty."""
        with NamedTemporaryFile(mode="w+", delete=False) as empty_file:
            pass

        kwargs = {
            "capacity_file": self.valid_capacity,
            "weights_file": self.valid_weights,
            "profits_file": self.valid_profits
        }
        kwargs[file_to_empty] = empty_file.name

        with self.assertRaises(ValueError) as cm:
            kp.load_knapsack_data(**kwargs)
        self.assertIn(expected_error, str(cm.exception))

        unlink(empty_file.name)

    def test_empty_files(self):
        """Test error handling for empty input files."""
        test_cases = [
            ("capacity_file", "Capacity file is empty."),
            ("weights_file", "Weights file is empty."),
            ("profits_file", "Profits file is empty.")
        ]

        for file_arg, error_msg in test_cases:
            with self.subTest(file_type=file_arg):
                self._test_with_empty_file(file_arg, error_msg)

    def test_different_lengths(self):
        """Test error for mismatched lengths between weights and profits."""
        with NamedTemporaryFile(mode="w+", delete=False) as short_profits:
            short_profits.write("1\n2\n3\n")

        with self.assertRaises(ValueError) as cm:
            kp.load_knapsack_data(
                self.valid_capacity,
                self.valid_weights,
                short_profits.name
            )
        self.assertIn(
            "Lists weights and profits have different length 10 != 3.",
            str(cm.exception)
        )
        unlink(short_profits.name)

    def test_non_positive_weights(self):
        """Test error handling for zero or negative weights."""
        for bad_weight in ["0\n1\n2\n3\n4\n5\n6\n7\n8\n9", 
                           "1\n2\n3\n4\n5\n6\n7\n8\n9\n-5"]:
            with NamedTemporaryFile(mode="w+", delete=False) as bad_weights:
                bad_weights.write(bad_weight)

            with self.assertRaises(ValueError) as cm:
                kp.load_knapsack_data(
                    self.valid_capacity,
                    bad_weights.name,
                    self.valid_profits
                )
            self.assertIn(
                "All weights must be positive integers.", str(cm.exception)
            )
            unlink(bad_weights.name)

    def test_negative_capacity(self):
        """Test error handling for negative capacity values."""
        with NamedTemporaryFile(mode="w+", delete=False) as negative_cap:
            negative_cap.write("\n-100\n")

        with self.assertRaises(ValueError) as cm:
            kp.load_knapsack_data(
                negative_cap.name,
                self.valid_weights,
                self.valid_profits
            )
        self.assertIn(
            "Capacity cannot be negative (-100).",
            str(cm.exception)
        )
        unlink(negative_cap.name)

    def test_capacity_smaller_than_min_weight(self):
        """Test error when capacity is less than all item weights."""
        with NamedTemporaryFile(mode="w+", delete=False) as small_cap:
            small_cap.write("10")

        with self.assertRaises(ValueError) as cm:
            kp.load_knapsack_data(
                small_cap.name,
                self.valid_weights,
                self.valid_profits
            )
        self.assertIn(
            ("Capacity: 10 is smaller than the minimum weight: 23."
             " No items can be selected."),
            str(cm.exception)
        )
        unlink(small_cap.name)


class TestBuildKnapsackQubo(unittest.TestCase):
    """Test standard QUBO construction for the knapsack problem."""
    def setUp(self):
        self.weights = [2, 3, 4]
        self.profits = [5, 6, 7]
        self.capacity = 5

    def test_qubo(self):
        """Test that the constructed QUBO matches expected BQM structure."""
        actual_qubo = kp.build_knapsack_qubo(self.weights, self.profits, self.capacity)
        actual_bqm = BinaryQuadraticModel.from_qubo(actual_qubo)

        expected_linear_terms = dict()
        expected_quadratic_terms = dict()
        
        n = len(self.weights)
        for i in range(n):
            expected_term = (
                        - self.profits[i]
                        + self.weights[i] ** 2
                        - 2 * self.capacity * self.weights[i]
                    )
            expected_linear_terms.update({i: expected_term})

            for j in range(i+1, n):
                expected_term = 2 * self.weights[i] * self.weights[j]
                expected_quadratic_terms.update({(j, i): expected_term})

        self.assertEqual(actual_bqm.linear, expected_linear_terms)
        self.assertEqual(actual_bqm.quadratic, expected_quadratic_terms)


class TestBuildKnapsackQuboAux(unittest.TestCase):
    """Test auxiliary binary encoding QUBO construction for knapsack."""
    def setUp(self):
        self.weights = [12, 7, 11, 8, 9]
        self.profits = [24, 13, 23, 15, 16]
        self.capacity = 26

    def test_qubo(self):
        """Test structure of the auxiliary-variable QUBO."""
        actual_qubo = kp.build_knapsack_qubo_aux(
            self.weights, self.profits, self.capacity)
        actual_bqm = BinaryQuadraticModel.from_qubo(actual_qubo)

        expected_linear_terms = dict()
        expected_quadratic_terms = dict()
        
        n = len(self.weights)
        m = int(log2(self.capacity))
        for i in range(n):
            expected_term = -self.profits[i] + self.weights[i]**2
            expected_linear_terms.update({i: expected_term})

            for j in range(i+1, n):
                expected_term = 2 * self.weights[i] * self.weights[j]
                expected_quadratic_terms.update({(j, i): expected_term})
            
            for k in range(m):
                expected_term = -2 * self.weights[i] * 2**k
                expected_quadratic_terms.update({(k+n, i): expected_term})

            expected_term = -2 * self.weights[i] * (self.capacity + 1 - 2**m)
            expected_quadratic_terms.update({(n+m, i): expected_term})

        for i in range(m):
            expected_term = 2 ** (2*i)
            expected_linear_terms.update({i+n: expected_term})

            for j in range(i+1, m):
                    expected_term = 2 ** (i + j + 1)
                    expected_quadratic_terms.update({(j+n, i+n): expected_term})
            
            expected_term = (self.capacity + 1 - 2**m) * 2 ** (i+1)
            expected_quadratic_terms.update({(n+m, i+n): expected_term})
        
        expected_term = (self.capacity + 1 - 2**m) ** 2
        expected_linear_terms.update({n+m: expected_term})

        self.assertEqual(actual_bqm.linear, expected_linear_terms)
        self.assertEqual(actual_bqm.quadratic, expected_quadratic_terms)


if __name__ == "__main__":
    unittest.main()
