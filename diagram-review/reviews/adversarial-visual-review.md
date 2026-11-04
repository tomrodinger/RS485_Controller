# Adversarial review: two-motor connection diagram

Reviewed 2026-10-26. Scope: visual and technical communication only. No hardware, generator, datasheet, or published artifact changed.

## Evidence inspected

- `datasheet/assets/two-motor-connection-ai.png`, viewed at full image scale.
- All four actual product JPEGs in `images/rs485-controller/`: component-side, ports, label-side, with-antenna.
- `datasheet/generate_datasheet.py`, especially the electrical specification, connector table, and two-motor wiring page.
- `datasheet/README.md` and the photo provenance README.

The generator is the factual context supplied for this review, not an independent new validation of the schematic or motor connectors. Motor connector order and motor physical appearance have not been established by the inspected assets.

## Verdict on current image

Reject as an installation/wiring illustration. Its electrical net idea is broadly understandable, but its most realistic object contains the most dangerous spatial fiction. It mixes a photographic-looking PCB with schematic pads that appear to be real connection points. A caption outside the image cannot reliably undo that visual claim.

1. **Fabricated controller terminals.** The right-edge row carrying J1 +20 V, J1 GND, J2 A, J2 B, and J2 GND is not where those connectors exist. The actual J1 is the green two-way screw terminal beside the PD input. The actual J2 is the separate eight-pin header, visibly present at the opposite edge in this orientation. The image even depicts that real header while inviting the reader to ignore it and use invented pads instead. These are physically misleading leader endpoints, not harmless diagram layout choices.
2. **No usable pin identification.** J2 has eight pins: GND/A/B/GND/A/B/3.3 V/5 V in the documented pin-number order. The current illustration never shows how its three bus labels relate to that header. Its invented connections could encourage attaching motor power to an unrelated expansion pad. A physically grounded variant needs an enlarged pinout inset with a stated viewing side and connector orientation, or visibly detached logical connection boxes.
3. **Power return and data reference are visually conflated.** Both grounds must be common, but high-current motor returns belong on wiring sized for that current. The black J1 and J2 lines have the same weight and merge into one long elaborate loop. The view fails to teach that the J2 reference lead cannot be the only motor-current return. Distinguish the substantial supply return from a thin reference lead, while visibly connecting both to the same GND net.
4. **Bus topology is visually weak.** A and B are widely separated ribbons with long perpendicular motor drops. That conflicts with the accompanying instruction to keep A/B together as a twisted pair along one bus and keep stubs short. Use adjacent paired lines, a subtle paired-cable convention, or an explicitly conceptual bus corridor. The exact physical motor connector sequence must remain unclaimed until verified.
5. **Junction grammar needs simplification.** The ground loop and multiple large junction dots demand unnecessary tracing. Green/blue lines cross black motor returns with light halos; the graphic relies on the viewer understanding a mixed 3D-wire/vector-wire convention. Use one consistent rule: dot at a genuine junction, no dot at a crossing, a clear bridge or sufficient separation at unrelated crossings. Prefer routing that removes crossings.
6. **Generic motors imply unsupported physical detail.** The black/silver front-facing objects resemble ordinary flange/stepper motors and carry V+/GND/A/B badges on their front faces. No inspected evidence establishes that those are the actual motor terminals or their order. Use verified motor photography if available, or a deliberately simplified motor symbol with a detached logical terminal block labelled “signals shown; connector order varies.”
7. **Hierarchy rewards illustration detail over the connection task.** Large 3D motors, board textures, shadows, and the charger consume much of the frame. The optional laptop and antenna are prominent enough to compete with the core path: PD source → J3 → J1 → both motor supplies, J2 → shared A/B bus. Make the controller and its actual connection points the central instructional object. Put optional programming in a quiet secondary area or inset.
8. **Too much label furniture.** Rounded gradient badges, dark-green captions, arrows in A → A/B → B, motor headings, and COMMON GROUND use several competing styles. A/B arrows can imply data only travels in the indicated direction. Use stable labels “A” and “B” repeated at endpoints, plain connectors, a compact net legend, and one title/caption hierarchy.
9. **Small-size risks.** At the generator's approximately 245-point-high datasheet placement, detailed PCB silkscreen and cable decoration shrink sharply. Lettering in the badges remains more useful than actual terminal identification. Every candidate must be judged at its intended datasheet width, not just as a zoomed PNG. A beautiful full-screen image can still fail at print size.
10. **Voltage certainty is overstated graphically.** The source should explicitly support 20 V PD. J1 is the negotiated PD rail, not an independently regulated guaranteed 20 V output. “20 V PD example” and a brief “verify J1 voltage” instruction communicate the intended example without promising successful negotiation under every source/cable condition.

## Factual constraints for every candidate

- J3: USB-C PD power input. J5: USB-C programming/data input. Do not exchange them or suggest that J5 supplies motor power at J1.
- J1 pin 1: positive PD rail, labelled +20 V on the PCB; J1 pin 2: GND. These connections physically belong to the green two-way terminal.
- J2: pin 1 GND, pin 2 A, pin 3 B, pin 4 GND, pin 5 A, pin 6 B, pin 7 3.3 V, pin 8 5 V. Both bus groups are electrically parallel. Depict one valid group consistently if only one is needed.
- The documented label-side orientation has USB-C sockets left and J2 right; reading J2 bottom upward gives pins 1 through 8. Any alternate view must explicitly map this orientation rather than mirror it casually.
- Each motor gets positive supply and a substantial supply return; both share A, B, and common reference. No A/B inversion, floating return, or power through a J2 logic rail.
- A/B run together along one RS485 bus, with short motor branches. No unqualified “one cable per isolated controller channel” reading.
- No invented current rating, guaranteed motor count, fixed cable-length limit, guaranteed operating voltage independent of PD, or universal motor connector pin order.
- Do not add termination at every motor as decoration. The current generator identifies onboard R5 = 220 Ω across A/B and says additional termination must be chosen for the complete bus.
- Antenna can be shown as included equipment but should not resemble a mandatory wire in the motor circuit.

## Five materially distinct art directions

### A. Photographic installation plate

Use the real controller photograph as the dominant anchor, cleanly isolated against white. Actual wires enter the actual J1 screw terminal and chosen J2 pins. A large connector inset shows the selected J2 GND/A/B group in the same view orientation. Put the source at left, controller central-left, two restrained motor silhouettes to the right. Use flat, exact typography and linework over the photo; avoid attempting to generate readable silkscreen.

Strength: greatest physical trust and easiest translation from page to workbench. Risk: real photo perspective makes exact pin endpoints and occlusion difficult. Reject if an endpoint appears to penetrate a board pad or component rather than its actual connector.

### B. Service-manual orthographic drawing

A precisely traced, simplified top/label view of the controller, drawn to the real outline and connector locations. Suppress most small components. Show only J1, J2, J3, J5 and enough landmarks for orientation. Run orthogonal wires through generously spaced routing lanes. Motors are flat technical pictograms with off-object logical terminals. Use one clear pin inset and small numeric connection steps.

Strength: exceptional print legibility and exact endpoint control; appropriate for a datasheet. Risk: a plain drawing may feel less product-rich. It must still be recognizable as the real board rather than an arbitrary green rectangle.

### C. Editorial system map with honest abstraction

Separate a real product photo from the electrical map. Show a detached controller block containing named connector groups J3, J1, J2; place the photo above or beside it with a fine identification leader. Use two bus corridors: “Motor supply” and “RS485 A/B + reference.” Connect two clearly labelled motor blocks. An inset maps the logical connectors to actual J1/J2 locations.

Strength: cleanest explanation of the system and easiest for a nonexpert to follow. Risk: too many inset transitions. Never attach abstract terminals directly to a realistic PCB in a way that implies their physical locations.

### D. Premium restrained isometric assembly

An accurate shallow-isometric controller based on the actual board and connector arrangement, with a consistent shallow-isometric source/motor treatment. Keep geometry deliberate, white/soft-neutral background, restrained shadows, and 4–5 nets. Route wires to the actual terminal/header location; use a magnified connector callout when the pins are obscured. Place all explanatory labels in flat 2D outside the rendered objects.

Strength: polished product presentation with understandable depth. Risk: physically persuasive generated errors and occluded connectors. This direction has the highest rejection risk and needs the strictest connector-by-connector visual review.

### E. Guided two-stage wiring instruction

One composition with two clear steps: “1. Supply and common return” and “2. Shared RS485 bus.” Reuse the same modest real-board drawing and same orientation across both panels. The first panel emphasizes J3/J1 and robust motor returns; the second emphasizes J2 and paired A/B routing, while the already-connected power paths recede in gray. End with a small complete-system thumbnail and “Power off while wiring; verify J1 voltage.”

Strength: teaches the task with the least tracing burden and clarifies the two purposes of GND. Risk: more total layout area, less suitable for a very shallow datasheet slot. Require a tall candidate or deliberately allocate more space in a future approved layout.

These should differ in layout, representation, and information hierarchy, not just background tint, motor angle, or line color.

### Representation boundary

A simplified code/vector board is allowed and can be preferable: it must be visibly diagrammatic, keep the real J1/J2/J3/J5 placement relationship, and identify orientation. It does not need to reproduce every resistor or silkscreen mark. The strict objection is fabricated connections presented with photographic authority. Detached schematic ports are also allowed when their abstraction is explicit and a physical connector locator is provided. AI-generated part artwork can be combined with exact code/vector wiring and labels; judge the resulting composition by its endpoints and clarity, not by whether every pixel came from one method. A generated motor should remain a generic symbol unless real reference evidence supports its physical connector details.

## Scoring rubric

Score only candidates that pass every hard gate. Stars are preference feedback, not evidence of electrical correctness.

| Criterion | Weight | Full-credit evidence |
|---|---:|---|
| Electrical correctness and truthful physical endpoints | 30 | Every connection can be traced to a valid real connector/pin or an explicitly detached logical interface; nets and return path correct. |
| First-use clarity | 20 | A new reader identifies PD input, positive output, motor return, A/B, and optional programming without searching captions. |
| Product fidelity and orientation | 15 | Board outline, key connectors, header, antenna relationship and view agree with actual photos; no mirrored pinout. |
| Routing and junction clarity | 15 | A/B visibly paired, branches short in concept, crossings unambiguous, common reference clear, motor return distinct. |
| Typography and print legibility | 10 | Labels readable at intended datasheet width and on mobile; no distorted/garbled characters; strong contrast. |
| Visual hierarchy and craft | 10 | Controlled whitespace, consistent label grammar, aligned composition, minimal distractions, coherent rendering style. |

Suggested interpretation: 90–100 ready for owner selection after technical sign-off; 80–89 strong candidate with specific repairs; 70–79 requires substantial revision; below 70 abandon direction or rebuild. Any hard gate failure means rejected regardless of numeric score or star average.

## Hard rejection criteria

- Wire endpoints imply J1/J2 terminals on unrelated holes, component pins, or invented board pads.
- J3/J5 swapped; J5 shown as the motor-power path; motors supplied from J2 3.3 V/5 V.
- V+/GND polarity reversed or unresolved; A/B swapped; any motor lacks a real supply return/common reference.
- J2 header count/order is wrong, mirrored, or presented as physical while ambiguous about view direction.
- A junction dot connects unlike nets, a crossing reads as a short, or any line ends without an explained endpoint.
- J2 signal-ground lead is shown as the only motor-current return.
- Invented motor pin order presented as a real connector; inaccurate hardware detail too persuasive to treat as abstract.
- Core labels unreadable at final use size, missing, misspelled, or generated as pseudo-text.
- Image claims unsupported board current, motor count, cable length, or power behavior.
- Raster is blurry at intended placement, labels are clipped, or a required connection is hidden behind an object.

## Iteration and review method

1. Produce one coherent first candidate for each direction, using the same factual checklist and target size. Assign stable candidate IDs and retain every PNG.
2. Review the full image and a final-size version. Perform a separate endpoint audit: PD source→J3; J1 positive→both V+; J1 GND→both motor returns; J2 reference→common GND; J2 A→both A; J2 B→both B. State “pass/fail/uncertain” for each; uncertainty is not a pass.
3. Reject factual failures before collecting aesthetic ranking. Record the failure precisely with image coordinates or a crop reference.
4. Make revisions with a stated hypothesis, such as “move data buses adjacent and shorten stubs.” Preserve the predecessor and add a new candidate ID so ratings and comments stay attached to the viewed image.
5. Take the top two different directions through at least two focused review cycles. Stop iterating a direction that repeatedly invents hardware; change the representation method instead.
6. Use a stable comparison view with a fixed image background, zoom/fullscreen, candidate title/version, 1–5 star buttons, freeform comment, and visible review status. Make persistence and export behavior explicit. Keep technical rejection separate from personal stars.

Useful review prompts: “Which wire would you connect first?”, “Where exactly is J2 pin 1?”, “Could you mistake the 5 V pin for motor power?”, “Which path carries motor return current?”, and “Can you trace A/B to both motors without losing the pair?” A website should support those judgments rather than make viewers hunt for controls.
