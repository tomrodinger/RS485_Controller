#!/usr/bin/env python3
"""Build the PCB 0.5 review datasheet v0.4 without modifying the v0.1 edition.

Technical PDF assets are composed as vector Form XObjects after ReportLab lays
out the pages. Examples are immutable snapshots of the latest English M17 PDF.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import argparse
import hashlib
import json
import os
import tempfile

os.environ['SOURCE_DATE_EPOCH'] = '1793664000'
import fitz
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
M = 43
GREEN = colors.HexColor('#08765b')
DARK = colors.HexColor('#153a32')
INK = colors.HexColor('#203c39')
GRAY = colors.HexColor('#586c69')
LIGHT = colors.HexColor('#eef6f3')
RULE = colors.HexColor('#d5e4df')
DATE = '3 November 2026'
VERSION = '0.4'
ESPRESSIF_URL = 'https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf'
STYLE = ParagraphStyle('body', fontName='Helvetica', fontSize=9.7, leading=14.6, textColor=INK)
SMALL = ParagraphStyle('small', parent=STYLE, fontSize=8.2, leading=11.8, textColor=GRAY)
SCHEMATIC = REPO / 'PCB/0.5/schematic/0.5-index-schTop.pdf'
FIGURES = {
    'locator': 'connector-locator.pdf',
    'mechanical': 'mechanical-dimensions.pdf',
    'gpio-overview': 'gpio-overview.pdf',
    'gpio-detail': 'gpio-detail.pdf',
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Sheet:
    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
        self.c.setTitle(f'Gearotons RS485 Controller — PCB 0.5 — Review datasheet v{VERSION}')
        self.c.setAuthor('Gearotons')
        self.c.setSubject('Power, connector locations, GPIO pad maps, mechanical dimensions, canonical software examples and controller schematic')
        self.page = 0
        self.w, self.h = A4
        self.figures = []
        self.sections = []
        self.placeholders = []

    @property
    def cw(self):
        return self.w - 2 * M

    def text(self, value, x, y, size=10, color=INK, font='Helvetica'):
        self.c.setFillColor(color)
        self.c.setFont(font, size)
        self.c.drawString(x, self.h - y - size * .85, value)

    def para(self, value, y, x=M, w=None, style=STYLE):
        p = Paragraph(value, style)
        _, height = p.wrap(self.cw if w is None else w, self.h)
        if y + height > self.h - 55:
            raise ValueError(f'Page {self.page} paragraph overflow: {y + height:.1f}: {value[:70]}')
        p.drawOn(self.c, x, self.h - y - height)
        return y + height

    def line(self, x1, y1, x2, y2, color=RULE, width=.7):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(x1, self.h - y1, x2, self.h - y2)

    def rect(self, x, y, width, height, fill=LIGHT, radius=6, stroke=None):
        self.c.setFillColor(fill)
        self.c.setStrokeColor(stroke or fill)
        self.c.roundRect(x, self.h - y - height, width, height, radius, fill=1, stroke=bool(stroke))

    def image(self, path, x, y, width, height):
        with Image.open(path) as image:
            iw, ih = image.size
        scale = min(width / iw, height / ih)
        dw, dh = iw * scale, ih * scale
        self.c.drawImage(str(path), x + (width - dw) / 2, self.h - y - dh, dw, dh, mask='auto')
        return dh

    def new(self, kicker, title, subtitle, size=A4, compact=False):
        if self.page:
            self.c.showPage()
        self.w, self.h = size
        self.c.setPageSize(size)
        self.page += 1
        self.sections.append({'page': self.page, 'title': title, 'size_points': list(size)})
        if compact:
            self.image(ROOT / 'assets/gearotons-logo.png', M, 18, 95, 25)
            self.text(title, M + 122, 23, 17, DARK, 'Helvetica-Bold')
            self.text('REVIEW DRAFT', self.w - 140, 26, 8, GREEN, 'Helvetica-Bold')
            self.line(M, 53, self.w - M, 53)
            self.para(subtitle, 64, style=SMALL)
        else:
            self.image(ROOT / 'assets/gearotons-logo.png', M, 27, 116, 30)
            self.text('REVIEW DRAFT', self.w - 140, 34, 8, GREEN, 'Helvetica-Bold')
            self.line(M, 67, self.w - M, 67)
            self.text(kicker.upper(), M, 84, 8, GREEN, 'Helvetica-Bold')
            self.text(title, M, 103, 25, DARK, 'Helvetica-Bold')
            self.para(subtitle, 139, style=SMALL)
        self.line(M, self.h - 44, self.w - M, self.h - 44)
        self.text(f'RS485 Controller  |  PCB 0.5  |  DS v{VERSION}  |  {DATE}', M, self.h - 33, 7, GRAY)
        self.text(f'{self.page:02}', self.w - M - 12, self.h - 33, 8, GREEN, 'Helvetica-Bold')

    def h2(self, value, y):
        self.text(value, M, y, 13, DARK, 'Helvetica-Bold')
        return y + 24

    def table(self, headers, rows, widths, y, x=M, font_size=9, padding=8):
        head = ParagraphStyle('thead', parent=SMALL, fontName='Helvetica-Bold', textColor=colors.white, fontSize=8.5, leading=12)
        body = ParagraphStyle('cell', parent=STYLE, fontSize=font_size, leading=font_size * 1.4)
        data = [[Paragraph(str(cell), head) for cell in headers]] + [[Paragraph(str(cell), body) for cell in row] for row in rows]
        table = Table(data, colWidths=widths, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DARK),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
            ('LINEBELOW', (0, -1), (-1, -1), .6, RULE),
        ]))
        _, height = table.wrap(sum(widths), self.h)
        if y + height > self.h - 55:
            raise ValueError(f'Page {self.page} table overflow: {y + height:.1f}')
        table.drawOn(self.c, x, self.h - y - height)
        return y + height

    def note(self, title, body, y):
        p = Paragraph(body, SMALL)
        _, height = p.wrap(self.cw - 26, self.h)
        total = height + 46
        if y + total > self.h - 55:
            raise ValueError(f'Page {self.page} note overflow: {y + total:.1f}')
        self.rect(M, y, self.cw, total)
        self.text(title, M + 13, y + 11, 10, GREEN, 'Helvetica-Bold')
        p.drawOn(self.c, M + 13, self.h - y - 31 - height)
        return y + total

    def vector(self, path, y, height, allow_missing=False):
        path = Path(path)
        if not path.exists():
            if not allow_missing:
                raise FileNotFoundError(f'Required technical asset is missing: {path}')
            self.rect(M, y, self.cw, height, stroke=RULE)
            self.para(f'<b>INTERIM LAYOUT ONLY — VERIFIED FIGURE PENDING</b><br/>{escape(path.name)}', y + 32, x=M + 24, w=self.cw - 48)
            self.placeholders.append(str(path))
        elif path.suffix.lower() == '.pdf':
            with fitz.open(path) as source:
                if len(source) != 1:
                    raise ValueError(f'Technical figures must be single-page PDFs; supply additional detail pages separately: {path}')
            self.figures.append({'page': self.page - 1, 'path': path, 'rect': [M, y, self.w - M, y + height]})
        else:
            self.image(path, M, y, self.cw, height)
        return y + height

    def code(self, path, y, font_size=8.1, leading=10.6):
        text = Path(path).read_text()
        lines = text.rstrip('\n').split('\n')
        widest = max(stringWidth(line, 'Courier', font_size) for line in lines)
        if widest > self.cw - 26:
            raise ValueError(f'Code line is wider than page: {path}, {widest:.2f} > {self.cw - 26:.2f}')
        height = 24 + leading * len(lines)
        if y + height > self.h - 55:
            raise ValueError(f'Code block overflow: {path}')
        self.rect(M, y, self.cw, height, fill=colors.HexColor('#f1f5f3'), stroke=RULE)
        for i, line in enumerate(lines):
            self.text(line, M + 13, y + 12 + i * leading, font_size, INK, 'Courier')
        return y + height

    def save(self):
        self.c.save()


def validate_examples():
    provenance = json.loads((ROOT / 'review/example-provenance-v0.2.json').read_text())
    provenance['examples'] = [entry for entry in provenance['examples'] if entry['language'] == 'Arduino']
    for example in provenance['examples']:
        path = REPO / example['snapshot']
        if sha256(path) != example['sha256']:
            raise ValueError(f'Canonical code snapshot changed: {path}')
        if not example['matches_pdf_ignoring_layout_whitespace']:
            raise ValueError('Canonical PDF/source correspondence was not verified.')
    return provenance


def compose_vectors(layout, output, figures, sections):
    document = fitz.open(layout)
    for figure in figures:
        with fitz.open(figure['path']) as source:
            document[figure['page']].show_pdf_page(fitz.Rect(figure['rect']), source, 0, keep_proportion=True, overlay=True)
    document.set_metadata({**document.metadata, 'title': f'Gearotons RS485 Controller — PCB 0.5 — Review datasheet v{VERSION}', 'author': 'Gearotons'})
    document.set_toc([[1, section['title'], section['page']] for section in sections])
    document.save(output, garbage=4, deflate=True, no_new_id=True)
    document.close()


def build(output, technical_dir, allow_missing=False, connection_illustration=None):
    provenance = validate_examples()
    if connection_illustration and sha256(connection_illustration) == '8ebcae4624b29a2fcdbbd408a0a26a6627be6a1d25f8c829b9c6b11a98c39df7':
        raise ValueError('The v0.1 AI connection image is excluded from v0.4.')
    assets = {key: technical_dir / name for key, name in FIGURES.items()}
    figure_manifest = technical_dir / 'figures.json'
    if figure_manifest.exists():
        for key, filename in json.loads(figure_manifest.read_text()).items():
            if key in assets:
                assets[key] = technical_dir / filename
    with tempfile.TemporaryDirectory(prefix='controller-v02-') as temp:
        layout = Path(temp) / 'layout.pdf'
        s = Sheet(layout)
        cw = s.cw

        s.new('Programmable motion control', 'RS485 Controller', 'ESP32-S3 development board for Gearotons servomotors and other RS485 devices')
        s.text('Affordable and Simple All-in-One Motion Control', M, 172, 12, GREEN, 'Helvetica-Bold')
        s.text('From Education to Innovation', M, 193, 10, GREEN)
        s.image(REPO / 'images/rs485-controller/with-antenna.jpg', M, 220, 258, 225)
        s.image(REPO / 'images/rs485-controller/component-side.jpg', M + 276, 220, 233, 225)
        s.para('Actual product photographs. External antenna included; cables, power supply and motors are separate system components.', 454, style=SMALL)
        for x, value, label in [(M, '11.7 g', 'Including attached antenna'), (M + 173, '230400 baud', 'Canonical example setting'), (M + 346, 'PCB 0.5', 'Hardware covered here')]:
            s.rect(x, 493, 163, 62)
            s.text(value, x + 12, 505, 17, DARK, 'Helvetica-Bold')
            s.text(label, x + 12, 531, 8, GRAY)
        y = s.h2('A compact controller for shared-bus motion', 579)
        y = s.para('Run motor-control logic directly on the ESP32-S3. The board combines native USB programming, a half-duplex RS485 interface, a USB-C PD power input and accessible GPIO pads in a compact open PCB.', y) + 15
        for text in [
            '<b>Embedded control:</b> dual-core LX7 processor, up to 240 MHz; 2.4 GHz Wi-Fi and Bluetooth 5 LE capabilities depend on application firmware.',
            '<b>Simple wiring:</b> two parallel A/B/GND groups, automatic RS485 direction circuitry, reset and programming buttons.',
            '<b>Motor-power integration:</b> standard assembly requests 20 V USB-C PD, with a direct motor-power output at the screw terminal.',
        ]:
            y = s.para(text, y) + 10

        s.new('Specifications', 'Electrical & power', 'Design values are distinguished from measurements and qualified product limits.')
        y = s.table(['Parameter', 'Specification / conditions'], [
            ('Processor / module', 'ESP32-S3-MINI-1U; dual-core Xtensa LX7, up to 240 MHz.'),
            ('Wireless hardware', '2.4 GHz Wi-Fi 802.11b/g/n and Bluetooth 5 LE; external antenna included. Wireless control requires suitable firmware.'),
            ('Programming supply, J5', '5 V nominal USB input. Native ESP32-S3 USB data connection; motor power is supplied separately.'),
            ('PD power input, J3', 'Standard design requests 20 V using CH221K and R27 = 200 kΩ. Actual voltage depends on the source and successful PD negotiation.'),
            ('Motor-power output, J1', 'Pin 1 = J3 VBUS rail (labelled +20 V); pin 2 = GND. Direct pass-through, not a separately regulated 20 V output.'),
            ('Logic / RS485 interface', '3.3 V logic; SP3485EN half-duplex differential transceiver. Controller, USB and motor grounds are common; no galvanic isolation.'),
            ('RS485 example setting', '230400 baud, 8 data bits, no parity, 1 stop bit. TX = GPIO4; RX = GPIO5. Board maximum baud rate is not specified.'),
            ('Bus loading / protection', 'R5 = 220 Ω across A/B. R1 = 560 Ω pulls A high; R3 = 560 Ω pulls B low. SM712 transient suppressor on the bus.'),
            ('Auxiliary power pins, J2', '3.3 V rail and J5-associated 5 V rail. Available external current is not specified. The 5 V rail is not generated from the PD input.'),
        ], [147, cw - 147], 177)
        y = s.note('Verify motor power before connecting', 'Use a USB-C PD supply that explicitly offers 20 V and a suitable cable. Measure J1 before attaching motors; a non-PD or unsuccessful source may leave the rail at a lower voltage. J5 alone does not provide motor power at J1.', y + 20)
        s.para('<b>Not yet specified:</b> board current consumption, continuous motor-power pass-through current, maximum cable length and environmental limits. Component ratings are not board ratings; product-level ESD/EMC ratings have not been established.', y + 16, style=SMALL)

        s.new('Interfaces · physical locator', 'Power, programming & status', 'Locate connectors, switches and indicator LEDs before connecting or programming the controller.')
        y = s.vector(assets['locator'], 175, 455, allow_missing)
        y = s.para('Component-side view (B.Cu). Curved dashed leaders identify the connectors, switches, LEDs and U7 antenna socket. The eight J2 contacts are labelled by signal. Attach the included antenna before using the radio; the electrical reference follows.', y + 12, style=SMALL)
        s.note('Separate the two USB-C functions', '<b>J3:</b> USB-C PD motor-power input. <b>J5:</b> native USB programming and 5 V logic power. The J3 USB data pins are unconnected. USB-C connector shape does not indicate which function it provides.', y + 18)

        s.new('Interfaces · electrical reference', 'Connector pinout & controls', 'The two RS485 groups on J2 are electrically parallel; all grounds share one reference.')
        y = s.table(['J2 pin', 'Signal', 'Use'], [
            ('1', 'GND', 'Common ground'), ('2', 'A', 'RS485 A'), ('3', 'B', 'RS485 B'),
            ('4', 'GND', 'Same net as pin 1'), ('5', 'A', 'Same bus as pin 2'), ('6', 'B', 'Same bus as pin 3'),
            ('7', '3.3 V', 'Logic supply rail; external load not rated'), ('8', '5 V', 'Programming USB supply rail; external load not rated'),
        ], [58, 74, cw - 132], 177)
        y = s.h2('Power, programming, switches and indicators', y + 22)
        y = s.table(['Reference', 'Function'], [
            ('J1 · POWER OUT', 'Two-way screw terminal. Pin 1 is the positive PD rail; pin 2 is GND. Verify polarity on the board.'),
            ('J3 · PD POWER IN', 'USB-C power input and PD negotiation. This socket does not program the ESP32-S3.'),
            ('J5 · USB-C PROG', 'Native USB D−/D+ connect to GPIO19/GPIO20. Use a data-capable USB cable.'),
            ('S1 · RESET', 'Pulls the module EN signal low to reset the controller.'),
            ('S2 · PROG', 'Pulls GPIO0 low; hold during reset to enter ROM download mode.'),
            ('D4 · yellow LED', 'Logic-power indication.'),
            ('D5 · green LED', 'Receive activity; indication depends on bus traffic.'),
            ('D6 · red LED', 'Transmit activity; indication depends on bus traffic.'),
        ], [128, cw - 128], y, font_size=8.6)
        s.para('Keep motor supply voltage off J2. Its 3.3 V and 5 V pins are auxiliary logic rails, not motor-power terminals. Refer to the physical locator and actual PCB labels for orientation.', y + 14, style=SMALL)

        if connection_illustration:
            s.new('System wiring · selected illustration', 'Two-motor connection diagram',
                  'Natural illustration · computer USB to J5 PROG, PD supply to J3 · electrical reference follows.',
                  size=landscape(A3), compact=True)
            s.vector(connection_illustration, 88, s.h - 165, False)
            s.para('Computer: J5 USB-C PROG. Motor-power supply: J3 PD POWER IN. Connector mating faces are not shown; match actual labels.', s.h - 70, style=SMALL)
        s.new('System wiring', 'Connect two servomotors', 'One 20 V-capable USB-C PD source can feed J3 and supply the motors through J1.')
        y = 177
        y = s.para('Use the following net-by-net connections for both motors. Connect the data bus along one route and distribute motor supply/return wiring for the combined motor current.', y) + 20
        y = s.table(['Net', 'Controller connection', 'Motor 1 and Motor 2'], [
            ('+20 V', 'J1 pin 1', 'Each motor V+ / positive supply'),
            ('GND', 'J1 pin 2 and J2 pin 1 or 4', 'Each motor GND / supply return'),
            ('A', 'J2 pin 2 or 5', 'A to A, onward along the bus'),
            ('B', 'J2 pin 3 or 6', 'B to B, onward along the bus'),
        ], [70, 183, cw - 253], y)
        steps = [
            ('Check power while disconnected', 'With motors disconnected, connect a 20 V-capable PD source to J3 and measure J1. Check polarity, then turn the source off before wiring the motors.'),
            ('Wire the common ground and motor supply', 'Connect both motor supply returns and controller GND. Motor returns must be sized for motor current; the data-ground lead must not be the only motor-current return.'),
            ('Connect the differential bus', 'Connect A to A and B to B. Route A/B as a twisted pair along one bus, keeping branches short. Give each motor a distinct alias before addressed motion commands.'),
            ('Power and test deliberately', 'Secure both motors before discovery or movement examples. The power supply, cable and distribution wiring must support the combined load.'),
        ]
        y += 22
        for number, (title, body) in enumerate(steps, 1):
            y = s.para(f'<b>{number}. {title}.</b> {body}', y) + 14
        s.para('The M17 motor reference specifies 12–24 V operation; the controller standard PD request is 20 V. R5 already loads A/B with 220 Ω. Select additional end termination for the complete bus instead of adding resistors at every motor. No fixed motor-count guarantee is specified.', y, style=SMALL)

        s.new('Mechanical integration', 'Detailed PCB dimensions', 'Nominal revision 0.5 KiCad geometry. Dimensions are in millimetres and exclude connector overhang and antenna.')
        y = s.vector(assets['mechanical'], 176, 470, allow_missing)
        y = s.para('Use the dimensioned drawing for board outline, corner radius, mounting-hole diameter, hole-centre spacing and edge insets. These are design values without manufacturing tolerances; confirm enclosure clearances on a physical unit.', y + 12, style=SMALL)
        s.note('Mounting and assembled envelope', 'PCB thickness is 1.6 mm nominal. Keep clearance around underside components and connector solder joints. Overall assembled height and antenna/cable envelope are not specified. The Ø1.50 mm holes are not M2 or M3 clearance holes.', y + 18)

        s.new('GPIO access · unpopulated through holes', 'Breakout headers — solder required',
              'Rear / label-side view (F.Cu). Breakout headers are not fitted; solder headers or wires to the required through-hole pads.',
              size=A3, compact=True)
        y = s.vector(assets['gpio-overview'], 95, s.h - 285, allow_missing)
        y = s.para('<b>Every pad is labelled by signal at its physical location.</b> Green: GPIO. Gray: GND. Amber: PD-control points. Blue labels: surface service pads. Dashed socket and module outlines locate components fitted on the opposite face.', y + 12, style=SMALL) + 12
        y = s.para('<b>Shared functions:</b> GPIO4 / TX and GPIO5 / RX are connected to onboard RS485. GPIO43 / TX0 and GPIO44 / RX0 are UART0. GPIO0/3/45/46 are module strapping signals; GPIO0 is connected to PROG. Use 3.3 V logic and avoid disturbing boot, USB or RS485.', y, style=SMALL) + 12
        y = s.para('<b>PD CFG, PD VDD and PD PG are not GPIO.</b> The gold rectangular service pads are surface pads, not through holes. Breakout holes are unpopulated; the fitted J2 RS485 header is separate and appears on the component-side locator.', y, style=SMALL) + 12
        s.para(f'<b>Module reference:</b> <link href="{ESPRESSIF_URL}" color="#08765b"><u>Official Espressif ESP32-S3-MINI-1 / MINI-1U datasheet (PDF)</u></link>. Zoom in on this vector drawing to inspect individual labels.', y, style=SMALL)

        s.new('Bring-up', 'Getting started', 'Prepare the hardware and software, establish communication, then enable motion deliberately.')
        y = 180
        steps = [
            ('Prepare the hardware', 'Attach the included external antenna. With power off, check the motor polarity and A/B/GND connections. Secure the mechanism before running any movement example.'),
            ('Use the programming port', 'Connect J5 USB-C PROG with a data-capable cable. J3 is the separate USB-C PD power input, not a programming port.'),
            ('Install Arduino support', 'Install the Arduino ESP32 board package and “Servomotor by Gearotons” from Library Manager. Select an ESP32-S3 target; configure native USB CDC for the USB serial console as appropriate for the board package.'),
            ('Enter download mode if needed', 'Hold S2 PROG, press and release S1 RESET, then release PROG. Select the detected USB device and upload the application.'),
            ('Verify motor power and identity', 'Check J1 voltage before connecting motors. Use the correct motor alias and ensure the mechanism can safely perform one full rotation before running the Arduino example.'),
        ]
        for number, (title, body) in enumerate(steps, 1):
            s.rect(M, y, 24, 24, fill=GREEN, radius=5)
            s.text(str(number), M + 8, y + 5, 10, colors.white, 'Helvetica-Bold')
            y = s.para(f'<b>{title}.</b> {body}', y, x=M + 36, w=cw - 36) + 20
        y = s.h2('Arduino example for the controller', y + 2)
        y = s.para('The following installation guide uses the Arduino IDE instructions and screenshot from the M17 servomotor datasheet. The Arduino basic motor-control program is retained unchanged from M17 datasheet v1.10; setup notes remain outside the code.', y) + 18
        s.note('The example commands motor motion', 'The program enables the motor drive, requests one shaft rotation in one second, then disables the drive. Match the motor alias and serial connection to the intended motor, and secure the mechanism before running it.', y)

        s.new('Getting started · Arduino IDE', 'Install the Arduino library', 'Arduino Library Manager instructions and original screenshot from the M17 servomotor datasheet.')
        y = s.para('Install the library through the Arduino Library Manager:', 177) + 12
        for step in [
            '1. Open Arduino IDE',
            '2. Go to Sketch → Include Library → Manage Libraries',
            '3. Search for "Servomotor"',
            '4. Find the library called "Servomotor by Gearotons" and click Install',
        ]:
            y = s.para(escape(step), y) + 8
        y += 5
        height = s.image(ROOT / 'assets/arduino-install-v0.3/arduino_library_installation.png', M, y, cw, 430)
        s.para('Original M17 screenshot; Tools → Manage Libraries is the route shown. Choose the Gearotons library and the latest version. The pictured ESP32C3 target is illustrative; select the ESP32-S3 target for this controller.', y + height + 10, style=SMALL)

        s.new('Getting started · canonical Arduino', 'Arduino: basic motor control', 'Verbatim program from the English M17 servomotor datasheet, v1.10 · reference PDF page 13.')
        y = s.para('Install “Servomotor by Gearotons” using Arduino Library Manager. The unchanged ESP32 pin definitions in this reference are GPIO4 TX and GPIO5 RX.', 176, style=SMALL) + 14
        y = s.code(ROOT / 'assets/examples-v0.2/arduino_library_example.cpp', y, font_size=8.1, leading=10.35)
        s.para('This is the program printed in M17 datasheet v1.10, not a newer working-tree variant. Source snapshot and PDF correspondence are recorded in the accompanying example-provenance JSON.', y + 15, style=SMALL)

        s.new('Design reference', 'Controller schematic & resources', 'The appendix reproduces the full controller sheet with ESP32-S3-MINI-1U retained as one module block.')
        y = s.h2('Full controller schematic', 181)
        y = s.para('The following landscape appendix embeds the supplied revision 0.5 controller schematic as vector content. It includes the board power, PD negotiation, native USB, RS485, controls and indicator circuitry. Zoom in to read component values without a raster-image resolution limit.', y) + 18
        y = s.para('Source sheet: <font name="Courier">PCB/0.5/schematic/0.5-index-schTop.pdf</font>. The module symbol and its external connections remain intact; no ESP32 module-internal schematic has been added.', y) + 23
        y = s.h2('Official module documentation', y)
        y = s.para(f'<link href="{ESPRESSIF_URL}" color="#08765b"><u>Espressif ESP32-S3-MINI-1 / ESP32-S3-MINI-1U datasheet</u></link><br/>Manufacturer reference for the module pin definitions, boot configuration, radio, electrical specifications and module mechanical details.', y) + 24
        y = s.h2('Software, tutorials and design files', y)
        y = s.para('<b>Controller source:</b> <link href="https://github.com/tomrodinger/RS485_Controller" color="#08765b"><u>github.com/tomrodinger/RS485_Controller</u></link><br/><b>Motor setup and protocol:</b> <link href="https://tutorial.gearotons.com" color="#08765b"><u>tutorial.gearotons.com</u></link><br/><b>Arduino library:</b> <link href="https://github.com/tomrodinger/Servomotor_Arduino_Library" color="#08765b"><u>github.com/tomrodinger/Servomotor_Arduino_Library</u></link><br/><b>Feedback:</b> <link href="https://tutorial.gearotons.com/feedback" color="#08765b"><u>tutorial.gearotons.com/feedback</u></link>', y) + 24
        y = s.h2('Specification and review basis', y)
        y = s.para('PCB 0.5 schematic, board geometry and assembly BOM; supplied firmware examples; owner-provided 11.7 g mass and included-antenna statement; M17 English datasheet v1.10 (Arduino program) and its Arduino IDE installation guide; official Espressif, MaxLinear and TI component references. No component current, environmental or ESD rating has been promoted to a board-level guarantee.', y) + 16
        s.note('DS v0.4 · owner review draft', 'Prepared 3 November 2026. Physical product measurements and limits remain subject to confirmation where marked not specified. Hardware/software source is supplied under the repository MIT licence. Earlier review PDFs are preserved separately.', y)

        s.new('Appendix · vector source sheet', 'Full controller schematic', 'PCB 0.5 · module retained as a black box · A3 landscape appendix for comfortable digital zoom and larger-format printing.', size=landscape(A3), compact=True)
        s.vector(SCHEMATIC, 88, s.h - 143, False)
        s.save()
        compose_vectors(layout, output, s.figures, s.sections)

    result = {
        'version': VERSION, 'date': DATE, 'output': str(output), 'sha256': sha256(output),
        'pages': s.sections, 'vector_figures': [{'page': item['page'] + 1, 'path': str(item['path']), 'sha256': sha256(item['path'])} for item in s.figures],
        'interim_placeholders': s.placeholders, 'connection_illustration': str(connection_illustration) if connection_illustration else None,
        'connection_illustration_sha256': sha256(connection_illustration) if connection_illustration else None,
        'arduino_installation_image_sha256': sha256(ROOT / 'assets/arduino-install-v0.3/arduino_library_installation.png'),
        'python_example_included': False,
        'excluded_prior_ai_image': 'datasheet/assets/two-motor-connection-ai.png',
        'canonical_example_sha256': {entry['language']: entry['sha256'] for entry in provenance['examples']},
        'espressif_datasheet_link': ESPRESSIF_URL,
        'schematic_source_sha256': sha256(SCHEMATIC),
        'preserved_v0.1_sha256': sha256(ROOT / 'rs485_controller_datasheet_v0.1_review.pdf'),
        'technical_geometry_sha256': sha256(technical_dir / 'pcb-geometry.json') if (technical_dir / 'pcb-geometry.json').exists() else None,
        'breakout_label_manifest_sha256': sha256(technical_dir / 'breakout-labels.json'),
        'breakout_detail_pages_removed': True,
    }
    (ROOT / 'review/build-v0.4.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'rs485_controller_datasheet_v0.4_review.pdf')
    parser.add_argument('--technical-dir', type=Path, default=ROOT / 'assets/technical-v4')
    parser.add_argument('--allow-missing-figures', action='store_true', help='Interim layout only; final builds require verified figures.')
    parser.add_argument('--connection-illustration', type=Path, default=ROOT / 'assets/connection-v0.4/two-motor-connection-v0.4.pdf', help='Optional owner-selected natural illustration; the old v0.1 AI image is never used.')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = build(args.output, args.technical_dir, args.allow_missing_figures, args.connection_illustration)
    print(f"Built {args.output} ({len(result['pages'])} pages; {len(result['interim_placeholders'])} interim placeholders)")
