#!/usr/bin/env python3
"""Build the owner-review PDF. Run from any directory; requires ReportLab and Pillow."""
from pathlib import Path
import argparse
import os
os.environ['SOURCE_DATE_EPOCH']='1792972800' # 2026-10-26, reproducible review edition
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
W,H=A4
M=43
CW=W-2*M
GREEN=colors.HexColor('#08765b')
DARK=colors.HexColor('#153a32')
INK=colors.HexColor('#203c39')
GRAY=colors.HexColor('#586c69')
LIGHT=colors.HexColor('#eef6f3')
RULE=colors.HexColor('#d5e4df')
DATE='26 October 2026'
STYLE=ParagraphStyle('body',fontName='Helvetica',fontSize=9.4,leading=14,textColor=INK,spaceAfter=0)
SMALL=ParagraphStyle('small',parent=STYLE,fontSize=8,leading=11,textColor=GRAY)
BOLD=ParagraphStyle('bold',parent=STYLE,fontName='Helvetica-Bold')
class Sheet:
 def __init__(self,path):
  self.c=canvas.Canvas(str(path),pagesize=A4,pageCompression=1)
  self.c.setTitle('Gearotons RS485 Controller — PCB 0.5 — Review datasheet v0.1')
  self.c.setAuthor('Gearotons')
  self.c.setSubject('Product specifications, connectors, two-motor wiring and software setup')
  self.page=0
 def text(self,s,x,y,size=10,color=INK,font='Helvetica'):
  self.c.setFillColor(color);self.c.setFont(font,size);self.c.drawString(x,H-y-size*.85,s)
 def para(self,s,y,x=M,w=CW,style=STYLE):
  p=Paragraph(s,style);_,h=p.wrap(w,H)
  if y+h>H-50:raise ValueError(f'Page {self.page}: paragraph overflow {y+h}: {s[:65]}')
  p.drawOn(self.c,x,H-y-h);return y+h
 def line(self,x1,y1,x2,y2,color=RULE,width=.7):
  self.c.setStrokeColor(color);self.c.setLineWidth(width);self.c.line(x1,H-y1,x2,H-y2)
 def rect(self,x,y,w,h,fill=LIGHT,r=6,stroke=None):
  self.c.setFillColor(fill);self.c.setStrokeColor(stroke or fill)
  self.c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
 def image(self,path,x,y,w,h):
  im=Image.open(path);iw,ih=im.size;s=min(w/iw,h/ih);dw,dh=iw*s,ih*s
  self.c.drawImage(str(path),x+(w-dw)/2,H-y-dh,dw,dh,mask='auto')
  return dh
 def new(self,kicker,title,subtitle):
  if self.page:self.c.showPage()
  self.page+=1
  self.image(ROOT/'assets/gearotons-logo.png',M,27,116,30)
  self.text('REVIEW DRAFT',W-140,34,8,GREEN,'Helvetica-Bold')
  self.line(M,67,W-M,67)
  self.text(kicker.upper(),M,84,8,GREEN,'Helvetica-Bold')
  self.text(title,M,103,25,DARK,'Helvetica-Bold')
  self.para(subtitle,139,style=SMALL)
  self.line(M,H-44,W-M,H-44)
  self.text(f'RS485 Controller  |  PCB 0.5  |  DS v0.1  |  {DATE}',M,H-33,7,GRAY)
  self.text(f'{self.page:02}',W-M-12,H-33,8,GREEN,'Helvetica-Bold')
 def h2(self,s,y):self.text(s,M,y,13,DARK,'Helvetica-Bold');return y+24
 def table(self,headers,rows,widths,y,x=M):
  head=ParagraphStyle('thead',parent=SMALL,fontName='Helvetica-Bold',textColor=colors.white,fontSize=8.5,leading=12)
  body=ParagraphStyle('cell',parent=STYLE,fontSize=8.7,leading=12.1)
  data=[[Paragraph(str(s),head) for s in headers]]+[[Paragraph(str(s),body) for s in row] for row in rows]
  t=Table(data,colWidths=widths,hAlign='LEFT')
  t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),DARK),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,-1),(-1,-1),.6,RULE)]))
  _,h=t.wrap(sum(widths),H)
  if y+h>H-50:raise ValueError(f'Page {self.page}: table overflow {y+h}')
  t.drawOn(self.c,x,H-y-h);return y+h
 def note(self,title,body,y,h=67):
  self.rect(M,y,CW,h)
  self.text(title,M+13,y+11,10,GREEN,'Helvetica-Bold')
  self.para(body,y+29,x=M+13,w=CW-26,style=SMALL)
 def save(self):self.c.save()

def build(out):
 s=Sheet(out)
 s.new('Programmable motion control','RS485 Controller','ESP32-S3 development board for Gearotons servomotors and other RS485 devices')
 s.text('Affordable and Simple All-in-One Motion Control',M,172,12,GREEN,'Helvetica-Bold')
 s.text('From Education to Innovation',M,192,10,GREEN)
 s.image(REPO/'images/rs485-controller/with-antenna.jpg',M,218,258,225)
 s.image(REPO/'images/rs485-controller/component-side.jpg',M+276,218,233,225)
 s.para('Actual product photographs. External antenna included; cables, power supply and motors are separate system components.',451,style=SMALL)
 for x,val,label in [(M,'11.7 g','Including attached antenna'),(M+173,'230400 baud','RS485 example setting'),(M+346,'PCB 0.5','Hardware covered here')]:
  s.rect(x,489,163,62)
  s.text(val,x+12,501,17,DARK,'Helvetica-Bold');s.text(label,x+12,527,8,GRAY)
 y=s.h2('A compact controller for shared-bus motion',573)
 y=s.para('Run motor-control logic directly on the ESP32-S3. The board combines native USB programming, a half-duplex RS485 interface, a USB-C PD power input and accessible GPIO pads in a compact open PCB.',y)
 y+=16
 for text in ['<b>Embedded control:</b> dual-core LX7 processor, up to 240 MHz; 2.4 GHz Wi-Fi and Bluetooth 5 LE capabilities depend on application firmware.', '<b>Simple wiring:</b> two parallel A/B/GND groups, automatic RS485 direction circuitry, reset and programming buttons.', '<b>Motor-power integration:</b> 20 V USB-C PD request in the standard assembly, with a screw-terminal power output.']:
  y=s.para(text,y)+10
 s.para('For robotics, automation prototypes, teaching and distributed motion systems. This draft describes hardware capabilities; installed firmware determines application behavior.',y+3,style=SMALL)

 s.new('Specifications','Electrical & power','Design values are distinguished from measurements and qualified product limits.')
 y=s.table(['Parameter','Specification / conditions'],[
 ('Processor / module','ESP32-S3-MINI-1U; dual-core Xtensa LX7, up to 240 MHz.'),
 ('Wireless hardware','2.4 GHz Wi-Fi 802.11b/g/n and Bluetooth 5 LE; external antenna included. Wireless control requires suitable firmware.'),
 ('Programming supply, J5','5 V nominal USB input. Native ESP32-S3 USB data connection; motor power is supplied separately.'),
 ('PD power input, J3','Standard design requests 20 V using CH221K and R27 = 200 kΩ. Actual voltage depends on the supply and successful PD negotiation.'),
 ('Motor-power output, J1','Pin 1 = J3 VBUS rail (labelled +20 V); pin 2 = GND. This is a direct pass-through, not a separately regulated 20 V output.'),
 ('Logic / RS485 interface','3.3 V logic; SP3485EN half-duplex differential transceiver. Controller, USB and motor grounds are common; no galvanic isolation.'),
 ('RS485 example setting','230400 baud, 8 data bits, no parity, 1 stop bit. TX = GPIO4; RX = GPIO5. Board maximum baud rate is not specified.'),
 ('Bus loading / protection','R5 = 220 Ω across A/B. R1 = 560 Ω pulls A high; R3 = 560 Ω pulls B low. SM712 transient suppressor on the bus.'),
 ('Auxiliary power pins, J2','3.3 V rail and J5-associated 5 V rail. Available external current is not specified. The 5 V rail is not generated from the PD input.'),
 ],[147,CW-147],177)
 y=s.h2('Power routing',y+24)
 boxw=154
 for x,title,body in [(M,'J5 · PROGRAM','5 V USB + native USB data'),(M+177,'3.3 V logic','Diode-fed buck supply'),(M+354,'J3 → J1','PD rail → motor supply')]:
  s.rect(x,y,boxw,56);s.text(title,x+10,y+10,10,GREEN,'Helvetica-Bold');s.para(body,y+29,x=x+10,w=boxw-20,style=SMALL)
 y+=73
 s.note('Verify motor power before connecting', 'Use a USB-C PD supply that explicitly offers 20 V and a suitable cable. Measure J1 before attaching motors; a non-PD or unsuccessful source may leave the rail at a lower voltage. J5 alone does not provide motor power at J1.',y,76)
 y+=91
 s.para('<b>Not yet specified:</b> board current consumption, continuous motor-power pass-through current, maximum cable length, operating/storage temperature and humidity limits. Component ratings are not board ratings. Product-level ESD/EMC ratings have not been established.',y,style=SMALL)

 s.new('Interfaces','Connectors & controls','Match the printed PCB labels before attaching wires. The two bus groups are electrically parallel.')
 y=s.table(['J2 pin','Signal','Use'],[
 ('1','GND','Common ground'),('2','A','RS485 A'),('3','B','RS485 B'),('4','GND','Common ground; same net as pin 1'),('5','A','Same bus as pin 2'),('6','B','Same bus as pin 3'),('7','3.3 V','Logic supply rail; external load not rated'),('8','5 V','Programming USB supply rail; external load not rated')], [53,64,199],180)
 s.image(REPO/'images/rs485-controller/label-side.jpg',M+332,182,177,216)
 s.para('<b>Label-side orientation</b><br/>USB-C sockets to the left, J2 to the right. Reading J2 from the bottom upward: pins 1 through 8.<br/><br/>Header pitch: 2.54 mm.<br/>Identify pin 1 by the GND label at the end nearest the POWER OUT terminal.',420,x=M+332,w=177,style=SMALL)
 y=s.h2('Power, programming and status',max(y,490)+18)
 y=s.table(['Reference','Function'],[
 ('J1 · POWER OUT','Two-way screw terminal, 5.0 mm pad spacing. Pin 1 is the positive PD rail; pin 2 is GND. Verify polarity on the board.'),
 ('J3 · USB-C PD POWER IN','Power input and PD negotiation. USB data pins are unconnected; this socket does not program the ESP32-S3.'),
 ('J5 · USB-C PROG','Native USB D−/D+ connect to GPIO19/GPIO20. Use a data-capable USB cable for programming.'),
 ('S1 / S2','S1 RESET pulls EN low. S2 PROG pulls GPIO0 low for download mode.'),
 ('D4 / D5 / D6','Yellow: logic power. Green: receive activity. Red: transmit activity. Activity indication depends on traffic.')], [140,CW-140],y)
 s.para('Keep motor supply voltage off J2. The 3.3 V and 5 V pins are not motor-power terminals. Both bus groups and all GND points share the same electrical reference.',y+14,style=SMALL)

 s.new('System wiring','Connect two servomotors','Example: one 20 V-capable USB-C PD source powers the controller and the motors through J1.')
 s.image(ROOT/'assets/two-motor-connection-ai.png',M,172,CW,245)
 s.para('Functional illustration generated with AI and checked against the schematic. Terminal positions are schematic, not physical locations or motor connector pin order. Use the actual PCB labels and motor documentation.',425,style=SMALL)
 y=s.table(['Net','Controller connection','Motor 1 and Motor 2'],[
 ('+20 V · red','J1 pin 1','Each motor V+ / positive supply'),
 ('GND · black','J1 pin 2 and J2 pin 1 or 4','Each motor GND / supply return'),
 ('A · green','J2 pin 2 or 5','A to A, onward along the bus'),
 ('B · blue','J2 pin 3 or 6','B to B, onward along the bus')],[94,181,CW-275],462)
 y+=18
 s.para('<b>1.</b> With power off, connect both motor supply returns and controller GND to a common ground. Provide motor returns sized for motor current; the data-ground lead must not be the only motor-current return.',y)
 y+=47
 s.para('<b>2.</b> Connect A to A and B to B. Route A/B as a twisted pair along one bus, keeping branch leads short. Give each motor a distinct alias before normal addressed motion commands.',y)
 y+=44
 s.para('<b>3.</b> Check polarity and the J1 voltage, then power the system. Secure both motors before running discovery or movement examples. The supply, cable and distribution wiring must support the combined load.',y)
 y+=44
 s.para('The M17 motor reference specifies 12–24 V motor operation. The controller standard PD request is 20 V. R5 already loads A/B with 220 Ω; choose any additional end termination for the complete bus rather than adding resistors at every motor. No fixed motor-count guarantee is specified.',y,style=SMALL)

 s.new('Mechanical integration','Dimensions & expansion','Nominal dimensions derived from the revision 0.5 KiCad board outline. Units: millimetres.')
 s.table(['Item','Design value'],[
 ('Board outline','48.89 × 36.88 mm'),('PCB thickness','1.6 mm nominal'),('Corner cutouts','4 × Ø1.50 mm'),('Hole centre spacing','45.89 × 33.88 mm'),('Hole centre inset','1.50 mm from each adjacent edge'),('Unit mass','11.7 g including attached external antenna'),('Assembled envelope','Height, connector overhang and antenna/cable dimensions not specified')],[112,152],183)
 # Exact nominal board outline: label-side view, USB left and J2 right.
 x0=370;y0=200;k=4.05;bw=36.88*k;bh=48.89*k
 s.rect(x0,y0,bw,bh,fill=LIGHT,r=1.5*k,stroke=GREEN)
 for hx in [1.5,35.38]:
  for hy in [1.5,47.39]:
   s.c.setStrokeColor(GREEN);s.c.setFillColor(colors.white);s.c.circle(x0+hx*k,H-(y0+hy*k),.75*k,fill=1,stroke=1)
 for yy in [7.545,31.025]:s.rect(x0-8,y0+yy*k-11,13,22,fill=colors.HexColor('#dce4e1'),r=2)
 for i in range(8):s.line(x0+bw,y0+(27.115+i*2.54)*k,x0+bw+10,y0+(27.115+i*2.54)*k,GREEN,1.6)
 s.para('Label side<br/>Not to scale',y0+83,x=x0+25,w=bw-50,style=SMALL)
 # Horizontal dimension.
 s.line(x0,y0-19,x0+bw,y0-19,GRAY);s.line(x0,y0-24,x0,y0-5,GRAY);s.line(x0+bw,y0-24,x0+bw,y0-5,GRAY)
 s.text('36.88',x0+bw/2-16,y0-35,9,GREEN,'Helvetica-Bold')
 s.line(x0-28,y0,x0-28,y0+bh,GRAY);s.line(x0-33,y0,x0-8,y0,GRAY);s.line(x0-33,y0+bh,x0-8,y0+bh,GRAY)
 s.c.saveState();s.c.translate(x0-35,H-(y0+bh/2+16));s.c.rotate(90);s.c.setFont('Helvetica-Bold',9);s.c.setFillColor(GREEN);s.c.drawString(0,0,'48.89');s.c.restoreState()
 s.para('Outline excludes connectors and antenna. Hole dimensions are design values, not measured tolerances. The Ø1.5 mm corner cutouts are not M2/M3 clearance holes.',445,style=SMALL)
 y=s.h2('GPIO access',495)
 y=s.table(['Connection','Notes'],[
 ('Expansion pads','Unpopulated GPIO pads expose ESP32-S3 signals. Use 3.3 V logic and verify each function against the schematic before connecting external circuits.'),
 ('GPIO4 / GPIO5','Reserved by the onboard RS485 transmit / receive path in the supplied demos.'),
 ('GPIO19 / GPIO20','Used by the native USB D− / D+ connection. Avoid external loads while using USB.'),
 ('GPIO0 / 3 / 45 / 46','ESP32-S3 strapping pins. External circuitry can affect startup; GPIO0 is also connected to PROG.'),
 ('External antenna','Attach the included antenna before using the radio. Allow clearance around the antenna and protect its small coaxial connector from cable strain.')],[142,CW-142],y)
 s.para('Mount the PCB with clearance around underside components and connector solder joints. The open board has no specified ingress-protection rating. Use the KiCad geometry for enclosure design and confirm the assembled envelope on a physical unit.',y+15,style=SMALL)

 s.new('Bring-up & resources','Getting started','Program the ESP32-S3, establish communication, then enable motion deliberately.')
 y=s.h2('Initial setup',180)
 steps=[('Check the wiring','Connect the external antenna. With power off, check motor polarity and the A/B/GND connections on page 4.'),('Connect the programming port','Use J5 USB-C PROG with a data cable. J3 is the separate PD power socket.'),('Install the software','Use the Arduino ESP32 core and Gearotons Servomotor library. Select an ESP32-S3 target and configure native USB as appropriate for the board package.'),('Enter download mode if needed','Hold S2 PROG, press and release S1 RESET, then release PROG. Select the detected USB device and upload the application.'),('Apply and verify motor power','Use a suitable 20 V-capable PD source at J3. Verify J1 voltage first, then connect and power the motors. Match aliases and check discovery responses before enabling motion.')]
 for i,(title,body) in enumerate(steps,1):
  s.rect(M,y,23,23,fill=GREEN,r=5);s.text(str(i),M+8,y+5,10,colors.white,'Helvetica-Bold')
  s.para(f'<b>{title}.</b> {body}',y,x=M+35,w=CW-35)
  y+=47
 y=s.h2('UART configuration',y+8)
 s.rect(M,y,CW,76,fill=colors.HexColor('#173a33'))
 for i,line in enumerate(['#include <Arduino.h>','void setup() {','  Serial1.begin(230400, SERIAL_8N1, 5, 4); // RX, TX','}','void loop() {}']):s.text(line,M+13,y+10+i*12,8.6,colors.white,'Courier')
 y+=90
 y=s.para('This minimal snippet configures the RS485 UART and sends no motion commands. The repository contains separate motor-control, three-pass autodetection and ball-juggling examples. Build one program at a time; those examples can move motors.',y)+21
 y=s.h2('Documentation & design files',y)
 y=s.para('<b>Controller source:</b> <link href="https://github.com/tomrodinger/RS485_Controller" color="#08765b">github.com/tomrodinger/RS485_Controller</link><br/><b>Motor setup and protocol:</b> <link href="https://tutorial.gearotons.com" color="#08765b">tutorial.gearotons.com</link><br/><b>Feedback:</b> <link href="https://tutorial.gearotons.com/feedback" color="#08765b">tutorial.gearotons.com/feedback</link>',y)+16
 y=s.para('<b>Specification basis.</b> Revision 0.5 schematic, PCB and assembly BOM; supplied firmware examples; owner-provided mass and antenna statement; Gearotons M17 English datasheet v1.10. Manufacturer references: <link href="https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.html" color="#08765b">Espressif module datasheet</link>, <link href="https://www.maxlinear.com/ds/sp3485.pdf" color="#08765b">MaxLinear SP3485</link>, <link href="https://www.ti.com/product/TPS54202" color="#08765b">TI TPS54202</link>, and WCH CH221K configuration table in the repository CH224K.pdf.',y,style=SMALL)+12
 s.para('<b>Review status.</b> DS v0.1, 26 October 2026. Pending owner review before publication. Values marked “not specified” require product-level confirmation; neither the drawings nor component data establish qualified board limits. Hardware/software source is supplied under the repository MIT licence.',y,style=SMALL)
 s.save()

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'rs485_controller_datasheet_v0.1_review.pdf');args=ap.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True);build(args.output);print(args.output)
