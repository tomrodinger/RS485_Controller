#!/usr/bin/env python3
"""Retain the selected natural composition, add signal labels and computer USB."""
from pathlib import Path
import importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('natural_art',ROOT/'diagram-review/round2/build_round2.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
OUT=ROOT/'datasheet/assets/connection-v0.4';OUT.mkdir(exist_ok=True)
m.HERE=OUT;m.BOARD_SVG=ROOT/'datasheet/assets/technical-v4/board-component-base.svg'

class Plate(m.Plate):
    def text(self,x,y,text,*args,**kwargs):
        replacements={
            'J2 pins 2 / 3 share one paired housing':'A / B share one paired housing on J2',
            'Controller · PCB 0.5 geometry':'Controller · component side (B.Cu)',
        }
        return super().text(x,y,replacements.get(text,text),*args,**kwargs)
    def finish(self,slug):
        # Small laptop illustration; the USB data lead terminates at J5, never J3.
        self.text(650,1430,'Computer',34,'ink',700,'middle')
        self.rect(400,1470,475,255,'#344b45','#173a33',18,4)
        self.rect(420,1488,435,215,'#e8f2ed',r=6)
        self.rect(420,1488,435,29,'#d0e1d7',r=6)
        for i in range(3):self.circle(438+i*16,1503,4,['#bf6d68','#c5a34b','#6d9f7b'][i])
        self.text(455,1555,'Arduino IDE',29,'ink',600)
        for x,y,w in [(455,1581,310),(455,1609,230),(477,1637,280),(477,1665,190)]:self.rect(x,y,w,7,'#89aa9a',r=3)
        self.add('<path d="M 400 1725 L 875 1725 L 945 1774 Q 950 1786 930 1786 L 345 1786 Q 325 1786 335 1774 Z" fill="#ccd8d1" stroke="#6a8575" stroke-width="3"/>')
        self.rect(578,1732,120,24,'#a5b7ab',r=5)
        self.rect(340,1741,35,11,'#223d34',r=3)
        self.endpoint('Computer.USB',340,1747)
        jx,jy=self.anchors['J5.USB'];usb=[self.anchors['J5.USB'],[230,jy],[230,1747],self.anchors['Computer.USB']]
        self.line(usb,'#7765ad',14)
        self.text(650,1820,'USB data → J5 PROG',29,'#67549d',600,'middle')
        # Distinct plug at the programming socket mouth; PD cable remains at J3.
        self.rect(jx-30,jy-13,29,26,'#c4bdde','#67549d',5,2)
        slug='two-motor-connection-v0.4'
        super().finish(slug)
        p=OUT/(slug+'.routes.json');data=json.loads(p.read_text())
        data['usb_connections']=[{'from':'J5.USB','to':'Computer.USB','type':'native_usb_data_and_programming','points':usb,'stroke':'#7765ad','width':14}]
        data['j2_function_labels']=['GND','A','B','GND','A','B','3.3V','5V']
        data['source_style']='Owner-selected r2-05-natural-pigtails; retained natural artwork and circuit routes.'
        p.write_text(json.dumps(data,indent=2)+'\n')
        subprocess.run(['rsvg-convert','-f','pdf','-o',str(OUT/(slug+'.pdf')),str(OUT/(slug+'.svg'))],check=True)

if __name__=='__main__':
    m.Plate=Plate;m.wide_reference(photo=False,editorial=False,natural=True)
