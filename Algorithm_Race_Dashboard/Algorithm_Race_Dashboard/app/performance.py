"""
performance.py
--------------
Measures the algorithms on identical datasets and stores the results
in Pandas DataFrames. All numbers produced here are REAL measurements
taken on the machine running the dashboard.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from algorithms import SORTING_ALGORITHMS
from utils import generate_dataset, make_identical_copies, validate_sort

# outputs/ folder at the project root (one level above app/)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def time_algorithm(func, data: List[int], trials: int = 3):
    """
    Run 'func' on a fresh copy of 'data' 'trials' times.
    Returns (result, stats, average_seconds, min_seconds).
    Operation counts are deterministic, so we keep those from the last run.
    """
    times = []
    result, stats = None, None
    for _ in range(max(1, trials)):
        copy = list(data)                # identical input for every trial
        start = time.perf_counter()
        result, stats = func(copy)
        times.append(time.perf_counter() - start)
    return result, stats, sum(times) / len(times), min(times)


def run_benchmark(data: List[int], algorithms: List[str], trials: int = 3,
                  input_type: str = "", ) -> pd.DataFrame:
    """Benchmark the selected sorting algorithms on the SAME dataset."""
    copies = make_identical_copies(data, algorithms)
    rows = []
    for name in algorithms:
        func = SORTING_ALGORITHMS[name]
        result, stats, avg_t, min_t = time_algorithm(func, copies[name], trials)
        rows.append({
            "Algorithm": name,
            "Input Type": input_type,
            "Size": len(data),
            "Trials": trials,
            "Avg Time (s)": avg_t,
            "Min Time (s)": min_t,
            "Comparisons": stats["comparisons"],
            "Swaps": stats["swaps"],
            "Moves": stats["moves"],
            "Correct": validate_sort(data, result),
        })
    return pd.DataFrame(rows)


def run_scaling_benchmark(sizes: List[int], input_type: str, algorithms: List[str],
                          trials: int = 3, seed: Optional[int] = 42,
                          progress_callback=None) -> pd.DataFrame:
    """Benchmark every algorithm on every size (same dataset per size)."""
    frames = []
    for i, size in enumerate(sizes):
        data = generate_dataset(size, input_type, seed)
        frames.append(run_benchmark(data, algorithms, trials, input_type))
        if progress_callback:
            progress_callback((i + 1) / len(sizes))
    return pd.concat(frames, ignore_index=True)


def export_results(df: pd.DataFrame, prefix: str = "results") -> Path:
    """Save a DataFrame as CSV inside outputs/ and return the file path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"{prefix}_{stamp}.csv"
    df.to_csv(path, index=False)
    return path
