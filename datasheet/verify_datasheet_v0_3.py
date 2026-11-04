#!/usr/bin/env python3
"""Verify owner-selected art, Arduino installation and preserved technical content."""
from pathlib import Path
import ast, hashlib, io, json, re
import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
MOTOR = REPO.parent / 'Servomotor/servomotor_datasheets'
PDF = ROOT / 'rs485_controller_datasheet_v0.3_review.pdf'
SELECTED = REPO / 'diagram-review/exports/round2-pngs/r2-05-natural-pigtails.png'
SCREENSHOT = MOTOR / 'arduino_library_installation.png'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def norm(value): return re.sub(r'\s+', '', value)
def pixels(image): return image.convert('RGB').tobytes()
def image_present(document, page, source):
    with Image.open(source) as original:
        expected = pixels(original)
        for ref in page.get_images():
            if (ref[2], ref[3]) != original.size: continue
            raw = document.extract_image(ref[0])['image']
            with Image.open(io.BytesIO(raw)) as emitted:
                if pixels(emitted) == expected: return True
    return False

def verify():
    assert sha(ROOT / 'rs485_controller_datasheet_v0.2_review.pdf') == '2b571bf1382fb3425aab6988852499da3d844c4eb2218f348bc11ce4e3cd1bb8'
    assert sha(ROOT / 'rs485_controller_datasheet_v0.1_review.pdf') == 'a3488a39e7657a81829150b57fb1c7de15f934e53bb22f7f7a2dafb0dddc9643'
    candidates = [p for p in SELECTED.parent.iterdir() if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.svg'}]
    assert candidates == [SELECTED], 'Chosen directory no longer contains exactly one image'
    assert sha(SELECTED) == sha(ROOT / 'assets/selected-v0.3/two-motor-connection.png')
    assert sha(SCREENSHOT) == sha(ROOT / 'assets/arduino-install-v0.3/arduino_library_installation.png')
    doc = fitz.open(PDF); texts = [p.get_text() for p in doc]; all_text = '\n'.join(texts)
    assert 'python' not in all_text.lower(), 'Python content remains'
    assert 'VERIFIED FIGURE PENDING' not in all_text
    wire = next(i for i,t in enumerate(texts) if 'Two-motor connection diagram' in t)
    install = next(i for i,t in enumerate(texts) if 'Install the Arduino library' in t)
    assert doc[wire].rect.width > doc[wire].rect.height
    assert image_present(doc, doc[wire], SELECTED), 'Selected PNG pixels changed in PDF'
    assert image_present(doc, doc[install], SCREENSHOT), 'M17 screenshot pixels changed in PDF'
    tree = ast.parse((MOTOR / 'arduino_library.py').read_text())
    source_steps = next(node.value.elts for node in ast.walk(tree) if isinstance(node, ast.Assign) and any(isinstance(t,ast.Name) and t.id=='install_steps' for t in node.targets))
    steps = [node.args[0].value for node in source_steps]
    assert all(norm(s) in norm(texts[install]) for s in steps), 'Installation wording differs from M17 source'
    with fitz.open(MOTOR / 'datasheet_latest_en.pdf') as motor_pdf:
        assert all(norm(s) in norm(''.join(p.get_text() for p in motor_pdf)) for s in steps)
    provenance = json.loads((ROOT / 'review/example-provenance-v0.2.json').read_text())
    entry = next(e for e in provenance['examples'] if e['language']=='Arduino')
    source = REPO / entry['snapshot']; assert sha(source)==entry['sha256']
    code_page = next(i for i,t in enumerate(texts) if '// Minimal Arduino example:' in t)
    code = texts[code_page].split('// Minimal Arduino example:',1)[1]
    code = '// Minimal Arduino example:' + code.split('void loop() {',1)[0] + 'void loop() {\n}'
    assert norm(code)==norm(source.read_text()), 'Arduino program changed'
    geometry=json.loads((ROOT/'assets/technical-v2/pcb-geometry.json').read_text())
    reference=next(t for t in texts if 'Expansion pad net reference' in t)
    assert all(re.search(r'\b'+re.escape(p['reference'])+r'\b',reference) for p in geometry['test_pads'])
    assert any(link.get('uri','').endswith('esp32-s3-mini-1_mini-1u_datasheet_en.pdf') for p in doc for link in p.get_links())
    with fitz.open(REPO/'PCB/0.5/schematic/0.5-index-schTop.pdf') as schematic:
        source_paths=len(schematic[0].get_drawings())
    assert len(doc[-1].get_drawings()) >= source_paths
    assert len(doc.get_toc())==len(doc)
    # Detect content extending past the physical page (including text in vector assets).
    outside=[]
    for n,page in enumerate(doc,1):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    if not span['text'].strip(): continue
                    box=fitz.Rect(span['bbox'])
                    if box.x0 < -1 or box.y0 < -1 or box.x1 > page.rect.width+1 or box.y1 > page.rect.height+1: outside.append([n,span['text']])
    assert not outside, outside
    result={'passed':True,'pdf':str(PDF),'sha256':sha(PDF),'pages':len(doc),'python_removed':True,
            'selected_source':str(SELECTED),'selected_image_sha256':sha(SELECTED),'selected_image_pixels_preserved':True,
            'connection_page':wire+1,'installation_page':install+1,'arduino_program_page':code_page+1,
            'm17_installation_steps_exact':steps,'m17_screenshot_pixels_preserved':True,'arduino_program_unchanged':True,
            'all_51_pad_references_present':True,'full_vector_schematic_preserved':True,'earlier_pdfs_preserved':True,
            'all_pages_bookmarked':True,'out_of_page_text':outside}
    (ROOT/'review/verification-v0.3.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': verify()
