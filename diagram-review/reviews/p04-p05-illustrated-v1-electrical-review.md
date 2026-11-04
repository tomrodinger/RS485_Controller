# Illustrated motor variants p04 and p05

Candidates: `p04-illustrated-natural-v1` and `p05-illustrated-stylized-v1`, PNG/SVG/route JSON under `diagram-review/candidates/`.

**Electrical decision: both pass. No additional hard veto.** The known touching GND/V+ labels in each detached function key require the already planned spacing repair before final presentation acceptance.

Both PNGs were viewed at original resolution. The stylized motor connector was additionally enlarged: six contacts are visible. Neither candidate attaches an individual wire to a generated motor contact or claims a mating-face pin orientation. The realistic motor artwork remains distinct from the dashed electrical function key, with the instruction `Use the supplied six-wire pigtail`. Its open/unmated connector therefore does not purport to be a completed physical connection. Maintain that separation and instruction.

The reproducible validator passed both candidates:

```sh
python3 diagram-review/reviews/validate_candidate_routes.py \
  diagram-review/candidates/p04-illustrated-natural-v1.routes.json \
  diagram-review/candidates/p05-illustrated-stylized-v1.routes.json
```

For each: eleven actual declared routes, all eight independently sourced required external paths, three evidence hashes verified, J2 selected contacts 1/2/3 correct, no merged source net classes, correct motor internal equivalence, exact anchors, and exact matching SVG polylines/colours/widths/basic visibility.

Visual trace confirms distinct J1 positive/return mouths, heavy parallel motor returns, optional separate J2 reference lead, first A/B pair into Motor 1 and second pair onward to Motor 2, and separately insulated Motor 2 spare A/B ends. No wire endpoint is obscured by motor artwork. J3 and J5 are correctly identified.

Remaining nonblocking advice: use explicit `twisted pair` wording rather than only `keep each pair together`; review at the actual intended export/display size. Machine coverage remains limited as printed by the validator: mechanical cable, connector count/orientation, detached key geometry, caps, crossings, and raster readability still require visual review.
