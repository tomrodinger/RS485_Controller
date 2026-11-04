#!/usr/bin/env python3
"""Copy reviewed round-two assets into the existing private feedback gallery."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import zipfile

HERE = Path(__file__).resolve().parent
REVIEW = HERE / 'site/public/review'
ASSETS = REVIEW / 'assets'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prior = json.loads((HERE / 'review-session.json').read_text())['candidates']
    original_ids = {entry['id'] for entry in prior}
    manifest = json.loads((REVIEW / 'candidates.json').read_text())
    originals = [entry for entry in manifest if entry['id'] in original_ids]
    assert len(originals) == 6
    for entry in prior:
        assert digest(REVIEW / entry['image']) == entry['sha256'], entry['id']
    new = json.loads((HERE / 'round2/candidates.json').read_text())
    new.sort(key=lambda item: (item['slug'] != 'r2-05-natural-pigtails', item['slug']))
    entries = []
    for item in new:
        source = HERE / 'round2' / item['png']
        header = source.read_bytes()[:24]
        assert header[:8] == b'\x89PNG\r\n\x1a\n'
        width, height = struct.unpack('>II', header[16:24])
        target = ASSETS / item['png']
        shutil.copy2(source, target)
        shutil.copy2(source, HERE / 'exports' / item['png'])
        entries.append({
            'id': item['slug'], 'title': item['title'],
            'style': 'Round 2 · natural illustration',
            'description': item['description'],
            'image': 'assets/' + item['png'], 'width': width, 'height': height,
            'revision': 'r2', 'reviewStatus': 'New variation · owner review',
        })
    with zipfile.ZipFile(ASSETS / 'round2-pngs.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for item in new:
            archive.write(HERE / 'round2' / item['png'], item['png'])
    shutil.copy2(ASSETS / 'round2-pngs.zip', HERE / 'exports/round2-pngs.zip')
    (REVIEW / 'candidates.json').write_text(json.dumps(entries + originals, indent=2) + '\n')
    evidence = {'original_six_assets_preserved': True, 'new_candidates': [
        {**entry, 'sha256': digest(REVIEW / entry['image'])} for entry in entries
    ]}
    (HERE / 'reviews/qa/round2-gallery-assets.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(f'Prepared {len(entries)} new candidates; preserved {len(originals)} originals.')


if __name__ == '__main__':
    main()
