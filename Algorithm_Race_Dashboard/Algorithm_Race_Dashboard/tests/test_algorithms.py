"""
Unit tests for algorithms.py

Run from the project root with either:
    python -m pytest tests -v
    python -m unittest discover tests -v
"""

import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from algorithms import SORTING_ALGORITHMS, binary_search  # noqa: E402
from utils import generate_dataset, validate_sort  # noqa: E402


class TestSortingAlgorithms(unittest.TestCase):
    def check_all(self, data):
        for name, func in SORTING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                original = list(data)
                result, stats = func(data)
                self.assertEqual(result, sorted(original))
                self.assertEqual(data, original, "input must not be modified")
                for key in ("comparisons", "swaps", "moves"):
                    self.assertGreaterEqual(stats[key], 0)

    def test_random_arrays(self):
        rng = random.Random(1)
        for n in (2, 10, 100, 1000):
            self.check_all([rng.randint(-1000, 1000) for _ in range(n)])

    def test_sorted_array(self):
        self.check_all(list(range(500)))

    def test_reverse_sorted_array(self):
        self.check_all(list(range(500, 0, -1)))

    def test_duplicates(self):
        self.check_all([5, 3, 5, 1, 3, 3, 9, 1, 5] * 20)
        self.check_all([7] * 100)

    def test_empty_array(self):
        self.check_all([])

    def test_single_element(self):
        self.check_all([42])

    def test_large_sorted_no_recursion_error(self):
        for t in ("Sorted", "Reverse Sorted", "Random"):
            data = generate_dataset(10000, t, seed=3)
            for func in SORTING_ALGORITHMS.values():
                self.assertTrue(validate_sort(data, func(data)[0]))


class TestBinarySearch(unittest.TestCase):
    def setUp(self):
        self.data = list(range(0, 200, 2))  # even numbers 0..198

    def test_existing_elements(self):
        for target in (0, 2, 100, 198):
            idx, stats = binary_search(self.data, target)
            self.assertEqual(self.data[idx], target)
            self.assertLessEqual(stats["steps"], len(self.data).bit_length())
            self.assertEqual(stats["trace"][-1]["decision"], "found")

    def test_missing_elements(self):
        for target in (-1, 1, 99, 1000):
            idx, stats = binary_search(self.data, target)
            self.assertEqual(idx, -1)
            self.assertGreater(stats["steps"], 0)

    def test_empty_and_single(self):
        self.assertEqual(binary_search([], 5)[0], -1)
        self.assertEqual(binary_search([5], 5)[0], 0)
        self.assertEqual(binary_search([5], 4)[0], -1)

    def test_duplicates(self):
        data = [1, 2, 2, 2, 3]
        idx, _ = binary_search(data, 2)
        self.assertEqual(data[idx], 2)


if __name__ == "__main__":
    unittest.main()
