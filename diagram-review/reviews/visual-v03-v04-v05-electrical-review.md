# Revised functional maps v03, v04, v05

All three PNGs viewed at original resolution. **No hard electrical veto.** They remain functional maps, not physical mating-face or wire-installation drawings.

v03 and v04 retain correct parallel J1 supply/return and correct J2 → Motor 1 first pair → Motor 1 second pair → Motor 2 first pair routing. They now state A3=A5 and B4=B6, successful PD negotiation, twisted A/B pairing, and optional external J2 ground reference. Motor 2 spare A/B are separately capped.

v05's two panels also preserve the graph: the second panel fades the existing parallel power/return rather than removing them; active data reaches contacts 3/4 on Motor 1 and continues from 5/6 to Motor 2 contacts 3/4. The optional thin J2 reference reaches the existing substantial ground-return node. Distinct spare insulation remains visible.

Two minor instruction repairs were sent to the author:

- v04 bottom pin-table instruction still says `Use pins 1 / 2 / 3`. Make pin 1 explicitly optional there too, e.g. `Use pins 2 / 3 for A/B; pin 1 is an optional reference.`
- v05 `Connect power first` should communicate the wiring sequence: `Wire parallel power, then the bus—all with power off.` The existing bottom text already says to wire with power off, but the leading instruction should agree.

No additional routing changes requested.
