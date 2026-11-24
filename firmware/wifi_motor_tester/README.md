# RS485 controller Wi-Fi motor tester

This bench firmware runs a local web page for discovering Gearotons motors, identifying a motor by its green LED, and resetting individual motors and testing a quarter revolution in either direction on an unloaded M17. Use RS485 controller hardware 0.5 with its antenna attached. The M17 needs its own appropriate motor power. Connect A to A, B to B, and common ground following the controller datasheet. Use one controller on the test bus. Keep motor power accessible.

## Connect

1. Install the Wi-Fi motor tester and start the controller.
2. On your phone or computer, join **RS485-controller-…**. This is an open Wi-Fi network; leave the password blank. One client can connect at a time. If prompted about internet access, choose to stay connected.
3. Open **http://192.168.4.1/**. If your device remembers the older password-protected network, forget that saved network and join again.

## Test an individual motor

- **Detect motors** collects three passes of broadcast replies and lists each unique hardware ID and reported alias. Detection takes several seconds. A scan sends no motion commands and does not reset motors or reassign aliases.
- **Blink motor LED** flashes the selected motor’s green LED. All individual commands use its 64-bit hardware ID, including when multiple motors report the same alias.
- **Reset motor** reboots the selected motor. The tester waits for the motor to restart and checks for a reply from the same hardware ID.
- **Turn +90° / Turn −90°** requires a clear, secured, unloaded shaft with the power stage off. Check the box for that motor, then choose a direction. The box stays checked through rescans and page reloads in the same browser tab. Uncheck it at any time. The tester verifies the M17 identity, checks its status, queue and position, enters closed-loop control, then requests a quarter turn over 1.5 seconds. It checks the Hall position change (within 0.05 turn) and requests a motor stop and release. The shaft can move freely afterward. After detection you can turn the motor immediately. A blink is optional. Wait for the result before another turn. If a page has expired, the tester displays fresh controls and skips that submission. A lost Wi-Fi connection does not cancel an accepted test.
- **Motor release unconfirmed** means you should turn off the motor supply and inspect wiring and power before continuing. Browser controls are not a physical emergency stop. Use physical power removal if motion must stop immediately. Keep loaded axes and other controllers off this test bus.

A missing device may be unpowered, disconnected, in a fault state, or obscured by overlapping discovery responses. Check power, common ground and A/B, then run detection again. The motor must answer the M17 protocol at 230400 baud with a compatible application installed before the turn test will run. No motion is requested at startup.

## Build from source

Use Arduino ESP32 core **3.3.3**, **Gearotons Servomotor 0.10.1**, and `arduino-cli`:

```sh
arduino-cli compile --fqbn esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashMode=dio,FlashSize=4M firmware/wifi_motor_tester
```

The RS485 UART uses GPIO4 TX and GPIO5 RX at 230400 baud, 8N1. The board switches transmit direction in hardware.
