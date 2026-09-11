"""Run the ZIP-backed reproducible pipeline from the repository root."""
from __future__ import annotations
import os
from pathlib import Path
from build_project import main as build_project_main


def run() -> dict:
    os.environ.setdefault("OLIST_PROJECT_DIR", str(Path.cwd()))
    return build_project_main()


if __name__ == "__main__":
    run()
