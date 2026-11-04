#!/usr/bin/env python3
"""Cross-check published design values against a fresh KiCad netlist and PCB."""
import re,json,math
from pathlib import Path

def parse(path):
 toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',Path(path).read_text());stack=[];root=None
 for t in toks:
  if t=='(':
   n=[]
   if stack:stack[-1].append(n)
   else:root=n
   stack.append(n)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root

def sub(x,key):return [a for a in x if isinstance(a,list) and a and a[0]==key]
def val(x,key,default=None):
 a=sub(x,key);return a[0][1] if a else default

import argparse, subprocess, tempfile
ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser()
ap.add_argument('--kicad-cli',default='kicad-cli')
args=ap.parse_args()
with tempfile.TemporaryDirectory(prefix='controller-datasheet-') as tmp:
 output=Path(tmp)/'current.net'
 subprocess.run([args.kicad_cli,'sch','export','netlist','--output',str(output),str(ROOT/'PCB/0.5/0.5.kicad_sch')],check=True,capture_output=True)
 n=parse(output)
p=parse(ROOT/'PCB/0.5/0.5.kicad_pcb')
nets={}
for net in sub(sub(n,'nets')[0],'net'):
 for node in sub(net,'node'):nets[(val(node,'ref'),val(node,'pin'))]=val(net,'name')
comps={val(c,'ref'):c for c in sub(sub(n,'components')[0],'comp')}
footprints={next(v[2] for v in sub(f,'property') if v[1]=='Reference'):f for f in sub(p,'footprint')}
checks=0
def check(condition,message):
 global checks
 if not condition:raise AssertionError(message)
 checks+=1
expected=['GND','/index/schTop/RS485A','/index/schTop/RS485B','GND','/index/schTop/RS485A','/index/schTop/RS485B','+3.3V','+5V']
for pin,name in enumerate(expected,1):check(nets[('J2',str(pin))]==name,f'J2 pin {pin}')
for pin,name in [('1','+20V'),('2','GND')]:check(nets[('J1',pin)]==name,f'J1 pin {pin}')
for ref,rail in [('J3','+20V'),('J5','+5V')]:
 for pin in ['A4','A9','B4','B9']:check(nets[(ref,pin)]==rail,f'{ref} {pin}')
for pin in ['A6','B6','A7','B7']:check(nets[('J3',pin)].startswith('unconnected-'),f'J3 data {pin}')
for pin,net in [('8','/index/schTop/TX_RS485'),('9','/index/schTop/RX_RS485'),('23','/index/schTop/USB_D-'),('24','/index/schTop/USB_D+')]:check(nets[('U7',pin)]==net,f'U7 {pin}')
for ref,value in [('U7','ESP32-S3-MINI-1U'),('U5','SP3485EN'),('U8','CH221K'),('U9','TPS54202DDC'),('R27','200k'),('R31','62k'),('R5','220R'),('R1','560R'),('R3','560R')]:check(val(comps[ref],'value')==value,f'{ref} value')
properties=[val(a,'name') for a in sub(comps['R31'],'property')]
check('dnp' in properties and 'exclude_from_bom' in properties,'R31 standard DNP')
for pin in ['1','2']:check(nets[('R31',pin)]==nets[('R27',pin)],'R31 optional parallel configuration')
check(float(val(sub(p,'general')[0],'thickness'))==1.6,'PCB thickness')
pts=[]
for a in p:
 if isinstance(a,list) and a[0] in ['gr_arc','gr_line'] and val(a,'layer')=='Edge.Cuts':
  for key in ['start','end']:pts.append(tuple(map(float,sub(a,key)[0][1:3])))
check(abs(max(x for x,y in pts)-min(x for x,y in pts)-36.88)<1e-6,'outline width')
check(abs(max(y for x,y in pts)-min(y for x,y in pts)-48.89)<1e-6,'outline length')
holes=[a for a in sub(p,'gr_circle') if val(a,'layer')=='Edge.Cuts']
check(len(holes)==4,'four corner holes')
for a in holes:
 c=list(map(float,sub(a,'center')[0][1:3]));e=list(map(float,sub(a,'end')[0][1:3]))
 check(abs(math.dist(c,e)*2-1.5)<1e-6,'corner hole diameter')
check(set(tuple(map(float,sub(a,'center')[0][1:3])) for a in holes)=={(38.15,104.5),(72.03,104.5),(38.15,150.39),(72.03,150.39)},'corner centers')
# Independent PCB-vs-schematic pad net check for every numbered pad.
for ref,f in footprints.items():
 for pad in sub(f,'pad'):
  if pad[1] and sub(pad,'net'):
   check(nets[(ref,pad[1])]==sub(pad,'net')[0][2],f'PCB/schematic mismatch: {ref}.{pad[1]}')
# J2 pitch in its own footprint coordinates.
a=footprints['J2'];padcoords={pad[1]:list(map(float,sub(pad,'at')[0][1:3])) for pad in sub(a,'pad') if pad[1]}
for pin in range(1,8):check(abs(math.dist(padcoords[str(pin)],padcoords[str(pin+1)])-2.54)<1e-6,'J2 pitch')
print(f'PASS: {checks} design checks; all numbered PCB pads agree with fresh schematic nets.')
