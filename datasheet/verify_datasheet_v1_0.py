#!/usr/bin/env python3
"""Check source-derived pad labels, USB target and public-release PDF content."""
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
    preserved={'0.1':'a3488a39e7657a81829150b57fb1c7de15f934e53bb22f7f7a2dafb0dddc9643','0.2':'2b571bf1382fb3425aab6988852499da3d844c4eb2218f348bc11ce4e3cd1bb8','0.3':'95ccd1b12db3a811c81cb7a4ab7965e258b7765478654f985bebc028bbcd72e1','0.4':'5d79bacdf43fd809f5c94216e42635d9231a6a65de1ac93ef3311650d2a31393'}
    for version,digest in preserved.items():assert sha(ROOT/f'rs485_controller_datasheet_v{version}_review.pdf')==digest,version
    geometry=json.loads((TECH/'pcb-geometry.json').read_text())
    assert sha(TECH/'pcb-geometry.json')==sha(ROOT/'assets/technical-v2/pcb-geometry.json')
    source={p['reference']:p for p in geometry['test_pads']};labels=json.loads((TECH/'breakout-labels.json').read_text())
    assert len(labels)==len(source)==51 and {l['reference'] for l in labels}==set(source)
    drawing=ET.parse(TECH/'breakout-headers.svg').getroot();texts=list(drawing.iter(NS+'text'))
    aliases={'TP4':('GPIO43','TXD0'),'TP5':('GPIO44','RXD0'),'TP45':('GPIO4','RS485TX'),'TP46':('GPIO5','RS485RX')}
    pcb=(REPO/'PCB/0.5/0.5.kicad_pcb').read_text()
    for label in labels:
        tp=source[label['reference']]
        assert label['signal']==tp['label'] and label['position_mm']==tp['label_side_mm']
        x,y=label['label_xy'];target=label['signal'].replace('_',' ') if not tp.get('gpio') else label['signal']
        matches=[t for t in texts if abs(float(t.get('x'))-x)<.0001 and abs(float(t.get('y'))-y)<.0001 and t.text==target and t.get('text-anchor')==label['anchor']]
        assert len(matches)==1,('Missing physical signal label',label['reference'],target)
        u,v=tp['label_side_mm'];assert label['marker_xy']==[260+u*30,170+v*30]
        assert label['label_background'] is None
        if label['reference'] in aliases:
            gpio,alias=aliases[label['reference']]
            assert label['signal']==gpio and label['pcb_alias']==alias
            assert f'(gr_text "{alias}"' in pcb
            ax,ay=label['alias_xy']
            matching_aliases=[t for t in texts if t.text==alias+'*' and abs(float(t.get('x'))-ax)<.0001 and abs(float(t.get('y'))-ay)<.0001 and t.get('text-anchor')==label['anchor']]
            assert len(matching_aliases)==1,('Missing PCB alias beside GPIO',gpio,alias)
            assert matching_aliases[0].get('fill')==matches[0].get('fill')
        else:assert label['pcb_alias'] is None
    assert not [r for r in drawing.iter(NS+'rect') if r.get('fill','').lower() in ['white','#fff','#ffffff'] and (r.get('width'),r.get('height'))!=('1600','1850')], 'White label boxes remain'
    assert source['TP4']['u7_pin_function']=='TXD0' and source['TP5']['u7_pin_function']=='RXD0'
    assert source['TP45']['net']=='/index/schTop/TX_RS485' and source['TP46']['net']=='/index/schTop/RX_RS485'
    pd_pads={'TP43':'PG','TP44':'VDD','TP47':'CFG'}
    for ref,function in pd_pads.items():
        assert source[ref]['through_hole'] and source[ref]['drill']==['0.9']
        assert source[ref]['net']==f'Net-(U8-{function})'
    assert not [r for r in drawing.iter(NS+'rect') if r.get('fill')=='#d9bb75'], 'Gold pad finish remains'
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
    pdf=ROOT/'rs485_controller_datasheet_v1.0.pdf';doc=fitz.open(pdf);page_text=[p.get_text() for p in doc];text='\n'.join(page_text)
    assert len(doc)==14 and len(doc.get_toc())==14
    # Cover hierarchy, one detailed photograph, and the additional views at the end.
    assert image_present(doc,doc[0],REPO/'images/rs485-controller/component-side.jpg')
    assert len(doc[0].get_images())==2  # Brand logo and the board-only photograph.
    assert '11.7 g' not in page_text[0] and '230400 baud' not in page_text[0]
    assert page_text[0].count('PCB 0.5')==1  # Footer only.
    assert 'bright LEDs' in page_text[0] and 'red TX' in page_text[0] and 'green RX' in page_text[0]
    subtitle_spans=[span for block in doc[0].get_text('dict')['blocks'] for line in block.get('lines',[]) for span in line['spans'] if 'ESP32-S3 development board' in span['text']]
    assert subtitle_spans and all(span['size']>=11 and 'Bold' in span['font'] for span in subtitle_spans)
    for page in page_text:
        assert 'Datasheet v1.0' in page and 'DS v1.0' not in page
    assert 'More views of the controller' in page_text[-1]
    for name in ['component-side','with-antenna','ports','label-side']:
        with Image.open(REPO/f'images/rs485-controller/{name}.jpg') as photo:
            w,h=photo.size
            for box in [(0,0,24,24),(w-24,0,w,24),(0,h-24,24,h),(w-24,h-24,w,h)]:
                assert all(low>=253 for low,high in photo.convert('RGB').crop(box).getextrema()),('Photo background is not white',name,box)
    for name in ['with-antenna','ports','label-side']:
        assert image_present(doc,doc[-1],REPO/f'images/rs485-controller/{name}.jpg'),name
    assert '11.7 g including the supplied external antenna' in page_text[-1]
    forbidden=['review draft','owner review','working-tree','source snapshot','example-provenance','canonical','Specification and review basis','Later change','retained unchanged','source sheet:','module retained as a black box']
    for phrase in forbidden:
        assert phrase.lower() not in text.lower(),('Internal editorial text remains',phrase)
    assert 'review' not in (doc.metadata.get('title','')).lower()
    assert 'Datasheet v1.0' in doc.metadata['title']
    assert sha(REPO/'PCB/0.5/schematic/0.5-index-schTop.pdf')=='758f2c36d60bb5a5f2791e664161804895850cf46098232ab78dcc718596d35e'
    cleanup=json.loads((ROOT/'review/release-schematic-cleanup.json').read_text())
    assert cleanup['changed_pixels_outside_comment']==0 and cleanup['changed_circuit_ink_pixels']==0 and cleanup['circuit_text_and_values_preserved']
    assert 'Unspecified product ratings:' in text
    assert 'current consumption' in text and 'motor-power pass-through current' in text and 'ESD/EMC ratings' in text
    assert not any(phrase.lower() in text.lower() for phrase in ['Python','Find every expansion pad','Pad region A','Pad region B','Pad region C','Pad region D','Pad region E','Expansion pad net reference','VERIFIED FIGURE PENDING'])
    locator=doc[2];connection=doc[4];mechanical=doc[6];breakout=doc[7]
    assert 'Breakout headers' in page_text[7] and 'solder required' in page_text[7]
    assert 'headers are not fitted' in page_text[7].lower() and 'Rear / label-side view (F.Cu)' in page_text[7]
    assert 'Broken-out corner' in page_text[6]
    assert 'J5 PROG' in page_text[4] and 'Computer' in page_text[4]
    assert all(p['label'].replace('_',' ') in page_text[7] for p in source.values())
    for gpio,alias in aliases.values():assert gpio in page_text[7] and alias+'*' in page_text[7]
    assert 'PCB label aliases:' in page_text[7] and 'final character in TXD0/RXD0 is zero' in page_text[7]
    assert 'not the differential A/B bus' in page_text[7] and 'not independent spare GPIO' in page_text[7]
    page_flow=[re.sub(r'\s+',' ',page).strip() for page in page_text]
    assert 'HASL-finished plated through-hole pads' in page_flow[7]
    assert not any(phrase in text.lower() for phrase in ['gold rectangular','surface service pads','surface service points','surface pads, not through holes'])
    assert 'CH221K requests 20 V' in page_flow[1] and '15 V or 12 V' in page_flow[1]
    assert 'Below 12 V, the motors will likely not work correctly' in page_flow[1]
    assert 'J5 alone is sufficient to power and program the module' in page_flow[1]
    assert 'Using a separate motor power supply' in page_flow[5]
    assert 'external supply positive directly to each motor V+' in page_flow[5]
    assert 'external supply negative to controller GND' in page_flow[5]
    assert 'Leave J3 and J1 pin 1 unused' in page_flow[5]
    assert 'For programming only, connect J5 USB-C PROG to a computer' in page_flow[8]
    assert 'no motor supply or J3 connection is needed' in page_flow[8]
    pd_url='https://www.wch-ic.com/downloads/CH224DS1_PDF.html'
    assert all(any(link.get('uri')==pd_url for link in doc[index].get_links()) for index in [7,11])
    assert image_present(doc,doc[9],ROOT/'assets/arduino-install-v0.3/arduino_library_installation.png')
    provenance=json.loads((ROOT/'review/example-provenance-v0.2.json').read_text());entry=next(e for e in provenance['examples'] if e['language']=='Arduino')
    cpp=REPO/entry['snapshot'];assert sha(cpp)==entry['sha256']
    code=page_text[10].split('// Minimal Arduino example:',1)[1]
    code='// Minimal Arduino example:'+code.split('void loop() {',1)[0]+'void loop() {\n}'
    assert norm(code)==norm(cpp.read_text())
    with fitz.open(ROOT/'assets/release-v1.0/controller-schematic.pdf') as sch:assert len(doc[12].get_drawings())>=len(sch[0].get_drawings())
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
            'public_release_text_clean':True,'schematic_editorial_note_removed':True,'circuit_marks_preserved_outside_comment':True,'unspecified_product_ratings_retained':True,'schematic_vectors_preserved':True,'earlier_pdfs_preserved':True,'out_of_page_text':outside}
    result.update({'cover_single_board_only_photo':True,'esp32_s3_subtitle_enlarged_and_bold':True,'cover_weight_baud_revision_boxes_removed':True,'tx_rx_led_feature_present':True,'expanded_datasheet_footer_on_every_page':True,'additional_product_views_page':14,'measured_mass_retained_as_small_gallery_note':True})
    result.update({'breakout_gpio_and_pcb_aliases':{gpio:alias for gpio,alias in aliases.values()},'all_breakout_labels_have_no_background_boxes':True,'alias_note_explains_uart0_and_wired_rs485_signals':True})
    result['all_four_product_photos_have_white_background_corners']=True
    result.update({'pd_control_pads_confirmed_plated_through_hole':pd_pads,'pd_pad_finish':'HASL (owner-confirmed)','old_gold_surface_pad_description_removed':True,'power_delivery_chip_datasheet_link':pd_url,'pd_20v_request_and_15v_12v_motor_operation_explained':True,'below_12v_motor_limitation_retained':True,'j5_only_programming_explained':True,'separate_motor_supply_requires_common_ground':True,'separate_motor_supply_positive_kept_off_pd_rail':True})
    (ROOT/'review/verification-v1.0.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':verify()
