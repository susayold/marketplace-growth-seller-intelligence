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
    # Legacy snapshots are 2904x1720 and contain the report canvas at (0, 176).
    # Current verified canvas snapshots are already cropped to 2064x1161.
    # Do not apply the legacy crop to the current size: PIL pads out-of-bounds
    # crops with black pixels, which makes the exported PDF look truncated.
    images = []
    for page in PAGES:
        image = Image.open(ROOT / page).convert("RGB")
        if image.width >= 2502 and image.height >= 1584:
            image = image.crop((0, 176, 2502, 1584))
        images.append(image)
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
