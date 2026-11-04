#!/usr/bin/env python3
"""Remove only an internal future-change comment from a presentation copy."""
from pathlib import Path
from collections import Counter
import hashlib,json
import fitz
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT.parent/'PCB/0.5/schematic/0.5-index-schTop.pdf'
OUTPUT=ROOT/'assets/release-v1.0/controller-schematic.pdf'

def prepare():
    before=fitz.open(SOURCE);page=before[0];words=page.get_text('words')
    start=page.search_for('Later')[0];end=page.search_for('recommends')[0]
    lines=[];removed=[]
    for y in (start.y0,end.y0):
        line=[w for w in words if abs(w[1]-y)<.1 and 250<w[0]<420]
        assert line
        rect=fitz.Rect(min(w[0] for w in line),min(w[1] for w in line),max(w[2] for w in line),max(w[3] for w in line))
        rect=rect+(-.4,-.4,.4,.4)
        lines.append(rect);removed.extend(w[4] for w in line)
    assert removed[0]=='Later' and removed[-1]=='recommends'
    original=Counter(w[4] for w in words)
    image_before=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
    for rect in lines:page.add_redact_annot(rect,fill=None,cross_out=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                          graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)
    before.set_metadata({**before.metadata,'title':'RS485 Controller schematic — PCB 0.5','author':'Gearotons'})
    before.save(OUTPUT,garbage=4,deflate=True)
    after=fitz.open(OUTPUT);updated=Counter(w[4] for w in after[0].get_text('words'))
    assert original-updated==Counter(removed),(original-updated,removed)
    assert not updated-original
    assert 'Later' not in after[0].get_text() and len(after[0].search_for('47pF'))==1
    image_after=after[0].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
    # RGB comparison proves every circuit mark outside the comment is preserved.
    a=Image.frombytes('RGB',(image_before.width,image_before.height),image_before.samples)
    b=Image.frombytes('RGB',(image_after.width,image_after.height),image_after.samples)
    changed_non_comment=sum(1 for old,new in zip(a.getdata(),b.getdata()) if old!=new and not (old[0]==old[1] and old[2]>=old[0] and (old[2]>old[0] or old[0]>=250)))
    assert changed_non_comment==0,'A circuit-colour pixel changed'
    difference=ImageChops.difference(a,b)
    painter=ImageDraw.Draw(difference)
    for rect in lines:
        r=(rect+(-1,-1,1,1))*2
        painter.rectangle((int(r.x0),int(r.y0),int(r.x1)+1,int(r.y1)+1),fill=(0,0,0))
    assert difference.getbbox() is None,'Changed pixels outside the removed comment'
    result={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'output':str(OUTPUT),'sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
            'removed_comment':' '.join(removed),'redaction_boxes':[list(r) for r in lines],
            'circuit_text_and_values_preserved':True,'changed_pixels_outside_comment':0,
            'changed_circuit_ink_pixels':changed_non_comment,'source_file_unchanged':True,'output_vector_paths':len(after[0].get_drawings())}
    (ROOT/'review/release-schematic-cleanup.json').write_text(json.dumps(result,indent=2)+'\n')
    after[0].get_pixmap(matrix=fitz.Matrix(2,2)).save(ROOT/'review/release-schematic-preview.png')
    print(json.dumps(result,indent=2))
if __name__=='__main__':prepare()
