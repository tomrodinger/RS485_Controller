# p03 visual reinspection and premium variant direction

## Repaired p03

Viewed `diagram-review/candidates/p03-connector-landmarks-v3.png` at full size and rendered its SVG to 1300 px and 900 px widths for a separate legibility check.

All three targeted repairs are effective:

- J5 PROGRAM is completely visible; J3/J5 functions remain distinct.
- Six gray cavity-to-function traces are gone. A single neutral connector stub and a gap now separate the motor illustration from a dashed functional key. The image no longer offers a traceable assignment from connector cavities to functions.
- The thin J2 lead is expressly optional; J1/J2 already-common ground is stated beside it and in the footer. The substantial motor-current returns remain clear.

No new physical-endpoint, header-count/order, crossing, or unlike-net junction veto was found. The first three of the eight header contacts are used consistently. Motor 1's second A/B pair continues to Motor 2's first pair, and Motor 2's spare pair has independent caps. **Current visual score: 90/100** as a draft schematic pictorial wiring guide.

The neutral stub does not claim an installed real harness. That limitation is now honest and should stay explicit. Motor connector-face orientation remains unestablished.

## Actual-size legibility

At 1300 px width, the 22 px native J2 labels become 11 px; 24 px functional-strip labels become 12 px. They are readable but small. The 18 px motor pair-link note is only 9 px and should be larger or moved out of the body art. At 900 px fit width, core pin/function labels become approximately 7.6–8.3 px; that view provides an overview, not a comfortable wiring instruction. The gallery should expose a clear zoom/full-resolution action.

The title is much larger than the connection labels. A premium revision can reduce title height and spend the recovered area on the controller, strip labels, and local annotations. This will improve usefulness more than adding visual effects. No publication-ready small-print claim should be made from the current candidate.

## Isolated motor asset assessment

Viewed `diagram-review/working/motor-asset-v1.png`. The asset supplies a believable black ribbed housing, brushed silver faceplate and shaft, and a visible white six-contact side connector. Those materials offer a clear aesthetic change from the flat green schematic motors. It should be described as AI illustrative artwork rather than a verified product photograph. The electrical composition must remain exact and independent of the rendered contact cavities.

Native-size viewing shows a few tiny colored edge fringes around the shaft. Inspect the asset against white at its actual placed size before declaring the composition polished. At roughly 400–450 px placed width those may be negligible; a visible colored halo would need an asset repair/regeneration rather than being hidden with stronger shadows.

## Recommended premium composition

Use a quiet white product plate with three clear device columns, anchored to a common baseline: controller left, Motor 1 center, Motor 2 right. Give the motors their natural black/silver materials rather than tinting them green. Preserve the motor asset's aspect ratio and use roughly 400–450 px width on a 2600–2800 px canvas. A little extra canvas height, around 1750–1850 px, is preferable to squeezing the functional keys between motor art and bus routing.

The electrical layer remains flat and exact. Keep positive and motor return in a dedicated upper corridor, paired A/B in a lower corridor, and functional pigtail keys below each motor. Avoid passing wires over the rendered motor housing. A single neutral harness indicator may point toward each detached key, but individual socket cavities must not be assigned functions. Keep the dashed key visibly separate, and label it “Pigtail functions” locally. Add short “PAIR 1 · IN” and “PAIR 2 · ONWARD” labels if they fit without crowding; Motor 2's second group becomes “SPARE · INSULATE.”

Use a compact title such as “Two-motor connection” and let “Parallel power · shared RS485 bus” be the secondary line. Device names should align and use the same typographic hierarchy. The actual connector function labels deserve more weight than the description of the picture's style or landmarks. A small brand eyebrow can remain, but avoid a large headline that competes with the diagram.

Suggested native type scale for a 2600 px composition intended for 1300 px desktop viewing:

- Title: 50–56 px.
- Device names: 36–40 px.
- J1/J2 and pigtail functions: 30–34 px; J2 row pitch can stay around 40–44 px.
- Local reference/PD/pair-link notes: 26–28 px.
- Secondary artwork/antenna labels: 22–24 px only if genuinely secondary.

For a later 180 mm print-width adaptation, core labels would need approximately 40 px native to reach about 8 pt. The desktop scale above is not a promise of print legibility.

Treat the supply as a small restrained card with precise “20 V-capable USB-C PD” wording. The existing dark green card has high visual weight; reducing its fill area or making it an outlined white card will keep attention on the connection task. Keep USB-C power cable gray so it is distinguishable from the black DC return network.

Use the same slightly rounded stroke joins, white crossing separation, branch-dot rule, and limited net palette throughout. A product asset already supplies enough texture; added glows, heavy shadows, cable gradients, and 3D badges would reduce the clarity of the exact overlay. Very light grounding shadows beneath the products are sufficient if the transparent asset needs anchoring.

Controller art can stay visibly schematic with truthful connector landmarks; that is an honest combination with illustrative motor artwork when the caption states the drawing's status. Alternatively an actual controller photo could match the motor's detail level, but it would require a fresh physical-endpoint audit. Do not introduce that complexity merely to make the two rendering styles identical.

## Premium review gates

1. Motor image is placed at true aspect and the white six-contact connector stays visible.
2. No colored electrical line enters an unverified cavity or an arbitrary PCB pad.
3. The schematic functional key is visibly detached from the rendered connector face.
4. J1/J2 physical landmark relationships, eight contacts, and selected pins remain exact.
5. White crossing gaps remain visible after adding assets or shadows.
6. At 1300 px width, every connection label can be read without mentally reconstructing tiny text. At 900 px, overview plus zoom is acceptable; do not pretend all instructions are readable.
7. A/B internal continuity and separately insulated spare pair remain explicit; typography changes must not remove that information.
