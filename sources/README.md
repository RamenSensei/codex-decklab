# Source Folder

Put PDF, DOCX, and optional image reference files in this directory.

Supported inputs:

- PDF: extractable text, page previews, and embedded image clues
- DOCX: headings, body text, tables, and embedded images
- PNG/JPG/WebP: visual or content references, including standalone data charts
  that should be preserved in generated slides

When a standalone chart exists only inside a PDF page render, the workflow can
crop it into `build/extracted_images/source_visual_crops/` and register it in
`build/source_visual_refs.json` as a high-fidelity reference image.

Suggested naming:

- `01_brief.pdf`
- `02_research.docx`
- `brand_reference.png`
