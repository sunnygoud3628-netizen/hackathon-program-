"""
dashboard.py
------------
Algorithm Race Dashboard - Streamlit entry point.

Run from the project root:
    streamlit run app/dashboard.py
"""

import sys
from pathlib import Path

# Make sure sibling modules (algorithms, utils, ...) can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import streamlit as st

from algorithms import ALGORITHM_INFO, SORTING_ALGORITHMS, binary_search
from performance import export_results, run_benchmark, run_scaling_benchmark
from utils import (DATASET_SIZES, INPUT_TYPES, complexity_table, format_time,
                   generate_dataset, theoretical_curves)
import visualizations as viz

st.set_page_config(page_title="Algorithm Race Dashboard", page_icon="🏁", layout="wide")

# ----------------------------------------------------------------- styling --
st.markdown("""
<style>
.block-container {padding-top: 1.6rem;}
.hero {padding: 1.4rem 1.6rem; border-radius: 16px;
       background: linear-gradient(120deg, #0f172a 0%, #1e293b 60%, #0e7490 140%);
       border: 1px solid #334155; margin-bottom: 1rem;}
.hero h1 {margin: 0; color: #f8fafc; font-size: 2.2rem;}
.hero p {margin: .3rem 0 0; color: #cbd5e1;}
div[data-testid="stMetric"] {background: #111827; border: 1px solid #1f2937;
       border-radius: 12px; padding: .8rem 1rem;}
.badge {display:inline-block; padding:2px 10px; border-radius:999px; font-size:.75rem;
        font-weight:600; margin-left:6px;}
.measured {background:#064e3b; color:#6ee7b7;}
.illustrative {background:#3f3f46; color:#e4e4e7;}
</style>
""", unsafe_allow_html=True)

MEASURED = '<span class="badge measured">MEASURED</span>'
ILLUSTRATIVE = '<span class="badge illustrative">ILLUSTRATIVE</span>'

st.markdown("""
<div class="hero">
  <h1>🏁 Algorithm Race Dashboard</h1>
  <p>Compare Merge Sort, Quick Sort, Heap Sort and Binary Search on identical datasets —
  theory vs. real measurements on <b>your</b> machine.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------- sidebar --
with st.sidebar:
    st.header("⚙️ Dataset configuration")
    size = st.selectbox("Dataset size", DATASET_SIZES, index=2,
                        format_func=lambda v: f"{v:,}")
    input_type = st.radio("Input type", INPUT_TYPES)
    seed = st.number_input("Random seed (reproducibility)", 0, 10_000, 42)
    st.header("🏎️ Algorithms")
    selected = st.multiselect("Sorting algorithms", list(SORTING_ALGORITHMS),
                              default=list(SORTING_ALGORITHMS))
    trials = st.slider("Trials per algorithm (averaged)", 1, 10, 3)
    run = st.button("▶ Run Algorithms", type="primary", use_container_width=True)
    st.caption("Every algorithm receives its own identical copy of the same dataset.")

# ------------------------------------------------------------- run action --
if run:
    if not selected:
        st.sidebar.error("Select at least one algorithm.")
    else:
        data = generate_dataset(size, input_type, int(seed))
        with st.spinner("Racing..."):
            st.session_state["results"] = run_benchmark(data, selected, trials, input_type)
        st.session_state["data"] = data
        st.session_state["config"] = (size, input_type, int(seed), trials)

tab_race, tab_scale, tab_search, tab_theory = st.tabs(
    ["🏁 Race results", "📈 Scaling", "🔍 Binary search", "📚 Theory & analysis"])

# ------------------------------------------------------------ race tab -----
with tab_race:
    if "results" not in st.session_state:
        st.info("Configure the dataset in the sidebar and press **Run Algorithms**.")
    else:
        df: pd.DataFrame = st.session_state["results"]
        s, it, sd, tr = st.session_state["config"]
        st.markdown(f"#### Results for n = {s:,}, {it} input, seed {sd}, "
                    f"{tr} trial(s) {MEASURED}", unsafe_allow_html=True)

        winner = df.loc[df["Avg Time (s)"].idxmin(), "Algorithm"]
        cols = st.columns(len(df))
        for col, (_, row) in zip(cols, df.iterrows()):
            with col:
                st.markdown(f"**{row['Algorithm']}** {'🏆' if row['Algorithm'] == winner else ''}")
                st.metric("Avg time", format_time(row["Avg Time (s)"]))
                st.metric("Comparisons", f"{row['Comparisons']:,}")
                st.metric("Swaps / Moves", f"{row['Swaps']:,} / {row['Moves']:,}")
                if row["Correct"]:
                    st.success("Output sorted ✔")
                else:
                    st.error("Output incorrect ✘")

        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.time_bar_chart(df), use_container_width=True)
        c2.plotly_chart(viz.comparisons_bar_chart(df), use_container_width=True)
        c3, c4 = st.columns(2)
        c3.plotly_chart(viz.swaps_bar_chart(df), use_container_width=True)
        c4.plotly_chart(viz.count_bar_chart(df, "Moves", "Array writes (Merge Sort moves)"),
                        use_container_width=True)

        with st.expander("Raw results table"):
            st.dataframe(df, use_container_width=True)
        with st.expander("Dataset preview (first 50 values)"):
            st.write(st.session_state["data"][:50])

        e1, e2 = st.columns(2)
        if e1.button("💾 Save CSV to outputs/"):
            path = export_results(df, "race")
            st.success(f"Saved to {path}")
        e2.download_button("⬇ Download CSV", df.to_csv(index=False), "race_results.csv",
                           "text/csv")

# ----------------------------------------------------------- scaling tab ---
with tab_scale:
    st.markdown(f"#### Execution time across dataset sizes {MEASURED}", unsafe_allow_html=True)
    st.write("Runs the selected algorithms on every size "
             f"({', '.join(f'{v:,}' for v in DATASET_SIZES)}) using the "
             f"**{input_type}** input type from the sidebar.")
    if st.button("Run scaling benchmark"):
        if not selected:
            st.error("Select at least one algorithm in the sidebar.")
        else:
            bar = st.progress(0.0)
            st.session_state["scaling"] = run_scaling_benchmark(
                DATASET_SIZES, input_type, selected, trials, int(seed), bar.progress)
            bar.empty()
    if "scaling" in st.session_state:
        sdf = st.session_state["scaling"]
        st.plotly_chart(viz.scaling_line_chart(sdf), use_container_width=True)
        st.plotly_chart(viz.scaling_line_chart(sdf, "Comparisons"), use_container_width=True)
        st.dataframe(sdf, use_container_width=True)
        a, b = st.columns(2)
        if a.button("💾 Save scaling CSV to outputs/"):
            st.success(f"Saved to {export_results(sdf, 'scaling')}")
        b.download_button("⬇ Download scaling CSV", sdf.to_csv(index=False),
                          "scaling_results.csv", "text/csv")

# ------------------------------------------------------ binary search tab --
with tab_search:
    st.markdown(f"#### Binary search on the sorted dataset {MEASURED}", unsafe_allow_html=True)
    base = st.session_state.get("data") or generate_dataset(size, input_type, int(seed))
    sorted_data = sorted(base)
    st.caption(f"Searching in a sorted copy of the current dataset (n = {len(sorted_data):,}).")
    default_target = sorted_data[len(sorted_data) // 3] if sorted_data else 0
    target = st.number_input("Target value", value=int(default_target), step=1)
    idx, bstats = binary_search(sorted_data, int(target))

    m1, m2, m3 = st.columns(3)
    m1.metric("Result", f"index {idx}" if idx >= 0 else "not found")
    m2.metric("Search steps", bstats["steps"])
    m3.metric("Max steps ⌈log₂(n+1)⌉", (len(sorted_data)).bit_length())

    st.plotly_chart(viz.binary_search_steps_chart(bstats["trace"], int(target)),
                    use_container_width=True)
    if bstats["trace"]:
        step = st.slider("Inspect step", 1, len(bstats["trace"]), 1) \
            if len(bstats["trace"]) > 1 else 1
        st.plotly_chart(viz.binary_search_array_chart(sorted_data, bstats["trace"], step),
                        use_container_width=True)
        st.dataframe(pd.DataFrame(bstats["trace"]), use_container_width=True, hide_index=True)

# ------------------------------------------------------------- theory tab --
with tab_theory:
    st.markdown("#### Algorithm descriptions")
    cols = st.columns(2)
    for i, (name, info) in enumerate(ALGORITHM_INFO.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.write(info["description"])

    st.markdown("#### Theoretical time complexity")
    st.table(complexity_table().set_index("Algorithm"))

    st.markdown(f"#### Growth rates {ILLUSTRATIVE}", unsafe_allow_html=True)
    st.plotly_chart(viz.theoretical_chart(theoretical_curves(DATASET_SIZES)),
                    use_container_width=True)
    st.caption("These curves are computed from formulas, not measured.")

    st.markdown("#### Why measured times differ from theory")
    st.markdown("""
- **Big-O hides constants.** Merge, Quick and Heap Sort are all O(n log n), but each does a
  different amount of work per step (copying, swapping, sifting).
- **Cache locality.** Quick Sort scans memory sequentially; Heap Sort jumps between parent
  and child indices, causing more cache misses.
- **Memory allocation.** Merge Sort needs an extra O(n) buffer.
- **Input order matters.** Quick Sort's O(n²) worst case appears with bad pivots; the
  median-of-three pivot used here makes sorted/reverse inputs fast instead.
- **Python overhead.** Interpreter cost per operation dominates at small n, so tiny datasets
  may not follow the asymptotic curve. Python's built-in `sorted()` (Timsort, in C) would beat all three.
- **Measurement noise.** Background processes, CPU frequency scaling and garbage collection
  affect timings — that is why multiple trials are averaged.
- **Operation counts are deterministic**, while times vary run to run; compare both.
""")
