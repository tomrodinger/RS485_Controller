from pathlib import Path
from html import escape
import base64
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
COL = dict(ink='#162a35', muted='#586975', edge='#ced8de', red='#c83939', black='#27333b', a='#087e60', b='#2165bd')

def text(x, y, s, size=28, color='ink', weight=400, anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{COL.get(color,color)}" font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>'

def box(x,y,w,h,fill='#fff',stroke='#ced8de',r=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'

def wire(points, color, width=7):
    p=' '.join(f'{x},{y}' for x,y in points)
    # White casing makes a crossing without a junction unambiguous.
    return f'<polyline points="{p}" fill="none" stroke="white" stroke-width="{width+8}" stroke-linecap="round" stroke-linejoin="round"/><polyline points="{p}" fill="none" stroke="{COL[color]}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'

def dot(x,y,color):
    return f'<circle cx="{x}" cy="{y}" r="10" fill="{COL[color]}"/>'

def port(x,y,color):
    return f'<circle cx="{x}" cy="{y}" r="8" fill="white" stroke="{COL[color]}" stroke-width="4"/>'

def schematic():
    s=[]
    s += [box(110,430,540,690,'#f3f7f8'), box(1050,500,480,620), box(1810,500,480,620)]
    s += [text(145,485,'RS485 Controller',34,weight=700),text(145,520,'Connector functions · PCB 0.5',23,'muted')]
    s += [text(145,572,'J1 POWER OUT',26,weight=700),text(610,560,'1  +20 V',25,'red',600,'end'),text(610,610,'2  GND',25,'black',600,'end')]
    s += [text(145,748,'J2 RS485',26,weight=700),text(610,822,'1  GND',25,'black',600,'end'),text(610,872,'2  A',25,'a',600,'end'),text(610,922,'3  B',25,'b',600,'end')]
    s += [text(145,1000,'J2 pins 4–8 unused here',23,'muted'),text(145,1040,'Both bus groups are parallel',23,'muted')]
    s += [box(145,620,220,62,'#fff'),text(165,659,'J3  PD POWER',24,weight=600)]
    s += [box(145,1060,220,42,'#fff'),text(163,1089,'J5  PROGRAM',22,'muted')]
    # Deliberately external, non-geometric six-lead functional mapping.
    for x,name in [(1050,'Motor 1'),(1810,'Motor 2')]:
        s += [text(x+30,550,name,34,weight=700),text(x+30,589,'J4 pigtail · functional breakout',22,'muted')]
        for yy,pin,label,c in [(640,1,'GND · black','black'),(690,2,'V+ · red','red'),(810,3,'A · green','a'),(860,4,'B · blue','b'),(980,5,'A · green','a'),(1030,6,'B · blue','b')]:
            s += [text(x+30,yy+9,str(pin),23,'muted'),text(x+80,yy+9,label,25,c,600)]
        s += [text(x+30,1110,'Lead functions; not a connector-face view',19,'muted')]
        s += [text(x+30,756,'INCOMING PAIR',19,'muted',700),text(x+30,938,'SECOND PAIR',19,'muted',700)]
        s += [text(x+80,902,'A3 = A5  ·  B4 = B6',24,'muted',600)]
    # Supply: the two branches are parallel. Black return carries motor current.
    s += [wire([(650,560),(750,560),(750,280),(1740,280),(1740,690),(1810,690)],'red',9)]
    s += [wire([(950,280),(950,690),(1050,690)],'red',9)]
    s += [wire([(650,610),(800,610),(800,350),(1680,350),(1680,640),(1810,640)],'black',9)]
    s += [wire([(900,350),(900,640),(1050,640)],'black',9)]
    # Red branch crosses black bus with a white bridge and no junction dot.
    s += [wire([(950,330),(950,370)],'red',9)]
    s += [dot(950,280,'red'),dot(900,350,'black')]
    # Thin ground-reference wire joins the substantial motor return.
    s += [wire([(650,810),(735,810),(735,650),(800,650),(800,610)],'black',4),dot(800,610,'black')]
    # RS485 bus uses the duplicate A/B pigtail pair on motor 1.
    s += [wire([(650,860),(855,860),(855,810),(1050,810)],'a'),wire([(650,910),(905,910),(905,860),(1050,860)],'b')]
    s += [wire([(1530,980),(1600,980),(1600,810),(1810,810)],'a'),wire([(1530,1030),(1650,1030),(1650,860),(1810,860)],'b')]
    # Motor2 spare pair ends are independently insulated, never shorted.
    s += [wire([(2290,980),(2335,980)],'a'),wire([(2290,1030),(2335,1030)],'b')]
    s += [box(2333,968,20,24,'#162a35','#162a35',4),box(2333,1018,20,24,'#162a35','#162a35',4)]
    for x,y,c in [(650,560,'red'),(650,610,'black'),(650,810,'black'),(650,860,'a'),(650,910,'b'),(1050,640,'black'),(1050,690,'red'),(1050,810,'a'),(1050,860,'b'),(1530,980,'a'),(1530,1030,'b'),(1810,640,'black'),(1810,690,'red'),(1810,810,'a'),(1810,860,'b'),(2290,980,'a'),(2290,1030,'b')]:
        s += [port(x,y,c)]
    s += [text(1080,242,'POWER IN PARALLEL',24,weight=700),text(1080,321,'Positive supply',23,'red',600),text(1080,390,'Motor-current return / common GND',23,'black',600)]
    s += [text(1080,435,'20 V nominal after successful PD negotiation',24,'muted')]
    s += [text(112,1195,'Read the circuit',27,weight=700),text(112,1240,'Power: J1 → both motors.  Data: J2 → Motor 1 pair 1 → pair 2 → Motor 2 pair 1.',25),text(112,1280,'Motor 2 pair 2 is spare: insulate A and B separately.  All GND connections share one reference.',25)]
    s += [text(580,1150,'J1 / J2 GND already common on PCB; thin reference lead is optional.',22,'muted',400,'middle'),text(1670,1170,'A/B CONTINUES AS ONE BUS',23,'muted',700,'middle'),text(1670,1210,'Route A/B as twisted pair; keep branch leads short.',22,'muted',400,'middle')]
    # USB-C PD path is segregated from all motor nets.
    s += [box(110,160,510,120,'#162a35','#162a35'),text(145,211,'20 V-capable USB-C PD supply',25,'#fff',700),text(145,252,'USB-C cable to J3',24,'#e5eff2')]
    s += [wire([(190,280),(190,340),(80,340),(80,650),(145,650)],'black',6)]
    return ''.join(s)

def wrap(body,title,subtitle,footer):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="2400" height="1440" viewBox="0 0 2400 1440">
<style>text{{font-family:Arial,Helvetica,sans-serif}} </style>
<rect width="2400" height="1440" fill="#fff"/>
{text(90,81,title,48,weight=700)}{text(92,125,subtitle,25,'muted')}
{body}
<path d="M90 1335H2310" stroke="#ced8de" stroke-width="2"/>
{text(90,1384,footer,23,'muted')}
</svg>'''

def photo_guide():
    data=base64.b64encode((ROOT/'images/rs485-controller/ports.jpg').read_bytes()).decode()
    # Native source is square 2486 x 2486 per manifest and sips verification.
    # Rotate CCW with a uniform scale; the JPEG pixels remain unchanged.
    s=[box(80,170,730,1140,'#f3f7f8')]
    s += [text(115,224,'01  Locate the real ports',31,weight=700),text(115,269,'Component side · USB-C ports left',23,'muted')]
    s += [f'<g transform="translate(110,335) scale(.27)"><image width="2486" height="2486" transform="translate(0,2486) rotate(-90)" xlink:href="data:image/jpeg;base64,{data}"/></g>']
    # Numbered locator marks are identification, never electrical endpoints.
    loc=[(240,435,'1'),(205,620,'3'),(205,875,'5'),(710,485,'2')]
    for x,y,n in loc:
        s += [f'<circle cx="{x}" cy="{y}" r="23" fill="#fff" stroke="#162a35" stroke-width="3"/>',text(x,y+8,n,24,weight=700,anchor='middle')]
    s += [text(115,1070,'1  J1   Motor power output',26,weight=600),text(115,1115,'2  J2   Eight-pin RS485 header',26,weight=600),text(115,1160,'3  J3   USB-C PD power input',26,weight=600),text(115,1205,'5  J5   USB-C programming',26,weight=600)]
    s += [text(115,1260,'Markers locate connectors; they are not wire endpoints.',20,'muted')]
    s += [text(870,224,'02  Connect the functional pigtails',31,weight=700),text(870,269,'Use the map below; motor connector-face orientation is not implied.',23,'muted')]
    s += [f'<g transform="translate(820,270) scale(.65)">{schematic()}</g>']
    # Real J2 orientation inset, separate from motor functional breakouts.
    s += [box(870,1165,1440,145,'#f3f7f8'),text(900,1205,'J2 in this photographed orientation · top → bottom',24,weight=700),text(900,1250,'1 GND  |  2 A  |  3 B  |  4 GND  |  5 A  |  6 B  |  7 3.3 V  |  8 5 V',25),text(900,1287,'Use pins 2 / 3 for A/B; pin 1 is optional reference. Keep motor power off the 3.3 V / 5 V pins.',22,'muted')]
    return ''.join(s)

def guided_panel(y, step):
    s=[box(70,y,1860,800,'#f7f9fa')]
    title='01  Connect supply and motor returns' if step==1 else '02  Continue the shared RS485 bus'
    subtitle='Both motors take power in parallel from J1.' if step==1 else 'Power from Step 1 is faded. A/B continues through Motor 1’s duplicate pair.'
    s += [text(105,y+62,title,41,weight=700),text(107,y+110,subtitle,29,'muted')]
    for x,w,name in [(110,360,'CONTROLLER'),(780,400,'MOTOR 1'),(1480,400,'MOTOR 2')]:
        s += [box(x,y+280,w,430),text(x+25,y+326,name,32,weight=700)]
    # Identical circuit/device geometry in both stages; inactive power fades.
    p=[]
    p += [wire([(470,y+360),(540,y+360),(540,y+180),(1380,y+180),(1380,y+410),(1480,y+410)],'red',9)]
    p += [wire([(680,y+180),(680,y+410),(780,y+410)],'red',9)]
    p += [wire([(470,y+410),(590,y+410),(590,y+230),(1320,y+230),(1320,y+360),(1480,y+360)],'black',9)]
    p += [wire([(640,y+230),(640,y+360),(780,y+360)],'black',9)]
    p += [wire([(680,y+210),(680,y+250)],'red',9),dot(680,y+180,'red'),dot(640,y+230,'black')]
    p += [box(110,y+140,360,85,'#162a35','#162a35'),text(135,y+176,'20 V-capable USB-C PD',27,'#fff',700),text(135,y+210,'USB-C cable → J3',25,'#e5eff2')]
    p += [wire([(150,y+225),(150,y+250),(90,y+250),(90,y+660),(110,y+660)],'black',6)]
    s += [('<g opacity=".18">' if step==2 else '<g>')+''.join(p)+'</g>']
    s += [text(135,y+372,'J1 1  +20 V',29,'red',600),text(135,y+422,'J1 2  GND',29,'black',600),text(135,y+672,'J3 PD POWER',26,'muted',600)]
    for x in (780,1480):
        s += [text(x+25,y+372,'J4 1   GND · black',28,'black',600),text(x+25,y+422,'J4 2   V+ · red',28,'red',600)]
    if step==1:
        for x in (780,1480):
            s += [text(x+25,y+520,'Six-wire motor pigtail',27,'muted'),text(x+25,y+563,'A/B wiring follows in Step 2',25,'muted')]
        s += [text(135,y+520,'J2 data follows in Step 2',25,'muted'),text(105,y+760,'J1 is the negotiated PD rail: 20 V nominal after successful negotiation. Verify voltage and polarity.',28,'muted')]
    else:
        s += [wire([(470,y+490),(530,y+490),(530,y+450),(590,y+450),(590,y+410)],'black',4),dot(590,y+410,'black')]
        s += [wire([(470,y+540),(640,y+540),(640,y+490),(780,y+490)],'a'),wire([(470,y+590),(690,y+590),(690,y+540),(780,y+540)],'b')]
        s += [wire([(1180,y+600),(1250,y+600),(1250,y+490),(1480,y+490)],'a'),wire([(1180,y+650),(1300,y+650),(1300,y+540),(1480,y+540)],'b')]
        for x in (780,1480):
            for yy,pin,label,c in [(490,3,'A · green','a'),(540,4,'B · blue','b'),(600,5,'A · green','a'),(650,6,'B · blue','b')]:
                s += [text(x+25,y+yy+11,f'{pin}   {label}',29,c,600)]
            s += [text(x+25,y+576,'A3 = A5  ·  B4 = B6',23,'muted',600)]
        s += [text(135,y+502,'J2 1  GND',29,'black',600),text(135,y+552,'J2 2  A',29,'a',600),text(135,y+602,'J2 3  B',29,'b',600)]
        for yy,c in [(600,'a'),(650,'b')]:
            s += [wire([(1880,y+yy),(1900,y+yy)],c),box(1898,y+yy-13,20,26,'#162a35','#162a35',3)]
        s += [text(105,y+760,'Motor 2 pins 5/6 are spare: insulate separately. Route A/B as twisted pair; keep branch leads short.',28,'muted')]
    for x,yy,c in [(470,360,'red'),(470,410,'black'),(780,360,'black'),(780,410,'red'),(1480,360,'black'),(1480,410,'red')]:
        s += [port(x,y+yy,c)]
    if step==2:
        for x,yy,c in [(470,490,'black'),(470,540,'a'),(470,590,'b'),(780,490,'a'),(780,540,'b'),(1180,600,'a'),(1180,650,'b'),(1480,490,'a'),(1480,540,'b'),(1880,600,'a'),(1880,650,'b')]:
            s += [port(x,y+yy,c)]
    return ''.join(s)

def guided():
    data=base64.b64encode((ROOT/'images/rs485-controller/ports.jpg').read_bytes()).decode()
    s=[text(80,95,'The wiring, in two passes.',58,weight=700),text(82,156,'Wire parallel power, then the paired bus — all with power off.',31,'muted'),text(82,210,'Motor blocks show external pigtail functions, not a mating-face view.',28,'muted')]
    s += [f'<g transform="translate(1650,30) scale(.105)"><image width="2486" height="2486" transform="translate(0,2486) rotate(-90)" xlink:href="data:image/jpeg;base64,{data}"/></g>']
    for yy,label,px,py in [(74,'J1',1684,75),(148,'J3',1684,147),(240,'J5',1684,240)]:
        s += [text(1578,yy,label,23,weight=700),f'<path d="M1615 {yy-7}H{px}" stroke="#586975" stroke-width="1.5" fill="none"/>']
    s += [text(1940,104,'J2',23,weight=700),'<path d="M1930 97H1885" stroke="#586975" stroke-width="1.5" fill="none"/>']
    s += [text(1650,318,'Actual controller · J2 faces right',20,'muted')]
    s += [guided_panel(350,1),guided_panel(1210,2)]
    s += [text(80,2085,'Ground reference',30,weight=700),text(80,2130,'J1 / J2 GND already share one PCB net. The thin J2 reference lead is optional;',28,'muted'),text(80,2170,'retain the substantial J1 return to each motor. Wire with power off and verify the PCB labels.',28,'muted')]
    return '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="2000" height="2200" viewBox="0 0 2000 2200"><style>text{font-family:Arial,Helvetica,sans-serif}</style><rect width="2000" height="2200" fill="white"/>'+''.join(s)+'</svg>'

def main():
    entries=[
        ('v03-precise-electrical-revised',wrap(schematic(),'Two motors. One shared RS485 bus.','Electrical map · six-wire pigtail functions are shown as external breakouts, not mating-face geometry.','Wire with power off. Verify J1 voltage and polarity before attaching motors. Supply and wiring must support the combined load.')),
        ('v04-photo-guided-revised',wrap(photo_guide(),'From the real board to the correct connections.','Photographic port guide + an exact electrical map · controller PCB revision 0.5','Actual controller photograph; motor pigtail functions shown schematically. Verify J1 voltage, PCB labels and motor documentation.')),
        ('v05-guided-two-step',guided()),
    ]
    for name,svg in entries:
        p=OUT/f'{name}.svg'; p.write_text(svg)
        subprocess.run(['rsvg-convert','-o',str(OUT/f'{name}.png'),str(p)],check=True)
        print(p)

if __name__=='__main__': main()
