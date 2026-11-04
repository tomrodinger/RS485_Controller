#!/usr/bin/env python3
"""Source-faithful board diagrams; SVG, raster previews, and vector PDF export."""
from pathlib import Path
import json,math,subprocess
from html import escape

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'datasheet/assets/technical-v2'
G=json.loads((OUT/'pcb-geometry.json').read_text())
C={'ink':'#173b35','muted':'#61766f','green':'#197a60','board':'#258267','edge':'#b9cec3','light':'#f1f6f3','gold':'#d9bb75','grey':'#dce3df','gpio':'#157c64','ground':'#52616b','pd_control':'#ad6f27','service_smd':'#327da0'}
F=G['footprints'];W=G['bounds_mm']['width'];H=G['bounds_mm']['height']

def xy(raw,face='component'):
    return [raw[0]-G['bounds_mm']['xmin'],G['bounds_mm']['ymax']-raw[1] if face=='component' else raw[1]-G['bounds_mm']['ymin']]
def fmt(n):return f'{n:.6f}'.rstrip('0').rstrip('.')
class Drawing:
    def __init__(self,w,h):self.w=w;self.h=h;self.items=[f'<rect width="{w}" height="{h}" fill="white"/>']
    def add(self,s):self.items.append(s)
    def rect(self,x,y,w,h,fill='white',stroke='none',r=0,sw=1,dash=None):
        self.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{fmt(r)}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="{fmt(sw)}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    def circle(self,x,y,r,fill='white',stroke='none',sw=1):self.add(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="{fmt(sw)}"/>')
    def line(self,pts,color='ink',sw=1,dash=None):self.add('<polyline points="'+' '.join(f'{fmt(x)},{fmt(y)}' for x,y in pts)+f'" fill="none" stroke="{C.get(color,color)}" stroke-width="{fmt(sw)}" stroke-linecap="round" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    def text(self,x,y,s,size=28,color='ink',bold=False,anchor='start',rotate=None):self.add(f'<text x="{fmt(x)}" y="{fmt(y)}" font-size="{fmt(size)}" fill="{C.get(color,color)}" font-weight="{700 if bold else 400}" text-anchor="{anchor}"'+(f' transform="rotate({rotate} {fmt(x)} {fmt(y)})"' if rotate else '')+'>'+escape(str(s))+'</text>')
    def svg(self,viewbox=None):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="'+(' '.join(map(str,viewbox)) if viewbox else f'0 0 {self.w} {self.h}')+'"><style>text{font-family:Arial,Helvetica,sans-serif}</style>'+''.join(self.items)+'</svg>'
    def export(self,name,viewbox=None):
        path=OUT/(name+'.svg');path.write_text(self.svg(viewbox))
        for ext,args in [('png',[]),('pdf',['-f','pdf'])]:subprocess.run(['rsvg-convert',*args,'-o',str(OUT/(name+'.'+ext)),str(path)],check=True)

def bounds(ref,face='component',layer=None):
    points=[]
    for gr in F[ref]['graphics']:
        if layer and gr['layer']!=layer:continue
        for key in ['start_mm','end_mm','center_mm']:
            if key in gr:points.append(xy(gr[key],face))
    return [min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]

def board(d,ox,oy,scale,face='component',context=True,numbers=True):
    def p(a):u,v=xy(a,face);return ox+u*scale,oy+v*scale
    d.rect(ox,oy,W*scale,H*scale,'board' if face=='component' else '#e8f1eb','green',1.5*scale,.12*scale)
    for hole in G['mounting_holes']:
        x,y=p(hole['center']);d.circle(x,y,.75*scale,'white','edge',.12*scale)
    # Test-point holes genuinely traverse the board; show both faces honestly.
    for tp in G['test_pads']:
        x,y=p(tp['position_mm'])
        if tp['through_hole']:
            d.rect(x-tp['size_mm'][0]*scale/2,y-tp['size_mm'][1]*scale/2,tp['size_mm'][0]*scale,tp['size_mm'][1]*scale,'#b9c9be','#718e7b',.3*scale,.08*scale)
            d.circle(x,y,.45*scale,'white','#708776',.08*scale)
        elif face=='label':
            d.rect(x-tp['size_mm'][0]*scale/2,y-tp['size_mm'][1]*scale/2,tp['size_mm'][0]*scale,tp['size_mm'][1]*scale,'gold','#9c8249',.12*scale,.08*scale)
    if face=='label':
        # Opposite-face connector landmarks are dashed, not drawn as fitted here.
        for ref in ['J1','J3','J5','U7','S1','S2']:
            a,b,c,e=bounds(ref,face,'B.Fab' if ref not in ['J1','S1','S2'] else 'B.SilkS')
            d.rect(ox+a*scale,oy+b*scale,(c-a)*scale,(e-b)*scale,'none','#b3c5bb',.3*scale,.07*scale,'3 3')
        return
    # Component face is B.Cu. Render remaining components from actual Fab bounds.
    if context:
        for ref,fp in F.items():
            if fp['side_layer']!='B.Cu' or ref.startswith('TP') or ref in ['J1','J2','J3','J5','U7','S1','S2','D4','D5','D6']:continue
            gs=[g for g in fp['graphics'] if g['layer']=='B.Fab']
            if not gs:continue
            a,b,c,e=bounds(ref,face,'B.Fab')
            if c>a and e>b:
                color = '#263e34' if ref.startswith('U') else '#77857c' if ref.startswith('L') else '#d6c8a4' if ref.startswith('C') else '#a8bcb0'
                d.rect(ox+a*scale,oy+b*scale,(c-a)*scale,(e-b)*scale,color,'#5c8470',.08*scale,.04*scale)
    for ref in ['J1','J3','J5','U7']:
        a,b,c,e=bounds(ref,face,'B.SilkS' if ref=='J1' else 'B.Fab')
        d.rect(ox+a*scale,oy+b*scale,(c-a)*scale,(e-b)*scale,'#459968' if ref=='J1' else '#d8e1dc' if ref!='U7' else '#cbd8ce','#547b65',.25*scale,.1*scale)
    for pad in F['J1']['pads']:
        x,y=p(pad['position_mm']);d.circle(x,y,1.5*scale,'#d3ded5','#779a83',.12*scale);d.line([(x-.8*scale,y-.45*scale),(x+.8*scale,y+.45*scale)],'#73897a',.18*scale)
        d.rect(ox+.02*scale,y-.7*scale,1.1*scale,1.4*scale,'#183e2d','#82b08d',.12*scale,.08*scale)
    for ref in ['J3','J5']:
        a,b,c,e=bounds(ref,face,'B.Fab');d.rect(ox+a*scale,oy+(b+.8)*scale,.8*scale,(e-b-1.6)*scale,'#294b3a','#96ada0',.3*scale,.08*scale)
    # Exact header body and contact centrelines from local Fab geometry.
    d.rect(ox+34.343*scale,oy+2.725*scale,2.54*scale,20.32*scale,'#263c30','#17291e',.16*scale,.08*scale)
    for i in range(1,9):
        u,v=G['illustration_anchors_mm'][f'J2.{i}'];d.rect(ox+36.883*scale,oy+(v-.3)*scale,(u-36.883)*scale,.6*scale,'gold','#a08744',.02*scale,.05*scale)
        if numbers:d.text(ox+33.7*scale,oy+(v+.4)*scale,str(i),1.2*scale,'white',True,'end')
    for ref in ['S1','S2']:
        x,y=p(F[ref]['origin_mm'][:2]);d.rect(x-1.5*scale,y-1.95*scale,3*scale,3.9*scale,'#c8d5cd','#718f7d',.3*scale,.08*scale);d.circle(x,y,.95*scale,'#314b3c')
    for ref,col in [('D4','#edbd34'),('D5','#81d08a'),('D6','#e27873')]:
        x,y=p(F[ref]['origin_mm'][:2]);d.rect(x-.6*scale,y-scale,1.2*scale,2*scale,col,'#dde8df',.15*scale,.12*scale)
    x,y=p(G['module_rf_socket']['position_mm']);d.circle(x,y,.7*scale,'gold','#92752d',.12*scale);d.circle(x,y,.15*scale,'#33443b')
    ux,uy=p(F['U7']['origin_mm'][:2]);d.text(ux,uy-1.2*scale,'ESP32-S3',1.5*scale,'#4c6554',True,'middle');d.text(ux,uy+1*scale,'MINI-1U',1.25*scale,'#4c6554',False,'middle')
    if numbers:
        for ref,dx,dy in [('J1',8.4,5.3),('J3',8.4,18),('J5',8.4,42.5)]:d.text(ox+dx*scale,oy+dy*scale,ref,1.5*scale,'white',True)
        for ref in ['S1','S2']:
            x,y=p(F[ref]['origin_mm'][:2]);d.text(x-2*scale,y+.4*scale,ref,1.05*scale,'white',True,'end')

def base():
    d=Drawing(1440,1590);board(d,0,0,1)
    d.export('controller-component-landmarks',[-3,-2,48,53])
    # Alias requested by the main agent; same geometry and viewBox.
    (OUT/'board-component-base.svg').write_text(d.svg([-3,-2,48,53]))
    print('Published controller-component-landmarks.svg; mm viewBox -3 -2 48 53')

if __name__=='__main__':base()

def all_figures():
    # Connector callouts around the component-side physical layout.
    d=Drawing(1500,1050); ox,oy,sc=390,80,17
    board(d,ox,oy,sc)
    calls=[('J1 · Motor power out',F['J1']['origin_mm'][:2],40,150),('J3 · PD power input',F['J3']['origin_mm'][:2],40,320),('J5 · USB-C PROG',F['J5']['origin_mm'][:2],40,710),('J2 · 8-pin header',F['J2']['origin_mm'][:2],1120,270),('U7 · ESP32-S3 module',F['U7']['origin_mm'][:2],1120,760),('U7 · antenna socket',G['module_rf_socket']['position_mm'],1120,690),('S1 · RESET',F['S1']['origin_mm'][:2],1120,610),('S2 · PROG / BOOT',F['S2']['origin_mm'][:2],1120,540),('D4 · Power LED',F['D4']['origin_mm'][:2],1120,850),('D5 · RX LED',F['D5']['origin_mm'][:2],1120,180),('D6 · TX LED',F['D6']['origin_mm'][:2],1120,110)]
    for idx,(label,pos,x,y) in enumerate(calls):
        u,v=xy(pos);px,py=ox+u*sc,oy+v*sc;end=x+300 if x<ox else x-15-idx*5
        route_y=py-25 if label.startswith('D6') else py
        d.line([(px,py),(px,route_y),(end,route_y),(end,y-7)],'ink',1.5);d.circle(px,py,3,'gold');d.text(x,y,label,26,'ink',True)
    d.text(40,990,'Component side (B.Cu) · J2 pin 1 at top · connectors extend beyond PCB',19,'muted')
    d.export('connector-locator')
    d.export('controller-component-landmarks')
    d=Drawing(1500,1050);ox,oy,sc=300,80,17; board(d,ox,oy,sc,context=False,numbers=False)
    def dim(x1,y1,x2,y2,t,tx,ty):
        d.line([(x1,y1),(x2,y2)],'ink',2);d.circle(x1,y1,3,'ink');d.circle(x2,y2,3,'ink');d.text(tx,ty,t,27,'ink',True,'middle')
    d.line([(ox,oy),(ox,35)],'muted',1); d.line([(ox+W*sc,oy),(ox+W*sc,35)],'muted',1)
    d.line([(ox,oy),(255,oy)],'muted',1); d.line([(ox,oy+H*sc),(255,oy+H*sc)],'muted',1)
    for hx in (ox+1.5*sc,ox+(W-1.5)*sc): d.line([(hx,oy+(H-1.5)*sc),(hx,940)],'muted',1)
    for hy in (oy+1.5*sc,oy+(H-1.5)*sc): d.line([(ox+(W-1.5)*sc,hy),(975,hy)],'muted',1)
    dim(ox,40,ox+W*sc,40,'36.88',ox+W*sc/2,30)
    dim(260,oy,260,oy+H*sc,'48.89',210,oy+H*sc/2)
    dim(ox+1.5*sc,935,ox+(W-1.5)*sc,935,'33.88 hole centres',ox+W*sc/2,965)
    dim(970,oy+1.5*sc,970,oy+(H-1.5)*sc,'45.89',1015,oy+H*sc/2)
    d.text(40,1010,'4 × Ø1.50 holes · centres 1.50 from each adjacent edge · corner R1.50',20,'ink',True)
    # Enlarged top-left corner, showing edge offsets and drilled hole.
    x,y,ss=1140,125,50
    d.rect(x,y,220,220,'light','green',75,2)
    d.circle(x+75,y+75,37.5,'white','ink',2)
    d.line([(x,y-10),(x,y-42),(x+75,y-42),(x+75,y+75)],'ink',1.5)
    d.text(x+37,y-50,'1.50',25,'ink',True,'middle')
    d.line([(x-10,y),(x-42,y),(x-42,y+75),(x+75,y+75)],'ink',1.5)
    d.text(x-45,y+46,'1.50',25,'ink',True,'end')
    d.line([(x+100,y+50),(x+155,y+10),(x+240,y+10)],'ink',1.5)
    d.text(x+240,y+5,'Ø1.50',25,'ink',True)
    d.line([(x+20,y+20),(x+110,y+160),(x+210,y+160)],'ink',1.5)
    d.text(x+210,y+155,'R1.50',25,'ink',True)
    d.text(x,y+260,'Corner detail · mm',25,'ink',True)
    d.export('mechanical-dimensions')
    d=Drawing(1000,1100);ox,oy,sc=200,80,17;board(d,ox,oy,sc,'label')
    for tp in G['test_pads']:
        u,v=tp['label_side_mm'];x,y=ox+u*sc,oy+v*sc;d.circle(x,y,5,C[tp['category']])
    for name,(u,v) in {'A':(23,3),'B':(13,13),'C':(20,24),'D':(11,32),'E':(32,36)}.items():
        d.circle(ox+u*sc,oy+v*sc,28,'none','ink',2);d.text(ox+u*sc,oy+v*sc+8,name,24,'ink',True,'middle')
    d.text(80,975,'Label side (F.Cu) · coloured marks locate all 51 test points',21,'ink',True)
    d.text(80,1010,'A–D: through-hole pads  ·  E: surface service pads',20,'muted')
    d.export('gpio-overview')
    d.text(80,1045,'Use the next five pages for individually numbered pad labels.',20,'ink',True)
    d.export('gpio-detail')
    for region in 'ABCDE':
        pts=[t for t in G['test_pads'] if (t.get('region')==region if region!='E' else not t.get('region'))]
        # True geometry shown on left; index at each pad links to readable names at right.
        us=[t['label_side_mm'][0] for t in pts];vs=[t['label_side_mm'][1] for t in pts]
        lo,hi=min(us)-2,max(us)+2; lv,hv=min(vs)-2,max(vs)+2
        scale=min(420/(hi-lo),620/(hv-lv));x0,y0=65,125
        d=Drawing(1100,1100);d.text(55,60,f'Region {region} · label side (F.Cu)',30,'ink',True)
        d.rect(x0,y0,(hi-lo)*scale,(hv-lv)*scale,'light','edge',8,2)
        pts.sort(key=lambda t:int(t['reference'][2:]))
        for i,t in enumerate(pts):
            u,v=t['label_side_mm'];x=x0+(u-lo)*scale;y=y0+(v-lv)*scale
            d.circle(x,y,12,C[t['category']],'white',1);d.text(x,y+4,t['reference'].replace('TP',''),11,'white',True,'middle')
            col=i//8;row=i%8;tx=540+col*275;ty=145+row*85
            d.text(tx,ty,t['reference'],20,'ink',True);d.text(tx,ty+25,t['label'],19,'muted')
        d.text(55,1000,'Markers show TP reference numbers; the matching labels identify each signal.',19,'muted')
        if region=='E':d.text(55,1035,'Surface-mount service pads; these are not through holes.',19,'muted')
        d.export('gpio-detail-'+region.lower())

if __name__=='__main__':all_figures()
