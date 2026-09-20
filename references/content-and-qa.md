# Content and coverage checks

## Reading and indexing

Extract text with page boundaries preserved. `pdftotext -layout` works for born-digital PDFs but loses crossed-out corrections, annotations, checkboxes, and some formula ordering. View those pages as images. For PowerPoint or images use available appropriate readers/renderers and preserve slide/image numbering. A heading-only scan is an index, not a substitute for reading.

Read the whole teaching scope, then revisit exact pages when authoring. Inventory definitions, assumptions, results, methods, example patterns, code/output interpretation, diagnostics, and limitations as appropriate to the subject. Not every example dataset needs copying; its underlying method does.

Keep a ledger in the task workspace:

| Source | Locator | Topic / question | Sheet block | Evidence / status |
|---|---|---|---|---|
| lecture-A.pdf | PDF p.12 / slide 10 | theorem and conditions | module-A.topic-3 | checked |
| mock.pdf | Q1(a) | false claim / counterexample | module-A.topic-3 | derived; no solution supplied |

For multiple-choice or true/false questions account for **every option**, not only correct choices. Computational questions need the workflow, interpretation, and essential numerical example when space permits. Put exam connections inside relevant modules, rather than an appendix displacing lecture coverage.

## Fidelity and compression

- Preserve notation and dimensions, including row/column derivatives, df, log bases, parameter scalings, and known versus estimated variance.
- Keep assumptions near formulas: independence, rank, definiteness, nonzero denominators, finite moments, support, or method-specific conditions.
- Distinguish one-way implications and equivalences; sufficient conditions are not automatically necessary.
- Retain distinctions such as population/estimate, test/selection, confidence/prediction, conditional/marginal, and joint/marginal assumptions when relevant.
- For other disciplines preserve units, physical assumptions, algorithm preconditions, complexity, sign conventions, and version-sensitive syntax as applicable.
- Do not copy demonstrably incorrect source statements. Mark corrections briefly and explain discrepancies in delivery. Label unresolved uncertainty.
- Remove duplicated prose and redundant examples first, then tighten wording or rearrange formulas. Do not omit conditions, units, qualifiers, or required topics just to fit.
- Put source pages near topics. Explain the page-number convention if PDF and printed numbering differ.

## Verify the actual artifact

The renderer audit records content/output hashes, every block's column/bounds, and font sizes. It detects layout omissions, not inaccurate or incomplete summaries.

Review the PDF alongside the ledger, checking mapped content rather than only question labels. Recompute important examples independently. Check signs, denominators, matrices, fractions, exponents, and subscripts on the rendered page; correct source text can still render badly.

Render all pages at 180–220 dpi. Zoom into dense regions and long formulas, and inspect representative regions at actual A4 size. Requested density does not justify missing glyphs, overlap, or unreadably compressed formulas. The default minimum font size is a guardrail, not a readability guarantee; change it only with an appropriate user density preference and successful visual inspection.
