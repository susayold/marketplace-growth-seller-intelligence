from pathlib import Path

from PIL import Image


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT / "tmp" / "powerbi-unified-final-scale2"
OUTPUT = PROJECT / "deliverables" / "final-market-dashboard.pdf"
DASHBOARD = PROJECT / "dist" / "assets" / "dashboard"
PAGES = [
    "Executive Overview.png",
    "Seller Acquisition.png",
    "Seller Activation & Retention.png",
    "Commercial Performance.png",
    "Customer Experience & Operations.png",
    "Root Cause & Diagnostic.png",
    "Decision Center.png",
]


def main() -> None:
    # Scale-2 bridge snapshots include a 2502x1408 report canvas at (0, 176).
    # Crop the Power BI canvas only; exclude Desktop chrome and the Filters pane.
    images = [
        Image.open(ROOT / page).convert("RGB").crop((0, 176, 2502, 1584))
        for page in PAGES
    ]
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    for index, image in enumerate(images, start=1):
        image.save(DASHBOARD / f"page-{index}.png", "PNG", optimize=True)
    images[0].save(
        OUTPUT,
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=images[1:],
    )
    for image in images:
        image.close()
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
