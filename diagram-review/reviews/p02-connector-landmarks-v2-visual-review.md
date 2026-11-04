# Adversarial visual review: p02 connector landmarks v2

Inspected PNG, SVG and route JSON. This is an acceptable and distinct pictorial direction: visibly schematic board artwork preserves the real J1/J2/J3/J5 placement relationship, eight header contacts, top-down pin functions, and the selected first three contacts. I found no new unlike-net junction or fabricated expansion-pad endpoint. It should remain a draft pending the repairs below.

## Blocking and required repairs

1. **Known J5 label occlusion.** The ESP shield hides part of PROGRAM. Move the shield and/or place the J5 legend outside its footprint. Because J3 and J5 are different USB-C functions, this is a real clarity defect rather than decorative overlap.
2. **Individual motor cavity-to-function mapping remains too physical.** The six thin gray lines visibly run from specific drawn connector positions to the functional row. That visual grammar implies a connector contact order even though the footer disclaims a mating-face view. Replace the fan-out with a single neutral bundled sheath, then show a visibly detached dashed box labelled “Functional pigtail breakout.” The box can keep the six GND/V+/A/B/A/B wire functions and existing exact colored routing. Do not draw a traceable cavity-to-function permutation unless the viewing direction has been established.
3. **Ground reference optionality.** The top note correctly says J1/J2 GND are already common, but the extra J2 reference lead still looks like a required installation step. Add “thin reference lead shown; optional” near the lead, retaining the substantial J1 motor returns. This is a required wording repair for instructional clarity, not an electrical-net failure.

## Routing and legibility

- Power is visibly parallel, with an adequate hierarchy between heavy motor returns and thinner reference lead. The upper supply corridor and lower bus corridor are easy to distinguish.
- White casing at unlike-net crossings is consistent. The black branch over red and blue over green read as crossing rather than junction. Genuine branch dots are present where expected.
- A/B stays visually paired in both runs and the motor's duplicate A/B functions are stated. The internal linkage note inside the motor is small; enlarge or move it to the breakout caption if it must survive thumbnail viewing.
- The motor pigtail function strip is readable at full image scale. GND/V+ are closer together than A/B, but not colliding. A/B outgoing/unused roles can be understood by tracing; a small “IN” and “ONWARD” above the first and second pairs would reduce that burden, but is optional.
- The supply description and PD qualifier are clear. “+20 V nominal” near the rail is supported by the PD-negotiation note.
- The giant title and three footer lines take substantial space, but do not currently crowd wire labels. A later print adaptation should trade some title area for larger connector and pigtail labels.
- The spare A/B caps are independently drawn and the label states separate insulation. No false short is implied.
- This remains a schematic illustration. It gives truthful landmarks and interface functions; it cannot establish physical motor connector-face orientation or the exact hardware mating procedure.

## Score

Current visual/technical communication score: **84/100**, conditional on correcting J5 and the gray fan-out semantics. Electrical correctness is not independently re-certified here; the route JSON is consistent with the displayed intended nets. Suggested score after these targeted repairs and reinspection: approximately 89–91/100.

No new alternate layout is necessary to solve these issues. The strongest repair preserves this composition and clarifies the bundle-to-functional-breakout boundary. It is materially different from the pure electrical map, photo-guide map, and two-step instruction already produced.
