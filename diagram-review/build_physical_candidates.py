#!/usr/bin/env python3
"""Draw accurate connector landmarks and exact wiring; render exportable PNGs."""
from pathlib import Path
from html import escape
import json,subprocess,base64,math
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'candidates';OUT.mkdir(exist_ok=True)
C={'ink':'#173a33','muted':'#64766f','edge':'#d6e3dc','green':'#157659','board':'#238467','red':'#d84042','gnd':'#283335','a':'#16835e','b':'#256bc1','light':'#f1f6f2'}
S=[];routes=[];anchors={}
def add(s):S.append(s)
def text(x,y,s,size=30,color='ink',weight=400,anchor='start'):
 add(f'<text x="{x}" y="{y}" fill="{C.get(color,color)}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>')
def rect(x,y,w,h,fill='white',stroke='none',r=10,sw=2):
 add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="{sw}"/>')
def circle(x,y,r,fill,stroke='none',sw=2):add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="{sw}"/>')
def line(points,color,width=8,halo=True):
 p=' '.join(f'{x},{y}' for x,y in points)
 if halo:add(f'<polyline points="{p}" fill="none" stroke="white" stroke-width="{width+8}" stroke-linecap="round" stroke-linejoin="round"/>')
 add(f'<polyline points="{p}" fill="none" stroke="{C.get(color,color)}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
def endpoint(ref,x,y):anchors[ref]=[x,y]
def route(ref1,ref2,points,net,width=9):
 assert points[0]==tuple(anchors[ref1]),(ref1,points[0],anchors[ref1])
 assert points[-1]==tuple(anchors[ref2]),(ref2,points[-1],anchors[ref2])
 line(points,net,width);routes.append({'from':ref1,'to':ref2,'net':net,'points':points,'width':width})
def label(x,y,title,sub=None,w=250):
 rect(x,y,w,78 if sub else 50,'white','edge',10)
 text(x+16,y+32,title,25,'ink',700)
 if sub:text(x+16,y+60,sub,20,'muted')
def header(title,sub):
 rect(0,0,2600,1600,'#fff')
 text(100,105,'GEAROTONS  /  RS485 CONTROLLER',25,'green',700)
 text(100,185,title,63,'ink',700)
 text(102,237,sub,28,'muted')
def board():
 # Schematic component-side drawing follows ports.jpg CCW, never mirrored.
 bx,by,bw,bh=270,470,430,560
 rect(bx+8,by+12,bw,bh,'#dfe9e2','none',20)
 rect(bx,by,bw,bh,'board','#126149',20,3)
 for x in [bx+20,bx+bw-20]:
  for y in [by+20,by+bh-20]:circle(x,y,9,'#fff','#b1ccbb',4)
 # True two-way terminal at upper left. Wire mouths face left; screws are separate.
 rect(255,535,89,100,'#3c9c64','#166a44',6)
 for yy in [555,605]:
  rect(249,yy-12,19,24,'#132d23','#79b88a',3)
  circle(310,yy,14,'#d9e0de','#758d82',3)
  line([(301,yy-5),(319,yy+5)],'#657c73',3,False)
 text(352,557,'J1',28,'#fff',700);text(352,588,'POWER OUT',20,'#e8f4ec',700)
 text(286,526,'+',26,'#fff',700);text(286,662,'GND',20,'#e8f4ec',700)
 endpoint('J1.1',249,555);endpoint('J1.2',249,605)
 # USB shells face left. J3 is next to J1; J5 farther away.
 for yy,ref,txt in [(770,'J3','PD POWER'),(940,'J5','PROGRAM')]:
  rect(248,yy-40,98,80,'#d7ddda','#a4b7ac',10)
  rect(245,yy-24,20,48,'#26332e','#c0ccc5',8)
  text(362,yy-4,ref,28,'#fff',700);text(362,yy+26,txt,21,'#e5f3e9',700)
 endpoint('J3.USB',245,770)
 # Header actually has eight physical contacts; selected first group at top.
 rect(666,548,33,337,'#242c27','#101914',4)
 signals=['GND','A','B','GND','A','B','3.3 V','5 V']
 for i,signal in enumerate(signals):
  yy=570+i*40
  rect(695,yy-6,29,12,'#d1af62','#a78643',1)
  text(650,yy+7,f'{i+1}  {signal}',22,'#fff',600,'end')
  endpoint(f'J2.{i+1}',724,yy)
 for i in range(3):
  yy=570+i*40;rect(703,yy-12,34,24,'#222b26','#58655d',3)
  anchors[f'J2.{i+1}']=[737,yy]
 text(650,530,'J2 · RS485',25,'#fff',700,'end')
 # Key landmarks; intentionally simplified, no fake electrical terminals.
 rect(520,875,140,130,'#cbd5ce','#91a498',8)
 text(590,925,'ESP32-S3',19,'#4f6557',700,'middle')
 text(590,955,'MINI-1U',18,'#4f6557',400,'middle')
 for i in range(4):
  for j in range(3):circle(390+i*29,670+j*24,5,'#d7e9db','#187451',2)
 for x,y in [(410,1000),(460,1000)]:rect(x,y,31,21,'#b4c1b8','#124e39',3);circle(x+15,y+10,6,'#2b352d')
 text(480,1095,'RS485 Controller · component side',27,'ink',700,'middle')
 text(480,1130,'J2 pins 4–8 remain unused',23,'muted',400,'middle')
 # Small neutral RF detail is clearly identified and cannot be mistaken for a bus wire.
 circle(643,887,6,'#b8a666','#6e682b',2)
 line([(643,887),(650,927),(650,1000),(745,1000)],'#aab8af',3,False)
 rect(745,986,100,28,'#d8e0da','#aab8af',3)
 text(795,1042,'RF antenna',19,'muted',400,'middle')
 # J5 is deliberately open, not a broken motor-power path.
 
 
def motor(x,name):
 # Technical pictogram of real M17: shaft above, rear-side 6-contact connector.
 y=470;w=330
 rect(x+20,y+60,w-40,300,'#27352f','#1b2822',20)
 for yy in range(y+112,y+285,15):line([(x+26,yy),(x+w-26,yy)],'#3e4e45',3,False)
 rect(x+7,y+25,w-14,88,'#d4ded7','#8da397',14)
 for xx in [x+45,x+w-45]:
  for yy in [y+45,y+91]:circle(xx,yy,8,'#62796a')
 circle(x+w/2,y+70,42,'#a6b7aa','#698574',3)
 circle(x+w/2,y+70,29,'#526a59')
 rect(x+w/2-15,y-25,30,94,'#c4d0c7','#8da194',8)
 rect(x+11,y+318,w-22,57,'#203128','#14291e',9)
 # Mating 6-wire plug at actual lower side. Neutral loom avoids unverified face orientation.
 rect(x+100,y+347,130,47,'#fafcf8','#a0b5a6',4)
 rect(x+116,y+372,98,26,'#e5ebe3','#a0b5a6',4)
 for xx in range(6):rect(x+122+xx*15,y+374,8,14,'#c8d4c8','none',1)
 line([(x+165,y+398),(x+165,y+416)],'#99ad9c',14,False)
 text(x+w/2,y-64,name,37,'ink',700,'middle')
 text(x+w/2,y-28,'Gearotons M17 servomotor',23,'muted',400,'middle')
 # Each harness is explicitly a six-lead functional fan-out, not a numbered face view.
 panelx=x-10;panely=935
 add(f'<rect x="{panelx}" y="{panely}" width="350" height="98" rx="9" fill="#f1f6f2" stroke="#a8bdb0" stroke-width="2" stroke-dasharray="8 6"/>')
 text(x+345,852,'Six-wire pigtail',22,'ink',600);text(x+345,882,'Function key below',20,'muted')
 labels=['GND','V+','A','B','A','B'];net=['gnd','red','a','b','a','b']
 for i,(lab,n) in enumerate(zip(labels,net)):
  xx=x+25+i*50
  # Physical harness lives above the function strip; all mains attach to its labelled wire tails.
  
  text(xx,971,lab,24,n,700,'middle')
  line([(xx,986),(xx,1003)],n,8,False)
  endpoint(f'{name.replace(" ","")}.{i+1}',xx,1003)
 text(x+165,y+310,'A pairs linked · B pairs linked',18,'#e5f1e7',400,'middle')
 # Use visible annotation to separate pigtail functions from mating geometry.
 
def finish(name,foot):
 text(100,1430,foot,26,'ink',600)
 text(100,1480,'20 V is nominal after PD negotiation. Verify J1 voltage and polarity before attaching motors.',25,'muted')
 text(100,1525,'Drawing is schematic; not to scale. Motor pigtail strip shows functions, not a connector mating-face view.',23,'muted')
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="2600" height="1600" viewBox="0 0 2600 1600"><style>text{font-family:Arial,Helvetica,sans-serif}</style>'+''.join(S)+'</svg>'
 p=OUT/f'{name}.svg';p.write_text(svg);subprocess.run(['rsvg-convert','-o',str(OUT/f'{name}.png'),str(p)],check=True)
 (OUT/f'{name}.routes.json').write_text(json.dumps({'anchors':anchors,'routes':routes,'notes':'J1/J2 GND are internally common. Motor A3=A5; B4=B6. Grey pigtail loom is non-geometric; functional ends are identified separately.'},indent=2)+'\n')
 print(p)
def physical():
 S.clear();routes.clear();anchors.clear()
 header('A wiring guide with real connector landmarks.','Parallel motor power above · one paired RS485 bus below · shared DC ground')
 board();motor(1200,'Motor 1');motor(2000,'Motor 2')
 # Required topology: two parallel supply branches, pair continuing through motor1 duplicates.
 endpoint('PWR_POS',1170,300);endpoint('PWR_GND',1120,350)
 route('J1.1','PWR_POS',[(249,555),(160,555),(160,300),(1170,300)],'red',11)
 route('J1.2','PWR_GND',[(249,605),(210,605),(210,350),(1120,350)],'gnd',11)
 route('PWR_POS','Motor1.2',[(1170,300),(1170,1090),(1275,1090),(1275,1003)],'red',11)
 route('PWR_POS','Motor2.2',[(1170,300),(1940,300),(1940,1090),(2075,1090),(2075,1003)],'red',11)
 route('PWR_GND','Motor1.1',[(1120,350),(1120,1115),(1225,1115),(1225,1003)],'gnd',11)
 route('PWR_GND','Motor2.1',[(1120,350),(1900,350),(1900,1115),(2025,1115),(2025,1003)],'gnd',11)
 # Optional explicit reference lead (already common on board) shares no motor-current-only routing.
 route('J2.1','PWR_GND',[(737,570),(820,570),(820,400),(1120,400),(1120,350)],'gnd',5)
 route('J2.2','Motor1.3',[(737,610),(875,610),(875,1180),(1325,1180),(1325,1003)],'a',8)
 route('J2.3','Motor1.4',[(737,650),(920,650),(920,1225),(1375,1225),(1375,1003)],'b',8)
 route('Motor1.5','Motor2.3',[(1425,1003),(1425,1275),(2125,1275),(2125,1003)],'a',8)
 route('Motor1.6','Motor2.4',[(1475,1003),(1475,1320),(2175,1320),(2175,1003)],'b',8)
 for node,col in [('PWR_POS','red'),('PWR_GND','gnd')]:circle(*anchors[node],10,col)
 for i,n in [(5,'a'),(6,'b')]:
  xx,yy=anchors[f'Motor2.{i}'];line([(xx,yy),(xx,1137)],n,8);rect(xx-11,1137,22,32,'gnd','none',6)
 text(2300,1203,'Spare A/B',22,'muted',700,'middle');text(2300,1235,'Insulate separately',22,'muted',400,'middle')
 text(1310,276,'MOTOR POWER · PARALLEL',26,'ink',700)
 text(450,285,'+20 V nominal',25,'red',700);text(450,336,'GND / motor-current return',25,'gnd',700)
 text(1830,1372,'A/B daisy-chain · use a twisted pair',27,'ink',600,'middle')
 text(270,420,'Optional reference lead from J2 pin 1',21,'muted',600);text(270,450,'J1/J2 GND are already common',21,'muted');circle(1120,400,7,'gnd')
 # PD cable is a real mechanical cable to actual J3, distinct from motor-return notation.
 rect(105,1185,510,138,'ink','none',18)
 text(137,1234,'20 V-capable USB-C PD supply',29,'#fff',700)
 text(137,1280,'USB-C cable → J3 PD POWER',24,'#dbece1')
 add('<path d="M150 1185V805Q150 770 187 770H242" fill="none" stroke="white" stroke-width="29"/>')
 add('<path d="M150 1185V805Q150 770 187 770H242" fill="none" stroke="#75857b" stroke-width="18"/>')
 rect(218,749,29,42,'#66776c','#405449',5)
 finish('p03-connector-landmarks-v3','Motor power: J1. Data: J2 pin 2 = A, pin 3 = B. J2 pin 1 reference lead is optional when J1 establishes common ground.')
if __name__=='__main__':physical()
