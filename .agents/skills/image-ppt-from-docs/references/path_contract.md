# Fixed path contract

Use these paths exactly. Do not create ad hoc sibling folders for generated
slides, temporary plates, alternate render passes, or local text overlays.

## Inputs

- `sources/`: user-provided PDFs, DOCX files, and optional reference images.

## Intermediate files

- `build/source_manifest.json`: machine-readable extraction manifest.
- `build/source_summary.md`: extraction summary for deck planning.
- `build/presentation_brief.md`: inferred scenario, audience, tone, and density strategy.
- `build/deck_plan.json`: complete deck plan.
- `build/prompts/slide_XX.txt`: final prompt for each generated slide image.
- `build/page_renders/`: source page previews from extraction only.
- `build/extracted_images/`: embedded source images from extraction only.

## Final outputs

- `output/images/slide_XX.png`: final generated slide images.
- `output/contact_sheet.jpg`: QA overview.
- `output/deck.pptx`: image-based PowerPoint deck.
- `output/README.md`: short delivery note.

## Forbidden workflow folders

Do not create or use folders such as:

- `build/generated_full/`
- `build/generated_plates/`
- `build/local_render/`
- `output/slides/`
- `tmp/slides/`

If an image needs to be copied from Codex's default generated-image location,
copy it directly to `output/images/slide_XX.png`.
