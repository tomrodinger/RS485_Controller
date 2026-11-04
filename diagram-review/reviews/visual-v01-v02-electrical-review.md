# Functional-map candidate review: v01 and v02

Files viewed at original resolution: `visual-candidates/v01-precise-electrical.png` and `visual-candidates/v02-photo-guided.png`.

**Electrical decision: both pass as functional maps, 93/100 each.** No unlike-net short or wrong endpoint found. They intentionally use abstract connector-function blocks and therefore do not yet constitute a realistic physical wiring illustration. Estimated fit to the full physical-illustration objective: v01 70/100; v02 78/100. These are review judgments, not measured safety ratings.

## Endpoint trace

- Supply USB cable reaches J3, with 20 V-capable PD source clearly stated.
- J1 positive branches to Motor 1 V+ and Motor 2 V+; no signal-pin motor power.
- J1 GND has an independent substantial return branch to Motor 1 GND and Motor 2 GND.
- J2 pin 1 reference joins the return independently of the heavy motor-current path.
- J2 pin 2 reaches Motor 1 contact 3 A; pin 3 reaches Motor 1 contact 4 B.
- Motor 1 contact 5 A reaches Motor 2 contact 3 A; contact 6 B reaches Motor 2 contact 4 B.
- Motor 2 contacts 5 and 6 end separately capped, with correct insulation instruction.
- Red/black crossings are visually separated by white gaps rather than junction dots. Actual parallel power branches have dots.
- v02 photograph port markers identify J1/J2/J3/J5 correctly, with USB left and header right. Stated J2 top-to-bottom order agrees with the photo and PCB.

## Remaining issues

1. **Motor-internal A/B continuity is only implicit.** Source evidence says contacts 3 and 5 are the same A net; 4 and 6 are the same B net. With external ports on opposite sides of a block, the map can resemble an active motor repeater. State `3 = 5 (A), 4 = 6 (B); internally common` or add clear internal same-net links without crossing unlike nets.
2. **J1 +20 V needs the negotiation qualifier.** The verify-J1 footer is useful; a short `nominal after PD negotiation` note makes the rail behavior accurate.
3. **Pair construction is not shown.** Add `route A/B as a twisted pair` near the two bus segments. The separated line geometry is acceptable for an abstract map when this instruction is present.
4. **v02 pin table needs separators.** `1 GND 2 A 3 B ...` should have clear spacing, cells, or separators, especially when reduced into a PDF. The small nested map in v02 needs actual-size legibility review.
5. **Physical attachment is outside these candidates' scope.** No wires enter real J1 apertures, real selected J2 contacts, or seated six-contact motor mating plugs. Their explicit abstract styling makes this honest; it also leaves the user's realistic physical-connection request unfinished. Keep these as reference/secondary views or accompany an accurate physical diagram.

No caption excuse was used to accept a physically wrong endpoint: the diagrams do not depict such endpoints at all. This differs from the rejected AI image, which visibly attached wires to false features.
