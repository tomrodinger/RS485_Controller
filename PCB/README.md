# PCB revision guide

- `0.5/`: latest numbered design. Schematic and PCB revision fields are 0.5, dated 2025-11-29. Production outputs and assembly CSVs are included as supplied.
- `0.2/`, `0.1/`: historical revisions.

Open the matching `.kicad_pro`, then its root schematic. Footprints and symbols used by a design are embedded in the PCB and schematic. Some historical library-table entries still refer to the original designer's local libraries; replacing a symbol may require configuring those libraries.

Do not use the ignored historical `0.5.xml` export as a source for the controller pinout: it describes an older, different adapter. Regenerate netlists from the current root schematic. The revision 0.5 schematic marks R31 (62 kΩ) as DNP; the standard PD request uses R27 (200 kΩ) alone.
