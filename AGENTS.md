# Project instructions for Codex

Use the `$image-ppt-from-docs` skill when the user asks to turn local PDF/DOCX
materials into a visual, image-based slide deck.

Default assumptions:
- Source files live in `./sources/` unless the user names another folder.
- Final outputs go to `./output/`.
- Use Codex built-in image generation only.
- Infer presentation scenario, audience, and communication setting from the
  materials instead of defaulting to executives.
- Decide page count and detail density from the source complexity and purpose.
- Keep one visual system across the deck, but allow slide-level differences in
  information density.

Direct image-to-slide workflow:
- Each generated image is the final slide image.
- Prompts must ask the image model to render the exact slide text directly when
  the user requests text-bearing slides.
- After copying generated images into `output/images/`, create the contact sheet
  and build `output/deck.pptx` directly.
- Do not create local post-generation slide-rendering or text-overlay scripts.
- Do not add reflective, corrective, or explanatory text beyond the planned
  `on_slide_text`.
- If a generated slide has wrong/missing/unreadable text, regenerate that slide
  with a stricter prompt. If it still fails, report the limitation instead of
  silently switching workflows.

Source chart preservation:
- When source materials include standalone data charts, plots, tables rendered
  as images, or figure-like diagrams, extract those visuals as separate source
  assets before planning slides.
- If the visual is not available as an embedded image but is visible in a PDF
  page render, crop it into `build/extracted_images/source_visual_crops/` and
  register it in `build/source_visual_refs.json`.
- Feed the extracted chart asset together with the corresponding page, section,
  caption, or surrounding text to the image model as real reference image input
  for any slide that uses it; do not rely on text-only local file paths.
- Prompts for those slides must explicitly ask the image model to preserve the
  source chart's structure, data values, labels, axis relationships, and visual
  appearance as much as possible instead of redrawing it from memory.
- In `deck_plan.json`, represent these requirements with `source_visual_refs`
  entries that include the visual path, matching source context,
  `attach_as_image_input: true`, and `input_fidelity: "high"`.
- If exact chart preservation is not possible through image generation, report
  the limitation rather than silently changing the data or chart design.
