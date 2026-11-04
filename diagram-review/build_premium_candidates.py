#!/usr/bin/env python3
"""AI-created part art + independently checkable vector connections."""
from pathlib import Path
import base64
import build_physical_candidates as b
ROOT=Path(__file__).resolve().parent
original_text=b.text
original_header=b.header
original_finish=b.finish
asset='motor-asset-v1.png';slug='p06-illustrated-natural-v2';variant='Natural-material illustration'

def big_text(x,y,s,size=30,color='ink',weight=400,anchor='start'):
    if s in ['1  GND','2  A','3  B','4  GND','5  A','6  B','7  3.3 V','8  5 V']:size=29
    if s in ['PD POWER','PROGRAM']:size=26
    return original_text(x,y,s,size,color,weight,anchor)
b.text=big_text

def header(title,sub):
    original_header('Two motors. One complete connection map.','USB-C PD power · parallel motor supply · one shared RS485 daisy-chain')

def illustrated_motor(x,name):
    # Artwork is an identity illustration; it has NO electrical wire endpoint.
    raw=base64.b64encode((ROOT/'working'/asset).read_bytes()).decode()
    b.add(f'<image x="{x-45}" y="425" width="420" height="475" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{raw}"/>')
    b.text(x+165,400,name,38,'ink',700,'middle')
    b.text(x+165,913,'Six-wire pigtail functions',24,'muted',400,'middle')
    b.add(f'<rect x="{x-30}" y="943" width="390" height="92" rx="10" fill="#f1f6f2" stroke="#a8bdb0" stroke-width="2" stroke-dasharray="8 6"/>')
    # Detached functional ports, never drawn into the asset's visible connector cavities.
    for i,(lab,n) in enumerate(zip(['GND','V+','A','B','A','B'],['gnd','red','a','b','a','b'])):
        xx=x+25+i*50
        b.text(xx-8 if i == 0 else xx+4 if i == 1 else xx,981,lab,26 if lab == 'GND' else 30,n,700,'middle')
        b.line([(xx,991),(xx,1003)],n,8,False)
        b.endpoint(f'{name.replace(" ","")}.{i+1}',xx,1003)
    # Pair equivalence is printed beside the illustration, outside all wire lanes.
    b.text(x+355,704,'A leads linked',22,'a',600)
    b.text(x+355,740,'B leads linked',22,'b',600)
    b.text(x+355,776,'Same bus',23,'muted')

def finish(name,foot):
    # Match logical paths to the motor function key, not a mechanical mating view.
    original_finish(slug,'Motor power: J1. Data: J2 pin 2 = A, pin 3 = B. Both motor power returns and controller GND share one reference.')

b.header=header;b.motor=illustrated_motor;b.finish=finish
for asset,slug,variant in [('motor-asset-v1.png','p06-illustrated-natural-v2','Natural-material illustration'),('motor-asset-stylized-v1.png','p07-illustrated-stylized-v2','Restrained cartoon illustration')]:
    b.physical()
