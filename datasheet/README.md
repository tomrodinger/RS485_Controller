# RS485 Controller datasheet

## Maintainer handoff — 4 November 2026

### Context reset checkpoint — 5 November 2026

Start with this handoff and `../AGENTS.md` after clearing context. The decisions, product corrections, source links and build evidence from the latest documentation work are saved here and in `review/presentation-refresh-v1.0.json`; no chat transcript is needed. All requested product edits are complete and were committed and pushed to `origin/main` on 5 November in `bfe9a90ec0ca8b57887a6d3fc370f0991e329458`. Both the commit-pinned public PDF and the public main-branch PDF were downloaded and matched byte for byte. This documentation checkpoint records the publication evidence; further work should start with the owner's next feedback.

- **Current artifact:** `rs485_controller_datasheet_v1.0.pdf`, 14 pages, SHA-256 `42f08e750f1c0ad086d90d8fa704f87d13df0b1e064e52e3e3b6f62f9cabcdfe`. A fresh rebuild on 5 November reproduced that hash and passed `verify_datasheet_v1_0.py`. The PDF footer retains the content date 4 November 2026 and document version 1.0; hardware remains RS2 / PCB 0.5.
- **Cover and photos:** one detailed board-only component-side image on page 1; larger bold ESP32-S3 description; no large weight, baud-rate or PCB-revision boxes; bright red TX and green RX LEDs listed as a feature. Other product views are on page 14, with the accurate 11.7 g including antenna retained as a small note. Every footer says “Datasheet v1.0”. All four product-photo backgrounds are white.
- **Breakout map:** page 8 shows GPIO43 / TXD0, GPIO44 / RXD0, GPIO4 / RS485TX and GPIO5 / RS485RX, with an explanatory asterisk note. TXD0/RXD0 end in zero. Labels are plain text with no white boxes; faint opposite-face outlines are interrupted behind labels. All 51 source-derived contact positions are preserved.
- **PD and power corrections:** PD CFG / PD VDD / PD PG are HASL-finished plated through-hole pads connected to the CH221K, not spare GPIO. The map shows the pad finish as silver-gray and links the chip datasheet. The chip requests 20 V; if the source instead delivers 15 V or 12 V, M17 motors can still operate. Below 12 V they will likely not work correctly. J5 alone powers/programs the ESP32-S3. A separate motor supply must share controller ground; the documented arrangement powers motors directly and leaves J3 and J1 positive unused.
- **Saved sources:** the current builder and verifier are `generate_datasheet_v1_0.py` and `verify_datasheet_v1_0.py`; map artwork comes from `review/geometry-v4/build_technical_assets.py`. Image masters, exact background-edit prompts, dimensions and hashes are in `../images/rs485-controller/`. Original full-resolution photos remain recoverable from Git history, including commit `ec4ad6f69b8118686cfa3072b01a84e20ae843a9`.
- **Verification and limits:** affected pages 1, 2, 6, 8, 9, 12 and 14 were rendered and visually inspected during the work. Automated checks cover aliases against PCB text/nets, PD-pad drills, no label boxes, white photo backgrounds, power guidance, Arduino preservation, electrical routes and page bounds. No new physical motor, electrical or thermal qualification was performed; retain all unspecified board ratings.
- **Repository boundary:** commit the controller sources, PDF, photo assets and audit records. `diagram-review/site/` is a separate, already-pushed private repository and was clean at this checkpoint; keep it ignored here. Local `.venv-datasheet/`, caches and regenerable page PNGs also remain ignored. Product registration and PCB files are unchanged.

### Current released state

The owner reviewed and approved the 13-page datasheet v1.0 for public launch. It was published in commit `27ee2e222349cd57c9a223fb262a55f6a45d1a2a`; that public download was compared byte for byte with the checked launch PDF. The current **[datasheet v1.0](rs485_controller_datasheet_v1.0.pdf)** is the 14-page presentation and technical-text refresh, still for **PCB revision 0.5**. It was built, verified and visually inspected, then committed and pushed on 5 November in `bfe9a90ec0ca8b57887a6d3fc370f0991e329458`. Its public downloads match the checked PDF. `review/presentation-refresh-v1.0.json` records current publication evidence, while `review/release-v1.0.json` preserves the original launch record.

- Public repository: <https://github.com/tomrodinger/RS485_Controller>.
- Public PDF: <https://raw.githubusercontent.com/tomrodinger/RS485_Controller/main/datasheet/rs485_controller_datasheet_v1.0.pdf>.
- Published launch PDF SHA-256: `4dfcba25a5ceacff20ad8305ac91da044ab4e0c2aef2f2011713c8bd2900cf45`.
- Current published 14-page PDF SHA-256: `42f08e750f1c0ad086d90d8fa704f87d13df0b1e064e52e3e3b6f62f9cabcdfe`. Publication checks and photo-edit provenance are recorded in `review/presentation-refresh-v1.0.json`; `review/release-v1.0.json` retains the original publication record.
- Immutable current PDF: <https://raw.githubusercontent.com/tomrodinger/RS485_Controller/bfe9a90ec0ca8b57887a6d3fc370f0991e329458/datasheet/rs485_controller_datasheet_v1.0.pdf>.
- Product documentation / PCB QR target: <https://9o.at/products/rs2/0.5>.
- `PRODUCT_DATA.yaml` is the documentation registration. Keep `product: RS2`, `version: '0.5'`, `type: pcb`; these identifiers match QR codes on shipped PCBs. Document version 1.0 does **not** rename the hardware to 1.0.
- Public documentation flags are `python: false`, `arduino: true`, `mcp: false`. The firmware list is empty; neither a supplied USB/RS485 bridge nor a ready-made wireless application is promised.
- Later registration commits are `5dac6b27affde5953d283b104ca941a5531c151a` and `eaea1b3426ba397725677de95f0fe8cb84b832da`. Preserve those settings when changing documentation.

The requested presentation refresh is complete: a single detailed board-only photo on the cover, a larger bold ESP32-S3 subtitle, removal of the cover's weight/baud/revision boxes, bright TX/RX LEDs in the feature list, expanded “Datasheet v1.0” footers, and a final page with the three other product views. All four product photographs now have white backgrounds in the JPEG/WebP derivatives. The three board-only views have transparent cutout masters; the antenna-connected view has a white-background master. Page 8 now pairs GPIO43/44 with the exact PCB labels TXD0/RXD0 and GPIO4/5 with RS485TX/RS485RX, explains the aliases and wired RS485 functions in an asterisk note, and uses plain text labels without background boxes. The PD pad description and HASL finish, CH221K datasheet links, 20/15/12 V motor guidance, J5-only programming and separate motor-supply common-ground instructions are also updated. The measured 11.7 g mass remains a small note on the photo page. Keep v1.0 for this requested refresh. The older PDFs and diagram candidates are historical development records; do not use them as the current product download.

### Accepted product facts and limits

- One unit weighs **11.7 g including its attached external antenna**. The antenna ships with the product. This is the owner's measurement, not a new laboratory measurement.
- Module: ESP32-S3-MINI-1U with external antenna connector. Do not infer a specific flash/PSRAM SKU from the module family.
- J5 is **USB-C PROG**, native USB data/programming and 5 V logic input. The computer in the wiring illustration connects here. J5 alone powers and programs the ESP32-S3; J3 and motor power are not required for programming only.
- J3 is **USB-C PD POWER IN**. CH221K with R27 = 200 kΩ requests 20 V in the standard assembly; R31 = 62 kΩ is optional/DNP. If the source cannot provide 20 V and supplies 15 V or 12 V instead, Gearotons M17 motors can still operate. Below 12 V they will likely not work correctly. This is the owner's operating guidance, consistent with the M17 reference's 12–24 V range; it is not new bench qualification or a guarantee of a particular supply's PD negotiation. J3 does not program the ESP32-S3.
- J1 is **MOTOR POWER OUT**: pin 1 is the direct J3 PD VBUS rail, pin 2 GND. It is not a separately regulated 20 V output; the actual voltage depends on PD negotiation. J5 alone does not supply motor power at J1.
- J2 pins 1–8 are **GND, A, B, GND, A, B, 3.3 V, 5 V**. The two RS485 groups share one bus. J1 and J2 ground are common on the PCB; there is no galvanic isolation. The 5 V rail is associated with J5, not generated from the PD input.
- Motors may use a suitable separate external supply: positive goes directly to motor V+, negative to motor GND and controller GND (J2 pin 1 or 4, or J1 pin 2). Keep J5 connected to power the controller. The documented separate-supply arrangement leaves J3 and J1 pin 1 unused, so the two positive supply rails are not paralleled.
- **PD CFG / PD VDD / PD PG are HASL-finished plated through-hole pads**, connected to CH221K CFG / VDD / PG. The PCB source confirms TP47 / TP44 / TP43 respectively with 0.9 mm drills; the HASL finish is owner-confirmed. Pad colours in the map identify electrical function, not metal finish. Link the CH221K sections of the WCH CH224-family datasheet for more detail; do not describe these PD pads as gold surface pads.
- RS485 TX = GPIO4, RX = GPIO5. The example uses **230400 baud, 8N1**. Do not claim this is the maximum board baud rate or that arbitrary firmware is preinstalled.
- S1 = RESET/EN; S2 = PROG/BOOT/GPIO0. D4 = yellow power LED; D5 = green RX LED; D6 = red TX LED.
- Bus components: SP3485EN transceiver, R5 = 220 Ω across A/B, 560 Ω pull-up/pull-down bias and SM712 suppression. Component current/data-rate/temperature/ESD limits are not qualified board limits.
- Board current consumption, continuous motor-power pass-through current, auxiliary output-current ratings, maximum cable length, assembled height, environmental and product ESD/EMC limits are not specified. Keep these limits honest when polishing copy. No physical bench/motion/thermal qualification was performed in this chat.
- PCB outline: **36.88 × 48.89 mm**, nominal thickness **1.6 mm**. Four **Ø1.50 mm** holes have centres **1.50 mm** from adjacent edges, giving **33.88 × 45.89 mm** hole-centre spacing; all corner radii are **R1.50 mm**. These are KiCad design values, excluding connector/antenna overhang, without manufacturing tolerances.

### Accepted document and artwork decisions

The current 14-page layout is: overview; electrical/power; connector locator; pinout/controls; two-motor illustration; wiring reference; detailed dimensions; breakout map; getting started; Arduino IDE library installation; Arduino example; resources; full schematic; additional product photographs. The technical sections retain their established page numbers; page 8 includes the clarified PCB/GPIO aliases and label styling.

1. **Public presentation:** remove all draft badges, owner-review sections, internal file paths, working-tree/provenance commentary and editorial notes from the product PDF. Keep technical limitations and useful wiring instructions. The source/audit records belong in developer documentation, not customer copy.
2. **Programming:** the Python host example was explicitly removed by the owner. Keep the public material Arduino-only. The Arduino program remains byte-for-byte the M17 v1.10 reference; the snapshot is `assets/examples-v0.2/arduino_library_example.cpp`, with provenance in `review/example-provenance-v0.2.json`. Do not silently replace it with the newer Servomotor working-tree program.
3. **Installation:** use the four Arduino IDE Library Manager steps and original `arduino_library_installation.png` from the M17 datasheet. The screenshot shows a Tools menu route and an ESP32-C3 selection; the caption correctly directs this controller's user to ESP32-S3.
4. **Chosen wiring style:** the owner first preferred `natural-illustration.png`, then selected **`r2-05-natural-pigtails.png`** by deleting the other images from `diagram-review/exports/round2-pngs/`. That folder contains the one original selected PNG. Preserve that selection and do not repopulate the pruned folder with candidates.
5. **Current wiring illustration:** the derivative used in the release is `assets/connection-v0.4/two-motor-connection-v0.4.pdf`, with adjacent editable SVG, PNG and route JSON. It retains the natural motor art, a PCB-derived controller, single black two-cavity A/B housings, a white six-way motor plug, equal-width ground/positive wires, J2 function labels, and a laptop with a purple USB data lead to **J5**. The separate PD source connects to **J3**. It occupies landscape page 5.
6. **Motor connector accuracy:** six functional leads are GND / V+ / A / B / A / B. Each A/B pair has one shared black two-cavity housing with insulated contacts. Duplicate A contacts and duplicate B contacts are internally linked in the motor. Use parallel power and an A/B chain through Motor 1 to Motor 2. The spare Motor 2 pair must never be shorted. Motor mating-face cavity order remains unverified: the selected illustration uses a covered rear wire exit, not a colour-to-visible-cavity pinout. Twisting A/B was optional for the illustration; real wiring instructions recommend a twisted pair.
7. **Locator:** page 3 uses curved coloured dashed leaders instead of overlapping black L-shaped leaders. Both this locator and the wiring controller label all eight J2 contacts by **function**, not standalone numbers. The pinout table may still give pin numbers for reference.
8. **Mechanical inset:** page 7 shows a single broken-out PCB corner with jagged crop edges, not an oval/fully rounded closed tile. Preserve the checked hole, inset and radius dimensions.
9. **Breakout map:** page 8 is one large vector diagram titled **Breakout headers — solder required**, with all **51 pads individually labelled by signal** using plain text without background boxes. GPIO43/TXD0, GPIO44/RXD0, GPIO4/RS485TX and GPIO5/RS485RX show both names, with an asterisk note explaining UART0 aliases and the wired RS485 logic signals. TXD0/RXD0 end with the digit zero. It explicitly shows the rear/label side **F.Cu**, with USB sockets and module on the opposite face drawn as dashed silhouettes. It labels J5 PROG and J3 PD POWER IN. Breakout headers are **not fitted**; users must solder headers or wires. This statement does not refer to the separate fitted J2 RS485 header.
10. **Breakout scope:** 43 through-hole pads comprise 36 GPIO-linked pads, four GND and three PD-control points; eight additional contacts expose existing RS485 / auxiliary rails and GND. Preserve the source-derived geometry of all 51 contacts. PD CFG / PD VDD / PD PG are HASL-finished plated through-hole pads for the CH221K, not GPIO. The current map shows a silver-gray pad finish and links the chip documentation. The five former regional enlargements and separate lookup page were removed; do not restore those pages. GPIO4/5 are shared with onboard RS485, GPIO43/44 are UART0, GPIO19/20 carry native USB, and GPIO0/3/45/46 are strapping signals.
11. **View transforms:** source PCB bounds are x = 36.65…73.53, y = 103…151.89 mm. Component-side (B.Cu) drawing coordinates are `u=x−36.65, v=151.89−y`; rear/label-side (F.Cu) coordinates are `u=x−36.65, v=y−103`. Component-side USB sockets are at left and J2 at right; the original J2 pin 1 is at the top in that view. Do not swap view orientation when editing labels.
12. **Schematic:** use the full `PCB/0.5/schematic/0.5-index-schTop.pdf` with the ESP32 module as a block, not expanded internals. Release preparation removes only the internal “Later change this 47pF capacitor to 56pF…” comment from a presentation copy. **C17 remains 47 pF and the hardware/source schematic remains untouched.** Verification checks circuit text/values, circuit ink and pixels outside the removed comment. The official Espressif module datasheet is linked from the product document.

### Build and verification from this repository

Use a local ignored environment; do not depend on a temporary `/tmp` environment surviving. The pinned dependencies are ReportLab 4.1.0, Pillow 10.4.0 and PyMuPDF 1.26.5 in `requirements-v0.2.txt` (the filename is historical). `rsvg-convert` must also be available.

```sh
python3 -m venv .venv-datasheet
source .venv-datasheet/bin/activate
python -m pip install -r datasheet/requirements-v0.2.txt
python datasheet/review/geometry-v4/build_technical_assets.py
python datasheet/review/geometry-v4/build_connection_illustration.py
python datasheet/review/prepare_release_schematic.py
python datasheet/generate_datasheet_v1_0.py
python datasheet/verify_datasheet_v1_0.py
python datasheet/review/render_release.py
```

The first two steps regenerate source-derived technical figures and the current natural wiring art. Their dependencies deliberately include `review/geometry-v2/build_technical_assets.py`, `assets/technical-v2/pcb-geometry.json`, `diagram-review/round2/build_round2.py`, and `diagram-review/working/motor-asset-v1.png`. Preserve those files even though the release uses newer output paths. Do not regenerate the historical geometry or canonical example snapshots merely to rebuild current artwork.

The verifier requires the archived v0.1–v0.4 PDFs to prove they were preserved. It checks all 51 rendered pad labels against checked geometry, J2 names against PCB nets, source hashes, disjoint power/ground/A/B nets, the computer's actual SVG route to J5, the unchanged Arduino program, the M17 screenshot, the Espressif link, vector schematic preservation, document navigation, absence of draft/internal/Python content and page bounds.

Electrical route checking is independently implemented in `diagram-review/reviews/validate_candidate_routes.py` and its `canonical-netlist.json`. The canonical file retains audited source contact nets and raw-file hashes. Some evidence comes from the sibling `../Servomotor` repository; on a machine without that repository, the route checker reports reduced source-hash coverage rather than inventing mechanical orientation.

Key audit files are `review/build-v1.0.json`, `review/verification-v1.0.json`, `review/release-v1.0.json`, `review/presentation-refresh-v1.0.json`, `review/release-schematic-cleanup.json`, `review/geometry-v4/label-legibility-check.json` and `review/v1.0-pages/render-manifest.json`. Large generated page PNGs and preview screenshots are ignored and can be recreated with the render command. Inspect affected pages after any layout change. The owner requested that the current presentation refresh retain “Datasheet v1.0”; choose document revisions independently of PCB identity RS2/0.5 for later editions.

Original checks recorded in `review/verification.json` include **392 design checks**, KiCad 9.0.7 error-level DRC with zero violations/unconnected/parity issues, and successful compilation of the three separate Arduino demos with ESP32 Arduino core 3.3.3 and Servomotor library 0.10.1. The diagnostic C++ example needed a forward declaration. These records are design/compile checks, not hardware qualification.

### References and locations

- M17 reference sources: `../Servomotor/servomotor_datasheets/`. The Arduino snapshot was recovered from Servomotor commit `2bfca710f68febd80bb758b819c6d12523d7bf25` to match published M17 v1.10. The installation screenshot/steps were checked against the later local English datasheet too. Retained snapshots and hashes make the controller build independent of changing sibling example files.
- Visual style reference: `../RS485_adapter_git/datasheet/` and the M17 datasheets. These are references, not release build dependencies.
- Real controller photographs: `images/rs485-controller/`, already public since `ec4ad6f69b8118686cfa3072b01a84e20ae843a9`. Metadata-free JPEGs, WebP originals and smaller ecommerce variants are listed in `manifest.json`. The photos originally came from the owner's SharePoint folder; use the retained assets rather than depending on the expiring share link.
- Manufacturer PD reference: `../datasheets/CH224K.pdf` relative to this directory. The relevant configuration is the **CH221K** table; do not substitute the CH224K resistor table. The public PDF links the official WCH download page at <https://www.wch-ic.com/downloads/CH224DS1_PDF.html> from the breakout map and resources page.
- Official module reference: <https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf>.
- Unfinished pre-existing hardware is preserved in `PCB/V1_not_completed/` as a development archive; it is not the released product or production package.

### Private gallery and context recovery

The preference gallery remains owner-private at <https://gearotons-rs485-wiring-review.lovelymelon513.chatgpt.site>. It supports stars/comments, account-backed D1 persistence, local backup, export/import, independent zoom/expanded viewing and two-image comparison. It contains the original six directions and five round-two variants; the owner selected the natural pigtail direction in chat and by the single-file folder, not by a required star rating.

`diagram-review/site/` is a **separate private Git checkout**, not a submodule of this public repository. Its already-pushed source commit is `9aaf98d04907540a09e6b17345a3de8645c17c3c`, with a clean working tree at this checkpoint. Exact project identity is in its `.openai/hosting.json` and `diagram-review/site-registration.json`; source/deployment identifiers are retained in `diagram-review/review-session*.json`. Feedback uses D1 binding `DB`, table `diagram_feedback`. Use the Sites tools/skill for future website work, preserve the current audience, and do not publish feedback or credentials. Keep existing candidate IDs; increment revisions and use new asset filenames for changed drawings.

The app's private Git repository is already backed up separately. Its Git database, dependencies, build output and feedback database are excluded from public Git. Review-gallery source archives outside that checkout contain no credentials. The built-in image generation tool produced the motor art; the external API key provided in chat was never used or saved and must not be copied into any handoff or source file.

Read `diagram-review/README.md` and the retained electrical/visual adversarial reviews if further illustration changes are requested. The initial fully AI-generated wiring attempt was rejected for incorrect electrical connections; use the selected motor art with deterministic geometry/wires, not that rejected image.

## Public release · version 1.0

[Open datasheet v1.0](rs485_controller_datasheet_v1.0.pdf). This is the public release for PCB revision 0.5. Draft badges, owner-review notes, internal source/provenance commentary and the schematic's future-change note have been removed. The published operating limitations, circuitry, pad labels and unchanged Arduino example are retained. Earlier working editions remain archived locally.

Build and verify using the dependencies in `requirements-v0.2.txt`:

```sh
python datasheet/review/prepare_release_schematic.py
python datasheet/generate_datasheet_v1_0.py
python datasheet/verify_datasheet_v1_0.py
python datasheet/review/render_release.py
```

The schematic preparation edits a presentation copy only. It checks that all source circuit text and values remain, that only blue annotation ink is removed, and that no pixels outside the comment change. Release verification checks the absence of internal editorial text, preserved technical limits, diagrams, example code and links. Evidence and page renders are retained under `review/`.

## Revision 0.4 review draft

[Open the revised PDF](rs485_controller_datasheet_v0.4_review.pdf). It is now 13 pages. The component locator uses curved coloured dashed leaders, and both that locator (page 3) and the wiring illustration (page 5) label J2 contacts by signal instead of number. The updated wiring drawing adds a computer with a USB data cable to J5 PROG; the PD supply remains at J3.

The mechanical drawing (page 7) uses a broken-out corner fragment with jagged crop edges, preserving the checked hole diameter, corner radius and edge insets. Page 8 is one large vector drawing titled **Breakout headers — solder required**, with every one of the 51 pads labelled at its physical position. It states the rear/label-side F.Cu view, locates the USB sockets on the opposite face, distinguishes surface service pads, and makes clear that breakout headers are not fitted. The five regional blow-ups and separate pad lookup page have been removed.

```sh
python datasheet/review/geometry-v4/build_technical_assets.py
python datasheet/review/geometry-v4/build_connection_illustration.py
python datasheet/generate_datasheet_v0_4.py
python datasheet/verify_datasheet_v0_4.py
python datasheet/review/geometry-v4/render_review.py
```

Use the dependencies in `requirements-v0.2.txt`; `rsvg-convert` is also required to export the SVG figures. New drawings are isolated in `assets/technical-v4/` and `assets/connection-v0.4/`. Verification checks all 51 rendered pad labels against the unchanged checked geometry, derives J2 function order from actual PCB pad nets, validates the electrical routes and computer-to-J5 SVG route, and checks the PDF for omitted/obsolete sections and preserved Arduino/M17/schematic content. This is an archived intermediate edition; the original selected PNG and earlier PDFs are preserved. The current product document is public release v1.0.

## Revision 0.3 review draft · 3 November 2026

[Open the revised PDF](rs485_controller_datasheet_v0.3_review.pdf). The Python program and host setup are removed. The Arduino IDE installation page reproduces the four M17 Library Manager steps and its original screenshot. The existing Arduino example remains unchanged.

The selected diagram was found in `../diagram-review/exports/round2-pngs/`, which contains only `r2-05-natural-pigtails.png`. That exact PNG is copied to `assets/selected-v0.3/two-motor-connection.png` and embedded on landscape page 5. In this archived edition the installation guide is on page 16 and the Arduino program is on page 17. It has been superseded by public release v1.0.

Using the dependencies in `requirements-v0.2.txt`:

```sh
python datasheet/generate_datasheet_v0_3.py
python datasheet/verify_datasheet_v0_3.py
```

Source selection, hashes and screenshot provenance are recorded in `review/sources-v0.3.json`; build and verification evidence are in `review/build-v0.3.json` and `review/verification-v0.3.json`. Review renders are in `review/v0.3-pages/`. Verification checks that the selected diagram and M17 screenshot retain their original pixels inside the PDF, that the four installation steps match the M17 source/PDF, and that Python content is absent.

## Revision 0.2 review draft

The v0.2 review edition is built with `generate_datasheet_v0_2.py`; the v0.1 PDF and its original `generate_datasheet.py` builder are preserved. The new edition has no fixed page budget. It adds a complete connector/switch/LED locator, detailed mechanical dimensions, full-board and individually labelled expansion-pad views, the two unchanged programs from the latest English M17 datasheet, and a vector full-controller schematic appendix with the ESP32 module kept as a black box.

Install `requirements-v0.2.txt` in a Python virtual environment, then run:

```sh
python datasheet/generate_datasheet_v0_2.py
```

Technical figures live in `assets/technical-v2/`. The builder requires verified `connector-locator.pdf`, `mechanical-dimensions.pdf` and `gpio-overview.pdf` figures, plus detailed GPIO views. A `figures.json` file may map the figure keys `locator`, `mechanical`, `gpio-overview`, and `gpio-detail` to alternative filenames. `gpio-detail-a.pdf`, `-b.pdf`, etc. are automatically included as dedicated region pages. When these enlargements exist, a duplicate `gpio-detail.pdf` key is omitted; otherwise that file provides the detailed view. The checked `pcb-geometry.json` supplies a complete 51-reference pad table. PDF figures are embedded as vector content with PyMuPDF. The `--allow-missing-figures` option exists only for interim layout work and clearly marks missing figures; it must not be used for the completed owner-review PDF.

The prior `two-motor-connection-ai.png` is excluded from v0.2. By default the new edition uses a precise connection table and wiring instructions. An owner-selected natural illustration may be supplied with `--connection-illustration PATH`; it remains labelled as a review draft.

The canonical Python/Arduino snapshots are in `assets/examples-v0.2/`. Their byte hashes and correspondence to `datasheet_latest_en.pdf` version 1.10 are recorded in `review/example-provenance-v0.2.json`. The current Arduino working-tree example differs from that published PDF, so the matching source revision was recovered rather than substituting newer code. The builder verifies the snapshot hashes and does not adapt the listings. Python host/serial-transport and Arduino board setup notes remain outside the code.

`review/build-v0.2.json` records page layout, vector-asset hashes, code hashes and the output PDF hash. The landscape appendix embeds `PCB/0.5/schematic/0.5-index-schTop.pdf` as vector content on an A3 page. The official Espressif ESP32-S3-MINI-1 / MINI-1U PDF is linked directly from the document. Render and inspect every page before delivery; generated review renders belong in `review/v0.2-pages/`.

Run `python datasheet/verify_datasheet_v0_2.py` after building. This checks the preserved v0.1 hash, canonical snapshot and emitted-code correspondence, all 51 pad references, the official module hyperlink, and preservation of the source schematic's vector drawing paths. PDF bookmarks provide direct navigation to every section.

## Preserved revision 0.1

`rs485_controller_datasheet_v0.1_review.pdf` is the archived six-page A4 initial draft for PCB revision 0.5, retained as verification/history input. The supplied antenna is included in the stated 11.7 g mass. Only the current v1.0 PDF is the product release.

The pages cover the product overview, electrical and power behavior, connector pinout and controls, a two-motor connection diagram including common ground, mechanical geometry and expansion, and programming/setup resources. Text and the mechanical drawing remain vector objects in the PDF.

## Review priorities

1. Confirm the wiring illustration is clear. Its labelled ports express electrical connections; their illustrated positions do not represent physical connector locations or motor connector pin order. The exact controller pin table is on page 3.
2. Confirm the shipped board uses the standard PD configuration (R27 = 200 kΩ, R31 unpopulated), which requests 20 V. The design files mark R31 as DNP; populating the optional parallel 62 kΩ resistor changes the request.
3. Confirm the physical product matches the revision 0.5 drawings. Dimensions are taken from KiCad, not caliper measurements. Overall assembled height and antenna/cable envelope remain unspecified.
4. Supply measured board current, continuous motor-power pass-through rating and environmental/qualification limits if these should be stated. No component current, temperature, ESD or maximum data-rate rating has been promoted to a board-level guarantee.
5. Confirm any promised shipped firmware, flash/PSRAM variant and packaging beyond the board and antenna. These are not inferred from family-level module specifications.

## Verification

`review/sources.json` maps claims to their evidence. `review/verification.json` records the 392 automated design checks, clean KiCad error-level DRC/parity results, firmware compile results, document QA and input/output hashes. These checks do not replace physical hardware tests.

The diagnostic firmware test required a forward declaration for `ping_test_all_aliases` when compiled as C++. The main demo and juggling example compiled without logic changes. All three compiled with ESP32 Arduino core 3.3.3 and Servomotor library 0.10.1.

The AI diagram was generated with the built-in `image_gen` tool using the owner-provided controller photos as references. Its full prompt and constraints are saved in `assets/connection-diagram-prompt.txt`; the saved illustration is `assets/two-motor-connection-ai.png`. The A, B, positive supply and continuous common-ground nets were checked visually against the schematic, and are restated in the PDF connection table.

## Rebuild

Install the packages in `requirements.txt` in a Python virtual environment, then run:

```sh
python datasheet/generate_datasheet.py
python datasheet/verify_design.py --kicad-cli /path/to/kicad-cli
```

The builder resolves all assets relative to its own directory. On macOS with the standard KiCad installation, the CLI path is `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.

After editing, render every page and inspect it again:

```sh
pdftoppm -scale-to 1400 -png datasheet/rs485_controller_datasheet_v0.1_review.pdf /tmp/rs485-review
```

Publish the approved PDF, its builder, requirements, evidence and diagram together only after the owner has reviewed the draft. At that point update the PDF's review markers and publication status deliberately; do not silently present this review edition as a final qualified specification.
