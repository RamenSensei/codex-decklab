#!/usr/bin/env python3
"""Extract usable content from PDF/DOCX/image source folders for a visual deck workflow.

Outputs:
- source_manifest.json
- source_summary.md
- extracted_images/ and page_renders/ when possible
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable

SUPPORTED_DOCS = {".pdf", ".docx"}
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp"}
VISUAL_PRESERVATION_NOTE = (
    "Potential standalone chart/figure/table-image. Use this asset together "
    "with its source context and preserve structure, values, labels, axes, "
    "legend, proportions, and recognizable appearance as much as possible."
)


def is_metadata_sidecar(path: Path) -> bool:
    return path.name.startswith("._") or path.name == ".DS_Store" or "__MACOSX" in path.parts


@dataclass
class ExtractedItem:
    type: str
    text: str = ""
    level: int | None = None
    page: int | None = None
    rows: list[list[str]] | None = None
    image_path: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceRecord:
    path: str
    kind: str
    sha256: str
    items: list[ExtractedItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate(text: str, limit: int = 4000) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " ... [truncated]"


def image_dimensions_from_blob(blob: bytes) -> tuple[int | None, int | None]:
    try:
        from PIL import Image

        with Image.open(BytesIO(blob)) as im:
            return im.size
    except Exception:
        return None, None


def image_dimensions_from_path(path: Path) -> tuple[int | None, int | None]:
    try:
        from PIL import Image

        with Image.open(path) as im:
            return im.size
    except Exception:
        return None, None


def is_probable_source_visual(width: int | None, height: int | None) -> bool:
    if width is None or height is None:
        return True
    if min(width, height) < 120:
        return False
    if width * height < 60_000:
        return False
    aspect_ratio = width / height
    return 0.25 <= aspect_ratio <= 6.0


def source_visual_meta(
    width: int | None,
    height: int | None,
    *,
    context_ref: str,
    source_kind: str,
    force_candidate: bool = False,
) -> dict[str, Any]:
    candidate = force_candidate or is_probable_source_visual(width, height)
    meta: dict[str, Any] = {
        "width": width,
        "height": height,
        "context_ref": context_ref,
        "source_kind": source_kind,
        "source_visual_candidate": candidate,
    }
    if candidate:
        meta["preservation_instruction"] = VISUAL_PRESERVATION_NOTE
    return meta


def extract_pdf(path: Path, out_dir: Path, render_pages: int = 12) -> SourceRecord:
    rec = SourceRecord(path=str(path), kind="pdf", sha256=sha256_file(path))
    try:
        import fitz  # PyMuPDF
    except Exception as e:  # pragma: no cover
        rec.warnings.append(f"PyMuPDF import failed: {e}")
        return extract_pdf_with_poppler(path, out_dir, rec, render_pages)

    page_render_dir = out_dir / "page_renders" / path.stem
    extracted_img_dir = out_dir / "extracted_images" / path.stem
    page_render_dir.mkdir(parents=True, exist_ok=True)
    extracted_img_dir.mkdir(parents=True, exist_ok=True)

    try:
        doc = fitz.open(path)
    except Exception as e:
        rec.warnings.append(f"Cannot open PDF: {e}")
        return rec

    rec.items.append(ExtractedItem(type="document", text=path.name, meta={"pages": doc.page_count}))

    seen_xrefs: set[int] = set()
    for page_index in range(doc.page_count):
        page_no = page_index + 1
        try:
            page = doc.load_page(page_index)
            text = clean_text(page.get_text("text"))
            if text:
                rec.items.append(ExtractedItem(type="page_text", page=page_no, text=truncate(text, 6000)))
            else:
                rec.warnings.append(f"Page {page_no}: no extractable text; may be scanned or image-only")

            if page_index < render_pages:
                pix = page.get_pixmap(dpi=160, annots=True)
                render_path = page_render_dir / f"page_{page_no:03d}.png"
                pix.save(render_path)
                rec.items.append(
                    ExtractedItem(
                        type="page_render",
                        page=page_no,
                        image_path=str(render_path),
                        meta={
                            "width": pix.width,
                            "height": pix.height,
                            "context_ref": f"{path.name} page {page_no}",
                            "source_kind": "pdf_page_render",
                            "source_visual_candidate": False,
                        },
                    )
                )

            for img_i, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)
                try:
                    image = doc.extract_image(xref)
                    ext = image.get("ext", "png")
                    img_path = extracted_img_dir / f"page_{page_no:03d}_img_{img_i:02d}.{ext}"
                    image_blob = image["image"]
                    img_path.write_bytes(image_blob)
                    width = image.get("width")
                    height = image.get("height")
                    if not width or not height:
                        width, height = image_dimensions_from_blob(image_blob)
                    meta = source_visual_meta(
                        width,
                        height,
                        context_ref=f"{path.name} page {page_no}",
                        source_kind="pdf_embedded_image",
                    )
                    meta["ext"] = ext
                    rec.items.append(
                        ExtractedItem(
                            type="embedded_image",
                            page=page_no,
                            image_path=str(img_path),
                            meta=meta,
                        )
                    )
                except Exception as e:
                    rec.warnings.append(f"Page {page_no}: image {img_i} extraction failed: {e}")
        except Exception as e:
            rec.warnings.append(f"Page {page_no}: extraction failed: {e}")

    doc.close()
    return rec


def extract_pdf_with_poppler(path: Path, out_dir: Path, rec: SourceRecord, render_pages: int) -> SourceRecord:
    """Fallback PDF extraction using Poppler CLI tools when PyMuPDF is unavailable."""
    rec.items.append(ExtractedItem(type="document", text=path.name))

    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            result = subprocess.run(
                [pdftotext, "-layout", str(path), "-"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            pages = result.stdout.split("\f")
            for idx, page_text in enumerate(pages, start=1):
                page_text = clean_text(page_text)
                if page_text:
                    rec.items.append(ExtractedItem(type="page_text", page=idx, text=truncate(page_text, 6000)))
            if not any(item.type == "page_text" for item in rec.items):
                rec.warnings.append("pdftotext produced no extractable page text; PDF may be scanned")
        except Exception as e:
            rec.warnings.append(f"pdftotext fallback failed: {e}")
    else:
        rec.warnings.append("pdftotext not found; install Poppler or PyMuPDF for PDF text extraction")

    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm and render_pages > 0:
        page_render_dir = out_dir / "page_renders" / path.stem
        page_render_dir.mkdir(parents=True, exist_ok=True)
        prefix = page_render_dir / "page"
        try:
            subprocess.run(
                [pdftoppm, "-f", "1", "-l", str(render_pages), "-r", "160", "-png", str(path), str(prefix)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for i, rendered in enumerate(sorted(page_render_dir.glob("page-*.png")), start=1):
                target = page_render_dir / f"page_{i:03d}.png"
                rendered.replace(target)
                width, height = image_dimensions_from_path(target)
                rec.items.append(
                    ExtractedItem(
                        type="page_render",
                        page=i,
                        image_path=str(target),
                        meta={
                            "width": width,
                            "height": height,
                            "context_ref": f"{path.name} page {i}",
                            "source_kind": "pdf_page_render",
                            "source_visual_candidate": False,
                        },
                    )
                )
        except Exception as e:
            rec.warnings.append(f"pdftoppm fallback failed: {e}")
    elif render_pages > 0:
        rec.warnings.append("pdftoppm not found; page preview images were not rendered")

    return rec


def iter_docx_blocks(document: Any) -> Iterable[Any]:
    """Yield paragraphs and tables in document order for python-docx."""
    from docx.document import Document as _Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    parent_elm = document.element.body if isinstance(document, _Document) else document._element
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def docx_paragraph_level(paragraph: Any) -> int | None:
    style_name = (paragraph.style.name or "") if paragraph.style is not None else ""
    match = re.search(r"Heading\s+(\d+)", style_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_docx(path: Path, out_dir: Path) -> SourceRecord:
    rec = SourceRecord(path=str(path), kind="docx", sha256=sha256_file(path))
    try:
        from docx import Document
    except Exception as e:  # pragma: no cover
        rec.warnings.append(f"python-docx import failed: {e}")
        return rec

    extracted_img_dir = out_dir / "extracted_images" / path.stem
    extracted_img_dir.mkdir(parents=True, exist_ok=True)

    try:
        doc = Document(path)
    except Exception as e:
        rec.warnings.append(f"Cannot open DOCX: {e}")
        return rec

    rec.items.append(ExtractedItem(type="document", text=path.name))

    for block in iter_docx_blocks(doc):
        name = block.__class__.__name__.lower()
        if "paragraph" in name:
            text = clean_text(block.text)
            if text:
                level = docx_paragraph_level(block)
                item_type = "heading" if level else "paragraph"
                rec.items.append(ExtractedItem(type=item_type, text=text, level=level))
        elif "table" in name:
            rows: list[list[str]] = []
            for row in block.rows:
                rows.append([clean_text(cell.text) for cell in row.cells])
            if rows:
                flat = " | ".join(" / ".join(r) for r in rows[:10])
                rec.items.append(ExtractedItem(type="table", text=truncate(flat, 2000), rows=rows[:50]))

    # Extract related images. This does not preserve exact order, but provides references.
    for rel_id, rel in doc.part.rels.items():
        try:
            if "image" not in rel.reltype:
                continue
            blob = rel.target_part.blob
            content_type = rel.target_part.content_type
            ext = content_type.split("/")[-1].replace("jpeg", "jpg")
            img_path = extracted_img_dir / f"{rel_id}.{ext}"
            img_path.write_bytes(blob)
            width, height = image_dimensions_from_blob(blob)
            meta = source_visual_meta(
                width,
                height,
                context_ref=f"{path.name} embedded image relationship {rel_id}",
                source_kind="docx_embedded_image",
            )
            meta["content_type"] = content_type
            rec.items.append(ExtractedItem(type="embedded_image", image_path=str(img_path), meta=meta))
        except Exception as e:
            rec.warnings.append(f"Image relationship {rel_id} extraction failed: {e}")

    return rec


def image_record(path: Path) -> SourceRecord:
    width, height = image_dimensions_from_path(path)
    return SourceRecord(
        path=str(path),
        kind="reference_image",
        sha256=sha256_file(path),
        items=[
            ExtractedItem(
                type="reference_image",
                image_path=str(path),
                text=path.name,
                meta=source_visual_meta(
                    width,
                    height,
                    context_ref=path.name,
                    source_kind="user_reference_image",
                    force_candidate=True,
                ),
            )
        ],
    )


def fallback_context_ref(rec: SourceRecord, item: ExtractedItem) -> str:
    source_name = Path(rec.path).name
    if item.page:
        return f"{source_name} page {item.page}"
    if item.text:
        return f"{source_name}: {item.text}"
    return source_name


def build_source_visual_refs(records: list[SourceRecord]) -> dict[str, Any]:
    refs: list[dict[str, Any]] = []
    for rec in records:
        for item in rec.items:
            if not item.image_path:
                continue

            meta = item.meta or {}
            is_source_visual = bool(meta.get("source_visual_candidate"))
            is_page_context = item.type == "page_render"
            if not is_source_visual and not is_page_context:
                continue

            reference_role = "high_fidelity_source_visual" if is_source_visual else "page_context_image"
            preservation_instruction = (
                meta.get("preservation_instruction")
                if is_source_visual
                else "Use as page context when a chart or figure is not available as a separate extracted image."
            )
            refs.append(
                {
                    "id": f"visual_ref_{len(refs) + 1:03d}",
                    "path": item.image_path,
                    "source_path": rec.path,
                    "source_kind": rec.kind,
                    "item_type": item.type,
                    "page": item.page,
                    "context_ref": meta.get("context_ref") or fallback_context_ref(rec, item),
                    "reference_role": reference_role,
                    "attach_as_image_input": True,
                    "input_fidelity": "high" if is_source_visual else "standard",
                    "width": meta.get("width"),
                    "height": meta.get("height"),
                    "preservation_instruction": preservation_instruction,
                }
            )

    return {
        "description": (
            "Image assets to consider as real reference image inputs for slide generation. "
            "Attach high_fidelity_source_visual items to the image-generation call when a slide uses them; "
            "do not rely on mentioning the file path in text only."
        ),
        "refs": refs,
    }


def write_outputs(records: list[SourceRecord], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = [
        {
            **asdict(r),
            "items": [asdict(item) for item in r.items],
        }
        for r in records
    ]
    (out_dir / "source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    source_visual_refs = build_source_visual_refs(records)
    (out_dir / "source_visual_refs.json").write_text(
        json.dumps(source_visual_refs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines: list[str] = []
    lines.append("# Source Summary\n")
    lines.append("This file is generated for Codex deck planning. Use it to synthesize a story, not as slide text.\n")
    if source_visual_refs["refs"]:
        high_fidelity_count = sum(
            1 for ref in source_visual_refs["refs"] if ref["reference_role"] == "high_fidelity_source_visual"
        )
        page_context_count = sum(
            1 for ref in source_visual_refs["refs"] if ref["reference_role"] == "page_context_image"
        )
        lines.append(
            "\nSource visual references are listed in `build/source_visual_refs.json`. "
            f"{high_fidelity_count} high-fidelity source visual candidate(s) and "
            f"{page_context_count} page context image(s) are available for image-input attachment.\n"
        )
    for r_i, rec in enumerate(records, start=1):
        lines.append(f"\n## {r_i}. {Path(rec.path).name}\n")
        lines.append(f"- kind: `{rec.kind}`\n")
        lines.append(f"- sha256: `{rec.sha256[:16]}...`\n")
        if rec.warnings:
            lines.append("- warnings:\n")
            for w in rec.warnings:
                lines.append(f"  - {w}\n")
        for item in rec.items:
            if item.type == "document":
                continue
            prefix = f"### {item.type}"
            if item.page:
                prefix += f" - page {item.page}"
            if item.level:
                prefix += f" - H{item.level}"
            lines.append(f"\n{prefix}\n")
            if item.text:
                lines.append(truncate(item.text, 1800) + "\n")
            if item.rows:
                lines.append("\nTable preview:\n")
                for row in item.rows[:8]:
                    lines.append("| " + " | ".join(cell.replace("|", "/") for cell in row[:8]) + " |\n")
            if item.image_path:
                lines.append(f"\nImage/reference path: `{item.image_path}`\n")
                if item.meta.get("source_visual_candidate"):
                    lines.append("High-fidelity source visual candidate: `yes`\n")
                    lines.append(f"Context: `{item.meta.get('context_ref', fallback_context_ref(rec, item))}`\n")
                    lines.append(f"Preservation instruction: {item.meta.get('preservation_instruction')}\n")
    (out_dir / "source_summary.md").write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract PDF/DOCX/image source files for image-PPT deck generation.")
    parser.add_argument("source_dir", type=Path, help="Folder containing source files")
    parser.add_argument("--out", type=Path, default=Path("build"), help="Output folder")
    parser.add_argument(
        "--render-pages",
        type=int,
        default=12,
        help="Max PDF pages to render as reference images per PDF",
    )
    args = parser.parse_args()

    if not args.source_dir.exists():
        print(f"Source folder not found: {args.source_dir}", file=sys.stderr)
        return 2

    files = sorted([p for p in args.source_dir.rglob("*") if p.is_file() and not is_metadata_sidecar(p)])
    records: list[SourceRecord] = []
    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            records.append(extract_pdf(path, args.out, render_pages=args.render_pages))
        elif suffix == ".docx":
            records.append(extract_docx(path, args.out))
        elif suffix in SUPPORTED_IMAGES:
            records.append(image_record(path))

    if not records:
        print("No supported files found. Add PDF, DOCX, PNG/JPG/JPEG/WebP files.", file=sys.stderr)
        return 1

    write_outputs(records, args.out)
    print(f"Extracted {len(records)} source files into {args.out}")
    print(f"- {args.out / 'source_summary.md'}")
    print(f"- {args.out / 'source_manifest.json'}")
    print(f"- {args.out / 'source_visual_refs.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
