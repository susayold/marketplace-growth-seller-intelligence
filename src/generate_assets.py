"""Generate lightweight portfolio diagrams from the documented architecture."""
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]


def diagram(path: Path, title: str, boxes: list[tuple[str, float, float]], arrows: list[tuple[int, int]]) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title(title, fontsize=18, weight="bold", pad=18)
    for label, x, y in boxes:
        patch = FancyBboxPatch((x, y), 2.2, 0.8, boxstyle="round,pad=0.08", facecolor="#E8F1FB", edgecolor="#1F4E79", linewidth=1.5)
        ax.add_patch(patch)
        ax.text(x + 1.1, y + 0.4, label, ha="center", va="center", fontsize=10)
    for start, end in arrows:
        x1, y1 = boxes[start][1] + 2.2, boxes[start][2] + 0.4
        x2, y2 = boxes[end][1], boxes[end][2] + 0.4
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->", mutation_scale=15, color="#6B7280"))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    diagram(out / "architecture.png", "Marketplace Growth & Seller Intelligence — Architecture", [
        ("Drive raw ZIPs", 0.4, 4.4), ("Python ingest/profile", 3.2, 4.4), ("PostgreSQL raw/staging", 6.0, 4.4), ("Facts & marts", 8.8, 4.4), ("BI semantic model", 8.8, 2.0), ("Reports / decisions", 3.2, 2.0)
    ], [(0,1),(1,2),(2,3),(3,4),(3,5),(5,4)])
    diagram(out / "data_model.png", "Grain-safe star schema", [
        ("dim_date", 0.4, 4.4), ("dim_customer", 0.4, 3.0), ("dim_seller", 0.4, 1.6), ("fct_order", 4.0, 3.8), ("fct_order_item", 4.0, 2.4), ("fct_seller_funnel", 4.0, 1.0), ("marts", 8.0, 2.4)
    ], [(0,3),(1,3),(2,4),(3,4),(4,6),(5,6)])
    diagram(out / "pipeline.png", "Reproducible execution path", [
        ("Inventory", 0.4, 4.4), ("Profile", 2.8, 4.4), ("Fan-out QA", 5.2, 4.4), ("Build marts", 7.6, 4.4), ("Tests", 7.6, 2.4), ("Remote release", 10.0, 2.4)
    ], [(0,1),(1,2),(2,3),(3,4),(4,5)])


if __name__ == "__main__":
    main()
