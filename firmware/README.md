# Firmware for the Gearotons RS485 controller (PCB 0.5)

Each image is a complete, independently installable application. Install the USB bridge when a computer will issue motor commands. Install the Wi-Fi tester when you want to use a browser at the bench. Flashing switches between them.

**Hardware tests for release 0.1.0** used the RS485 controller, one M17 and a Mac. Release 0.1.1 updates the displayed names, including the Wi-Fi network and USB bridge names. [Image checksums](images/SHA256SUMS)

| Profile | Bench result |
|---|---|
| Wi-Fi tester | The Mac joined the board’s protected access point and loaded its local page. The scan found one M17, and that motor acknowledged the LED-identify command. The Hall sensor confirmed the requested 90° turn within the tester’s tolerance, then the motor reported its driver outputs off. Chrome rendered the controls at 390 px and 1280 px. |
| USB bridge | macOS enumerated the Gearotons bridge. Across two separate opens at 230400 8N1, Gearotons host software discovered the same M17 and read its matching identity and healthy status twice per session. |

Physical Linux, Windows, phone, multi-motor, and cable unplug/replug tests remain open. The LED-identify result records the motor’s protocol acknowledgment.

| Image | What to do after flashing |
|---|---|
| [USB to RS485 bridge](images/rs2-usb-rs485-bridge.bin) | Plug J5 PROG into the computer and open the new serial port at 230400 8N1 for the M17. [Bridge settings and host port names](usb_rs485_bridge/README.md) |
| [Wi-Fi motor tester](images/rs2-wifi-motor-tester.bin) | Read the board's Wi-Fi connection details over J5, join the board's network from a phone or computer, and open the local page. [Tester controls and setup](wifi_motor_tester/README.md) |

## Installing an image

Choose a firmware in the [RS485 controller browser installer](https://9o.at/products/rs2/0.5#firmware) to install directly from desktop Chrome or Edge.

### Manual installation

1. Start with an RS485 controller you can reprogram. The combined image replaces the existing application, bootloader, partition table and settings in the written region. Keep a copy of any custom firmware you need to restore. Disconnect motor power during flashing.
2. Connect a USB data cable to **J5 PROG**. Hold **S2 PROG**, tap and release **S1 RESET**, then release **S2**. Use the download-mode serial port that appears. The port name can change when an installed application starts.
3. Use Espressif's **esptool 5**. From the directory containing the images, substitute the actual port name and your selected file. For example, with the board on COM5:

   ```sh
   esptool --chip esp32s3 --port COM5 write-flash 0x0 rs2-usb-rs485-bridge.bin
   ```

   For the tester, use `rs2-wifi-motor-tester.bin` at the same address. On macOS or Linux substitute the actual `/dev/cu.usbmodem…` or `/dev/ttyACM…` port. Wait for esptool's verification, then tap S1 RESET if needed. [Espressif installation instructions](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/installation.html) · [Writing and verifying flash](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/esptool/basic-commands.html)
4. For motor tests, follow the [RS485 controller wiring and power documentation](https://9o.at/products/rs2/0.5). Connect matching A/B and a common ground. Use a suitable motor supply. J5 powers the controller logic. Fit the supplied antenna before using Wi-Fi.

## Building from source

The build uses Arduino CLI, Espressif Arduino core **3.3.3**, and Gearotons Servomotor library **0.10.1**. From this repository, run:

```sh
python3 firmware/build.py /path/to/new-output-directory
```

This produces two combined flash images and `SHA256SUMS`. The builder checks the ESP32-S3 bootloader and application digests, verifies their locations inside each Arduino merged image, and removes trailing flash padding. The hashes identify these exact builds. To check them on macOS use `shasum -a 256 -c SHA256SUMS`, on Linux use `sha256sum -c SHA256SUMS`, or on Windows compare `Get-FileHash IMAGE.bin -Algorithm SHA256` with the matching line.

## Bench acceptance

- **Bridge.** On each target OS, record the serial device name and run the Gearotons host software against one known M17. Read its identity twice at 230400 8N1, close and reopen the port, then repeat after USB unplug/replug. Check that the first response contains only the expected binary protocol frame. Enumeration alone tests only the computer-facing side.
- **Wi-Fi tester.** With one unloaded, secured M17, open the local page from a phone and a desktop browser. Verify its reported UID, visually confirm Identify on that motor, then deliberately request one bounded move and observe it stop. Repeat discovery with two motors. Check that reloading the page and power cycling do not start motion.
