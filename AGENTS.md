# Continuing work on the RS485 Controller

Read `README.md`, then the **Maintainer handoff** in `datasheet/README.md` before changing product documentation. That handoff records the owner's accepted decisions, source dependencies, release identity, build commands and remaining limits.

- The released hardware is **RS2 / PCB 0.5**. Datasheet **1.0** is a separate document revision. Preserve the RS2/0.5 identity in `PRODUCT_DATA.yaml`; it is encoded in shipped PCB QR codes.
- Public documentation is Arduino-only: `python: false`, `arduino: true`, `mcp: false`. Do not restore the removed Python example or advertise supplied bridge/wireless firmware.
- The owner approved the public datasheet. The public file is `datasheet/rs485_controller_datasheet_v1.0.pdf`; draft PDFs are historical archives, not the current product document.
- Keep the 11.7 g mass including the supplied external antenna, checked pin functions and measured-versus-design limitations accurate. Do not turn component ratings into board ratings.
- Diagram geometry comes from PCB 0.5. Preserve the single fully labelled breakout map, functional J2 labels, computer connection to J5 PROG, and PD supply connection to J3.
- Keep both GPIO and PCB names on the map: GPIO43/TXD0, GPIO44/RXD0, GPIO4/RS485TX and GPIO5/RS485RX. Use plain text labels without background boxes. PD CFG/VDD/PG are HASL-finished plated through-hole pads for the CH221K, not spare GPIO.
- Preserve the power guidance: CH221K requests 20 V; motors can operate if 15 V or 12 V is delivered, and will likely not work correctly below 12 V. J5 alone is sufficient for programming. An external motor supply requires a common ground with the controller; keep the positive supply rails separate as documented.
- All four product photos use white backgrounds. Retain the edited masters, prompts and provenance in `images/rs485-controller/`; page 1 uses one board-only photo and page 14 holds the other views.
- `diagram-review/site/` is a separate private Sites repository, already committed and pushed. Preserve its audience and feedback; do not add that directory to the public controller repository.
- Do not put chat transcripts, API credentials or private feedback into documentation. The API key shared in the conversation was not used or saved.
- Before publishing changed product material, build, run the relevant verifier, render and inspect affected pages. Current reproduction and verification commands are in the handoff.
