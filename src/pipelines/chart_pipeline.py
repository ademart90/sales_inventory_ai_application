import io
import base64
from typing import Literal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from langchain_core.tools import tool


@tool
def plot_chart(
    title: str,
    chart_type: Literal["bar", "line", "pie"],
    labels: list[str],
    values: list[float],
    y_axis_label: str = ""
) -> str:
    """
    Plots a clean executive chart from exact numbers in the sales or inventory JSON and returns a base64 PNG string.
    Call this tool whenever the user asks for a graph, chart, or visual comparison.
    """
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=160)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Martins Store Slate & Amber Palette
    palette = ["#1E293B", "#D97706", "#334155", "#F59E0B", "#475569"]
    colors = [palette[i % len(palette)] for i in range(len(labels))]

    if chart_type == "bar":
        bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor="none", zorder=3)
        ax.bar_label(bars, fmt="{:,.2f}", padding=4, fontsize=9, fontweight="bold", color="#0F172A")
        ax.set_ylabel(y_axis_label, fontsize=10, fontweight="bold", color="#334155")
        ax.grid(axis="y", linestyle="--", alpha=0.45, color="#CBD5E1", zorder=0)
    elif chart_type == "line":
        ax.plot(labels, values, marker="o", markersize=7, linewidth=2.5, color="#D97706", markerfacecolor="#1E293B", zorder=3)
        ax.fill_between(labels, values, color="#D97706", alpha=0.08)
        ax.set_ylabel(y_axis_label, fontsize=10, fontweight="bold", color="#334155")
        ax.grid(True, linestyle="--", alpha=0.45, color="#CBD5E1", zorder=0)
    elif chart_type == "pie":
        ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            wedgeprops={"edgecolor": "#FFFFFF", "linewidth": 2},
            textprops={"fontsize": 9.5, "color": "#0F172A"},
        )

    # Clean executive typography & spine removal
    ax.set_title(title, fontsize=12.5, fontweight="bold", color="#0F172A", pad=14, loc="left")
    if chart_type != "pie":
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CBD5E1")
        ax.spines["bottom"].set_color("#CBD5E1")
        ax.tick_params(axis="both", colors="#334155", labelsize=9.5)
        plt.xticks(rotation=20, ha="right")

    # Subtle branded watermark in bottom-right of exported PNG
    fig.text(
        0.99, 0.015, "Martins Store • AI Analytics",
        fontsize=8, color="#64748B", alpha=0.6, ha="right", va="bottom"
    )

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")
