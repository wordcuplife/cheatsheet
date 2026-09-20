---
name: cheatsheet
description: Create dense, handwritten-style, three-column printable A4 cheatsheet PDFs from lecture materials, optionally prioritizing supplied exam questions and solutions. Use for course revision sheets, formula sheets, and exam cheatsheets; retain source page references and verify content coverage and print layout.
---

# Cheatsheet

Turn supplied lecture materials into a source-faithful, compact study sheet. Exams and answers are optional. Default: **one A4 sheet printed on both sides (two PDF pages), three columns per page**, handwritten-style text and vector formulas. Follow explicit user choices for language, page count, density, output name, and style.

## Establish scope from the files

- Locate lectures, optional questions/solutions, and any style reference. Check page counts and final pages; read every lecture before selecting content. For scanned or formula-heavy pages, use OCR plus rendered-page inspection. Do not claim to have read unreadable or missing pages.
- Preserve module order and names, including subdivisions such as 4a and 4b. There is no fixed module count or subject restriction.
- With lectures alone, prioritize definitions, results, assumptions, formulas, workflows, and common confusions supported by the material. Do not invent exam predictions. With exams, map every question/subpart/option to lecture content; red stars identify supplied-exam coverage.
- Use the requested language, otherwise the conversation language, preserving technical terms and notation. Inspect supplied style samples; do not copy student names, IDs, or unrelated course content.
- State a short plan. Respect a user requirement for plan approval; existing approval persists. Ask only for material missing decisions, such as conflicting page limits. Do not assume the sheet is permitted in an actual exam.

## Build and audit the content

Maintain a working source index outside the skill directory: module, topic, PDF page, and printed page if different. Maintain a coverage ledger linking each major lecture topic and every exam subpart/option to a sheet block. Record gaps or unresolved conflicts.

Read [references/content-and-qa.md](references/content-and-qa.md). Preserve formula domains, assumptions, definitions, units, parameter conventions, and implication directions. Compress repeated exposition rather than silently deleting topics. Include proof recipes or counterexamples when useful. Verify supplied solutions; flag discrepancies. Without solutions, label worked results as derived, not official.

Group by module. Use blue topic titles, purple subheadings, black body, and red key results or exam connections with `★ Q2(b)`-style locators. Source references must resolve to actual supplied pages. Distinguish supplemental explanations from source claims.

## Render the established style

Read [references/renderer.md](references/renderer.md) before using the bundled renderer. It accepts structured text, adjusts size, handles any module count, and continues long modules across columns. It does not generate or fact-check content.

Palette: green `#64ba48` module headings and circled Arabic sequence numbers; blue `#087bff` topics; purple `#b924db` subtitles; red `#e9322a` important content. Pure white background, A4 portrait, about 6 mm side margins, print-safe headers/footers. Formulas stay vector-based. Dense text must remain legible at actual printed size.

Use available PDF/document readers for input. Rendering needs Python with `reportlab`, `matplotlib`, and `fonttools`; QA uses `pypdf` and a rasterizer such as Poppler. Prefer a configured runtime if available. Do not embed private Python paths or install dependencies without observing environment permissions.

Use a locally available licensed handwriting font or a supplied font. The renderer discovers HanziPen on macOS or accepts a path/index. Fonts and course files are not bundled. If no suitable handwriting font exists, disclose the limitation and obtain a font or agreed fallback; do not claim an exact match. Resolve missing characters rather than printing squares. Font subsets belong in task scratch space.

Keep generated files in the task workspace, never the installed skill. Use the requested output name, otherwise `Cheatsheet.pdf`. Do not overwrite an existing user file without authorization. If the page budget cannot fit legibly, improve concision and flow without dropping coverage, then resolve the page-count/density tradeoff with the user. The user may request a smaller minimum font size, but never clip or discard content to fit.

## Verify and deliver

1. Check the topic/exam ledger against the actual sheet. Layout audits prove block placement, not semantic completeness. Recalculate important examples and inspect formulas against sources.
2. Run `scripts/check_pdf.py` on the PDF and renderer audit. Require requested A4 pages, embedded fonts, and no replacement glyphs. Review warnings.
3. Render **every page** and view it. Check all columns, continuation headings, colors, equations, page references, margins, and actual-size readability. Fix overlap, compressed formulas, missing glyphs, or clipping; re-render changed pages. Inspect representative formulas at higher zoom.
4. Deliver the final PDF, describe coverage and material limitations, and give print settings: **A4, actual size / 100%, duplex, long-edge flip**. Do not expose internal audits as study content or claim complete coverage just because module titles appear.
