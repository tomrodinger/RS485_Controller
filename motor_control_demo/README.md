This is an Arduino program that runs on an ESP32-S3 module, also known as the RS485 Controller, which is a dev board supplied by Gearotons.

This demo should autodetect all the motors on the RS485 bus. The autodetection algorithm is already well defined, which is a three pass autodetection. It should log the detected motors to the console. After detecting them, it should cycle through one at a time to test them. The sequence for each is:
(1) Go to the closed loop mode (which at the same time enables the MOSFETs)
(2) Queue up two trapezoid moves: rotate half a rotation counterclockwise and then rotate back. The time should be half a second for each trapezoid move.
(3) Reset the motor (just that one that was used)

## Building the separate examples

Each `.cpp` is a separate Arduino program with its own `setup()` and `loop()`. Do not place all three in a single sketch. Use the Gearotons Servomotor Arduino library and an ESP32-S3 target. The main demo and autodetection test explicitly configure GPIO5 RX and GPIO4 TX at 230400 baud, 8N1. All examples can command motion; the juggling demo also assumes a specific three-motor mechanism and aliases X/Y/Z.

For Arduino CLI, put one `.cpp` into a sketch directory alongside an empty `.ino` whose name matches that directory. For example:

```sh
arduino-cli compile --fqbn esp32:esp32:esp32s3:CDCOnBoot=cdc /path/to/motor_control_demo
```

Native USB settings may need adjustment for your installation. The examples have been compile-checked with ESP32 Arduino core 3.3.3 and Servomotor library 0.10.1; this does not establish hardware or motion-test results. The diagnostic test includes a forward declaration needed when building it as a C++ translation unit.
