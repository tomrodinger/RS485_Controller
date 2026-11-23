# USB to RS485 bridge

Connect a USB **data** cable from the computer to the RS485 controller’s connector **J5 PROG**. The sketch exposes a CDC-ACM serial port and relays binary data to and from the half-duplex RS485 transceiver. Hardware switches bus direction. The firmware generates no motor commands or text messages on this connection.

Open the new port from the Gearotons host software. For an M17 use **230400 baud, 8 data bits, no parity, one stop bit**, no flow control, and DTR asserted (the usual pySerial default). Finish each request and wait for its reply before sending another. The computer's serial settings select the bus settings. The firmware accepts 300 through 1,000,000 baud, 5–8 data bits, none/odd/even parity and 1/1.5/2 stop bits. The upper rate is a software limit; usable bus speed depends on wiring and hardware. Unsupported line settings suspend forwarding. Hardware flow control, modem lines on the bus and serial break signaling are outside this profile.

| Host | Where to find it |
|---|---|
| macOS | A new `/dev/cu.usbmodem…` entry |
| Linux | A new `/dev/ttyACM…` entry with the kernel's `cdc_acm` driver. The user needs permission to open that serial device. |
| Windows 10/11 | Device Manager → Ports (COM & LPT) → USB Serial Device (COM number). Use the COM number reported on this machine. |

Use **J2 A/B/GND** and a separately suitable motor supply as shown in the RS485 controller datasheet. J5 provides controller logic power. On reconnect, select the bridge port again if its name changed. To switch firmware, use manual download mode as described in the [installation guide](../README.md).

[Espressif Arduino USB CDC](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/usb_cdc.html) · [Linux CDC-ACM](https://docs.kernel.org/usb/acm.html) · [Microsoft USB serial driver](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-driver-installation-based-on-compatible-ids)
