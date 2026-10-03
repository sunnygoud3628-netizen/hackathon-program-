"""
utils.py
--------
Helper functions: dataset generation, fair copies, validation and
data preparation for the charts.
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

DATASET_SIZES = [100, 500, 1000, 5000, 10000]
INPUT_TYPES = ["Random", "Sorted", "Reverse Sorted"]


def generate_random_dataset(size: int, seed: Optional[int] = None,
                            low: int = 0, high: Optional[int] = None) -> List[int]:
    """Random integers in [low, high). Duplicates are possible (realistic data)."""
    if high is None:
        high = max(size * 10, 10)
    rng = np.random.default_rng(seed)
    return rng.integers(low, high, size=size).tolist()


def generate_sorted_dataset(size: int, seed: Optional[int] = None) -> List[int]:
    """Random values sorted in ascending order."""
    return sorted(generate_random_dataset(size, seed))


def generate_reverse_sorted_dataset(size: int, seed: Optional[int] = None) -> List[int]:
    """Random values sorted in descending order."""
    return sorted(generate_random_dataset(size, seed), reverse=True)


def generate_dataset(size: int, input_type: str, seed: Optional[int] = None) -> List[int]:
    """Generate a dataset of the requested size and input type."""
    if input_type == "Random":
        return generate_random_dataset(size, seed)
    if input_type == "Sorted":
        return generate_sorted_dataset(size, seed)
    if input_type == "Reverse Sorted":
        return generate_reverse_sorted_dataset(size, seed)
    raise ValueError(f"Unknown input type: {input_type}")


def make_identical_copies(data: List[int], names: List[str]) -> Dict[str, List[int]]:
    """
    Give every algorithm its own independent copy of the SAME data,
    so no algorithm benefits from another one having sorted it already.
    """
    return {name: list(data) for name in names}


def is_sorted(data: List[int]) -> bool:
    """True if the list is in non-decreasing order."""
    return all(data[i] <= data[i + 1] for i in range(len(data) - 1))


def validate_sort(original: List[int], result: List[int]) -> bool:
    """
    A sort is correct when the output is ordered AND contains exactly
    the same elements as the input (compared with Python's built-in sorted).
    """
    return result == sorted(original)


def format_time(seconds: float) -> str:
    """Human-friendly time string."""
    if seconds < 1e-3:
        return f"{seconds * 1e6:.1f} µs"
    if seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds:.3f} s"


def theoretical_curves(sizes: List[int]) -> pd.DataFrame:
    """
    ILLUSTRATIVE growth curves (not measurements): n, n log n, n^2, log n.
    Values are normalised so the largest n log n value equals 1.
    """
    n = np.array(sizes, dtype=float)
    nlogn = n * np.log2(n)
    scale = nlogn.max()
    df = pd.DataFrame({
        "n": sizes,
        "O(log n)": np.log2(n) / np.log2(n).max(),
        "O(n log n)": nlogn / scale,
        "O(n²)": (n ** 2) / (n ** 2).max(),
    })
    return df.melt(id_vars="n", var_name="Complexity", value_name="Relative growth")


def complexity_table() -> pd.DataFrame:
    """Theoretical complexity table shown in the dashboard."""
    return pd.DataFrame(
        [
            ["Merge Sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)"],
            ["Quick Sort", "O(n log n)", "O(n log n)", "O(n²)", "O(log n)"],
            ["Heap Sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(1)"],
            ["Binary Search", "O(1)", "O(log n)", "O(log n)", "O(1)"],
        ],
        columns=["Algorithm", "Best", "Average", "Worst", "Space"],
    )
