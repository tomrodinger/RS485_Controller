# Reproducible candidate route validation

Run from the repository root:

```sh
python3 diagram-review/reviews/validate_candidate_routes.py diagram-review/candidates/p03-connector-landmarks-v3.routes.json
```

Multiple route JSON files can be supplied. Each must have an adjacent SVG with the same basename before `.routes.json`. Add `--json` for structured output or `--canonical PATH` to select an independent canonical model. Only the Python standard library is needed.

The script checks independently sourced PCB contact classes and evidence hashes, motor internal A/B equivalence, required external wire paths, full four-net connectivity and separation from auxiliary rails, selected controller contact functions, separate unused Motor 2 contacts, declared endpoint coordinates, and matching SVG polyline coordinates, colour, width, fill, transforms, and basic visibility. It does not accept an arbitrary fixed route count as proof of correctness.

**p03 result: PASS.** Eleven declared routes, eight required external paths, three source hashes verified; selected controller J2 contacts are 1/2/3.

Six temporary faulty candidates were exercised and correctly rejected: missing Motor 2 power return, wrong J2 header contact, wrong onward A/B net, route displaced from its anchor, wrong rendered signal colour, and an SVG route hidden with zero opacity. The temporary faulty files were not retained as deliverables.

Coverage omissions are printed on every run: mechanical USB cable, omitted capped spare-stub geometry, detached functional-key/body geometry, actual physical contact count and mating-face orientation, raster occlusion/readability, and crossing halos/junction dots. Full CSS rendering and pixel visibility are not simulated. A passing route check complements the visual adversarial review; it does not replace it.
