# Candidate review: ai-flat-technical-v1

**Decision: reject.** Original `diagram-review/candidates/ai-flat-technical-v1.png` viewed, including enlarged crops of controller, power distribution, and both motor connectors. Source image is 2146 × 733. A caption cannot cure the physical and electrical contradictions below.

## Critical vetoes

1. **No valid J1 motor return; apparent positive-to-return short.** At the green J1 terminal, the red supply conductor and the thick black return conductor both visibly begin at the right-hand contact labeled `+20 V`. The left-hand `GND` contact has only a short black label leader ending near its aperture. That leader does not join the black power-return trunk. Following the pictured physical attachment ties both motor supply rails to the same output contact; reading the label leader as a conductor instead still leaves the actual return route absent. This fails the basic requirement that red leave J1.1 and black leave J1.2 separately.
2. **Invented nine-position J2 and incorrect wire positions.** The rendered PCB header has nine visible rows of metal contacts/black housings. Its first two rows are bare; black is connected on row 3, green on row 4, and blue on row 5. The inset shows eight contacts and says pins 1/2/3 are GND/A/B. A real eight-position J2 at rows 3/4/5 would be B/GND/A, so copying these visible placements is electrically wrong. Do not count the inset as validation of the separate main-board drawing.
3. **Motor 1 onward A/B are open.** Its last green/blue pair hangs to the right and stops at A/B labels. Neither conductor continues to Motor 2. The first green/blue pair heads toward the controller, while the separate long blue controller route goes onward elsewhere. This is not the claimed daisy chain through the duplicated A/B pair.
4. **Motor 2 has contradictory extra data tails.** Below the six-contact connector appear tails/labels GND, V+, A, B, another A, and two insulated spare ends. The long controller blue line rises to the extra tail explicitly labeled `A`; the first A/B tails stop at labels. The connector has only six contacts, so this cannot be interpreted as the documented GND/V+/A/B/A/B pigtail without inventing splits and changing labels. Even if one hidden split is accepted, the drawing still tells the reader B-to-A.
5. **The power wiring is duplicated at the motor connectors.** On each motor, full-length red/black power wires arrive from the upper rails, while additional red/black tails leave the same contacts and stop under GND/V+ labels. Those tails look like separate physical leads; they are not thin text leaders. The result has more actual lead ends than a six-wire pigtail. These extra tails are neither connected onward nor insulated. Labels must sit beside a single continuous wire, not be created as additional physical wire ends.

## Other major failures

- **The pictured power-distribution block is electrically ambiguous.** A single two-lever common-looking connector lies across both red and black rails. A typical two-port lever connector joins its ports to one net, and no insulated positive/negative pole structure is established here. Do not claim a certain component identity from its appearance, but this depiction permits a shorting interpretation and fails acceptance. Use two clearly separated single-net splice blocks or a proven two-pole terminal block with distinct labeled poles.
- **The shared-reference lead crosses the red vertical branch without a clear crossing gap** and visually stops at that branch rather than continuing to the black return. The upper route is labeled shared ground but has no visibly complete safe endpoint. This adds another possible GND-to-positive connection.
- **GND / 0 V is placed above a red-rail junction**, increasing positive/return ambiguity around the distribution block.
- **Some data conductors terminate at text labels and resume below them**, leaving visual gaps. Labels must not be required as invisible continuity bridges in a purported physical wiring illustration.
- **No external antenna is shown** on the ESP32-S3-MINI-1U board. This is not a four-net continuity error, but the user requested the real controller appearance and the product uses an external antenna.
- **J5 is called not used while a ghost plug is shown partly inserted.** Remove the plug or depict an optional, fully connected cable. A semitransparent dangling plug suggests an incomplete physical connection.
- **20 V is presented unconditionally.** Adjacent documentation should retain the successful-PD-negotiation / verify-J1 caveat; the direct pass-through rail is not an independently regulated 20 V source.

## Correct elements to preserve

The controller has the right broad orientation: J1 upper-left, J3 beside J1 on the left, J5 lower-left, J2 right. The motor white connector is at the side near the rear rather than on the shaft face. Two motor bodies are present and parallel power is the stated intent. The inset J2 electrical table itself is correct. Those improvements do not resolve the vetoes.

## Isolated motor asset: motor-asset-v1.png

**Conditionally usable as a body/connector visual for exact composition.** The square face, shaft, four mounting holes, stacked black body, rear black section, and white six-contact side connector are plausible compared with the M17 reference. The image does not invent a signal label or pin-number orientation. Six exposed metal contacts can be counted.

The white connector is **unmated**: its open receptacle and six metal contacts are visible. Wires cannot simply emerge from those exposed contact tips and be described as a plugged-in pigtail. Add a distinct plausible mating plug seated into this housing, covering the mating contacts, then have exactly six wires leave that plug. Alternatively retain it as an unwired body thumbnail clearly separated from an external functional connector breakout; do not imply the abstract breakout is physically on the motor.

The reference establishes pigtail functions in order GND/V+/A/B/A/B but not the left/right orientation of this asset's visible mating face. Do not number the face or map a claimed leftmost black contact solely by appearance. Label the pigtail wires by function after leaving the mating housing. The asset's photorealistic finish makes a correct mate particularly important.

No requirement to regenerate this isolated asset is established by the electrical review; its principal limitation can be handled by adding an accurate mating-harness layer and deterministic wires.
