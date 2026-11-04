# Electrical and physical adversarial review

Reviewer: electrical adversary subagent. Date: 2026-10-26. Scope: source illustration, controller revision 0.5, controller photographs, M17 reference material. No hardware, firmware, or publication changes made.

## Evidence checked

- `datasheet/assets/two-motor-connection-ai.png`, viewed at original resolution.
- All four `images/rs485-controller/*.jpg` photographs, viewed directly.
- `PCB/0.5/0.5.kicad_pcb`, pad nets and footprint coordinates parsed directly.
- `datasheet/verify_design.py`: fresh run using installed KiCad CLI passed **392 checks**, including every numbered PCB pad against a newly exported schematic netlist.
- `datasheet/review/sources.json`, especially H1/H2 and the unestablished board pass-through current rating.
- `../Servomotor/servomotor_datasheets/AGENTS.md` and its required README; reference photographs `m17_series_overview.jpg`, drawing `M17-60_dimensions.png`, generated datasheet latest English PDF page 3, and source `specs.py`/`introduction.txt`.
- Additional direct motor evidence: `../Servomotor/API_documentation/autogeneration/hardware_setup.md:14–29` and `../Servomotor/PCB/Servomotor3/1.5/1.5.kicad_pcb`, J4 pad nets.

## Findings in the existing image

1. **Critical: controller wiring attaches to the wrong physical features.** The five colored leads emerge from the right-hand ESP32 expansion plated holes. J1 is actually the green two-way screw terminal. J2 is the eight-way right-angle pin header at the opposite edge. Correct text does not make a physically false attachment accurate. A caption saying terminal locations are schematic does not remove the visual inference created by wires entering specific photographed-looking holes.
2. **Critical: the motors have invented four-pin front terminals.** The real M17 has one white shrouded six-contact connector at the side near the rear. The image puts four freestanding labeled contacts on the shaft face, where no such connector exists. The real connector includes duplicated A/B contacts for daisy chaining.
3. **Major: the wiring shown cannot be built by following visible connector geometry.** J1 is unused, J2 is unused, and the illustrated motor points are nonexistent. The image therefore teaches the wrong physical action despite having a valid abstract four-net graph.
4. **Major: no realistic mating parts.** Bare colored lines enter plated holes and fake motor terminals. Real J2 attachment needs mating female contacts/housings or an explicitly identified adapter; the motor needs a mating six-wire plug/pigtail. Wiring into screw heads is also unacceptable: J1 wires enter its wire apertures and the screws clamp them.
5. **Major: motor A/B continuation is omitted physically.** Four function labels conceal the duplicated A/B pair. This matters because a realistic two-motor bus should go from controller A/B into one motor pair, then onward from the second pair to Motor 2. A functional breakout may collapse identical functions only if it is visually separate from the actual connector and explicitly identified as a breakout, without inventing four contacts on the motor.
6. **Major: the long separated A and B runs encourage the wrong cable construction.** A/B is a differential pair and the motor documentation specifically calls for twisting each pair if possible. Illustration paths may be simplified for readability, but a cable/twist cue or an adjacent instruction is needed. Large loops and long branches should not be presented as a recommended installation.
7. **Moderate: repeated crossings need more explicit treatment.** Motor GND, B, and the J1/J2 ground link cross unlike nets repeatedly. The image's colors/white halos and junction dots permit the intended interpretation at large size, but a reduced or monochrome copy is harder. Prefer a layout with fewer crossings and clearly gapped/bridged nonjunctions. Every actual branch gets a junction dot; every unlike-net crossing gets no dot and an unmistakable visual separation.
8. **Moderate: the extra external J1-GND to J2-GND loop can imply it is electrically required.** These points are already the same on-board ground net. An explicit reference-ground lead is acceptable, but the drawing should not imply the board grounds are isolated or that motor return current belongs in a small signal-ground lead. Use J1 GND as the motor-current return, and show/reference the existing common controller ground honestly.
9. **Moderate: the J1 output is labeled as an unconditional 20 V source.** The design directly connects J3 VBUS to J1; it does not independently regulate J1 to 20 V. The normal 20 V request depends on the standard configuration and successful negotiation with a suitable source. A concise nearby note should state nominal 20 V after PD negotiation / verify J1 before connecting motors. This limitation already appears in the draft PDF text.
10. **Moderate: identical-looking wires can imply that a skinny data-ground jumper is an adequate motor-current path.** Both motor black power leads must return to J1 GND using wiring and connections suitable for motor current. No board continuous pass-through current is established, so the diagram cannot itself guarantee support for an arbitrary two-motor load or supply wattage.
11. **Minor: generic motor geometry suppresses the integrated controller/rear connector.** A matching M17 visual should include a credible rear section and connector, and all leads should originate there. Shaft-side front contacts are specifically wrong.
12. **Minor: illustrative proportions are inconsistent.** The board is shown wider than a motor face although its narrow dimension is 36.88 mm and an M17 face is roughly 42.3 mm. Mixed object scales can be acceptable in an infographic, but avoid presenting this as a dimensional or installation-clearance illustration.

The original does get the abstract positive/A/B/common-GND graph right by labels. It also distinguishes the two USB sockets correctly for its chosen board orientation: PD is beside J1 and PROG is the far USB socket. Exactly two motors and the external antenna are present. Preserve those correct features.

## Canonical controller specification

| Connector | Contact | Function |
|---|---:|---|
| J1 two-way screw terminal | 1 | Positive motor supply: direct J3 VBUS rail, normally 20 V after successful negotiation |
| J1 | 2 | GND / motor-current return |
| J2 eight-way header | 1 | GND |
| J2 | 2 | RS485 A |
| J2 | 3 | RS485 B |
| J2 | 4 | GND, same net as pin 1 and J1 pin 2 |
| J2 | 5 | RS485 A, same net as pin 2 |
| J2 | 6 | RS485 B, same net as pin 3 |
| J2 | 7 | 3.3 V auxiliary rail; never motor V+ |
| J2 | 8 | 5 V programming-related rail; never motor V+ |
| J3 USB-C next to J1 | VBUS / GND | USB-C PD input, no USB programming data |
| J5 other USB-C | USB data / 5 V | Optional programming connection to laptop |

Any illustrated pin position must follow the selected view and visible PCB labels. Do not mirror a component-side photograph to get a desired cable direction.

## Canonical motor specification

Motor documentation states the pigtail sequence as **BLACK GND; RED V+; GREEN A; BLUE B; GREEN A; BLUE B**. It explicitly says the two A contacts are the same bus, as are the two B contacts, and the second pair exists for daisy chaining. This is corroborated by the motor revision 1.5 PCB J4 numbered pad nets:

| J4 electrical pad | Net | Pigtail color |
|---:|---|---|
| 1 | GND | Black |
| 2 | +24V PCB net name; operating supply 12–24 V | Red |
| 3 | RS485_A | Green |
| 4 | RS485_B | Blue |
| 5 | RS485_A, same as 3 | Green |
| 6 | RS485_B, same as 4 | Blue |

The dimension drawing names the physical header **S6B-PH-K(LF)(SN)**. The PCB uses a generic 1x06 2 mm pin-socket footprint. These sources establish six contacts and electrical sequence, but **do not yet prove the left/right pin orientation of a photographed mating face**. Do not stamp pad numbers onto a realistic connector face without resolving the viewing direction. A six-wire pigtail whose functional colors are labeled after it leaves the housing can be accurate without claiming a face orientation.

## Required two-motor graph

1. One suitable USB-C PD source enters J3 only. J5 may have a separate optional USB programming cable to a laptop.
2. J1.1 connects through a real distribution splice/block or a clearly shown parallel branch to Motor 1 RED/V+ and Motor 2 RED/V+.
3. J1.2 connects through a real return distribution splice/block or clearly shown parallel branch to Motor 1 BLACK/GND and Motor 2 BLACK/GND. This is the motor-current return path.
4. The controller common ground includes J1.2, J2.1, and J2.4. It must be evident that both motors and the RS485 transceiver share this reference. A separate J2 GND reference wire is allowed, but is not an additional electrical requirement when the J1 return already establishes common ground.
5. J2.2 (or J2.5) → Motor 1 first GREEN/A contact. Motor 1 second GREEN/A contact → Motor 2 first GREEN/A contact. No A connection ever meets B, V+, or GND.
6. J2.3 (or J2.6) → Motor 1 first BLUE/B contact. Motor 1 second BLUE/B contact → Motor 2 first BLUE/B contact. No B connection ever meets A, V+, or GND.
7. Motor 2 unused second A/B pair ends separately, insulated. It must not be shorted to itself, to GND, or to power. A termination component is not invented. Controller R5 already loads A/B with 220 Ω; termination decisions belong to the complete bus design.
8. Exactly two motors. No motor is powered through another motor in series. A/B continues through the duplicated bus pair; power/return are parallel distribution.

## Acceptance rubric for every candidate

All critical gates must pass. A polished image cannot trade away a gate.

- **P1: physical endpoints.** J1 leads enter actual terminal wire apertures; J2 leads leave actual selected header contacts through plausible mating housings; motor harnesses mate with the real rear/side six-contact connectors. Nothing enters GPIO/expansion holes, screws, motor shaft face, RF shield, or board mounting holes.
- **P2: identity and orientation.** J3 PD and J5 PROG are correct in the selected view. J2 contact order agrees with the photo/PCB labels. Positive and ground on J1 are not reversed. No mirrored photo or invented connector location.
- **P3: motor harness.** Six contacts / six-wire harness represented credibly. Two A and two B wires have the documented function; Motor 1 bus pair continues to Motor 2. Any abstract breakout is visibly external and labeled as such. Unknown face direction is not invented.
- **E1: four disjoint nets.** Trace V+, GND, A, B from each selected controller contact to every motor. Every required destination is reached; no different net is reached. Branch dots and crossing gaps are unambiguous even at final output size.
- **E2: parallel supply and common ground.** Both red leads meet J1 positive, both black power returns meet J1 GND, and the controller bus reference is the same ground. No signal-ground-only motor return; no positive connection to J2 3.3/5 V.
- **E3: plausible bus.** A/B are recognizable as a paired route; no long star branches portrayed as the recommended arrangement; duplicate motor contacts used honestly. No unexplained external resistors or bus-count guarantees.
- **E4: power behavior.** PD source states 20 V capability; output described as nominal after negotiation in the illustration or adjacent caption; no unsupported current/wattage rating or claim that J5 supplies the motors.
- **V1: actual-size legibility.** Readable connector names and colors at its intended PDF display size; no label hides a physical termination; no wires disappear beneath objects or ambiguously reappear elsewhere.
- **V2: standalone clarity.** The figure itself communicates where to connect. A disclaimer elsewhere in a document cannot cure a wire visibly attached to a false physical point.
- **V3: consistent conventions.** Red positive, black return, green A, blue B used consistently; optional programming cable visually identified, without looking electrically broken or unconnected.

## Controller photograph orientation and anchor estimates

Recommended physical view: rotate `ports.jpg` **90° counterclockwise**, no mirror. USB sockets then face left and the J2 pins face right; J1 is upper-left. Header top-to-bottom becomes GND/A/B/GND/A/B/3.3V/5V, so selected bus leads can travel right without crossing the board.

For the original 1600×1600 photograph, approximate exposed J2 pin-tip positions are: pin1 (1420,1420), pin2 (1340,1420), pin3 (1260,1420), pin4 (1180,1420), pin5 (1105,1420), pin6 (1025,1420), pin7 (947,1420), pin8 (867,1420). After the CCW transform `(x',y')=(y,1600-x)`, pins 1–8 lie approximately at `(1420,180)`, `(1420,260)`, `(1420,340)`, `(1420,420)`, `(1420,495)`, `(1420,575)`, `(1420,653)`, `(1420,733)`. These are image estimates, not mechanical coordinates; mating housings should cover the metal tips.

J1 screw centers in the original view are approximately GND (1230,240), V+ (1394,240). Do not attach cables to those centers: identify the wire apertures. J3 visible socket center is roughly (985,275); J5 is roughly (280,275). After rotation, their approximate centers are PD (275,615), PROG (275,1320).

More exact PCB source coordinates: J1 origin (40.57,144.200001,90°), local pad1 (-2.5,0), pad2 (2.5,0); J2 origin (72.263,139.005,90°), local contact x positions -8.89,-6.35,-3.81,-1.27,+1.27,+3.81,+6.35,+8.89 and y=-4; J3 origin (41,134.025,90°), J5 (41.015,110.545,90°).
