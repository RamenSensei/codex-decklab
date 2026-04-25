# deck_plan.json schema

Minimal shape:

```json
{
  "deck_title": "string",
  "scenario": "string",
  "audience": "string",
  "language": "source/user language, English, bilingual, or other inferred language",
  "aspect_ratio": "16:9",
  "style_system": "one concise art direction shared by the whole deck",
  "detail_strategy": "overall rationale for simplicity vs depth",
  "slides": [
    {
      "slide_no": 1,
      "title": "string",
      "message": "one sentence",
      "visual_role": "cover | context | evidence | framework | comparison | roadmap | case | method | timeline | closing | appendix",
      "detail_level": "low | medium | high",
      "on_slide_text": ["exact", "text"],
      "image_prompt": "complete slide image prompt",
      "source_refs": ["source file / page / section"],
      "source_visual_refs": [
        {
          "path": "build/extracted_images/..., build/extracted_images/source_visual_crops/..., or source image path",
          "context": "matching page / section / caption / surrounding text",
          "attach_as_image_input": true,
          "input_fidelity": "high",
          "preservation_goal": "preserve chart structure, data values, labels, axes, legend, proportions, and recognizable appearance"
        }
      ]
    }
  ]
}
```

Rules:

- `scenario` and `audience` should be inferred from the source context instead of being hard-coded.
- `language` should follow the user request and source material. If unspecified,
  prefer an internationally usable language choice, often English or bilingual,
  rather than assuming Chinese.
- `detail_level` is required per slide.
- Do not assume every slide must be sparse. Decide detail by communication need.
- Put exact text in quotes inside `image_prompt` when text must appear.
- `image_prompt` should describe a complete final slide image. Do not plan a
  separate local text-overlay or repaint step after image generation unless the
  user explicitly requested it.
- Never invent data. Use `source_refs` for claims and metrics.
- When a slide uses a standalone source chart, plot, table-image, or figure-like
  diagram, include it in `source_visual_refs` together with its matching source
  context. Set `attach_as_image_input` to `true` and `input_fidelity` to `high`.
  The slide prompt must ask the image model to preserve the original chart's
  structure, values, labels, axis relationships, legend, proportions, and
  recognizable appearance as much as possible.
- A local path in `source_visual_refs` is an attachment instruction for Codex,
  not slide text. When generating the slide, attach that file as an image input
  or report that the current environment cannot perform high-fidelity reference
  image generation.
- `style_system` must be shared by all slides, but should be chosen from the source context rather than hard-coded. When unspecified, prefer minimalist modern flat design with Apple keynote restraint, Bauhaus/constructivist geometry, and Swiss-grid discipline.
- Generated slide images must be copied directly to `output/images/slide_XX.png`.
  Intermediate planning stays in `build/`; generated slides do not.
