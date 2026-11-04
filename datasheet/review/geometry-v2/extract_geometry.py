#!/usr/bin/env python3
"""Extract exact PCB coordinates and independently compare fresh schematic nets."""
from pathlib import Path
import hashlib, json, math, re, subprocess, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'datasheet/assets/technical-v2'
REVIEW=Path(__file__).resolve().parent
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'

def parse(path):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',Path(path).read_text())
    stack=[];root=None
    for token in tokens:
        if token=='(':
            item=[]
            if stack:stack[-1].append(item)
            else:root=item
            stack.append(item)
        elif token==')':stack.pop()
        else:stack[-1].append(json.loads(token) if token.startswith('"') else token)
    return root

def sub(item,key):return [x for x in item if isinstance(x,list) and x and x[0]==key]
def val(item,key,default=None):
    a=sub(item,key)
    return a[0][1] if a else default
def coords(item,key):return list(map(float,sub(item,key)[0][1:3]))
def world(origin,local):
    x,y,*angle=origin;theta=math.radians(angle[0] if angle else 0);dx,dy=local
    return [round(x+math.cos(theta)*dx+math.sin(theta)*dy,9),round(y-math.sin(theta)*dx+math.cos(theta)*dy,9)]
def arc_center(a,b,c):
    ax,ay=a;bx,by=b;cx,cy=c;d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
    ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d
    uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d
    return [ux,uy],math.hypot(ax-ux,ay-uy)

def main():
    OUT.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
    board_path=ROOT/'PCB/0.5/0.5.kicad_pcb';pcb=parse(board_path)
    netfile=REVIEW/'fresh-netlist.xml'
    subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','--output',str(netfile),str(ROOT/'PCB/0.5/0.5.kicad_sch')],check=True,capture_output=True)
    xml=ET.parse(netfile).getroot();net_by_contact={};net_nodes={}
    for net in xml.findall('nets/net'):
        name=net.get('name');net_nodes[name]=[n.attrib for n in net.findall('node')]
        for node in net.findall('node'):net_by_contact[node.get('ref'),node.get('pin')]=name
    components={c.get('ref'):{'value':c.findtext('value'),'footprint':c.findtext('footprint')} for c in xml.findall('components/comp')}
    edges=[];holes=[];arcs=[]
    for item in pcb:
        if not isinstance(item,list) or not item or val(item,'layer')!='Edge.Cuts':continue
        shape={'type':item[0]}
        for key in ['start','end','center','mid']:
            if sub(item,key):shape[key]=coords(item,key)
        if item[0]=='gr_circle':
            shape['diameter_mm']=2*math.dist(shape['center'],shape['end']);holes.append(shape)
        if item[0]=='gr_arc':
            shape['derived_center'],shape['derived_radius_mm']=arc_center(shape['start'],shape['mid'],shape['end']);arcs.append(shape)
        edges.append(shape)
    pts=[e[k] for e in edges if e['type'] in ['gr_line','gr_arc'] for k in ['start','end']]
    xmin=min(p[0] for p in pts);xmax=max(p[0] for p in pts);ymin=min(p[1] for p in pts);ymax=max(p[1] for p in pts)
    def views(p):return {'label_side_mm':[p[0]-xmin,p[1]-ymin],'component_side_mm':[p[0]-xmin,ymax-p[1]]}
    footprints={};tp=[];pad_checks=0
    for f in sub(pcb,'footprint'):
        props={p[1]:p[2] for p in sub(f,'property')};ref=props['Reference'];origin=list(map(float,sub(f,'at')[0][1:]));side=val(f,'layer')
        obj={'reference':ref,'value':components.get(ref,{}).get('value',props.get('Value')),'footprint':f[1],
             'side_layer':side,'physical_face':'component' if side=='B.Cu' else 'label','origin_mm':origin,**views(origin[:2]),'pads':[],'graphics':[]}
        for pad in sub(f,'pad'):
            local=coords(pad,'at');pos=world(origin,local)
            p={'number':pad[1],'kind':pad[2],'shape':pad[3],'local_mm':local,'position_mm':pos,**views(pos),'size_mm':coords(pad,'size'),'layers':sub(pad,'layers')[0][1:]}
            if sub(pad,'drill'):p['drill']=sub(pad,'drill')[0][1:]
            if sub(pad,'net'):
                p['net']=sub(pad,'net')[0][2]
                if pad[1]:
                    assert p['net']==net_by_contact[ref,pad[1]],f'PCB/schematic mismatch {ref}.{pad[1]}'
                    pad_checks+=1
            obj['pads'].append(p)
        for kind in ['fp_line','fp_rect','fp_circle','fp_arc']:
            for graphic in sub(f,kind):
                g={'type':kind,'layer':val(graphic,'layer')}
                for key in ['start','end','center','mid']:
                    if sub(graphic,key):g[key+'_local_mm']=coords(graphic,key);g[key+'_mm']=world(origin,g[key+'_local_mm'])
                obj['graphics'].append(g)
        footprints[ref]=obj
        if ref.startswith('TP'):
            pad=obj['pads'][0];nodes=net_nodes.get(pad.get('net'),[]);u7=[n for n in nodes if n['ref']=='U7']
            gpio=None;function=None
            if u7:
                function=u7[0].get('pinfunction')
                if function and re.fullmatch(r'IO\d+',function):gpio=int(function[2:])
                elif function=='TXD0':gpio=43
                elif function=='RXD0':gpio=44
            category='gpio' if gpio is not None else 'ground' if pad.get('net')=='GND' else 'pd_control' if ref in ['TP43','TP44','TP47'] else 'service_smd'
            label=f'GPIO{gpio}' if gpio is not None else 'GND' if category=='ground' else {'TP43':'PD_PG','TP44':'PD_VDD','TP47':'PD_CFG'}.get(ref,pad.get('net'))
            if ref in ['TP8','TP11']:label='RS485 A'
            if ref in ['TP9','TP12']:label='RS485 B'
            entry={'reference':ref,'net':pad.get('net'),'gpio':gpio,'u7_pin_function':function,'u7_connections':u7,'label':label,'category':category,
                   'through_hole':pad['kind']=='thru_hole','footprint_side':side,'position_mm':pad['position_mm'],**views(pad['position_mm']),'size_mm':pad['size_mm'],'drill':pad.get('drill')}
            if ref in ['TP45','TP46']:entry['shared_function']='RS485 TX' if ref=='TP45' else 'RS485 RX'
            if ref in ['TP4','TP5']:entry['shared_function']='UART0 TX' if ref=='TP4' else 'UART0 RX'
            if entry['through_hole']:
                x,y=entry['position_mm'];entry['region']='A' if y<108 else 'B' if y<123 else 'C' if y<130 else 'D'
            tp.append(entry)
    tp.sort(key=lambda x:int(x['reference'][2:]));th=[p for p in tp if p['through_hole']]
    assert len(th)==43 and sum(p['category']=='gpio' for p in th)==36
    assert set(ref for ref in footprints if ref.startswith('J'))=={'J1','J2','J3','J5'}
    assert len(holes)==4 and all(abs(h['diameter_mm']-1.5)<1e-8 for h in holes)
    assert all(abs(a['derived_radius_mm']-1.5)<0.00001 for a in arcs)
    for h in holes:
        h.update(views(h['center']));h['edge_insets_mm']=[min(h['center'][0]-xmin,xmax-h['center'][0]),min(h['center'][1]-ymin,ymax-h['center'][1])]
        assert all(abs(d-1.5)<1e-8 for d in h['edge_insets_mm'])
    out={'schema_version':1,'source':'PCB/0.5/0.5.kicad_pcb','source_sha256':hashlib.sha256(board_path.read_bytes()).hexdigest(),
         'net_validation':{'fresh_netlist':'datasheet/review/geometry-v2/fresh-netlist.xml','numbered_pad_matches':pad_checks,'all_pass':True},
         'units':'mm','bounds_mm':{'xmin':xmin,'xmax':xmax,'ymin':ymin,'ymax':ymax,'width':xmax-xmin,'height':ymax-ymin},
         'views':{'label_side':{'layer':'F.Cu','transform':'u=x-36.65; v=y-103.00','usb':'left','J2_pin1':'bottom','face':'label / solder face'},
                  'component_side':{'layer':'B.Cu','transform':'u=x-36.65; v=151.89-y','usb':'left','J2_pin1':'top','face':'component face','explanation':'Physical flip about the horizontal board axis; no unlabelled mirror.'}},
         'edge_cuts':edges,'mounting_holes':holes,'corner_radius_mm':1.5,'corner_radius_derivation':'Three-point circle fit of each start/mid/end; radii agree within 0.00001mm; midpoint coordinates are rounded in source.',
         'mounting_center_spacings_mm':{'x':33.88,'y':45.89},'nominal_thickness_mm':float(val(sub(pcb,'general')[0],'thickness')),
         'footprints':footprints,'test_pads':tp,'through_hole_pad_count':len(th),'through_hole_gpio_count':36,
         'regions':{'A':'Two eight-pad rows near raw y104.56/107.10','B':'Two six-pad columns near raw x48.46/51.00','C':'Two six-pad rows near raw y125.58/128.12','D':'Three PD-control through-hole pads'},
         'connector_references':['J1','J2','J3','J5'],'absent_connector_references':['J4','J6'],
         'illustration_anchors_mm':{'J1.1':[0.02,5.189999],'J1.2':[0.02,10.189999],'J3.USB':[-0.49,17.865],'J5.USB':[-0.475,41.345],
                                   **{f'J2.{i}':[42.723,3.995+(i-1)*2.54] for i in range(1,9)}},
         'illustration_anchor_evidence':'J1 wire mouths at front silkscreen body edge x36.67 and each contact centreline; USB mouths at Fab local y=-4.84; J2 outer gold contact tips at Fab local y=7.11. These describe mating landmarks, not copper pad centres.',
         'controller_component_svg':{'path':'datasheet/assets/technical-v2/controller-component-landmarks.svg','viewBox_mm':[-3,-2,48,53],'coordinate_system':'component_side_mm'},
         'module_rf_socket':{'reference':'U7 integrated antenna coax socket','position_mm':world(footprints['U7']['origin_mm'],[-4.5,6.1]),'local_mm':[-4.5,6.1],'source':'U7 B.Fab concentric circles','side_layer':'B.Cu'},
         'notes':['Through-hole TP footprints exist on both copper faces; footprint side is not a statement of one-face accessibility.',
                  'U7 logical value is ESP32-S3-MINI-1U; footprint library name ESP32-S2-MINI-1U is reused and must not override the schematic component identity.',
                  'TP4 TXD0 maps to GPIO43, TP5 RXD0 to GPIO44 by ESP32-S3 module pin definitions; both also show original schematic pin-function names.',
                  'GPIO4/5 expansion points share the active RS485 TX/RX nets; do not treat them as uncommitted IO.']}
    (OUT/'pcb-geometry.json').write_text(json.dumps(out,indent=2)+'\n')
    report={'passed':True,'numbered_pad_net_matches':pad_checks,'through_hole_pad_count':43,'gpio_count':36,'ground_count':4,'pd_control_count':3,
            'dimensions_mm':[xmax-xmin,ymax-ymin],'corner_fitted_radii_mm':[a['derived_radius_mm'] for a in arcs],
            'all_landmarks_on_component_B_Cu':all(footprints[r]['side_layer']=='B.Cu' for r in ['J1','J2','J3','J5','U7','S1','S2','D4','D5','D6'])}
    (REVIEW/'extraction-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
