#!/usr/bin/env python3
"""Revision 0.4 drawings, from the checked PCB 0.5 geometry."""
from pathlib import Path
from html import escape
import importlib.util, json, math
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('geometry_core',ROOT/'datasheet/review/geometry-v2/build_technical_assets.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
OUT=ROOT/'datasheet/assets/technical-v4';OUT.mkdir(exist_ok=True);g.OUT=OUT
D=g.Drawing; G=g.G; F=g.F; W=g.W; H=g.H
FUNCTIONS=['GND','A','B','GND','A','B','3.3V','5V']

def board(d,x,y,k,context=True):
    g.board(d,x,y,k,context=context,numbers=False)
    for i,signal in enumerate(FUNCTIONS,1):
        u,v=G['illustration_anchors_mm'][f'J2.{i}']
        d.rect(x+29.8*k,y+(v-.83)*k,4.15*k,1.7*k,'#258267',r=.15*k)
        d.text(x+33.6*k,y+(v+.40)*k,signal,1.15*k,'white',True,'end')
    for ref,dx,dy in [('J1',8.4,5.3),('J3',8.4,18),('J5',8.4,42.5)]:d.text(x+dx*k,y+dy*k,ref,1.5*k,'white',True)
    for ref in ['S1','S2']:
        u,v=g.xy(F[ref]['origin_mm'][:2]);d.text(x+(u-2)*k,y+(v+.4)*k,ref,1.05*k,'white',True,'end')

def path(d,value,color,width=2,dash=None,fill='none'):
    d.add(f'<path d="{value}" fill="{fill}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')

def base():
    d=D(1440,1590);board(d,0,0,1)
    (OUT/'board-component-base.svg').write_text(d.svg([-3,-2,48,53]))

def locator():
    d=D(1650,1320);ox,oy,k=410,145,20
    board(d,ox,oy,k)
    def pos(ref):
        u,v=g.xy(G['module_rf_socket']['position_mm'] if ref=='RF' else F[ref]['origin_mm'][:2]);return ox+u*k,oy+v*k
    # Curved leaders are ordered by physical height and kept in separate corridors.
    for ref,title,sub,ty,col in [('J1','J1 · MOTOR POWER OUT','Direct PD rail and common GND',290,'#52786a'),('J3','J3 · PD POWER IN','USB-C power supply',510,'#52786a'),('J5','J5 · USB-C PROG','Computer / programming',1020,'#52786a')]:
        px,py=pos(ref);ex=355
        path(d,f'M {px} {py} C {px-70} {py}, {ex+70} {ty}, {ex} {ty}',col,2.4,'7 6')
        d.circle(px,py,5,'white',col,2)
        d.text(45,ty-16,title,26,'ink',True);d.text(45,ty+19,sub,21,'muted')
    # The LEDs share a horizontal row; splayed curves keep their paths distinct.
    for ref,label,tx,col in [('D6','D6 · TX / red',620,'#bf565b'),('D5','D5 · RX / green',930,'#21835f')]:
        px,py=pos(ref); path(d,f'M {px} {py} C {px} {py-90}, {tx} 155, {tx} 105','white',5.5);path(d,f'M {px} {py} C {px} {py-90}, {tx} 155, {tx} 105',col,2.4,'7 6');d.circle(px,py,5,'white',col,2);d.text(tx,82,label,26,col,True,'middle')
    for ref,title,sub,ty,col in [('S2','S2 · PROG / BOOT','Hold during reset to program',690,'#52786a'),('RF','Antenna socket','On the U7 module',785,'#a87d31'),('S1','S1 · RESET','Resets the ESP32-S3',900,'#52786a'),('D4','D4 · POWER / yellow','Logic power indicator',1075,'#a87d31')]:
        px,py=pos(ref);ex=1260
        path(d,f'M {px} {py} C {px+65} {py}, {ex-75} {ty}, {ex} {ty}',col,2.4,'7 6');d.circle(px,py,5,'white',col,2)
        d.text(1280,ty-12,title,27,'ink',True);d.text(1280,ty+24,sub,21,'muted')
    d.text(1270,215,'J2 · RS485 / AUX',27,'ink',True)
    d.text(1270,251,'Signal names are printed',21,'muted')
    d.text(1270,280,'beside all eight contacts.',21,'muted')
    d.text(700,1195,'U7 · ESP32-S3-MINI-1U',25,'ink',True,'middle')
    d.text(50,1260,'COMPONENT SIDE (B.Cu) · USB sockets at left · J2 header at right',24,'ink',True)
    d.export('connector-locator')

def mechanical():
    d=D(1500,1130);ox,oy,k=275,115,17
    g.board(d,ox,oy,k,context=False,numbers=False)
    def dim(x1,y1,x2,y2,label,tx,ty):
        d.line([(x1,y1),(x2,y2)],'ink',1.8);d.circle(x1,y1,2.5,'ink');d.circle(x2,y2,2.5,'ink');d.text(tx,ty,label,26,'ink',True,'middle')
    d.line([(ox,oy),(ox,65)],'muted',1);d.line([(ox+W*k,oy),(ox+W*k,65)],'muted',1)
    d.line([(ox,oy),(225,oy)],'muted',1);d.line([(ox,oy+H*k),(225,oy+H*k)],'muted',1)
    dim(ox,70,ox+W*k,70,'36.88',ox+W*k/2,55)
    dim(230,oy,230,oy+H*k,'48.89',170,oy+H*k/2)
    for hx in (ox+1.5*k,ox+(W-1.5)*k):d.line([(hx,oy+(H-1.5)*k),(hx,990)],'muted',1)
    for hy in (oy+1.5*k,oy+(H-1.5)*k):d.line([(ox+(W-1.5)*k,hy),(960,hy)],'muted',1)
    dim(ox+1.5*k,985,ox+(W-1.5)*k,985,'33.88 hole centres',ox+W*k/2,1023)
    dim(955,oy+1.5*k,955,oy+(H-1.5)*k,'45.89',1000,oy+H*k/2)
    # One physical corner, with deliberately jagged broken edges on the crop.
    x,y=1145,190;sc=52;rr=1.5*sc;hole=.75*sc;cx=x+rr;cy=y+rr
    outline=f'M {x+rr} {y} L {x+230} {y} L {x+221} {y+36} L {x+239} {y+72} L {x+221} {y+110} L {x+239} {y+149} L {x+222} {y+188} L {x+230} {y+230} L {x+188} {y+222} L {x+150} {y+240} L {x+112} {y+222} L {x+74} {y+240} L {x+38} {y+222} L {x} {y+230} L {x} {y+rr} A {rr} {rr} 0 0 1 {x+rr} {y} Z'
    path(d,outline,'#197a60',2.3,fill='#edf4ef');d.circle(cx,cy,hole,'white','ink',2)
    d.line([(cx-52,cy),(cx+52,cy)],'muted',1,'5 4');d.line([(cx,cy-52),(cx,cy+52)],'muted',1,'5 4')
    for xx in [x,cx]:d.line([(xx,y-10),(xx,y-65)],'muted',1)
    dim(x,y-55,cx,y-55,'1.50',(x+cx)/2,y-68)
    for yy in [y,cy]:d.line([(x-10,yy),(x-65,yy)],'muted',1)
    dim(x-55,y,x-55,cy,'1.50',x-92,y+rr/2+9)
    qx,qy=cx+hole/math.sqrt(2),cy-hole/math.sqrt(2)
    d.line([(qx,qy),(x+195,y-12),(x+255,y-12)],'ink',1.7);d.text(x+255,y-18,'Ø1.50',25,'ink',True,'end')
    ax,ay=cx-rr/math.sqrt(2),cy-rr/math.sqrt(2)
    d.line([(ax,ay),(x+114,y+164),(x+231,y+164)],'ink',1.7);d.text(x+231,y+155,'R1.50',25,'ink',True,'end')
    d.text(x+110,y+285,'Broken-out corner',26,'ink',True,'middle')
    d.text(x+110,y+320,'Same geometry at all four corners',20,'muted',False,'middle')
    d.text(55,1090,'mm · 4 × Ø1.50 mounting holes · centres 1.50 from adjacent edges · corners R1.50',24,'ink',True)
    d.export('mechanical-dimensions')

def breakout():
    d=D(1600,1850);ox,oy,k=260,170,30
    g.board(d,ox,oy,k,face='label')
    # Reinforce the USB silhouettes without implying they are fitted on this face.
    for ref,title,subtitle in [('J5','J5 · USB-C PROG','Computer / programming'),('J3','J3 · PD POWER IN','Motor-power USB-C supply')]:
        a,b,c,e=g.bounds(ref,'label','B.Fab');x=ox+a*k;y=oy+b*k;w=(c-a)*k;h=(e-b)*k
        d.rect(x,y,w,h,'#edf2ef','#7a9487',12,2,'8 6')
        d.rect(x-7,y+25,18,h-50,'#cad7d0','#7a9487',7,1.5,'6 5')
        d.text(x+w/2,y+h/2-43,ref,31,'ink',True,'middle')
        d.text(x+w/2,y+h/2+2,'USB-C PROG' if ref=='J5' else 'PD POWER IN',26,'ink',True,'middle')
        d.text(x+w/2,y+h/2+45,'Computer' if ref=='J5' else 'Power supply',23,'muted',False,'middle')
    d.text(ox+24*k,oy+13*k,'ESP32-S3 module',25,'#829d8c',False,'middle')
    d.text(ox+24*k,oy+13*k+35,'on opposite face',22,'#829d8c',False,'middle')
    labels=[]
    for tp in G['test_pads']:
        u,v=tp['label_side_mm'];x=ox+u*k;y=oy+v*k
        color=g.C[tp['category']];d.circle(x,y,8,color,'white',2)
        label=tp['label'];secondary=tp['reference']
        if tp.get('shared_function'):secondary += ' / '+tp['shared_function'].replace('UART0 ','').replace('RS485 ','')
        region=tp.get('region')
        if region=='A':
            above=v<3;tx=x;ty=y-57 if above else y+63;anchor='middle'
            if tp['reference']=='TP49':
                tx=x-43;ty=y+29;anchor='end'
                d.line([(x-30,y),(tx+7,ty-7)],color,1.4)
            else:
                if tp['reference']=='TP31':tx+=9
                d.line([(x,y+(-30 if above else 30)),(tx,ty+(8 if above else -23))],color,1.4)
            size=18;sy=ty-27 if above else ty+20
        elif region=='B':
            left=u<13;tx=x-40 if left else x+40;ty=y+3;anchor='end' if left else 'start';size=24;sy=ty+24
            if tp['reference']=='TP30':ty+=31
            d.line([(x+(-30 if left else 30),y),(tx+ (7 if left else -7),ty-3)],color,1.4)
        elif region=='C':
            above=v<24;tx=x;ty=y-39 if above else y+67;anchor='middle';size=18;sy=ty-27
            d.line([(x,y+(-30 if above else 30)),(x,ty+(9 if above else -24))],color,1.4)
        elif region=='D':
            tx=x;ty=y+49;anchor='middle';size=23;sy=ty+25
            d.line([(x,y+18),(x,ty-24)],color,1.4)
            label=label.replace('_',' ')
        else:
            tx=x+49;ty=y+6;anchor='start';size=25;sy=ty+26
            d.line([(x+23,y),(tx-9,y)],color,1.4)
        if region in ('A','C') and anchor=='middle':
            d.rect(tx-36,ty-20,72,27,'white','#d2e0d6',4,.6)
        d.text(tx,ty,label,size,color,True,anchor)
        if tp.get('shared_function'):
            d.rect(tx-20,sy-12,40,16,'white',r=3)
            d.text(tx,sy,tp['shared_function'].replace('UART0 ','')+'0' if region=='A' else tp['shared_function'].replace('RS485 ',''),13,'muted',False,anchor)
        labels.append({'reference':tp['reference'],'signal':tp['label'],'shared_function':tp.get('shared_function'),'position_mm':[u,v],'marker_xy':[x,y],'label_xy':[tx,ty],'anchor':anchor,'through_hole':tp['through_hole']})
    d.text(65,1710,'REAR / LABEL SIDE (F.Cu) · looking toward the PCB',30,'ink',True)
    d.text(65,1752,'USB-C sockets and module are on the opposite face; dashed outlines locate them.',25,'muted')
    d.text(65,1793,'Round holes: solder headers or wires here. Gold rectangular pads: surface service points.',24,'muted')
    d.export('breakout-headers')
    (OUT/'breakout-labels.json').write_text(json.dumps(labels,indent=2)+'\n')

if __name__=='__main__':
    base();locator();mechanical();breakout()
    (OUT/'figures.json').write_text(json.dumps({'locator':'connector-locator.pdf','mechanical':'mechanical-dimensions.pdf','gpio-overview':'breakout-headers.pdf'},indent=2)+'\n')
    print('Built revision 0.4 geometry figures; labelled',len(G['test_pads']),'pads.')
