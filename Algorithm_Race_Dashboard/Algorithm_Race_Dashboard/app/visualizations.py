"""
visualizations.py
-----------------
Plotly chart builders used by the dashboard.
"""

from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLORS = {
    "Merge Sort": "#22d3ee",
    "Quick Sort": "#f97316",
    "Heap Sort": "#a3e635",
    "Binary Search": "#facc15",
}
TEMPLATE = "plotly_dark"


def _style(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.01, font=dict(size=18)),
        template=TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(font_size=13),
    )
    return fig


def time_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart: average execution time (ms) per algorithm."""
    d = df.assign(**{"Avg Time (ms)": df["Avg Time (s)"] * 1000})
    fig = px.bar(d, x="Algorithm", y="Avg Time (ms)", color="Algorithm",
                 color_discrete_map=COLORS, text_auto=".3f",
                 hover_data={"Min Time (s)": ":.6f", "Trials": True, "Size": True})
    fig.update_yaxes(title="Average time (ms)")
    return _style(fig, "Measured execution time")


def count_bar_chart(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    """Generic bar chart for Comparisons / Swaps / Moves."""
    fig = px.bar(df, x="Algorithm", y=column, color="Algorithm",
                 color_discrete_map=COLORS, text_auto=",")
    fig.update_yaxes(title=column)
    return _style(fig, title)


def comparisons_bar_chart(df: pd.DataFrame) -> go.Figure:
    return count_bar_chart(df, "Comparisons", "Number of comparisons")


def swaps_bar_chart(df: pd.DataFrame) -> go.Figure:
    fig = count_bar_chart(df, "Swaps", "Number of swaps")
    fig.add_annotation(text="Merge Sort copies values instead of swapping (see Moves)",
                       xref="paper", yref="paper", x=0, y=-0.18, showarrow=False,
                       font=dict(size=11, color="#94a3b8"))
    return fig


def scaling_line_chart(df: pd.DataFrame, metric: str = "Avg Time (s)") -> go.Figure:
    """Line chart: metric vs dataset size, one line per algorithm."""
    d = df.copy()
    y = metric
    if metric == "Avg Time (s)":
        d["Avg Time (ms)"] = d["Avg Time (s)"] * 1000
        y = "Avg Time (ms)"
    fig = px.line(d, x="Size", y=y, color="Algorithm", markers=True,
                  color_discrete_map=COLORS,
                  hover_data={"Comparisons": ":,", "Swaps": ":,"})
    fig.update_xaxes(title="Dataset size (n)")
    return _style(fig, f"Measured {y} across dataset sizes")


def theoretical_chart(curves: pd.DataFrame) -> go.Figure:
    """ILLUSTRATIVE complexity growth curves (not measured)."""
    fig = px.line(curves, x="n", y="Relative growth", color="Complexity", markers=True,
                  line_dash="Complexity")
    fig.update_xaxes(title="n")
    return _style(fig, "Illustrative theoretical growth (normalised, not measured)")


def binary_search_steps_chart(trace: List[Dict], target: int) -> go.Figure:
    """Show how low / mid / high indices converge at each step."""
    if not trace:
        return _style(go.Figure(), "Binary search (empty dataset)")
    df = pd.DataFrame(trace)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["step"], y=df["high"], name="high", mode="lines+markers",
                             line=dict(color="#f43f5e")))
    fig.add_trace(go.Scatter(x=df["step"], y=df["low"], name="low", mode="lines+markers",
                             line=dict(color="#22d3ee"), fill="tonexty",
                             fillcolor="rgba(148,163,184,0.12)"))
    fig.add_trace(go.Scatter(
        x=df["step"], y=df["mid"], name="mid", mode="lines+markers+text",
        line=dict(color="#facc15", dash="dot"), marker=dict(size=11),
        text=df["mid_value"], textposition="top center",
        customdata=df[["mid_value", "decision"]],
        hovertemplate="Step %{x}<br>mid index %{y}<br>value %{customdata[0]}"
                      "<br>%{customdata[1]}<extra></extra>"))
    fig.update_xaxes(title="Step", dtick=1)
    fig.update_yaxes(title="Array index")
    return _style(fig, f"Binary search for {target}: search interval per step")


def binary_search_array_chart(data: List[int], trace: List[Dict], step: int) -> go.Figure:
    """Bar view of the sorted array at one step: active interval vs discarded."""
    t = trace[step - 1]
    colors = []
    for i in range(len(data)):
        if i == t["mid"]:
            colors.append("#facc15")
        elif t["low"] <= i <= t["high"]:
            colors.append("#22d3ee")
        else:
            colors.append("#334155")
    fig = go.Figure(go.Bar(x=list(range(len(data))), y=data, marker_color=colors,
                           hovertemplate="index %{x}<br>value %{y}<extra></extra>"))
    fig.update_xaxes(title="Index")
    fig.update_yaxes(title="Value")
    return _style(fig, f"Step {step}: low={t['low']}, mid={t['mid']}, high={t['high']} "
                       f"→ {t['decision']}")
