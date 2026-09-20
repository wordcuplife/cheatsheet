# Renderer interface

Python 3.9+ with `reportlab`, `matplotlib`, `fonttools`; verifier needs `pypdf`. Use a configured runtime or task-local environment. Visual QA needs `pdftoppm` or equivalent. Scripts work from any directory and contain no private runtime paths.

```bash
python3 scripts/render_cheatsheet.py \
  --input notes.txt --output 'Cheatsheet.pdf' --title 'Course cheatsheet' \
  --pages 2 --sources 'Lectures A-F; practice exam' \
  --legend 'Red stars: exam topics; p.: lecture PDF page'
python3 scripts/check_pdf.py \
  'Cheatsheet.pdf' --audit 'Cheatsheet.audit.json' --pages 2
pdftoppm -r 180 -png 'Cheatsheet.pdf' preview
```

Open every rendered image; software validation does not replace visual review or coverage checking.

## Content format

UTF-8, one paragraph/formula per line; blank lines ignored. `@` starts a module. Sequence numbers are Arabic integers drawn inside circles, independent of module labels such as Module 4a.

```text
@1|Module 1|Foundations
#1 Core concept [pp.3-5]
Black body text; preserve source conditions and notation.
:Purple subtitle / conditions
!★ Q1(a): red exam connection or important result.
=x^T A x=\sum_i\sum_j a_{ij}x_ix_j
!=E(X)=\mu
@2|Module 2|Applications
#1 Method [p.8]
Explain the workflow concisely.
```

Prefixes: `#` blue topic; `:` purple subtitle; `!` red text; `=` black formula; `!=` red formula; no prefix black body. HTML is escaped. Formulas use Matplotlib MathText without `$` delimiters, **not arbitrary LaTeX**. The helper supports exactly two-row `smallmatrix` expressions:

```text
=A=\left[\begin{smallmatrix}a&b\\c&d\end{smallmatrix}\right]
```

For larger matrices or unsupported notation, split into accurately labeled components or adapt the renderer with an available vector equation tool. Avoid ambiguous flattened matrices. Split long equations into separate `=` lines with explicit continuation signs instead of shrinking below readability.

## Controls

- `--font PATH --font-index 0`: TTF/OTF/TTC/OTC handwriting font; inspect the correct index for collections. Embedding restrictions are checked. Discovery prefers macOS HanziPen, otherwise DejaVu Sans with an audit warning. Missing Chinese characters fail clearly.
- `--font-size 6.15 --min-font-size 5.0`: body-size range, points; headings larger. Formula effective size also respects the minimum. Do not lower the minimum just to suppress overflow.
- `--pages 2`: exact page count, three columns each. Any module count supported. When one module per column fits, preserve that arrangement; otherwise flow blocks with continuation headers. Topic titles stay with the following block.
- `--title`, `--legend`, `--sources`: task-specific metadata. Long header/footer text causes an error; shorten labels, not lecture coverage.
- `--overwrite`: explicit replacement authorization; omitted by default.

Output is written atomically after successful layout. `<output-stem>.audit.json` records A4 dimensions, content/output hashes, font provenance, warnings, placements, and sizes. Temporary font subsets are not added to the skill or deliverables.

Pure white; green `#64ba48`, blue `#087bff`, purple `#b924db`, red `#e9322a`. A4 portrait, about 6 mm side margins. Print preferences request no scaling and duplex long-edge; still check the printer dialog.
