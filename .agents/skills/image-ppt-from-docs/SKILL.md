---
name: image-ppt-from-docs
description: Turn local PDF/DOCX source materials into a cohesive, modern, image-based multi-page PowerPoint deck using only Codex built-in image generation. Use when the user asks for 图片PPT, visual PPT, image deck, poster-like slides, or converting PDFs/DOCXs into polished presentation images.
---

# Image PPT from PDF/DOCX sources (Codex-only)

## Purpose

Create a multi-page, image-based PPT from local source documents using **only Codex’s built-in image generation path**. Do not switch to API scripts. Do not assume one fixed audience such as executives. Instead, infer the likely presentation scenario, communication setting, and audience from the source material and user request.

Examples of plausible scenarios include but are not limited to:

- academic conference talk
- research seminar
- internal strategy review
- executive briefing
- sales pitch / 宣讲会
- investor update
- public policy briefing
- training workshop
- product launch or solution introduction
- technical architecture review

The final deck should be modern, beautiful, clear, and presentation-ready. It does **not** need to be minimal at all costs. The model must decide the right level of detail per slide and for the overall deck:

- simplify when simplification helps communication
- preserve nuance when the material is technical, academic, evidence-heavy, or high-stakes
- avoid turning everything into shallow slogans
- avoid dumping paragraphs when a structured visual explanation works better

Each slide is normally a full-bleed image inserted into a PowerPoint page.

## Direct image-to-slide policy

Generated slide images are the final slide artwork. After each slide image is
generated and copied into `output/images/`, the workflow should proceed
directly to contact-sheet creation and PPTX assembly.

Do not add a second local rendering/typesetting layer after image generation
unless the user explicitly asks for that recovery path. In particular:

- Do not create local scripts that repaint slides or overlay additional text on
  top of generated slide images.
- Do not replace generated slide text with locally typeset text as a default
  quality strategy.
- Do not add extra explanatory, reflective, or "correction" text that was not
  in `on_slide_text`.
- Do not convert text-bearing slide prompts into text-free background prompts.
- Treat `on_slide_text` as the exact text budget for the image; make the image
  model render it directly.

If generated text is visibly wrong, cropped, unreadable, or missing, regenerate
only the failed slide with a more constrained prompt. If repeated regeneration
cannot make the text acceptable, stop and report the limitation instead of
silently switching to a different slide-construction method.

## Trigger examples

Use this skill when the user says things like:

- “把这些 PDF/DOCX 做成图片式 PPT”
- “根据资料生成多页图片 PPT”
- “自动把文件夹里的材料做成视觉化演示文稿”
- “用 Codex 直接生图做一套 slides”
- “Read sources/ and build a presentation deck from the docs”

## Inputs

Default input folder: `sources/` in the current working directory.

Accept:

- `.pdf`
- `.docx`
- `.png`, `.jpg`, `.jpeg`, `.webp` reference images
- optional user prompt describing language, page count, style constraints, or scenario hints

If the user does not specify, infer:

- language: follow the user request and source language; if unspecified and
  the source is internationally oriented, default to English or a bilingual
  treatment rather than assuming Chinese
- scenario: infer from source materials
- audience: infer from scenario and source materials
- page count: infer from source density and communication goal
- aspect ratio: default `16:9`
- detail density: infer per slide rather than forcing sparse output everywhere

## Outputs

Use the fixed path contract in `references/path_contract.md`. Create these folders/files exactly:

```text
sources/
build/
  source_manifest.json
  source_summary.md
  source_visual_refs.json
  presentation_brief.md
  deck_plan.json
  prompts/
    slide_01.txt
    ...
  extracted_images/
    source_visual_crops/
output/
  images/
    slide_01.png
    slide_02.png
    ...
  deck.pptx
  contact_sheet.jpg
  README.md
```

Do not create alternate slide/image folders. In particular, do not use
`build/generated_full/`, `build/generated_plates/`, `output/slides/`, or
temporary local-render folders. If Codex built-in image generation saves a file
under Codex's default generated-image location, copy that file directly to
`output/images/slide_XX.png`.

## Workflow

### 1. Inspect and extract source materials

Prepare the fixed folders first:

```bash
python3 .agents/skills/image-ppt-from-docs/scripts/prepare_workspace.py
```

Run the extractor:

```bash
python3 .agents/skills/image-ppt-from-docs/scripts/extract_sources.py sources --out build
```

If `python3` is not the active interpreter but `python` is available, use `python` consistently instead. If dependencies are missing, prefer a project-local virtual environment so system Python restrictions do not block the workflow:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python .agents/skills/image-ppt-from-docs/scripts/extract_sources.py sources --out build
```

Read `build/source_summary.md`, `build/source_manifest.json`, and
`build/source_visual_refs.json`.

Extractor boundary conditions:

- If PyMuPDF is unavailable, the extractor falls back to Poppler CLI tools when
  available (`pdftotext`, `pdftoppm`) and records warnings in the manifest.
- If a PDF is scanned or OCR-poor, preserve that warning and base the deck only
  on extractable text, page renders, or user-provided reference images.
- Ignore AppleDouble/macOS sidecars such as `._*`, `.DS_Store`, and `__MACOSX`.

Preserve:

- key claims and facts
- numbers, dates, names, quoted terms
- source hierarchy and section titles
- tables and diagrams when relevant
- visual references from source files

Standalone chart and figure preservation:

- If the source contains an independent data chart, plot, table rendered as an
  image, or figure-like diagram, treat it as a separate source visual asset, not
  just as background inspiration.
- Use `build/source_visual_refs.json` to find extracted source visuals and page
  context images. High-fidelity visual refs must be attached to the image
  generation call as real image inputs/reference images, not merely mentioned as
  local paths in the prompt.
- Use the extracted asset path from `build/extracted_images/`, a page context
  image from `build/page_renders/`, a page crop, or a user-provided reference
  image together with the corresponding source page, section, caption, or
  surrounding paragraph when planning any slide that uses that visual.
- If an independent chart/figure is visible only inside a page render, crop it
  into `build/extracted_images/source_visual_crops/` before slide planning and
  append it to `build/source_visual_refs.json`:

```bash
python3 .agents/skills/image-ppt-from-docs/scripts/crop_source_visual.py \
  build/page_renders/<source>/page_003.png \
  --bbox x1,y1,x2,y2 \
  --out build/extracted_images/source_visual_crops/<short_name>.png \
  --source-path sources/<source>.pdf \
  --page 3 \
  --context "caption or surrounding source text"
```

- Use `--relative` when the bbox is specified as fractions from 0 to 1.
- Preserve chart structure, data values, labels, axis relationships, legends,
  relative proportions, and recognizable visual appearance as much as possible.
  Do not redraw the chart from memory or simplify it in a way that changes the
  meaning.
- If the current Codex image-generation environment cannot attach local images
  as reference inputs for `$imagegen`, do not pretend high-fidelity preservation
  happened. Continue only for slides that do not require that source visual, or
  report the limitation and the affected visual refs.
- If the image model cannot preserve the chart faithfully enough, report that
  limitation in `output/README.md` and the final response instead of silently
  changing the chart or its data.

Do not dump all extracted text into slides. Synthesize.

### 2. Infer the presentation context

Before writing slide prompts, create `build/presentation_brief.md`.

This brief must explicitly state:

- probable presentation scenario(s)
- chosen primary scenario and why
- inferred audience(s)
- communication goal
- recommended overall tone
- recommended deck length and why
- detail strategy: where to be concise vs where to be detailed
- candidate visual direction(s)

Important rules:

- Do **not** hard-code “executive audience” unless the sources strongly indicate it.
- Be open to multiple contexts such as academic, business, technical, educational, or public-facing communication.
- Choose a primary scenario, but the deck should still be broadly usable.

### 3. Decide the story before generating images

Create `build/deck_plan.json` before image generation.

The plan must include:

- `deck_title`
- `scenario`
- `audience`
- `language`
- `aspect_ratio`
- `style_system`: unified art direction for the entire deck
- `detail_strategy`: overall rationale for the level of detail
- `slides`: array of slide objects

Each slide object must include:

- `slide_no`
- `title`
- `message`: one sentence that explains the slide’s point
- `visual_role`: cover / context / evidence / framework / comparison / roadmap / case / method / timeline / closing / appendix
- `detail_level`: `low | medium | high`
- `on_slide_text`: exact text to appear in the image; may be sparse or moderately detailed depending on need
- `image_prompt`: complete prompt for Codex `$imagegen`
- `source_refs`: source files or page/section notes used
- `source_visual_refs`: extracted chart, figure, table-image, or reference image
  paths used by the slide, plus the corresponding page/section/caption context,
  `input_fidelity`, and whether they must be attached as image inputs; use an
  empty array if the slide has no source visual to preserve

Recommended deck logic:

1. establish the topic and framing
2. explain context / problem / question
3. present key evidence or findings
4. explain mechanism / framework / method / architecture
5. discuss implications / options / roadmap / recommendations
6. close with synthesis / decision / next steps

For longer decks, add case studies, literature or related work, methodology, technical detail, implementation stages, risks, limitations, or appendix visuals.

### 4. Codex-only image generation path

Use **Codex built-in** image generation only.

Important operating rules:

- Explicitly invoke `$imagegen` or ask Codex to generate images directly.
- Do not use API scripts.
- For multiple slides, stay on the built-in path and generate one image per slide.
- For any slide whose `source_visual_refs` is non-empty, attach those referenced
  files as image inputs/reference images to the `$imagegen` call with
  high-fidelity preservation intent. Do not rely on writing a local file path in
  text; the image model must actually receive the image.
- Keep all final slide images under `output/images/`.
- Save each slide prompt under `build/prompts/slide_XX.txt`.
- Each generated image should be a complete slide, including the intended
  title, labels, annotations, and other `on_slide_text`.
- After copying the generated image to `output/images/slide_XX.png`, do not
  modify it except for mechanical file-format/size normalization needed by
  the PPTX builder.
- Do not store generated slides in `build/`; `build/` is only for extraction,
  planning, prompts, and source-derived previews.

Recommended generation strategy for multi-page decks:

1. Generate slide 1 first to establish the visual language.
2. Optionally generate one additional anchor slide (often a framework or evidence slide) if the deck needs both narrative and diagrammatic consistency.
3. Generate the remaining slides while preserving:
   - palette
   - typography feel
   - composition rhythm
   - image treatment
   - margin system
   - diagram language
4. If Codex supports using prior generated slides as references in the current environment, use the strongest one or two earlier slides as style anchors for later slides.
5. If a slide must be denser (for example an academic method slide or a technical architecture slide), keep the same style system but increase informational density thoughtfully.
6. If Codex supports image-reference attachment but not exact fidelity controls,
   still attach the source visual and state the preservation goal explicitly in
   the prompt. If the result materially changes the chart, regenerate or report
   the limitation.

### 5. Prompting rules for slide images

Write prompts like artifact specs, not vague illustration requests.

Every slide prompt must combine two layers: (1) communication clarity and (2) intentional art direction.

Each slide prompt should include:

- deliverable: “one 16:9 presentation slide image”
- inferred scenario and audience
- slide role
- core message
- exact allowed text
- layout hierarchy
- visual metaphor, chart type, or diagram type
- unified style system
- detail level for that slide
- source visual assets to preserve, when any extracted charts or figures are
  used, with their matching page/section/caption context
- constraints and exclusions

Use this structure:

```text
Create one 16:9 presentation slide image.
Scenario: ...
Audience: ...
Slide role: ...
Core message: ...
Detail level: low / medium / high, with a concise rationale.
Exact text to render, no extra words: ...
Visual design: ...
Composition: ...
Style system for the entire deck: ...
Reference images to attach, if applicable:
- path: ...
  purpose: high-fidelity source chart/figure reference
  matching source context: ...
  fidelity requirement: preserve the original chart structure, data values,
  labels, axis relationships, legend, proportions, and recognizable appearance
  as much as possible.
Source visual preservation instruction, if applicable: the attached source
visual is a reference image input, not a style-only inspiration. Integrate it
into the generated slide while keeping the chart/figure materially unchanged.
Constraints: modern, coherent, readable, polished spacing, no watermark, no fake logos, no clutter, no unrelated stock-photo clichés.
```

For Chinese slides, ask for simplified Chinese text and explicitly list exact text.

The prompt must request that the model render the listed text directly on the
slide. Do not ask for a text-free visual plate when the user requested a
text-bearing presentation.

Do **not** always force very little text. Instead:

- use sparse text for covers, big ideas, and closing pages
- allow moderate text for explanatory framework slides
- allow more structured labels or short annotations for evidence, methods, and architecture when necessary
- still avoid turning an image slide into a full document page


### 5A. Art direction standard: avoid generic or cheesy slides

The prompts must carry **real art direction** and **strong graphic-design intent**. The goal is not just “clean slides”; it is to produce slides that feel like they were designed by a contemporary presentation designer or editorial art director.

Always establish a concise **style thesis** for the deck before writing slide prompts. This should describe:

- overall visual mood
- graphic-design lineage or feel
- composition logic
- palette behavior
- typography feel
- image treatment
- diagram language

Good style-thesis language can include ideas such as:

- editorial, art-directed, contemporary, premium
- Swiss-inspired grid discipline
- refined information design
- gallery-catalog restraint
- design-forward keynote aesthetic
- modern research-poster clarity
- cinematic but controlled
- conceptual visual metaphor
- tactile, restrained texture
- sophisticated contrast and whitespace

Do **not** write weak, generic prompts such as “make it modern and beautiful.”

Instead, use richer, taste-aware guidance like:

- “contemporary editorial layout with confident negative space and asymmetrical balance”
- “refined Swiss-grid composition with strong hierarchy and disciplined alignment”
- “art-directed presentation aesthetic, minimal but not empty, with elegant information density”
- “high-end design language, avoiding stock-business clichés”
- “diagrammatic clarity with poster-level visual impact”

### 5B. Anti-cheesy rules

Actively avoid “土、俗、廉价模板感” output.

Exclude these common failure modes explicitly when relevant:

- clichéd corporate stock-photo look
- handshake imagery, cheering team poses, random office people, fake meetings
- glossy pseudo-3D business icons
- overused blue-gradient SaaS dashboard style unless the source clearly calls for it
- crowded infographic clutter
- heavy bevels, glows, drop shadows, neon gimmicks, or template-like ribbons
- childish icon packs or clip-art feel
- random decorative shapes with no narrative purpose
- fake app UI panels when a diagram would communicate better
- generic “AI brain” clichés unless reinterpreted in a refined way

Prefer:

- bold but disciplined composition
- elegant whitespace
- restrained palettes with one or two intentional accents
- strong visual hierarchy
- carefully chosen conceptual metaphors
- refined poster-like typography
- layout rhythm that feels designed rather than auto-generated
- image and text relationships that feel editorial and deliberate

### 5C. Artistic prompt enrichment pattern

When writing each slide prompt, include both the content spec and the design sensibility.

A stronger prompt frame looks like this:

```text
Create one 16:9 presentation slide image.
Scenario: ...
Audience: ...
Slide role: ...
Core message: ...
Detail level: ...
Exact text to render, no extra words: ...
Visual concept: ...
Composition: ...
Art direction: contemporary editorial graphic design, sophisticated hierarchy, strong grid discipline, refined whitespace, elegant asymmetry, high-end presentation design.
Typography feel: large, confident, poster-like, clean, highly legible, with tasteful contrast in scale and weight.
Palette and mood: ...
Style system for the entire deck: ...
Avoid: stock-business clichés, cheap template feel, clutter, gimmicky 3D, random icons, fake dashboards, excessive decoration, awkward text blocks.
Constraints: polished, tasteful, memorable, presentation-ready.
```

If a specific deck tone is appropriate, explicitly say so, for example:

- academic: “design-forward research communication, clean and intelligent rather than bureaucratic”
- strategy: “premium editorial strategy-deck feel, like a well-designed keynote rather than a consultancy template”
- product pitch: “persuasive and vivid, but art-directed and tasteful rather than promotional cliché”
- technical: “precise, elegant systems thinking aesthetic with clean abstractions and minimal noise”


### 6. Quality bar

Every slide must pass:

- one main point per slide
- coherent style across the deck
- readable at presentation size
- no hallucinated source claims
- no invented metrics unless clearly marked as illustrative
- no irrelevant decorative elements
- no accidental logos/watermarks
- no cropped important content
- the level of detail matches the communication need
- source charts and figure-like visuals are not materially changed when the
  slide claims to preserve them
- dense slides are intentionally dense, not messy
- simple slides are intentionally simple, not empty

After generation, create a contact sheet:

```bash
python .agents/skills/image-ppt-from-docs/scripts/qa_contact_sheet.py output/images --out output/contact_sheet.jpg
```

Inspect it. If a slide fails, regenerate only that slide with a more constrained prompt.

Inspection is a quick objective gate, not a design-reflection loop. Check only
for concrete delivery failures such as blank images, unreadable/cropped text,
missing required text, obvious hallucinated logos/watermarks, severe layout
breakage, or a slide that clearly ignores the prompt. Do not add post-generation
commentary or local text overlays as part of this step.

### 7. Build the PowerPoint

After slide images are generated and the objective contact-sheet gate has no
blocking failures, build the PowerPoint immediately:

```bash
python .agents/skills/image-ppt-from-docs/scripts/make_image_pptx.py output/images --out output/deck.pptx
```

Create a short `output/README.md` summarizing:

- source files used
- inferred scenario and audience
- page count
- output paths
- any caveats or manual review notes

### 8. Final response to user

Report:

- where the PPT is saved
- page count
- source folder used
- that the deck used **Codex built-in image generation** only
- inferred presentation scenario / audience
- any limitations, especially if some source material was scanned/OCR-poor or if a dense slide may need manual review

Do mention `build/deck_plan.json` if the user wants to tweak the deck.

## Style selection guidance

Let style follow context, and let context be inferred:

- default international visual direction: minimalist modern flat design with
  strong hierarchy, generous whitespace, crisp typography, and refined graphic
  systems inspired by Apple keynote restraint, Swiss/International Typographic
  Style, Bauhaus geometry, and constructivist composition
- academic / research: clean diagrams, disciplined hierarchy, neutral palette, strong evidence visuals
- consulting / strategy: premium editorial, concise frameworks, strong spacing, restrained palette
- technical / architecture: abstract systems diagrams, precise labeling, modular structure, low clutter
- public communication / policy: clear narrative infographics, accessible metaphors, trustworthy tone
- product / solution pitch: stronger hero imagery, persuasive structure, balanced clarity and aspiration
- education / workshop: guided explanations, more labeling, more sequential visuals

Prefer flat, graphic, presentation-native visuals over photorealistic stock
imagery unless the source material clearly needs real-world inspection. The
whole deck must still share one coherent visual language: palette, type feel,
spacing, image treatment, and compositional rhythm.

## Safety and confidentiality

- Treat source documents as confidential project files.
- Do not upload files to third-party services beyond the Codex/OpenAI workflow already being used.
- Do not invent citations or facts.
- If source docs contain sensitive personal data, minimize or anonymize it unless the user asks to preserve it.
- Respect copyright: transform and summarize; do not reproduce long copyrighted passages verbatim.
