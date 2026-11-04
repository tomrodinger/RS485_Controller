#!/usr/bin/env python3
"""Natural part artwork, source-derived PCB landmarks, explicit paired harnesses."""
from pathlib import Path
from html import escape
import base64, json, subprocess, sys, xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
INK='#173a33'; MUTED='#61746d'; RED='#d84042'; GND='#283335'; A='#16835e'; B='#256bc1'
COL={'ink':INK,'muted':MUTED,'red':RED,'gnd':GND,'a':A,'b':B}
NS='{http://www.w3.org/2000/svg}'
ET.register_namespace('', 'http://www.w3.org/2000/svg')
BOARD_GEOMETRY=ROOT/'datasheet/assets/technical-v2/pcb-geometry.json'
BOARD_SVG=ROOT/'datasheet/assets/technical-v2/board-component-base.svg'

class Plate:
    def __init__(self,w,h,title,sub):
        self.curved=False;self.pigtail=False;self.w=w;self.h=h;self.s=[];self.t=[];self.anchors={};self.routes=[];self.housings=[];self.looms=[];self.board_instances=[]
        self.rect(0,0,w,h,'#fff',r=0)
        self.text(100,90,'GEAROTONS / RS485 CONTROLLER',27,'a',700)
        self.text(100,175,title,64,'ink',700)
        self.text(102,230,sub,32,'muted')
    def add(self,s):self.s.append(s)
    def text(self,x,y,s,size=32,c='ink',weight=400,anchor='start',halo=None):
        h=f' paint-order="stroke" stroke="{COL.get(halo,halo)}" stroke-width="6" stroke-linejoin="round"' if halo else ''
        self.t.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{COL.get(c,c)}" text-anchor="{anchor}"{h}>{escape(s)}</text>')
    def rect(self,x,y,w,h,fill='#fff',stroke='none',r=10,sw=2,extra=''):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{COL.get(fill,fill)}" stroke="{COL.get(stroke,stroke)}" stroke-width="{sw}" {extra}/>')
    def circle(self,x,y,r,c):self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{COL.get(c,c)}"/>')
    def line(self,p,c,width=11,halo=True):
        q=' '.join(f'{x},{y}' for x,y in p)
        if self.curved and len(p)>2:
            import math
            d=f'M {p[0][0]} {p[0][1]}'
            for i in range(1,len(p)-1):
                a,b,nextp=p[i-1],p[i],p[i+1]
                l1=math.dist(a,b);l2=math.dist(b,nextp)
                if not l1 or not l2:continue
                r=min(30,l1/2,l2/2)
                before=[b[j]+(a[j]-b[j])*r/l1 for j in (0,1)]
                after=[b[j]+(nextp[j]-b[j])*r/l2 for j in (0,1)]
                d+=f' L {before[0]} {before[1]} Q {b[0]} {b[1]} {after[0]} {after[1]}'
            d+=f' L {p[-1][0]} {p[-1][1]}'
            if halo:self.add(f'<path d="{d}" fill="none" stroke="white" stroke-width="{width+10}" stroke-linecap="round"/>')
            self.add(f'<path d="{d}" fill="none" stroke="{COL.get(c,c)}" stroke-width="{width}" stroke-linecap="round"/>')
            return
        if halo:self.add(f'<polyline points="{q}" fill="none" stroke="white" stroke-width="{width+10}" stroke-linecap="round" stroke-linejoin="round"/>')
        self.add(f'<polyline points="{q}" fill="none" stroke="{COL.get(c,c)}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    def endpoint(self,ref,x,y):self.anchors[ref]=[round(x,4),round(y,4)]
    def route(self,ref1,ref2,middle,c,width=None):
        width=11 if c in ('red','gnd') else 8
        p=[self.anchors[ref1],*middle,self.anchors[ref2]]
        self.line(p,c,width)
        self.routes.append({'from':ref1,'to':ref2,'net':c,'points':p,'width':width})
    def image(self,path,x,y,w,h):
        typ='image/png' if path.suffix=='.png' else 'image/jpeg'
        data=base64.b64encode(path.read_bytes()).decode()
        self.add(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:{typ};base64,{data}"/>')
    def pair_housing(self,id,refs,x,y,pitch=50,vertical=False,spare=False):
        # One physical body, two independent cavities with a solid insulating wall.
        w,h=(100,pitch+42) if vertical else (pitch+54,62)
        self.rect(x-65 if vertical else x-27,y-21,w,h,GND,'#58635f',7,2,extra=f'data-housing-id="{id}" data-cavity-count="2"')
        cavity_positions=[(x,y),(x,y+pitch)] if vertical else [(x,y),(x+pitch,y)]
        for i,(xx,yy) in enumerate(cavity_positions):
            self.rect(xx-10,yy-10,20,20,'#101918','#abb7af',2,2,extra=f'data-cavity="{i+1}" data-contact="{refs[i]}"')
        self.housings.append({'id':id,'contacts':refs,'cavity_count':2,'shared_shell':True,'isolated_cavities':True,'spare':spare,'positions':cavity_positions})
    def harness(self,cx,top,motor,scale=1,show_labels=True):
        if self.pigtail:return self.natural_harness(cx,top,motor)
        name=f'Motor{motor}'; k=scale
        def X(v):return cx+v*k
        def Y(v):return top+v*k
        self.text(cx,Y(-28),'Detached white 6-way plug',29*k,'ink',600,'middle')
        self.rect(X(-130),Y(0),260*k,62*k,'#fdfdf8','#b3bdb3',8*k,2)
        self.rect(X(-42),Y(-12),84*k,16*k,'#f5f6ef','#b3bdb3',3*k,2)
        for xx in [-105,-63,-21,21,63,105]:
            self.rect(X(xx-9),Y(28),18*k,22*k,'#e2e5da','#a2ac9e',2*k,1)
        self.text(cx,Y(106),'Function key · cavity order not shown',23*k,'muted',400,'middle')
        self.rect(X(-248),Y(126),450*k,66*k,'#f3f7f3','#c4d5c9',6*k,2,extra='stroke-dasharray="7 7"')
        ends=[-220,-145,-45,5,115,165]
        nets=['gnd','red','a','b','a','b']
        for i,(en,c,lab) in enumerate(zip(ends,nets,['GND','V+','A','B','A','B'])):
            self.text(X(en),Y(154),lab,25*k,c,700,'middle')
            self.line([(X(en),Y(170)),(X(en),Y(260))],c,11 if c in ('gnd','red') else 8,False)
            self.endpoint(f'{name}.{i+1}',X(en),Y(260))
        for j,refs in enumerate([[f'{name}.3',f'{name}.4'],[f'{name}.5',f'{name}.6']]):
            ex=ends[2 if j==0 else 4]
            self.pair_housing(f'{name}-pair-{j+1}',refs,X(ex),Y(220),50*k,spare=(motor==2 and j==1))
        self.looms.append({'motor':motor,'plug_color':'white','plug_contacts':6,'wire_functions':['GND','V+','A','B','A','B'],'power_wire_width':11,'ground_wire_width':11,'connector_face_numbered':False,'detached_function_key':True,'physical_cavity_order_asserted':False})
    def natural_harness(self,cx,top,motor):
        name=f'Motor{motor}'
        self.text(cx,top-65,'White 6-way motor plug',29,'ink',600,'middle')
        self.rect(cx-130,top,260,62,'#fdfdf8','#aeb8ad',8,2)
        self.rect(cx-42,top-12,84,16,'#f5f6ef','#aeb8ad',3,2)
        starts=[-25,-15,-5,5,15,25];ends=[-220,-145,-45,5,115,165]
        for xx in [-105,-63,-21,21,63,105]:
            self.rect(cx+xx-8,top+7,16,12,'#e3e7dd','#b5bfb2',2,1)
        nets=['gnd','red','a','b','a','b']
        for i,(st,en,c) in enumerate(zip(starts,ends,nets)):
            d=f'M {cx+st} {top+58} C {cx+st} {top+135}, {cx+en} {top+130}, {cx+en} {top+190} L {cx+en} {top+260}'
            self.add(f'<path d="{d}" fill="none" stroke="{COL.get(c,c)}" stroke-width="{11 if c in ("gnd","red") else 8}" stroke-linecap="round"/>')
            self.endpoint(f'{name}.{i+1}',cx+en,top+260)
        self.rect(cx-43,top+38,86,48,'#f0f2ea','#adb8aa',9,2)
        for j,refs in enumerate([[f'{name}.3',f'{name}.4'],[f'{name}.5',f'{name}.6']]):
            self.pair_housing(f'{name}-pair-{j+1}',refs,cx+ends[2 if j==0 else 4],top+220,50,spare=motor==2 and j==1)
        for en,lab,c in zip(ends,['GND','V+','A','B','A','B'],nets):
            self.text(cx+en,top+187,lab,23,c,700,'middle',halo='white')
        self.text(cx,top-32,'Schematic harness · mating face not shown',22,'muted',400,'middle')
        self.looms.append({'motor':motor,'plug_color':'white','plug_contacts':6,'wire_functions':['GND','V+','A','B','A','B'],'power_wire_width':11,'ground_wire_width':11,'connector_face_numbered':False,'physical_cavity_order_asserted':False,'view':'closed rear face with shared wire bundle; mating face not shown'})
    def motor(self,cx,top,motor,w=450,harness_top=None):
        self.text(cx,top-30,f'Motor {motor}',46,'ink',700,'middle')
        self.image(ROOT/'diagram-review/working/motor-asset-v1.png',cx-w/2,top,w,w*1.3333)
        ht=harness_top if harness_top is not None else top+w*1.3333+70
        self.harness(cx,ht,motor)
        self.text(cx+w/2+25,top+w*.74,'A ↔ A',28,'a',600)
        self.text(cx+w/2+25,top+w*.74+40,'B ↔ B',28,'b',600)
        self.text(cx+w/2+25,top+w*.74+80,'Inside motor',22,'muted')
    def board(self,x,y,width):
        if not BOARD_GEOMETRY.exists() or not BOARD_SVG.exists():
            raise RuntimeError(f'Waiting for source-derived board asset: {BOARD_SVG}')
        data=json.loads(BOARD_GEOMETRY.read_text())
        svg=ET.parse(BOARD_SVG).getroot()
        vb=[float(v) for v in svg.get('viewBox').split()]
        k=width/vb[2]
        children=''.join(ET.tostring(n,encoding='unicode') for n in svg)
        self.add(f'<g transform="translate({x-vb[0]*k},{y-vb[1]*k}) scale({k})">{children}</g>')
        # Asset-local anchors are explicitly exported by the electrical geometry author.
        anchors=data['illustration_anchors_mm']
        for ref,p in anchors.items():self.endpoint(ref,x+(p[0]-vb[0])*k,y+(p[1]-vb[1])*k)
        a=self.anchors['J2.2'];b=self.anchors['J2.3']
        pitch=abs(b[1]-a[1]); hx=a[0]-30
        self.pair_housing('controller-J2-pair',['J2.2','J2.3'],hx,a[1],pitch,True)
        for ref,c in [('J2.2','a'),('J2.3','b')]:
            xx,yy=self.anchors[ref];self.line([(hx,yy),(hx+46,yy)],c,8,False);self.endpoint(ref,hx+46,yy)
        self.text(x+width/2,y+vb[3]*k+45,'Controller · PCB 0.5 geometry',30,'ink',600,'middle')
        self.text(x+width/2,y+vb[3]*k+85,'J2 pins 2 / 3 share one paired housing',27,'muted',400,'middle')
        self.board_instances.append({'geometry':str(BOARD_GEOMETRY.relative_to(ROOT)),'asset':str(BOARD_SVG.relative_to(ROOT)),'x':x,'y':y,'width':width,'scale':k,'view':'component_usb_left_j2_right'})
        return width,vb[3]*k
    def board_photo(self,x,y,width):
        data=base64.b64encode((ROOT/'images/rs485-controller/ports.jpg').read_bytes()).decode()
        # Photo coordinates normalized to its true square native aspect, then CCW.
        # Small crop removes unused background; no product feature is retouched.
        h=width*960/850;k=width/850
        self.rect(x-14,y-14,width+28,h+28,'#f2f4f1','#dce4dc',20,2)
        self.add(f'<svg x="{x}" y="{y}" width="{width}" height="{h}" viewBox="80 20 850 960"><image width="1000" height="1000" transform="translate(0,1000) rotate(-90)" href="data:image/jpeg;base64,{data}"/></svg>')
        # Visually checked photo locations: mouths, never screw heads/pad centres.
        pos={'J1.1':(89,133),'J1.2':(89,233),'J3.USB':(89,370),'J5.USB':(88,819)}
        for i,yy in enumerate([111,161,210,259,309,358,405,454],1):pos[f'J2.{i}']=(912,yy)
        for ref,(u,v) in pos.items():self.endpoint(ref,x+(u-80)*k,y+(v-20)*k)
        a=self.anchors['J2.2'];b=self.anchors['J2.3'];hx=a[0]-30
        self.pair_housing('controller-J2-pair',['J2.2','J2.3'],hx,a[1],b[1]-a[1],True)
        for ref,c in [('J2.2','a'),('J2.3','b')]:
            xx,yy=self.anchors[ref];self.line([(hx,yy),(hx+46,yy)],c,8,False);self.endpoint(ref,hx+46,yy)
        self.text(x+width/2,y+h+52,'Actual controller · component side',32,'ink',600,'middle')
        self.text(x+width/2,y+h+96,'One paired housing on J2 pins 2 / 3',28,'muted',400,'middle')
        self.board_instances.append({'kind':'actual_photo','source':'images/rs485-controller/ports.jpg','rotation':'CCW','x':x,'y':y,'width':width,'normalized_source_dimensions':[1000,1000],'crop_viewbox':[80,20,850,960],'photo_anchors':pos,'view':'component_usb_left_j2_right'})
        return width,h
    def source(self,x,y,w=600,portrait=False):
        self.rect(x,y,w,135,INK,r=16)
        self.text(x+27,y+50,'20 V-capable USB-C PD supply',31,'#fff',700)
        self.text(x+27,y+97,'USB-C cable → J3 PD POWER',27,'#dbece1')
        jx,jy=self.anchors['J3.USB']
        self.line([(x+w/2,y+135),(x+w/2,1300),(280,1300),(280,jy),(jx,jy)] if portrait else [(x+35,y),(x+35,jy),(jx,jy)],'#75857b',18)
    def footer(self,y):
        self.text(100,y,'Power in parallel. A/B continues through Motor 1 to Motor 2.',34,'ink',600)
        self.text(100,y+50,'J1 and J2 GND are common on the PCB; both motors have full-size power-return wires.',29,'muted')
        self.text(100,y+96,'20 V is nominal after PD negotiation. Wire with power off; verify voltage and polarity.',29,'muted')
        self.text(100,y+142,'A/B lines show electrical pairing; select compatible mating parts. Each black shell has two isolated cavities.',26,'muted')
    def finish(self,slug):
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><style>text{{font-family:Arial,Helvetica,sans-serif}}</style>'+''.join(self.s+self.t)+'</svg>'
        p=HERE/f'{slug}.svg';p.write_text(svg)
        subprocess.run(['rsvg-convert','-o',str(p.with_suffix('.png')),str(p)],check=True)
        p.with_suffix('.routes.json').write_text(json.dumps({'anchors':self.anchors,'routes':self.routes,'housings':self.housings,'looms':self.looms,'board_instances':self.board_instances,'notes':'Power parallel; full-width GND; two isolated cavities per black A/B housing; white six-way pigtails; motor internal A/B duplicates common.'},indent=2)+'\n')
        print(p.with_suffix('.png'))

def wide_reference(photo=False,editorial=False,natural=False):
    p=Plate(3200,2400,'Two motors. One complete connection map.','USB-C PD input · parallel motor power · one continuous RS485 bus')
    p.curved=natural;p.pigtail=natural
    if editorial:
        for x,w in [(245,740),(1290,630),(2290,630)]:
            p.rect(x,500,w,1120,'#f7f9f6',r=28)
    (p.board_photo if photo else p.board)(280,570,650)
    p.motor(1600,550,1,450,1260 if natural else 1220);p.motor(2600,550,2,450,1260 if natural else 1220)
    p.endpoint('PWR_POS',1180,330);p.endpoint('PWR_GND',1120,410)
    a=p.anchors['J1.1'];b=p.anchors['J1.2']
    p.route('J1.1','PWR_POS',[[140,a[1]],[140,330]],'red')
    p.route('J1.2','PWR_GND',[[205,b[1]],[205,410]],'gnd')
    for m,cx in [(1,1600),(2,2600)]:
        xx=cx-420
        dest=p.anchors[f'Motor{m}.2']
        p.route('PWR_POS',f'Motor{m}.2',[[xx,330],[xx,1660],[dest[0],1660]],'red')
        dest=p.anchors[f'Motor{m}.1']
        p.route('PWR_GND',f'Motor{m}.1',[[xx-60,410],[xx-60,1720],[dest[0],1720]],'gnd')
    for ref,motorref,c,lane,xx in [('J2.2','Motor1.3','a',1840,1010),('J2.3','Motor1.4','b',1900,1070)]:
        src=p.anchors[ref];dest=p.anchors[motorref]
        p.route(ref,motorref,[[xx,src[1]],[xx,lane],[dest[0],lane]],c)
    for a,b,c,lane in [('Motor1.5','Motor2.3','a',2010),('Motor1.6','Motor2.4','b',2070)]:
        src=p.anchors[a];dest=p.anchors[b];p.route(a,b,[[src[0],lane],[dest[0],lane]],c)
    for ref,c in [('PWR_POS','red'),('PWR_GND','gnd')]:p.circle(*p.anchors[ref],11,c)
    p.text(500,306,'V+ · direct PD VBUS from J1',28,'red',600)
    p.text(500,388,'GND · full-size motor return',28,'gnd',600)
    p.text(1920,290,'MOTOR POWER · PARALLEL',31,'ink',700,'middle')
    p.text(2100,2130,'A/B DAISY-CHAIN · KEEP EACH PAIR TOGETHER',30,'ink',700,'middle')
    p.text(2780,1570,'Spare A/B pair',26,'muted',600,'middle')
    p.text(2780,1610,'Two isolated cavities',23,'muted',400,'middle')
    p.source(130,1840)
    p.footer(2200)
    p.finish('r2-05-natural-pigtails' if natural else 'r2-01-photo-harness' if photo else 'r2-02-precision-harness')

def portrait(photo=False):
    p=Plate(2400,3000,'Power together. Data in sequence.','A practical two-motor wiring guide · detached connector function keys')
    p.rect(100,310,2200,1050,'#f7f9f6',r=25)
    (p.board_photo if photo else p.board)(330,400,650)
    p.text(1300,460,'01 / CONTROLLER',30,'a',700)
    p.text(1300,535,'J1 feeds both motors',42,'ink',700)
    p.text(1300,595,'Pin 1 = V+ · direct from PD VBUS',30,'red',600)
    p.text(1300,645,'Pin 2 = GND · shared motor return',30,'gnd',600)
    p.text(1300,750,'J2 starts the RS485 chain',38,'ink',700)
    p.text(1300,810,'Pin 2 = A · green   /   Pin 3 = B · blue',30,'ink',600)
    p.text(1300,870,'One black, two-cavity housing',29,'muted')
    p.text(1300,925,'J2 pins 1 and 4–8 are unused here.',28,'muted')
    p.text(1300,980,'J1 GND and J2 GND are common.',28,'muted')
    p.source(1280,1100,650,portrait=True)
    p.motor(800,1580,1,380,2180);p.motor(1800,1580,2,380,2180)
    # Parallel power descends at the left edge and splits above both motors.
    p.endpoint('PWR_POS',380,1420);p.endpoint('PWR_GND',320,1480)
    for ref,junction,c,x,lane in [('J1.1','PWR_POS','red',160,1420),('J1.2','PWR_GND','gnd',220,1480)]:
        src=p.anchors[ref];p.route(ref,junction,[[x,src[1]],[x,lane]],c)
    for m,cx in [(1,800),(2,1800)]:
        for end,junction,c,x,lane,low in [(2,'PWR_POS','red',cx-420,1420,2440),(1,'PWR_GND','gnd',cx-480,1480,2500)]:
            dst=p.anchors[f'Motor{m}.{end}'];p.route(junction,f'Motor{m}.{end}',[[x,lane],[x,low],[dst[0],low]],c)
    for ref,end,c,x,lane in [('J2.2',3,'a',1100,2590),('J2.3',4,'b',1160,2650)]:
        src=p.anchors[ref];dst=p.anchors[f'Motor1.{end}'];p.route(ref,f'Motor1.{end}',[[x,src[1]],[x,1330 if c=='a' else 1380],[260 if c=='a' else 200,1330 if c=='a' else 1380],[260 if c=='a' else 200,lane],[dst[0],lane]],c)
    for a,b,c,lane in [('Motor1.5','Motor2.3','a',2730),('Motor1.6','Motor2.4','b',2790)]:
        src=p.anchors[a];dst=p.anchors[b];p.route(a,b,[[src[0],lane],[dst[0],lane]],c)
    for ref,c in [('PWR_POS','red'),('PWR_GND','gnd')]:p.circle(*p.anchors[ref],11,c)
    p.text(1990,2460,'Spare A/B housing',27,'muted',600,'middle')
    p.text(1990,2500,'Keep cavities isolated',24,'muted',400,'middle')
    p.text(100,2880,'20 V nominal after PD negotiation. Verify voltage and polarity before connecting motors.',27,'muted')
    p.text(100,2925,'Lines show electrical pairing; use compatible mating parts. Motor cavity order is not specified.',26,'muted')
    p.finish('r2-03-photo-field-guide' if photo else 'r2-04-illustrated-field-guide')

if __name__=='__main__':
    wide_reference(photo=True)
    wide_reference(photo=False,editorial=True)
    portrait(photo=True)
    portrait(photo=False)
    wide_reference(photo=False,editorial=False,natural=True)
