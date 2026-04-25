#!/usr/bin/env python3
"""Crop a standalone source chart/figure from a rendered page or image.

This is an extraction helper for source visuals that are visible in a page
render but are not available as embedded image objects, for example vector PDF
charts. The crop is added to build/source_visual_refs.json as a high-fidelity
reference image candidate for later slide generation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

VISUAL_PRESERVATION_NOTE = (
    "Standalone chart/figure/table-image crop. Attach this asset as a real "
    "image input together with its source context and preserve structure, "
    "values, labels, axes, legend, proportions, and recognizable appearance "
    "as much as possible."
)


def parse_bbox(value: str) -> tuple[float, float, float, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("bbox must be four comma-separated values: x1,y1,x2,y2")
    try:
        x1, y1, x2, y2 = (float(part) for part in parts)
    except ValueError as e:
        raise argparse.ArgumentTypeError("bbox values must be numbers") from e
    if x2 <= x1 or y2 <= y1:
        raise argparse.ArgumentTypeError("bbox must satisfy x2 > x1 and y2 > y1")
    return x1, y1, x2, y2


def bbox_to_pixels(
    bbox: tuple[float, float, float, float],
    width: int,
    height: int,
    *,
    relative: bool,
) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox
    if relative:
        if min(bbox) < 0 or max(bbox) > 1:
            raise SystemExit("--relative bbox values must be between 0 and 1")
        x1, x2 = x1 * width, x2 * width
        y1, y2 = y1 * height, y2 * height

    px = (
        max(0, min(width, round(x1))),
        max(0, min(height, round(y1))),
        max(0, min(width, round(x2))),
        max(0, min(height, round(y2))),
    )
    if px[2] <= px[0] or px[3] <= px[1]:
        raise SystemExit("bbox is empty after clamping to image bounds")
    return px


def load_refs(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "description": (
                "Image assets to consider as real reference image inputs for slide generation. "
                "Attach high_fidelity_source_visual items to the image-generation call when a slide uses them; "
                "do not rely on mentioning the file path in text only."
            ),
            "refs": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def next_ref_id(refs: list[dict[str, Any]]) -> str:
    highest = 0
    for ref in refs:
        match = re.fullmatch(r"visual_ref_(\d+)", str(ref.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"visual_ref_{highest + 1:03d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Crop a source chart/figure and register it as a visual reference.")
    parser.add_argument("image", type=Path, help="Rendered page or image to crop")
    parser.add_argument("--bbox", required=True, type=parse_bbox, help="Crop box: x1,y1,x2,y2")
    parser.add_argument("--relative", action="store_true", help="Interpret bbox values as fractions of image size")
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output crop path, usually under build/extracted_images/",
    )
    parser.add_argument(
        "--refs",
        type=Path,
        default=Path("build/source_visual_refs.json"),
        help="Visual refs JSON to update",
    )
    parser.add_argument("--source-path", default="", help="Original source document path, if known")
    parser.add_argument("--page", type=int, default=None, help="Original source page, if known")
    parser.add_argument("--context", default="", help="Page/section/caption/surrounding text for the cropped visual")
    args = parser.parse_args()

    try:
        from PIL import Image
    except Exception as e:
        print(f"Pillow is required for cropping source visuals: {e}", file=sys.stderr)
        return 2

    if not args.image.exists():
        print(f"Input image not found: {args.image}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(args.image) as im:
        crop_box = bbox_to_pixels(args.bbox, im.width, im.height, relative=args.relative)
        cropped = im.crop(crop_box)
        cropped.save(args.out)
        crop_width, crop_height = cropped.size

    refs_data = load_refs(args.refs)
    refs = refs_data.setdefault("refs", [])
    context_ref = args.context or f"Crop from {args.image.as_posix()}"
    source_path = args.source_path or args.image.as_posix()
    refs.append(
        {
            "id": next_ref_id(refs),
            "path": args.out.as_posix(),
            "source_path": source_path,
            "source_kind": "source_visual_crop",
            "item_type": "source_visual_crop",
            "page": args.page,
            "context_ref": context_ref,
            "reference_role": "high_fidelity_source_visual",
            "attach_as_image_input": True,
            "input_fidelity": "high",
            "width": crop_width,
            "height": crop_height,
            "preservation_instruction": VISUAL_PRESERVATION_NOTE,
        }
    )
    args.refs.parent.mkdir(parents=True, exist_ok=True)
    args.refs.write_text(json.dumps(refs_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Cropped source visual: {args.out}")
    print(f"Updated refs: {args.refs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
