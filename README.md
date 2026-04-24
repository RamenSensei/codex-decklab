# Codex DeckLab

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#quick-start)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill-25573B)](.agents/skills/image-ppt-from-docs/SKILL.md)
[![Status](https://img.shields.io/badge/status-experimental-orange)](#boundaries)
[![License](https://img.shields.io/badge/license-MIT-green)](#license)
[![GitHub stars](https://img.shields.io/github/stars/RamenSensei/codex-decklab?style=social)](https://github.com/RamenSensei/codex-decklab/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/RamenSensei/codex-decklab?style=social)](https://github.com/RamenSensei/codex-decklab/forks)
[![GitHub last commit](https://img.shields.io/github/last-commit/RamenSensei/codex-decklab)](https://github.com/RamenSensei/codex-decklab/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/RamenSensei/codex-decklab)](https://github.com/RamenSensei/codex-decklab/issues)

NotebookLM-style source grounding for image-based slide decks, built as a
Codex-native skill.

Codex DeckLab turns PDF/DOCX files and reference images in `./sources/` into
polished, full-image PowerPoint decks. It uses Codex built-in image generation
and local deterministic scripts for extraction, QA contact sheets, and PPTX
assembly.

## Gallery
```
Use $image-ppt-from-docs. Read the files in sources/ and create a highly detailed, 15-slide Chinese image-based presentation for a professional audience. Let the model choose a unified academic conference style based on the materials. Save the output to output/.
```
[!contact-sheet.jpg](https://i.ibb.co/Zz9fZrsM/contact-sheet.jpg)


## Design Principles

- **Codex-native workflow**: source extraction, story planning, per-slide image
  generation, and PPTX assembly all happen through Codex plus local scripts.
- **Source-grounded deck generation**: preserve claims, numbers, dates, caveats,
  and source hierarchy from local materials instead of inventing unsupported
  content.
- **International language and audience**: do not assume Chinese or an
  executive audience. Infer language, scenario, and audience from the user
  request and source material. If unspecified, prefer English or a bilingual
  approach when it improves international usability.
- **Adaptive detail density**: do not force every slide to be minimal. Decide
  which slides need strong visuals and sparse text, and which need structured
  labels or annotations.
- **Unified deck system**: keep one coherent visual language across the deck.
- **Default visual direction**: minimalist, modern, flat, design-forward. Good
  references include Apple keynote restraint, constructivist composition,
  Bauhaus geometry, and Swiss / International Typographic Style.
- **High taste bar**: prompts must include explicit art direction and actively
  avoid cheap templates, stock-business cliches, clutter, and random decoration.

## Quick Start

### 1. Prepare the project

```bash
cd codex-decklab
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .agents/skills/image-ppt-from-docs/scripts/prepare_workspace.py
codex
```

Put your `.pdf`, `.docx`, `.png`, `.jpg`, or `.webp` files in `./sources/`.

### 2. Run the default workflow

Prompt Codex with this:

```text
Use $image-ppt-from-docs.
Read ./sources/ and create an international image-based PPT.
Use the language implied by the user request and source material; if unspecified, prefer English or bilingual where appropriate.
Infer the most suitable presentation scenario and audience from the materials.
Choose the slide count and level of detail based on the source density and communication goal.
Keep one unified minimalist modern flat visual system for the whole deck, with Apple keynote-like restraint, Bauhaus/constructivist geometry, and Swiss-grid discipline.
Output to output/ and save the plan in build/deck_plan.json.
```

### 3. Review outputs

After Codex finishes, check:

- `./output/deck.pptx`: final PowerPoint deck
- `./output/images/`: one full-slide image per page
- `./output/contact_sheet.jpg`: visual QA overview
- `./build/deck_plan.json`: editable story and prompt plan
- `./build/prompts/`: final prompt used for each slide

## Example Prompts

Use these prompts directly in Codex after placing source materials in
`./sources/`.

### General International Deck

```text
Use $image-ppt-from-docs.

Read all files in sources/ and create a 12-page international image-based PPT.
Infer the scenario, audience, language, and communication goal from the
materials. If language is not obvious, use English.

Use a minimalist modern flat visual system: Apple keynote-like restraint,
Bauhaus geometry, constructivist composition, Swiss-grid discipline, generous
whitespace, crisp hierarchy, and one restrained accent color.

Each generated image must be the final slide image, including the intended
title, labels, and annotations. Save final slide images directly to
output/images/slide_XX.png, then create output/contact_sheet.jpg and
output/deck.pptx. Do not create local text overlays or repaint scripts.
```

### Academic / Research Talk

```text
Use $image-ppt-from-docs.

Read sources/ and create a 15-page image-based research talk for a professional
academic audience. Preserve important definitions, theorem statements,
technical claims, numbers, dates, and source caveats. Use English unless the
source strongly suggests another language.

Style: modern research keynote, minimalist flat diagrams, Swiss grid,
constructivist proof-flow composition, restrained palette, high legibility for
conference projection. Use more detail on method/evidence slides and less text
on cover and closing slides.

Output only through the fixed workflow:
build/source_summary.md, build/presentation_brief.md, build/deck_plan.json,
build/prompts/slide_XX.txt, output/images/slide_XX.png,
output/contact_sheet.jpg, output/deck.pptx, output/README.md.
```

### Product / Strategy Brief

```text
Use $image-ppt-from-docs.

Read sources/ and create a concise 10-page image-based strategy brief for a
professional business and product audience. Infer the product, user problem,
market context, evidence, roadmap, risks, and recommended next steps from the
materials. Use English unless I specify otherwise.

Style: premium minimalist keynote, Apple launch-event restraint, flat geometric
visuals, bold typography, editorial spacing, no stock-business cliches, no fake
dashboards, no glossy 3D icons.

Make each generated image a complete final slide and save it directly under
output/images/. Build output/deck.pptx immediately after the contact sheet QA.
```

### Bilingual Deck

```text
Use $image-ppt-from-docs.

Read sources/ and create a 12-page bilingual image-based PPT with English as
the primary language and concise Chinese support text only where useful.
Infer the scenario and audience from the materials.

Use a clean international flat design system: Swiss grid, Bauhaus geometry,
constructivist composition, large clear type, generous whitespace, restrained
accent colors. Keep bilingual text short enough to remain readable in the
generated slide image.

Generate final slide images directly to output/images/slide_XX.png, then build
output/contact_sheet.jpg and output/deck.pptx. Do not use post-generation
local text overlays.
```

### Dense Technical Briefing

```text
Use $image-ppt-from-docs.

Read sources/ and create an 18-page technical briefing for engineers and
technical decision makers. Preserve architecture, workflow, method, constraints,
metrics, risks, and implementation sequence. Use high detail where the source
is technical, but organize it with diagrams, labels, callouts, and comparison
frames rather than paragraphs.

Style: minimalist modern flat systems diagrams, Apple keynote restraint,
Bauhaus modular geometry, Swiss alignment, crisp labels, restrained neutral
palette with one accent. Avoid fake UI screens unless the source is explicitly
about an interface.

Use the fixed path contract exactly. Each generated image is the final slide
image in output/images/. If a slide has missing or unreadable generated text,
regenerate only that slide with a stricter prompt.
```

### Custom Page Count and Language

```text
Use $image-ppt-from-docs.

Read sources/ and create a 20-page image-based PPT in Spanish for a public
policy audience. Infer the key public-facing narrative, evidence, tradeoffs,
stakeholders, timeline, and recommendations from the materials.

Use a minimalist modern flat editorial style with Bauhaus geometry,
constructivist poster-like composition, Swiss-grid structure, and a restrained
trustworthy palette. Keep all text readable in the generated images.

Output to output/ using the fixed path contract. Save the plan to
build/deck_plan.json before generating images.
```

## How to Customize Requests

Add any of these constraints to your prompt:

- `Create exactly 8 / 12 / 15 / 20 pages.`
- `Use English / French / Japanese / bilingual English-Chinese.`
- `Audience: board review / academic seminar / sales enablement / training workshop.`
- `Style: Apple keynote minimalism + Bauhaus geometry + Swiss grid.`
- `Detail density: high for method and evidence slides, sparse for cover and closing.`
- `Preserve all numerical claims, dates, method names, and caveats from the source.`
- `Use only diagrams and abstract visuals; avoid stock photography.`
- `Include an appendix-style final slide for limitations and source caveats.`

## Recommended Automated Workflow

1. Create a project directory.
2. Put PDFs, DOCX files, and optional reference images in `sources/`.
3. Start `codex` from that directory.
4. Codex automatically:
   - runs the extraction script
   - reads `build/source_summary.md`
   - creates `build/presentation_brief.md`
   - creates `build/deck_plan.json`
   - generates each final slide image directly as `output/images/slide_XX.png`
   - creates `output/contact_sheet.jpg` for QA
   - builds `output/deck.pptx`
   - writes `output/README.md`

## Outputs

- `build/source_summary.md`: extracted source summary
- `build/presentation_brief.md`: inferred scenario, audience, story strategy,
  and detail strategy
- `build/deck_plan.json`: slide titles, messages, prompts, and unified style
- `build/prompts/slide_01.txt` ...: final prompt for each slide
- `output/images/slide_01.png` ...: final slide images
- `output/deck.pptx`: full-bleed image-based PowerPoint deck
- `output/contact_sheet.jpg`: thumbnail overview for QA

## Fixed Path Contract

- Input: `sources/`
- Intermediate files: `build/`
- Slide images: `output/images/slide_XX.png`
- PPTX: `output/deck.pptx`
- QA overview: `output/contact_sheet.jpg`

Do not create replacement folders such as `build/generated_full/`,
`build/generated_plates/`, or `output/slides/`. After image generation, proceed
directly to contact sheet creation and PPTX assembly. Do not default to local
post-generation text overlays or slide repainting.

## Boundaries

This workflow is best for image-based, visual, presentation-oriented decks.

If the source material requires:

- very long tables
- exact formula typesetting
- dense academic citations
- extensive footnotes
- Word-document-like detail presentation

then Codex should still create `./build/deck_plan.json`, but the final deliverable may
need a mixed format of image slides plus native text/table slides. This example
package defaults to an all-image deck unless the user requests otherwise.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=RamenSensei/codex-decklab&type=Date)](https://www.star-history.com/#RamenSensei/codex-decklab&Date)

## License

MIT.
