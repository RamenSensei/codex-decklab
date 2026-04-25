#!/usr/bin/env python3
"""Prepare the fixed workspace folders for image-ppt-from-docs."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


FIXED_DIRS = [
    Path("sources"),
    Path("build"),
    Path("build/prompts"),
    Path("build/page_renders"),
    Path("build/extracted_images"),
    Path("build/extracted_images/source_visual_crops"),
    Path("output"),
    Path("output/images"),
]


def assert_relative(path: Path) -> None:
    if path.is_absolute() or ".." in path.parts:
        raise SystemExit(f"Refusing unsafe path: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create fixed build/output folders for the image PPT workflow.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove build/ and output/ before recreating fixed folders.",
    )
    args = parser.parse_args()

    for path in FIXED_DIRS:
        assert_relative(path)

    if args.clean:
        for path in [Path("build"), Path("output")]:
            if path.exists():
                shutil.rmtree(path)

    for path in FIXED_DIRS:
        path.mkdir(parents=True, exist_ok=True)

    print("Prepared fixed folders:")
    for path in FIXED_DIRS:
        print(f"- {path.as_posix()}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
