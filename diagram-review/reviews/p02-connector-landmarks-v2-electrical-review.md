# p02 connector landmarks v2: electrical and physical review

**Graph decision: pass. Presentation decision: repair before acceptance.** Reviewed the PNG at original resolution, route JSON, SVG polyline coordinates, and `build_physical_candidates.py`.

## Independent source comparison

The check loaded `reviews/canonical-netlist.json`, which was derived independently from controller and motor PCB pad nets. It normalized `J1.n`/`J2.n` to controller endpoints and `MotorN.n` to motor J4 contacts.

- All eight required external wire paths exist in the eleven declared routes.
- Every controller/motor endpoint is on its correct independently sourced net class; no splice identifier is shared across unlike nets.
- Every route starts and ends at its declared anchor coordinates.
- Each route JSON polyline has exactly one matching nonwhite SVG polyline.
- The rendered power graph is parallel: J1 positive to both V+ inputs and J1 GND to both power returns.
- J2 contacts 1/2/3 are visibly the first three contacts of an actual eight-contact header. The pin order agrees with the selected component-side orientation.
- Motor 1 first A/B pair receives the controller bus; second A/B pair continues to Motor 2 first pair. The motor pair equivalences are correct by source, with the illustration stating A pairs and B pairs are linked.
- Motor 2 second pair is visibly insulated separately. White crossing gaps distinguish unlike nets; actual power branch nodes have dots. No visual short found.

The JSON does **not** include the USB cable, spare insulation stubs, gray neutral fanout, or physical mating features. Passing the graph check does not validate those features or make their geometry electrically continuous.

## Required repairs

1. **Expose J5 PROGRAM.** Its text is covered by the ESP32 module. Move the label or module so the two USB functions can be read distinctly. This is already known to the main agent.
2. **Make the separate J2 reference lead explicitly optional.** The existing `J1/J2 GND are already common` note is correct. However, the bottom instruction `Use J2 pins 1 / 2 / 3 for GND / A / B` still reads as a requirement to install the extra pin-1 lead. Label the thin lead `Optional GND reference` and write the instruction as `J2 pins 2 / 3 = A / B. Pin 1 reference lead is optional with the J1 ground return connected.` The heavy J1 return must remain the motor-current path. Removing the optional lead entirely is also electrically valid, provided the existing shared reference is explicit.
3. **Remove the six neutral-loom hairpins.** In code each gray strand goes from `y+429 = 899` upward to `870`, then back down to the strip top at `905`. It therefore exits the plug bottom and doubles back into its body before fanning outward. Begin the fanout at the plug's bottom and route it downward directly, with enough vertical distance to separate six strands.
4. **Resolve the strip's physical-versus-mapping ambiguity.** Gray strands stop at strip top `y=905`; colored tails start at `y=956` and terminate on the routes at `973`. The intervening function labels do not create electrical continuity. The footer says the strip shows functions rather than face geometry, which appropriately avoids an invented mating-face order. For an actual wiring illustration, either connect each gray strand continuously to its colored tail around/behind a label, or explicitly label the strip `Functional mapping inset` and style it as a separate diagram connected to the real loom by a non-electrical leader. Do not present six interrupted strands as a physically continuous pigtail.

## Remaining noncritical improvements

- Replace `keep each pair together` with `route each A/B pair twisted together` or add a small paired-cable cue. The wide separated colored paths are readable abstract routing but do not depict recommended cable construction by themselves.
- The J1 two wire mouths, separate screws, header mating sockets, distinct USB landmarks, and six-contact motor housing substantially improve physical identity. Maintain those features during label/layout repairs.
- The neutral loom and explicit functional strip deliberately avoid claiming a left/right mating-face pin orientation, which remains unverified. Keep that limitation honest.
- The `20 V nominal after PD negotiation` note correctly describes J1 behavior. No unsupported board current rating is introduced.

No repair to the four-net topology is requested. Required changes concern readable identification, an optional lead instruction, and physical continuity/representation at the motor loom.
