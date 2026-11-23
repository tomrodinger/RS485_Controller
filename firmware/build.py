"""Build and check both RS485 controller images with Arduino CLI, without opening a serial port."""

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
PROFILES = {
    "usb_rs485_bridge": "USBMode=default,CDCOnBoot=default",
    "wifi_motor_tester": "USBMode=hwcdc,CDCOnBoot=cdc",
}


def verify_esp32s3_image(data):
    # Espressif image header: magic, chip_id=9 (ESP32-S3), appended digest flag.
    if len(data) < 56 or data[0] != 0xE9 or data[12:14] != b"\x09\x00":
        raise ValueError("Expected an ESP32-S3 image")
    if data[23] != 1 or hashlib.sha256(data[:-32]).digest() != data[-32:]:
        raise ValueError("ESP32 image digest mismatch")


def combined_image(build_dir, sketch):
    prefix = build_dir / f"{sketch}.ino"
    app = Path(f"{prefix}.bin").read_bytes()
    boot = Path(f"{prefix}.bootloader.bin").read_bytes()
    partitions = Path(f"{prefix}.partitions.bin").read_bytes()
    merged = Path(f"{prefix}.merged.bin").read_bytes()
    verify_esp32s3_image(app)
    verify_esp32s3_image(boot)
    # For the pinned standard 4 MB layout, the Arduino builder embeds bootloader,
    # partition table, OTA selection data and app. Drop only verified tail padding.
    end = 0x10000 + len(app)
    if (len(merged) != 4 * 1024 * 1024 or merged[:len(boot)] != boot
            or merged[0x8000:0x8000 + len(partitions)] != partitions
            or merged[0x10000:end] != app or merged[end:].strip(b"\xff")):
        raise ValueError("Unexpected Arduino merged image layout")
    return merged[:end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New or empty output directory")
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Choose a new or empty directory to keep releases separate")
    images = {}
    with tempfile.TemporaryDirectory(prefix="rs2-build-") as tmp:
        for sketch, usb in PROFILES.items():
            build = Path(tmp) / sketch
            board = f"esp32:esp32:esp32s3:{usb},FlashMode=dio,FlashSize=4M"
            subprocess.run(["arduino-cli", "compile", "--jobs", str(min(os.cpu_count() or 1, 6)),
                            "--fqbn", board, "--build-path", str(build), str(ROOT / sketch)],
                           check=True)
            images[f"rs2-{sketch.replace('_', '-')}.bin"] = combined_image(build, sketch)
    args.output.mkdir(parents=True, exist_ok=True)
    sums = []
    for name, data in images.items():
        (args.output / name).write_bytes(data)
        sums.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
    (args.output / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
