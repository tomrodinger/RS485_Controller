# Code-native candidate review

## Artifacts and iteration

Source: `diagram-review/visual-candidates/build_candidates.py`. SVGs are self-contained; the photographic candidate embeds the original JPEG as a data URI. PNGs are rendered with `rsvg-convert`, 2400 × 1440.

- v01 precise electrical: first functional map.
- v02 photo-guided: first port-locator/map composition.
- v03 precise electrical revised: adds internal motor pair equality, PD-negotiation qualifier, twisted-pair instruction, and makes the thin extra ground-reference lead explicitly optional.
- v04 photo-guided revised: same electrical revisions; corrects the source-dimension comment and explicitly uses the native 2486 × 2486 square JPEG with uniform scale and a CCW SVG rotation. J2 is on the right. Numbered locator markers identify actual J1/J2/J3/J5 connectors; they are not wiring endpoints.
- v05 guided two-step: third distinct direction, a 2000 × 2200 portrait composition with two stacked panels. Step 1 shows parallel motor supply and substantial common return; Step 2 reuses the same geometry with power ghosted and active J2 reference/A/B daisy chain. Both controller and both motors appear in both panels. A small actual-board thumbnail locates J1/J2/J3/J5 without dominating the page.

v01/v02 remain saved as predecessors. Their 1200-pixel-wide previews demonstrate the legibility tradeoff; they are not additional art directions.

## Electrical review

Independent electrical reviewer inspected v01/v02 and passed the functional endpoints: J1 positive and substantial return to both motors in parallel; J2 1/2/3 GND/A/B; Motor 1 pins 3/4 incoming and 5/6 onward to Motor 2 pins 3/4; separate capped Motor 2 spare pins 5/6; no unlike-net short found. They scored functional electrical quality 93/100, while distinguishing this from a realistic physical-wiring illustration. Their requested clarifications are incorporated in v03/v04.

Motor blocks are explicitly external functional breakouts. They do not claim motor connector-face orientation. A3=A5 and B4=B6 are stated within each motor. The photo is real; its locator marks do not depict attached wires. The schematic controller block is an abstract electrical interface, and does not claim physical port placement.

## Own adversarial assessment

v03: 85/100 as a standalone digital electrical map. v04: 82/100 as a standalone digital port guide plus electrical map. v05: 89/100 as a standalone guided wiring instruction. No electrical veto found on the stated functional-map scope after revision. All remain draft owner-review candidates.

Strengths: exact labels, unambiguous unlike-net crossings, separate thick motor-current return and thin optional reference lead, correct duplicate-pair daisy chain, no fake motor face, restrained high contrast, preserved SVG editability.

Limits that lower the score:

- Neither is a full physical wiring illustration. v03 intentionally contains no physical layout. v04 locates the real board connectors but uses a detached functional map for wiring; it does not show cable insertion into the real terminal mouth or header sockets.
- Both use functional pigtail rows, so a reader must map wire functions to their real harness. Exact motor connector-face orientation remains unestablished.
- A/B pairing is taught through adjacent routing and an explicit twisted-pair note. The line art is an electrical map, not a literal cable geometry diagram.
- The extra J2 ground-reference lead is optional because J1/J2 grounds are already connected on the PCB. It is retained to make common reference visible; the note prevents reading it as mandatory.
- The photo-plus-map candidate has small map text when fit to a narrow viewport. It requires full-resolution viewing/zoom. The 1200-pixel preview is already too small for comfortable reading of all subsidiary labels.
- These are not ready to drop into the existing shallow 245-point datasheet image slot. At 180 mm print width, 25 px on a 2400 px canvas is approximately 5.3 pt. A future approved print adaptation should remove secondary prose, enlarge labels, and allocate more page area.

Verification: SVG XML parsed successfully; both first candidates rendered to 2400 × 1440 PNGs; all four full PNGs were visually inspected. v03/v04 were re-rendered and visually checked after the changes. Photo source dimensions were verified with `sips` and `images/rs485-controller/manifest.json`. No hardware, datasheet, site, or publication state changed.

v05 verification: SVG parsed and rendered successfully to 2000 × 2200. Visually inspected the full two-panel render. Distinct power/data stages remain consistent: J1 pin 1 positive and pin 2 GND, motor J4 pin 1 GND and pin 2 positive, J2 1/2/3 reference/A/B, motor pair 3/4 incoming and 5/6 onward, separate Motor 2 spare caps. Step 2 deliberately fades the existing power wiring; active data labels stay readable. The functional blocks remain abstract and publication adaptation is still required.

Independent electrical follow-up passed v03/v04/v05 with no hard veto. Two minor wording clarifications were then applied and re-rendered: v04's pinout note now says pins 2/3 carry A/B and pin 1 is optional reference; v05's headline instruction explicitly says to wire parallel power then the bus with all power off. No routing changed.
