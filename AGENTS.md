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
