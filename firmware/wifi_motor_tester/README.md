# RS2 Wi-Fi motor tester

This bench firmware runs a local web page for discovering Gearotons motors, identifying a motor by its green LED, and testing a quarter revolution of an unloaded M17. Use RS2 hardware 0.5 with its antenna attached. The M17 needs its own appropriate motor power. Connect A to A, B to B, and common ground following the controller datasheet. Use one controller on the test bus. Keep motor power accessible.

## Connect

1. Install the Wi-Fi tester image. Connect a data-capable USB cable to J5 **USB-C PROG**. Open the controller’s USB serial port at 115200. Press Enter to print the Wi-Fi name, password and address.
2. On a phone or computer, join the displayed **Gearotons-RS2-…** network. The password is generated on the controller and saved in its settings. One client can connect at a time. If the phone reports no internet, choose to stay connected.
3. Open the printed HTTP address, normally **http://192.168.4.1/**. For later sessions you can use the saved Wi-Fi network directly. J5 only needs a computer when you want USB access or another firmware image.

## Test an individual motor

- **Detect motors** collects three passes of broadcast replies and lists each unique hardware ID and reported alias. Detection takes several seconds. A scan sends no motion commands and does not reset motors or reassign aliases.
- **Blink motor LED** flashes the selected motor’s green LED. All individual commands use its 64-bit hardware ID, including when multiple motors report the same alias.
- **Turn 90° and release** requires a clear, secured, unloaded shaft with the power stage off. Tick the confirmation for that motor and press the button. The tester verifies the M17 identity, checks its status, queue and position, enters closed-loop control, then requests a quarter turn over 1.5 seconds. It checks the Hall position change (within 0.05 turn) and requests a motor stop and release. The shaft can move freely afterward. Wait for the page result before repeating. A lost Wi-Fi connection does not cancel an accepted test.
- **Motor release unconfirmed** means you should turn off the motor supply and inspect wiring and power before continuing. Browser controls are not a physical emergency stop. Use physical power removal if motion must stop immediately. Keep loaded axes and other controllers off this test bus.

A missing device may be unpowered, disconnected, in a fault state, or obscured by overlapping discovery responses. Check power, common ground and A/B, then run detection again. The motor must answer the M17 protocol at 230400 baud with a compatible application installed before the turn test will run. No motion is requested at startup.

## Build from source

Use Arduino ESP32 core **3.3.3**, **Gearotons Servomotor 0.10.1**, and `arduino-cli`:

```sh
arduino-cli compile --fqbn esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashMode=dio,FlashSize=4M firmware/wifi_motor_tester
```

The RS485 UART uses GPIO4 TX and GPIO5 RX at 230400 baud, 8N1. The board switches transmit direction in hardware.
