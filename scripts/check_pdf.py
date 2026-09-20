#!/usr/bin/env python3
"""Structural PDF verification; visual and semantic source review remain required."""
import argparse
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf', type=Path)
    p.add_argument('--audit', type=Path, required=True)
    p.add_argument('--pages', type=int, default=2)
    a = p.parse_args()
    audit = json.loads(a.audit.read_text(encoding='utf-8'))
    errors = []
    if hashlib.sha256(a.pdf.read_bytes()).hexdigest() != audit['pdf_sha256']:
        errors.append('PDF differs from audited build')
    reader = PdfReader(a.pdf)
    if len(reader.pages) != a.pages or audit['pages'] != a.pages:
        errors.append('Wrong page count')
    if audit['expected_blocks'] != audit['rendered_blocks']:
        errors.append('Missing content blocks')
    placed = [b['id'] for b in audit['placements'] if b['id'] is not None]
    if len(placed) != audit['expected_blocks'] or len(set(placed)) != len(placed):
        errors.append('Duplicated or missing placement IDs')
    for b in audit['placements']:
        x0, y0, x1, y1 = b['bounds_pt']
        if not (1 <= b['page'] <= a.pages and 1 <= b['column'] <= 3 and
                16.9 <= x0 < x1 <= 578.4 and 30.9 <= y0 < y1 <= 804):
            errors.append('Invalid placement bounds: ' + str(b['id']))
    embedded = set()
    for i, page in enumerate(reader.pages, 1):
        if abs(float(page.mediabox.width) - 595.27559) > .1 or abs(float(page.mediabox.height) - 841.88976) > .1:
            errors.append(f'Page {i} is not portrait A4')
        text = page.extract_text() or ''
        if any(ch in text for ch in ['\ufffd', '\u25a1']):
            errors.append(f'Page {i}: replacement/square glyph; inspect source and rendering')
        for ref in page['/Resources']['/Font'].get_object().values():
            font = ref.get_object()
            descendants = font.get('/DescendantFonts')
            fonts = [f.get_object() for f in descendants] if descendants else [font]
            for f in fonts:
                d = f.get('/FontDescriptor')
                if d is None or not any(k in d.get_object() for k in ['/FontFile', '/FontFile2', '/FontFile3']):
                    errors.append('Font not embedded: ' + str(f.get('/BaseFont')))
                else:
                    embedded.add(str(f.get('/BaseFont')))
    print(json.dumps({'ok': not errors, 'errors': errors, 'pages': len(reader.pages),
                      'embedded_fonts': len(embedded), 'warnings': audit.get('warnings', []),
                      'remaining_checks': 'Source coverage, formula correctness, and visual inspection of every page'}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == '__main__':
    main()
