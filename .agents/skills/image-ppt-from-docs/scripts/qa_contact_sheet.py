#!/usr/bin/env python3
"""Create a contact sheet for quick visual QA of generated slide images."""
from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp"}


def is_metadata_sidecar(path: Path) -> bool:
    return path.name.startswith("._") or path.name == ".DS_Store" or "__MACOSX" in path.parts


def natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def list_images(images_dir: Path) -> list[Path]:
    files = [
        p
        for p in images_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGES and not is_metadata_sidecar(p)
    ]
    return sorted(files, key=natural_key)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a thumbnail contact sheet from slide images.")
    parser.add_argument("images_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output/contact_sheet.jpg"))
    parser.add_argument("--thumb-width", type=int, default=420)
    parser.add_argument("--cols", type=int, default=3)
    args = parser.parse_args()

    images = list_images(args.images_dir)
    if not images:
        raise SystemExit(f"No images found in {args.images_dir}")

    margin = 24
    label_h = 34
    gap = 18
    thumb_w = args.thumb_width
    thumb_h = int(thumb_w * 9 / 16)
    cols = max(1, args.cols)
    rows = math.ceil(len(images) / cols)
    sheet_w = margin * 2 + cols * thumb_w + (cols - 1) * gap
    sheet_h = margin * 2 + rows * (thumb_h + label_h) + (rows - 1) * gap

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except Exception:
        font = ImageFont.load_default()

    for i, path in enumerate(images):
        row, col = divmod(i, cols)
        x = margin + col * (thumb_w + gap)
        y = margin + row * (thumb_h + label_h + gap)
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (thumb_w, thumb_h), "white")
            canvas.paste(im, ((thumb_w - im.width) // 2, (thumb_h - im.height) // 2))
            sheet.paste(canvas, (x, y))
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=(210, 210, 210), width=1)
        draw.text((x, y + thumb_h + 8), path.name, fill=(30, 30, 30), font=font)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, quality=92)
    print(f"Saved contact sheet: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
