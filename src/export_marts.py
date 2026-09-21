"""Export manifest and lightweight delivery inventory for remote publication."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def build_manifest(project: Path) -> list[dict]:
    files = []
    for path in sorted(project.rglob("*")):
        if path.is_file() and ".git" not in path.parts and "tmp" not in path.parts and ".pytest_cache" not in path.parts:
            files.append({"path": path.relative_to(project).as_posix(), "bytes": path.stat().st_size})
    (project / "release_manifest.json").write_text(json.dumps(files, indent=2), encoding="utf-8")
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", default=".")
    args = parser.parse_args()
    print(f"manifest files={len(build_manifest(Path(args.project_dir)))}")


if __name__ == "__main__":
    main()

