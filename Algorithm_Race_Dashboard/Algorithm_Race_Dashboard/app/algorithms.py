"""
algorithms.py
-------------
Implementations of the four algorithms used in the Algorithm Race Dashboard:

    * Merge Sort   - divide and conquer
    * Quick Sort   - pivot-based partitioning (median-of-three pivot)
    * Heap Sort    - binary max-heap
    * Binary Search - halving the search interval on sorted data

Every sorting function:
    * does NOT modify the input list (it works on its own copy),
    * returns a tuple: (sorted_list, stats_dict)

stats_dict always contains the same keys so results can be compared fairly:
    comparisons : number of element-to-element comparisons
    swaps       : number of element exchanges (two positions swapped)
    moves       : number of array writes (used by Merge Sort, which
                  copies values instead of swapping them)
"""

from typing import Dict, List, Tuple


def _new_stats() -> Dict[str, int]:
    """Return a fresh, zeroed statistics dictionary."""
    return {"comparisons": 0, "swaps": 0, "moves": 0}


# ---------------------------------------------------------------------------
# Merge Sort
# ---------------------------------------------------------------------------
def merge_sort(data: List[int]) -> Tuple[List[int], Dict[str, int]]:
    """
    Sort a list using Merge Sort.

    Idea: split the list into two halves, sort each half recursively,
    then merge the two sorted halves together.
    Merge Sort does not swap elements; it writes values into a buffer,
    so we count those writes as 'moves' (swaps stays 0).
    """
    stats = _new_stats()
    arr = list(data)  # work on a copy
    if len(arr) <= 1:
        return arr, stats

    buffer = [0] * len(arr)

    def _sort(lo: int, hi: int) -> None:
        # Sort arr[lo:hi] (hi is exclusive)
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        _sort(lo, mid)
        _sort(mid, hi)
        _merge(lo, mid, hi)

    def _merge(lo: int, mid: int, hi: int) -> None:
        i, j, k = lo, mid, lo
        while i < mid and j < hi:
            stats["comparisons"] += 1
            if arr[i] <= arr[j]:  # '<=' keeps the sort stable
                buffer[k] = arr[i]
                i += 1
            else:
                buffer[k] = arr[j]
                j += 1
            k += 1
        while i < mid:
            buffer[k] = arr[i]
            i += 1
            k += 1
        while j < hi:
            buffer[k] = arr[j]
            j += 1
            k += 1
        # copy merged values back into the main array
        for idx in range(lo, hi):
            arr[idx] = buffer[idx]
            stats["moves"] += 1

    _sort(0, len(arr))
    return arr, stats


# ---------------------------------------------------------------------------
# Quick Sort
# ---------------------------------------------------------------------------
def quick_sort(data: List[int]) -> Tuple[List[int], Dict[str, int]]:
    """
    Sort a list using Quick Sort (Hoare-style partition, median-of-three pivot).

    Idea: choose a pivot, move smaller elements to its left and larger
    elements to its right, then sort both sides.

    Notes:
    * The median-of-three pivot (first, middle, last) avoids the classic
      O(n^2) worst case on already-sorted or reverse-sorted inputs.
      The O(n^2) worst case still exists theoretically for adversarial inputs.
    * We always recurse into the smaller partition and loop on the larger one,
      which keeps the recursion depth O(log n) and avoids RecursionError.
    """
    stats = _new_stats()
    arr = list(data)

    def _swap(i: int, j: int) -> None:
        arr[i], arr[j] = arr[j], arr[i]
        stats["swaps"] += 1

    def _median_of_three(lo: int, hi: int) -> int:
        mid = (lo + hi) // 2
        stats["comparisons"] += 1
        if arr[mid] < arr[lo]:
            _swap(mid, lo)
        stats["comparisons"] += 1
        if arr[hi] < arr[lo]:
            _swap(hi, lo)
        stats["comparisons"] += 1
        if arr[hi] < arr[mid]:
            _swap(hi, mid)
        return arr[mid]

    def _partition(lo: int, hi: int) -> int:
        pivot = _median_of_three(lo, hi)
        i, j = lo - 1, hi + 1
        while True:
            i += 1
            stats["comparisons"] += 1
            while arr[i] < pivot:
                i += 1
                stats["comparisons"] += 1
            j -= 1
            stats["comparisons"] += 1
            while arr[j] > pivot:
                j -= 1
                stats["comparisons"] += 1
            if i >= j:
                return j
            _swap(i, j)

    def _sort(lo: int, hi: int) -> None:
        while lo < hi:
            p = _partition(lo, hi)
            # recurse on the smaller side, iterate on the larger side
            if p - lo < hi - p:
                _sort(lo, p)
                lo = p + 1
            else:
                _sort(p + 1, hi)
                hi = p

    if len(arr) > 1:
        _sort(0, len(arr) - 1)
    return arr, stats


# ---------------------------------------------------------------------------
# Heap Sort
# ---------------------------------------------------------------------------
def heap_sort(data: List[int]) -> Tuple[List[int], Dict[str, int]]:
    """
    Sort a list using Heap Sort.

    Idea: build a max-heap (largest element at index 0), then repeatedly
    swap the root with the last element of the heap, shrink the heap,
    and restore the heap property ('sift down').
    """
    stats = _new_stats()
    arr = list(data)
    n = len(arr)

    def _sift_down(start: int, end: int) -> None:
        # Restore the max-heap property for the subtree rooted at 'start'.
        # 'end' is exclusive (the heap occupies arr[0:end]).
        root = start
        while True:
            child = 2 * root + 1
            if child >= end:
                break
            # pick the larger child
            if child + 1 < end:
                stats["comparisons"] += 1
                if arr[child] < arr[child + 1]:
                    child += 1
            stats["comparisons"] += 1
            if arr[root] < arr[child]:
                arr[root], arr[child] = arr[child], arr[root]
                stats["swaps"] += 1
                root = child
            else:
                break

    # 1) Build the max heap
    for start in range(n // 2 - 1, -1, -1):
        _sift_down(start, n)

    # 2) Extract the maximum repeatedly
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        stats["swaps"] += 1
        _sift_down(0, end)

    return arr, stats


# ---------------------------------------------------------------------------
# Binary Search
# ---------------------------------------------------------------------------
def binary_search(sorted_data: List[int], target: int) -> Tuple[int, Dict]:
    """
    Search for 'target' in an ascending sorted list.

    Returns (index, stats) where index is the position of the target,
    or -1 if the target is not present.

    stats contains:
        comparisons : number of three-way comparisons with the middle element
        steps       : number of iterations (search steps)
        trace       : list of dicts, one per step, with low / high / mid,
                      the value at mid and the decision taken.
                      This trace powers the step-by-step visualization.
    """
    low, high = 0, len(sorted_data) - 1
    stats = {"comparisons": 0, "steps": 0, "trace": []}

    while low <= high:
        mid = (low + high) // 2
        value = sorted_data[mid]
        stats["steps"] += 1
        stats["comparisons"] += 1

        if value == target:
            decision = "found"
        elif value < target:
            decision = "go right"
        else:
            decision = "go left"

        stats["trace"].append(
            {
                "step": stats["steps"],
                "low": low,
                "high": high,
                "mid": mid,
                "mid_value": value,
                "decision": decision,
            }
        )

        if decision == "found":
            return mid, stats
        if decision == "go right":
            low = mid + 1
        else:
            high = mid - 1

    return -1, stats


# Registry used by the dashboard / performance module.
SORTING_ALGORITHMS = {
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Heap Sort": heap_sort,
}

ALGORITHM_INFO = {
    "Merge Sort": {
        "description": "Divide-and-conquer: split the array in halves, sort each half "
        "recursively, then merge. Stable, predictable, needs O(n) extra memory.",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "space": "O(n)",
    },
    "Quick Sort": {
        "description": "Pick a pivot, partition elements around it, sort both sides. "
        "In-place and usually fastest in practice; this version uses a median-of-three pivot.",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)", "space": "O(log n)",
    },
    "Heap Sort": {
        "description": "Build a binary max-heap, then repeatedly move the largest element "
        "to the end. In-place with a guaranteed O(n log n), but poor cache locality.",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "space": "O(1)",
    },
    "Binary Search": {
        "description": "Search a sorted array by comparing the target with the middle "
        "element and discarding half of the remaining interval each step.",
        "best": "O(1)", "average": "O(log n)", "worst": "O(log n)", "space": "O(1)",
    },
}
