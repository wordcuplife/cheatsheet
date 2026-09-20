# Cheatsheet

Cheatsheet is a Codex skill for turning lecture materials and optional exam questions into dense, source-faithful, printable revision sheets.

The default output is a two-page A4 PDF designed for duplex printing, with three columns per page, compact handwritten-style text, vector formulas, source-page references, and optional exam-topic markers.

## Installation

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/wordcuplife/cheatsheet.git ~/.agents/skills/cheatsheet
```

Restart Codex after installation. Invoke the skill with `$cheatsheet`, or ask Codex to create a printable cheatsheet from supplied course materials.

## Example Request

```text
$cheatsheet Create a two-page A4 revision sheet from these lecture PDFs. Use the supplied practice exam to mark relevant topics and retain source page numbers.
```

## Requirements

The bundled renderer requires Python 3.9 or later and these Python packages:

```bash
python3 -m pip install reportlab matplotlib fonttools pypdf
```

Visual PDF review also requires Poppler's `pdftoppm`. On macOS it can be installed with:

```bash
brew install poppler
```

The renderer can discover HanziPen on macOS or accept a font explicitly with `--font`. Fonts are not distributed with this repository. If no suitable handwriting font is available, it falls back to DejaVu Sans and records a warning in the audit file.

## What It Does

- Reads all supplied lecture materials before selecting content.
- Builds a source and coverage ledger for lecture topics and optional exam questions.
- Preserves definitions, assumptions, notation, formulas, units, and implication directions.
- Renders compact A4 study notes in a three-column format.
- Produces a JSON audit describing page layout, block placement, font provenance, and file hashes.
- Checks page count, A4 dimensions, embedded fonts, placement completeness, and replacement glyphs.
- Requires visual inspection of every rendered page before delivery.

## Direct Renderer Usage

Prepare a UTF-8 notes file in the format described in [`references/renderer.md`](references/renderer.md), then run:

```bash
python3 scripts/render_cheatsheet.py \
  --input notes.txt \
  --output Cheatsheet.pdf \
  --title "Course cheatsheet" \
  --pages 2 \
  --sources "Lectures and practice exam"

python3 scripts/check_pdf.py \
  Cheatsheet.pdf \
  --audit Cheatsheet.audit.json \
  --pages 2
```

The structural checker does not prove that the summary is complete or mathematically correct. Source coverage, formula accuracy, and visual readability still require review.

## Printing

Use A4 paper, actual size or 100% scale, duplex printing, and long-edge flipping.

## Repository Contents

- `SKILL.md`: agent workflow and quality requirements.
- `references/content-and-qa.md`: source-fidelity and coverage checks.
- `references/renderer.md`: renderer input format and command-line interface.
- `scripts/render_cheatsheet.py`: deterministic PDF renderer.
- `scripts/check_pdf.py`: structural PDF verifier.
- `agents/openai.yaml`: skill-list metadata.
- `AGENTS.md`: repository maintenance guidance.
- `LICENSE`: MIT License.

## Privacy and Scope

Do not commit lecture files, exam papers, student names or IDs, generated cheatsheets, audit files, font files, local cache directories, credentials, or machine-specific private paths to this repository.

The skill helps produce revision material. It does not determine whether a cheatsheet is permitted in a particular assessment, and it does not guarantee exam coverage or results.

## License

MIT
