#!/usr/bin/env python3
"""Verify canonical programs, preserved v0.1, links and vector schematic in v0.2."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import fitz

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
OLD_HASH = 'a3488a39e7657a81829150b57fb1c7de15f934e53bb22f7f7a2dafb0dddc9643'
ESPRESSIF = 'https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized(text):
    return re.sub(r'\s+', '', text)


def verify(pdf_path, allow_interim=False):
    assert digest(ROOT / 'rs485_controller_datasheet_v0.1_review.pdf') == OLD_HASH, 'The preserved v0.1 PDF changed.'
    provenance = json.loads((ROOT / 'review/example-provenance-v0.2.json').read_text())
    document = fitz.open(pdf_path)
    texts = [page.get_text() for page in document]
    if not allow_interim:
        assert not any('VERIFIED FIGURE PENDING' in text for text in texts), 'Interim figure placeholder remains.'
    example_pages = {}
    for entry in provenance['examples']:
        source = REPO / entry['snapshot']
        assert digest(source) == entry['sha256'], f"Changed canonical {entry['language']} source snapshot."
        if entry['language'] == 'Python':
            start, end = '#!/usr/bin/env python3', 'servomotor.close_serial_port()'
        else:
            start, end = '// Minimal Arduino example:', 'void loop() {'
        page_index = next(i for i, text in enumerate(texts) if start in text)
        extracted = texts[page_index][texts[page_index].index(start):]
        extracted = extracted[:extracted.index(end) + len(end)]
        if entry['language'] == 'Arduino':
            extracted += '\n}'
        assert normalized(extracted) == normalized(source.read_text()), f"Rendered {entry['language']} program differs from canonical source."
        example_pages[entry['language']] = page_index + 1
    links = [link.get('uri') for page in document for link in page.get_links()]
    assert ESPRESSIF in links, 'Official Espressif module datasheet hyperlink is missing.'
    with fitz.open(REPO / 'PCB/0.5/schematic/0.5-index-schTop.pdf') as schematic:
        expected_drawings = len(schematic[0].get_drawings())
    appendix = document[-1]
    actual_drawings = len(appendix.get_drawings())
    assert appendix.rect.width > appendix.rect.height, 'Schematic appendix is not landscape.'
    assert actual_drawings >= expected_drawings, 'The full vector schematic was not preserved.'
    assert len(appendix.get_images()) <= 1, 'Unexpected raster imagery in vector appendix (logo is allowed).'
    assert normalized('not automatically a transparent USB-to-RS485 adapter') in normalized(' '.join(texts)), 'Python transport context is missing.'
    geometry_path = ROOT / 'assets/technical-v2/pcb-geometry.json'
    checked_pad_count = 0
    if geometry_path.exists():
        geometry = json.loads(geometry_path.read_text())
        reference = next(text for text in texts if 'Expansion pad net reference' in text)
        for pad in geometry['test_pads']:
            assert re.search(r'\b' + re.escape(pad['reference']) + r'\b', reference), f"Missing pad reference {pad['reference']} in emitted table."
        checked_pad_count = len(geometry['test_pads'])
    result = {
        'pdf': str(pdf_path), 'sha256': digest(pdf_path), 'pages': len(document),
        'v0.1_preserved': True, 'canonical_example_pages': example_pages,
        'canonical_program_tokens_match': True, 'canonical_snapshot_hashes_match': True,
        'official_espressif_link_present': True, 'schematic_vector_paths': actual_drawings,
        'source_schematic_vector_paths': expected_drawings,
        'appendix_landscape': True, 'interim_build': allow_interim,
        'checked_pad_references': checked_pad_count,
    }
    document.close()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, default=ROOT / 'rs485_controller_datasheet_v0.2_review.pdf')
    parser.add_argument('--allow-interim', action='store_true')
    args = parser.parse_args()
    result = verify(args.pdf, args.allow_interim)
    if not args.allow_interim:
        (ROOT / 'review/verification-v0.2.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
