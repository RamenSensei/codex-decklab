# Prompt patterns for image-based PPT slides (Codex-only)

## Master pattern with art direction

```text
Create one 16:9 presentation slide image.
Scenario: ...
Audience: ...
Slide role: ...
Core message: ...
Detail level: low / medium / high, with rationale.
Exact text to render, no extra words: "..."
Visual concept: ...
Composition: ...
Art direction: minimalist modern flat design, Apple keynote-like restraint, Bauhaus geometry, constructivist composition, Swiss-grid discipline, strong hierarchy, elegant negative space, high-end presentation design.
Typography feel: clean, international, highly legible, with confident scale contrast.
Palette and mood: ...
Style system for the entire deck: ...
Reference images to attach, if applicable:
- path: ...
  purpose: high-fidelity source chart/figure reference
  matching source context: ...
  fidelity: high; preserve chart structure, data values, labels, axes, legend,
  proportions, and recognizable appearance.
Avoid: stock-business clichés, cheap template feel, clutter, gimmicky 3D, fake dashboards, random icons, awkward text blocks.
Constraints: polished, tasteful, readable, presentation-ready.
```

Operational rule: the generated image is the final slide image. When the deck
requires text-bearing slides, prompts must ask the image model to render the
listed text directly. Do not prompt for a text-free background plate unless the
user explicitly asks for that asset type.

Source chart preservation rule: when the source contains an extracted
standalone data chart, plot, table-image, or figure-like diagram, include the
asset path and its matching page/section/caption context in the slide prompt,
then attach that file as a real reference image input to `$imagegen`. Ask the
image model to preserve the original structure, data values, labels, axis
relationships, legend, proportions, and recognizable appearance as much as
possible. Do not rely on a text-only local path, and do not ask the model to
redraw the chart from memory.

## Research / academic

```text
Create one 16:9 presentation slide image.
Scenario: academic conference talk.
Audience: researchers, graduate students, technically literate attendees.
Slide role: method / evidence / related work.
Core message: ...
Detail level: medium or high when the logic requires labels.
Exact text to render, no extra words: "..."
Visual concept: a rigorous yet visually engaging scientific explanation.
Composition: disciplined layout, projection-friendly hierarchy, strong diagram readability.
Art direction: design-forward research communication, contemporary editorial restraint, Swiss-grid clarity, intelligent and sophisticated rather than bureaucratic.
Typography feel: precise, calm, clean, with excellent legibility from a distance.
Style system: modern research deck, neutral palette, subtle accent color, refined diagram language.
Avoid: conference-template mediocrity, dense poster clutter, default office-document look.
```

## Modern international keynote

```text
Create one 16:9 presentation slide image.
Scenario: international professional presentation.
Audience: global professional audience.
Slide role: cover / framework / evidence / closing.
Core message: ...
Detail level: low / medium / high according to the slide's role.
Exact text to render, no extra words: "..."
Visual concept: a flat, geometric, presentation-native composition.
Composition: spacious, modern, confident hierarchy; Apple keynote restraint; Bauhaus/constructivist geometry; Swiss alignment.
Art direction: minimalist modern flat design, refined editorial keynote aesthetic, crisp vector-like forms, restrained palette with one intentional accent.
Typography feel: clean international sans-serif, large hierarchy, excellent projection readability.
Avoid: stock-photo business clichés, skeuomorphic objects, glossy 3D, cheap templates, clutter, fake dashboards.
```

## Technical architecture

```text
Create one 16:9 presentation slide image.
Scenario: architecture review or solution briefing.
Audience: engineering, product, or technical decision makers.
Slide role: framework / architecture.
Core message: ...
Detail level: high when the system needs explicit modules and flows.
Exact text to render, no extra words: "..."
Visual concept: a clear systems view with strong abstraction and clean flow.
Composition: labeled layers or modules, precise spacing, no wasted noise.
Art direction: elegant systems-thinking aesthetic, refined technical diagram design, minimal but not empty.
Typography feel: crisp and clean, with strong hierarchy for labels and section heads.
Style system: structured, low-clutter, technically credible, visually premium.
Avoid: fake product UI, glowing cloud icons, cheesy cyber visuals, random futuristic ornament.
```

## Pitch / 宣讲 / 方案沟通

```text
Create one 16:9 presentation slide image.
Scenario: product pitch, solution introduction, or 宣讲会.
Audience: mixed business or client audience.
Slide role: cover / problem / value / roadmap.
Core message: ...
Detail level: low to medium depending on persuasion need.
Exact text to render, no extra words: "..."
Visual concept: a persuasive narrative image with one strong visual anchor.
Composition: bold, memorable, structured, with clean support labels.
Art direction: premium editorial keynote aesthetic, expressive but controlled, visually striking without feeling like an ad template.
Typography feel: large, persuasive, polished, presentation-first.
Style system: unified modern visual language with restrained color accents.
Avoid: overhyped marketing cliché, stock-photo sales vibe, cheap glossy visuals.
```
