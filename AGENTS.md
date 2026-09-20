# Repository Guide

This repository contains a Codex skill and deterministic helpers for creating dense, source-faithful, printable A4 cheatsheets.

## Key Files

- `SKILL.md` is the source of truth for the agent workflow.
- `references/content-and-qa.md` defines source coverage and semantic checks.
- `references/renderer.md` documents the notes format and renderer controls.
- `scripts/render_cheatsheet.py` creates the PDF and layout audit.
- `scripts/check_pdf.py` validates structural PDF properties.
- `agents/openai.yaml` provides skill-list metadata.
- `README.md` is the public installation and usage guide.
- `LICENSE` contains the MIT License.

## Maintenance Contract

Keep the skill instructions, reference documentation, renderer interface, and verifier expectations aligned. Preserve these requirements:

- Read every supplied lecture before selecting content.
- Maintain source and exam-coverage ledgers outside the installed skill.
- Preserve notation, assumptions, units, qualifiers, and implication directions.
- Never silently drop content to satisfy a page limit.
- Keep the default A4 portrait, three-column layout print-safe.
- Keep formulas vector-based and fonts embedded.
- Retain overwrite protection and atomic output behavior.
- Treat structural validation as separate from semantic and visual review.
- Render and inspect every output page before delivery.

## Editing Guidance

Do not add course PDFs, exam papers, generated PDFs, audit files, font files, cache directories, student information, credentials, or private local paths.

When changing the text format or command-line interface, update both `references/renderer.md` and `README.md`. When changing audit fields or layout bounds, update `scripts/check_pdf.py` and its documentation together.

Before publishing a change:

1. Run the skill validator against the repository.
2. Compile both Python scripts without writing bytecode caches.
3. Check each command-line interface.
4. Run a representative render and structural verification when dependencies are available.
5. Render and inspect every generated test page.
6. Search for credentials, personal data, private paths, and generated artifacts.
