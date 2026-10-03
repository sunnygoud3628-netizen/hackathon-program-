# 🏁 Algorithm Race Dashboard

An interactive Streamlit dashboard for a **Design and Analysis of Algorithms (DAA)** project that
compares **Merge Sort, Quick Sort, Heap Sort** and **Binary Search** on identical datasets.

## 1. Project overview
The dashboard generates a dataset, gives every sorting algorithm its own identical copy, measures
execution time over several trials, counts comparisons / swaps / moves, validates the output,
and visualizes everything with Plotly. A Binary Search tab shows how `low`, `mid` and `high`
change at every step.

## 2. Problem statement
Textbook complexity (Big-O) says Merge, Quick and Heap Sort are all O(n log n) on average, yet in
practice they run at different speeds. This project measures that gap on real data and explains it.

## 3. Objectives
- Implement four classic algorithms correctly with operation counters.
- Compare them fairly on the **same** dataset.
- Measure average execution time across repeated trials.
- Visualize results and contrast them with theoretical complexity.
- Export results to CSV for reports.

## 4. Features
- Sidebar: dataset size (100, 500, 1,000, 5,000, 10,000), input type (Random, Sorted, Reverse
  Sorted), random seed, algorithm selection, number of trials, **Run Algorithms** button.
- Metric cards: average time, comparisons, swaps/moves, sorted-output validation, 🏆 fastest.
- Charts: time bar chart, comparisons bar chart, swaps bar chart, moves chart,
  time-vs-size line chart, comparisons-vs-size line chart.
- Binary Search: target input, step chart (low/mid/high), array view per step, trace table.
- Theory tab: algorithm descriptions, complexity table, illustrative growth curves, and an
  explanation of why measurements differ from theory.
- CSV export to `outputs/` and direct download.
- Badges clearly separate **MEASURED** results from **ILLUSTRATIVE** (formula-based) charts.

## 5. Technologies used
Python 3.9+, Streamlit, Plotly, Pandas, NumPy, pytest / unittest.

## 6. Folder structure
```
Algorithm_Race_Dashboard/
├── app/
│   ├── dashboard.py        # Streamlit UI (entry point)
│   ├── algorithms.py       # Merge, Quick, Heap Sort + Binary Search with counters
│   ├── visualizations.py   # Plotly chart builders
│   ├── performance.py      # Timing, trials, DataFrames, CSV export
│   └── utils.py            # Dataset generation, copies, validation, chart data
├── outputs/                # CSV results are written here
│   └── .gitkeep
├── tests/
│   └── test_algorithms.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 7. Installation (Windows + VS Code)
1. Install **Python 3.9 or newer** from python.org (tick *"Add Python to PATH"*).
2. Install **VS Code** and the **Python** extension (by Microsoft).
3. Unzip `Algorithm_Race_Dashboard.zip`.
4. In VS Code: **File → Open Folder…** → select the `Algorithm_Race_Dashboard` folder
   (the one containing `requirements.txt`).
5. Open a terminal: **Terminal → New Terminal**.
6. (Recommended) create and activate a virtual environment:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```
   If PowerShell blocks activation, run once:
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
   Then press `Ctrl+Shift+P` → *Python: Select Interpreter* → choose `venv`.
7. Install the dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## 8. Running the project
From the project root folder:
```powershell
streamlit run app/dashboard.py
```
The dashboard opens at http://localhost:8501. Stop it with `Ctrl+C`.

Run the tests:
```powershell
python -m pytest tests -v
```
(or without pytest: `python -m unittest discover tests -v`)

## 9. Algorithm explanations
| Algorithm | Best | Average | Worst | Space |
|---|---|---|---|---|
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) |
| Binary Search | O(1) | O(log n) | O(log n) | O(1) |

- **Merge Sort** – splits the list in halves, sorts each recursively and merges them. Stable.
  It copies values into a buffer, so it reports *moves* (array writes) instead of swaps.
- **Quick Sort** – partitions around a pivot (Hoare partition, **median-of-three** pivot) and
  recurses into the smaller side to keep recursion depth O(log n). The median-of-three pivot
  prevents the O(n²) case on sorted / reverse-sorted input, but O(n²) remains possible for
  adversarial inputs.
- **Heap Sort** – builds a max-heap and repeatedly swaps the root to the end, then sifts down.
- **Binary Search** – compares the target with the middle of the current interval and discards
  half each step; at most ⌈log₂(n+1)⌉ steps.

**Counting rules (consistent across algorithms):** every element-vs-element comparison counts as
one comparison; every exchange of two positions counts as one swap; every write into the array
during merging counts as one move.

## 10. Performance analysis
No benchmark numbers are included in this README on purpose: **all timings shown by the dashboard
are measured live on your computer** and will vary with hardware, Python version and load.
Use the *Scaling* tab to collect your own results and export them to `outputs/` for your report.

What to look for when interpreting your measurements:
- All three sorts should grow roughly like n log n; compare the shape against the illustrative curve.
- Comparison and swap counts are deterministic for a given seed; times vary slightly between runs.
- Differences between O(n log n) algorithms come from constant factors, memory access patterns,
  extra memory allocation and Python interpreter overhead.
- Very small datasets (n = 100) are dominated by overhead and timer resolution.

## 11. Future enhancements
- Animated step-by-step sorting visualization.
- More algorithms (Insertion, Counting, Radix, Timsort comparison).
- Nearly-sorted and many-duplicates input types.
- Memory usage measurement with `tracemalloc`.
- Statistical summaries (standard deviation, confidence intervals) across trials.
- Deployment on Streamlit Community Cloud.
