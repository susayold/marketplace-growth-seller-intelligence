"""Run the marketplace pipeline plus additional segmentation/statistical marts."""
from __future__ import annotations
import os
from pathlib import Path
from build_project import main as build_project_main
from additional_analysis import main as additional_analysis_main


def run() -> dict:
    os.environ.setdefault("OLIST_PROJECT_DIR", str(Path.cwd()))
    result = build_project_main()
    additional_analysis_main()
    return result


if __name__ == "__main__":
    run()
