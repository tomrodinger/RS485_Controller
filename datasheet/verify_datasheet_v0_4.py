#!/usr/bin/env python3
"""Check source-derived pad labels, USB target and revised PDF content."""
from pathlib import Path
import hashlib,io,json,re,sys,xml.etree.ElementTree as ET
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent
TECH=ROOT/'assets/technical-v4';ART=ROOT/'assets/connection-v0.4'
NS='{http://www.w3.org/2000/svg}'
sys.path.insert(0,str(REPO/'diagram-review/reviews'))
from validate_candidate_routes import validate, rounded_path_matches, points

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+','',s)
def image_present(document,page,source):
    with Image.open(source) as image:
        expected=image.convert('RGB').tobytes()
        for ref in page.get_images():
            if (ref[2],ref[3])!=image.size:continue
            with Image.open(io.BytesIO(document.extract_image(ref[0])['image'])) as actual:
                if actual.convert('RGB').tobytes()==expected:return True
    return False

def verify():
    preserved={'0.1':'a3488a39e7657a81829150b57fb1c7de15f934e53bb22f7f7a2dafb0dddc9643','0.2':'2b571bf1382fb3425aab6988852499da3d844c4eb2218f348bc11ce4e3cd1bb8','0.3':'95ccd1b12db3a811c81cb7a4ab7965e258b7765478654f985bebc028bbcd72e1'}
    for version,digest in preserved.items():assert sha(ROOT/f'rs485_controller_datasheet_v{version}_review.pdf')==digest,version
    geometry=json.loads((TECH/'pcb-geometry.json').read_text())
    assert sha(TECH/'pcb-geometry.json')==sha(ROOT/'assets/technical-v2/pcb-geometry.json')
    source={p['reference']:p for p in geometry['test_pads']};labels=json.loads((TECH/'breakout-labels.json').read_text())
    assert len(labels)==len(source)==51 and {l['reference'] for l in labels}==set(source)
    drawing=ET.parse(TECH/'breakout-headers.svg').getroot();texts=list(drawing.iter(NS+'text'))
    for label in labels:
        tp=source[label['reference']]
        assert label['signal']==tp['label'] and label['position_mm']==tp['label_side_mm']
        x,y=label['label_xy'];target=label['signal'].replace('_',' ') if not tp.get('gpio') else label['signal']
        matches=[t for t in texts if abs(float(t.get('x'))-x)<.0001 and abs(float(t.get('y'))-y)<.0001 and t.text==target and t.get('text-anchor')==label['anchor']]
        assert len(matches)==1,('Missing physical signal label',label['reference'],target)
        u,v=tp['label_side_mm'];assert label['marker_xy']==[260+u*30,170+v*30]
    # Independently map header function names from actual numbered PCB pad nets.
    functions={'GND':'GND','/index/schTop/RS485A':'A','/index/schTop/RS485B':'B','+3.3V':'3.3V','+5V':'5V'}
    pads={int(p['number']):p for p in geometry['footprints']['J2']['pads'] if p['number']}
    expected=[functions[pads[i]['net']] for i in range(1,9)]
    assert expected==['GND','A','B','GND','A','B','3.3V','5V']
    for file in [TECH/'connector-locator.svg',TECH/'board-component-base.svg',ART/'two-motor-connection-v0.4.svg']:
        nodes=list(ET.parse(file).getroot().iter(NS+'text'))
        assert not [t.text for t in nodes if re.fullmatch('[1-8]',t.text or '')],('Numeric header label',file)
        body=[t.text for t in nodes]
        assert all(body.count(signal)>=expected.count(signal) for signal in set(expected)),file
    route_path=ART/'two-motor-connection-v0.4.routes.json'
    circuit=validate(REPO/'diagram-review/reviews/canonical-netlist.json',route_path)
    assert circuit['passed'],circuit['errors']
    routes=json.loads(route_path.read_text());usb=routes['usb_connections'][0]
    assert {usb['from'],usb['to']}=={'J5.USB','Computer.USB'}
    path=points(usb['points'])
    assert path[0]==tuple(routes['anchors'][usb['from']]) and path[-1]==tuple(routes['anchors'][usb['to']])
    svg=ET.parse(ART/'two-motor-connection-v0.4.svg').getroot()
    assert len([p for p in svg.iter(NS+'path') if p.get('stroke')==usb['stroke'] and rounded_path_matches(p,path)])==1
    assert routes['anchors']['J5.USB']!=routes['anchors']['J3.USB']
    # Ensure all functional text remains vector and on the intended PDF pages.
    pdf=ROOT/'rs485_controller_datasheet_v0.4_review.pdf';doc=fitz.open(pdf);page_text=[p.get_text() for p in doc];text='\n'.join(page_text)
    assert len(doc)==13 and len(doc.get_toc())==13
    assert not any(phrase.lower() in text.lower() for phrase in ['Python','Find every expansion pad','Pad region A','Pad region B','Pad region C','Pad region D','Pad region E','Expansion pad net reference','VERIFIED FIGURE PENDING'])
    locator=doc[2];connection=doc[4];mechanical=doc[6];breakout=doc[7]
    assert 'Breakout headers' in page_text[7] and 'solder required' in page_text[7]
    assert 'headers are not fitted' in page_text[7].lower() and 'Rear / label-side view (F.Cu)' in page_text[7]
    assert 'Broken-out corner' in page_text[6]
    assert 'J5 PROG' in page_text[4] and 'Computer' in page_text[4]
    assert all(p['label'].replace('_',' ') in page_text[7] for p in source.values())
    assert image_present(doc,doc[9],ROOT/'assets/arduino-install-v0.3/arduino_library_installation.png')
    provenance=json.loads((ROOT/'review/example-provenance-v0.2.json').read_text());entry=next(e for e in provenance['examples'] if e['language']=='Arduino')
    cpp=REPO/entry['snapshot'];assert sha(cpp)==entry['sha256']
    code=page_text[10].split('// Minimal Arduino example:',1)[1]
    code='// Minimal Arduino example:'+code.split('void loop() {',1)[0]+'void loop() {\n}'
    assert norm(code)==norm(cpp.read_text())
    with fitz.open(REPO/'PCB/0.5/schematic/0.5-index-schTop.pdf') as sch:assert len(doc[-1].get_drawings())>=len(sch[0].get_drawings())
    assert any(link.get('uri','').endswith('esp32-s3-mini-1_mini-1u_datasheet_en.pdf') for p in doc for link in p.get_links())
    outside=[]
    for index,p in enumerate(doc,1):
        for b in p.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line['spans']:
                    if not span['text'].strip():continue
                    r=fitz.Rect(span['bbox'])
                    if r.x0 < -1 or r.y0 < -1 or r.x1 > p.rect.width+1 or r.y1 > p.rect.height+1:outside.append([index,span['text']])
    assert not outside,outside
    result={'passed':True,'pdf':str(pdf),'sha256':sha(pdf),'pages':len(doc),'all_51_physical_pad_labels_match_checked_geometry':True,
            'j2_signal_order_from_pcb_nets':expected,'numeric_header_labels_removed':True,'computer_usb_target':'J5 USB-C PROG',
            'svg_usb_route_matches_declared_endpoints':True,'electrical_routes':circuit,'single_breakout_page':8,
            'breakout_view':'Rear / label side F.Cu','headers_marked_unpopulated':True,'broken_out_corner_present':True,
            'python_absent':True,'arduino_listing_unchanged':True,'m17_installation_image_preserved':True,
            'schematic_vectors_preserved':True,'earlier_pdfs_preserved':True,'out_of_page_text':outside}
    (ROOT/'review/verification-v0.4.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':verify()
