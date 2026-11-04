# p03 connector landmarks v3

**Decision: accepted within its stated scope: schematic controller connector landmarks plus detached motor functional keys. No remaining blocking electrical issue found.** It does not claim a motor mating-face pin orientation.

Viewed the PNG at original resolution and revalidated the route JSON against the independent canonical netlist and actual SVG polylines. All eleven routes use the correct source net classes, all eight required external paths exist, every route meets its declared anchors, and every declared route matches exactly one nonwhite SVG polyline. No unlike-net junction found visually.

The p02 repairs are effective:

- J5 PROGRAM is readable and distinct from J3 PD POWER.
- Both the top annotation and bottom instruction make the separate J2 pin-1 reference lead optional. The substantial J1 motor-current return remains intact.
- The six hairpin strands are removed. A neutral bundle stub identifies the pigtail without claiming a physical contact order.
- The dashed, visibly detached function keys are sufficiently separated from the motor housing. Wires attach to labeled functional endpoints, while the text identifies the key rather than pretending the wires physically traverse the air gap.
- Eight actual J2 contacts retain the correct order, and the selected three wire endpoints enter their mating socket landmarks.
- Positive and return reach distinct J1 apertures, not the screws. Motor power remains parallel; Motor 1 duplicate A/B continues to Motor 2, whose spare pair is separately capped.

At native image size the labels are readable and no electrical endpoint is obscured. Keep the declared scope and detached-key treatment in later variants. A photorealistic motor asset must retain a clearly separate functional key; adding individual wires directly to its exposed unmated contacts would reintroduce the original physical problem.

Nonblocking improvements: use explicit `twisted pair` wording in place of only `keep each pair together`; update route-JSON notes to describe a neutral bundle stub and detached function key rather than a gray individual-wire loom. The graph still omits mechanical USB cable and capped-spare geometry, so those remain visual checks.

Publication-size limitation: this 2600×1600 diagram has small annotations designed for standalone viewing/zooming. Shrinking it into the original draft PDF's approximately 500-point-wide, 245-point-high figure slot would make those annotations too small and change its aspect ratio. Any later PDF placement needs its own actual-size layout review; standalone acceptance does not approve that placement.
