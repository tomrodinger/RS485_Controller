# RS485 Controller wiring-diagram review

## Current accepted state · 4 November 2026

The owner selected **r2-05-natural-pigtails**. The original chosen PNG is the only image in `exports/round2-pngs/`. The updated accepted illustration is [`../datasheet/assets/connection-v0.4/two-motor-connection-v0.4.pdf`](../datasheet/assets/connection-v0.4/two-motor-connection-v0.4.pdf), with SVG, PNG and route JSON alongside it. It adds functional J2 labels and a computer USB lead to J5 PROG. It is already embedded on page 5 of the publicly released [datasheet v1.0](../datasheet/rs485_controller_datasheet_v1.0.pdf).

The [maintainer handoff](../datasheet/README.md#maintainer-handoff--4-november-2026) is the authoritative continuation guide. The sections below record the earlier candidate rounds; their intermediate datasheet versions are archives. Earlier instructions to wait for the owner's selection have been fulfilled.

The live gallery remains private and its separate `site/` checkout is clean at already-pushed commit `9aaf98d04907540a09e6b17345a3de8645c17c3c`. It is excluded from the public repository. Reusable diagram builders, artwork, historical candidates and audit results outside that checkout are retained here. The temporary browser runners have expired; their structured results remain under `reviews/qa/`, and the app's unit tests remain in the private checkout.

Private review gallery: **https://gearotons-rs485-wiring-review.lovelymelon513.chatgpt.site**

Five new natural-material variations appear first, followed by the six original proposals. Use **Expand diagram**, zoom, compare two candidates, then give each a star rating and comments. Feedback saves to the signed-in account, with a local browser backup and JSON export/import. **Download new PNGs** provides the five round-two images. Existing image IDs and assets are preserved so prior feedback remains associated with the original drawings.

## Round two · 27 October 2026

| Gallery direction | PNG | Representation |
| --- | --- | --- |
| Natural pigtail illustration | [r2-05-natural-pigtails.png](exports/r2-05-natural-pigtails.png) | Curved wiring, shared rear wire exit on white motor plug, single two-cavity black A/B housings |
| Photo harness map | [r2-01-photo-harness.png](exports/r2-01-photo-harness.png) | Actual controller photograph and detached motor function keys |
| Illustrated component panels | [r2-02-precision-harness.png](exports/r2-02-precision-harness.png) | PCB-derived component placement and natural motor artwork |
| Photo field guide | [r2-03-photo-field-guide.png](exports/r2-03-photo-field-guide.png) | Portrait layout with controller connection explanations |
| Illustrated field guide | [r2-04-illustrated-field-guide.png](exports/r2-04-illustrated-field-guide.png) | Portrait layout with a PCB-derived controller |

[Download the round-two PNGs](exports/round2-pngs.zip). The [18-page datasheet v0.2](../datasheet/rs485_controller_datasheet_v0.2_review.pdf) is an intermediate archive from this round. It was superseded by the approved public datasheet v1.0.

Build artwork with `python3 diagram-review/round2/build_round2.py`. Check electrical routes and paired connector shells with `python3 diagram-review/reviews/validate_round2_harnesses.py`. Preparation of the existing private gallery uses `prepare_round2_gallery.py`; publication follows the Sites workflow. Session/deployment evidence is retained in `review-session-round2.json`, with image hashes and browser checks under `reviews/qa/`.

Motor plug mating-face order is not specified by the artwork. The physical harness variation uses a covered rear exit to avoid assigning colours to unverified visible cavities. All main ground and positive power paths retain equal thickness. The independent route validator also checks curved routes against declared electrical endpoints and constrains every rounded bend to its adjacent route segments.

## Original round-one PNGs

The exact published files are also in `exports/`:

| Gallery direction | PNG | Representation |
| --- | --- | --- |
| Electrical map | [electrical-map.png](exports/electrical-map.png) | Explicit functional circuit map |
| Photo-guided map | [photo-guide.png](exports/photo-guide.png) | Actual controller port locator beside the circuit map |
| Power first, then data | [two-step.png](exports/two-step.png) | Two-stage explanation; all wiring is done with power off |
| Connector landmarks | [connector-landmarks.png](exports/connector-landmarks.png) | Service-manual controller drawing and exact wiring |
| Natural-material illustration | [natural-illustration.png](exports/natural-illustration.png) | AI-created motor artwork with exact vector connections |
| Restrained cartoon illustration | [stylized-illustration.png](exports/stylized-illustration.png) | More diagrammatic AI motor artwork with exact connections |

[Download the six-PNG bundle](exports/rs485-controller-six-diagram-candidates.zip).

These are schematic preference drafts. Motor function keys are deliberately detached from connector-face geometry. The verified six-lead electrical sequence is GND / V+ / A / B / A / B; the duplicate A/B pair continues the bus to Motor 2. Both motor power returns connect to the controller's common ground. J1 and J2 ground are already common on the PCB, so a separately drawn J2 reference lead is optional when J1 establishes that ground.

## How the images were produced

The initial fully generated replacement failed adversarial review and is retained only in working history. It connected power/return to the same terminal, changed the header count, and omitted parts of the bus continuation. It is excluded from the gallery and download bundle.

The selected illustrated variants combine motor artwork created with the built-in **image_gen** tool and deterministic SVG wires/labels. Their prompts are saved in [prompts](prompts/): [full-diagram attempt](prompts/01-flat-technical.txt), [natural motor asset](prompts/02-motor-asset.txt), and [stylized motor asset](prompts/03-stylized-motor-asset.txt). Selected art is in `working/`; editable diagram SVGs sit beside their PNGs in `candidates/` and `visual-candidates/`.

Builders: `build_physical_candidates.py`, `build_premium_candidates.py`, and `visual-candidates/build_candidates.py`. They require Python 3 and `rsvg-convert`; the source photographs and generated art are embedded by the SVG builders. The sources retain earlier drafts rather than overwriting their PNGs.

## Independent checks and limitations

Electrical and visual adversaries reviewed real controller photos, revision 0.5 KiCad nets, motor documentation and motor PCB J4. The route validator uses an independently extracted canonical netlist, not a count of the renderer's own wires. It checks required paths, four disjoint nets, actual selected contacts, internal motor A/B links, endpoint coordinates and matching SVG paths. It also rejects deliberately faulty examples. It does not claim to validate mechanical mating geometry or physical current ratings.

Run a source-level route check with:

```sh
python3 diagram-review/reviews/validate_candidate_routes.py \
  diagram-review/candidates/p03-connector-landmarks-v3.routes.json \
  diagram-review/candidates/p06-illustrated-natural-v2.routes.json \
  diagram-review/candidates/p07-illustrated-stylized-v2.routes.json
```

Review notes are in `reviews/`. The API/sync/viewer code passed 18 unit tests. A fresh browser passed 13 workflow checks, including D1 persistence, cross-context account loading, rapid edits, offline recovery, export, filtering, independent comparison zoom, mobile overflow and PNG decoding. Three additional browser checks covered expanded viewing/focus return, mobile expansion and bundle download. Evidence is in `reviews/qa/`.

The gallery source is in `site/`, with its own private Sites Git repository. It is separate from the public controller repository. `review-session.json` records exact candidate hashes, native Site identifiers, source commit and deployment state. No external API key is stored in the source or site.

## Retrieve the owner's feedback

When the owner asks for revisions, use the Sites native database tools with project ID `appgprj_6adf3d35bc9081918dbbf9957d7e9fb8`. The deployed D1 binding is `DB`; the table returned by the native overview is `diagram_feedback`. Read ratings/comments with `read_database_table_rows`. Do not expose user IDs or publish comments without authorization.

Retain stable candidate IDs when revising a direction. Increment its revision and use a new image filename so the reviewed image is unambiguous and browser caches cannot silently show an earlier revision. The gallery warns when existing notes belong to an older revision. Publish the selected diagram into the datasheet only after the owner reviews it.
