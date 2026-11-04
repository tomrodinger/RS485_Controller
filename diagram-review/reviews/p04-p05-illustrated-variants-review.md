# Preference review: illustrated natural and stylized variants

Reviewed `p04-illustrated-natural-v1` and `p05-illustrated-stylized-v1` in PNG, plus their SVGs rendered at 1300 px and 900 px widths. Verified that p03, p04 and p05 route arrays are equal in their JSON files; this review does not substitute for the electrical reviewer's endpoint checks.

## Status and scores

Both concepts pass for the preference gallery after repairing the known GND/V+ typography collision. No new unlike-net crossing, wrong physical endpoint, extra header contact, or fictional motor cavity assignment was found. They remain draft schematic illustrations, requiring publication adaptation.

Current scores including the known label collision: **p04 88/100; p05 89/100**. Conditional scores after a successful spacing repair: **p04 90/100; p05 91/100**. The one-point style distinction is a preference judgment, not an electrical claim.

## Honest abstraction and concept clarity

The motor artwork's white connector is plainly unmated. Electrical lines terminate at detached dashed function keys rather than enter the pictured cavities. This is truthful functional-map abstraction and avoids the previous false connector-face mapping. It is suitable for comparing visual preferences.

A novice may still wonder whether the dashed key represents an extra adapter. Improve the local caption to “Six-wire pigtail functions” or “Pigtail function key.” The current “Use the supplied six-wire pigtail” is an instruction, but does not name what the box below represents. The footer's schematic/mating-face caveat should remain. No individual gray cavity-to-function traces should be reintroduced.

The internal equality callout is clearer and larger than p03's tiny note on the motor body. Add a small heading “Motor J4 links” or “Internal motor links” if practical. Bare A3=A5 and B4=B6 could be mistaken for references to J2 pin numbers, even though J2 pin 3 is B; the strip itself currently shows functions without pin numbers. A motor-specific heading resolves that possible ambiguity without adding a physical face-order claim.

## Material and style comparison

**p04 natural:** stronger product-real/premium impression. The fine brushed metal, natural shaft reflections and ribbing make the motor recognizable without relying on an artificial terminal panel. At the actual placed size the previously noted tiny edge fringes are not a material distraction on white. The rendering is more photograph-like than the simplified controller, so viewers should understand that this is illustrative artwork. Texture adds interest, but becomes less meaningful at small fit widths.

**p05 stylized:** slightly stronger overall graphic consistency. Cleaner edge definition and more even materials bridge the simplified controller and exact vector wiring. The shaft, plate, dark body and white connector remain readable at smaller sizes. It is my slight preference for the diagram as a cohesive instruction; p04 may win if the owner's preference is a more photographic product presentation.

Neither variant should gain additional gloss, heavy shadow, texture, or perspective wire effects. The exact electrical layer is already the correct visual counterweight to the detailed motor art. The white background and restrained palette support the task.

## Typography repair

The first two pigtail function anchors are 50 px apart. GND and V+ currently read as “GNDV+” at reduced size. Color separation helps but does not excuse the collision.

Reducing GND to 26 px and V+ to 30 px may leave only roughly 2–3 px native gap in Arial Bold, about 1 px at a 1300 px fit. Inspect the actual second render rather than assume the size change resolves it. A small label-only adjustment—GND 6–8 px left and V+ 3–5 px right—can preserve the exact wire anchors while making a real gap. Alternatively use 24/26 px, or increase the actual first-two anchor spacing to 60–65 px and repeat the endpoint audit. Moving labels slightly is lower risk than changing correct net routing.

## Actual-size review

At 1300 px width, the enlarged controller pin functions now read around 15 px and are substantially better than p03. The pigtail functions and motor equality callout also read at useful desktop size, subject to the first-two-label repair. No rendered assets obscure labels. J5 PROGRAM remains completely visible. White separation at the green/blue crossing and power crossings is clear.

At 900 px width, the overall topology remains comprehensible, but secondary reference/PD/mating-face notes and the six-wire caption require zoom. Core labels are improved compared with p03 but the diagram should still be presented as an overview at that width, with an obvious full-resolution action. Do not claim comfortable small-print use from these fit-width views.

The prominent title still consumes more area than its instructional value requires. A later print adaptation could shorten it and enlarge the functional keys further. This does not block digital preference review.

## Reinspection required for revision 2

- GND and V+ have a visible gap at full size and at 1300 px width.
- Local key caption makes its schematic/function role explicit.
- Exact route endpoints and crossing separation are unchanged by typography edits.
- Motor artwork remains unmated and no cavity-to-function assignment appears.
- Motor-specific internal linkage remains clear; spare A/B caps remain separate.
