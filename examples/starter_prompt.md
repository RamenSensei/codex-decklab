Use $image-ppt-from-docs.

Task:
- Read all PDF/DOCX files under `sources/`.
- Infer the most suitable presentation scenario and audience from the materials.
- Create an international, presentation-ready image-based PPT. Use the language
  requested by the user or implied by the source; if unspecified, prefer English
  or a bilingual approach when appropriate.
- Choose page count and slide-by-slide detail level based on the source density and communication goal.
- Keep the whole deck visually unified, modern, clear, and presentation-ready.
- Do not over-simplify by default.
- Output: `output/deck.pptx`, `output/images/`, `output/contact_sheet.jpg`, `build/presentation_brief.md`, and `build/deck_plan.json`.
- Save each final slide prompt under `build/prompts/`.
- Treat each generated image as the final slide image. Do not create local
  text-overlay or repaint scripts after image generation.
- If a generated image fails concrete QA, regenerate only that slide.

- Make the prompts design-forward and art-directed: minimalist modern flat
  design, Apple keynote-like restraint, Bauhaus/constructivist geometry, and
  Swiss-grid discipline. Avoid cheap template aesthetics, stock-business
  clichés, clutter, and cheesy visuals.
