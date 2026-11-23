#include <Arduino.h>
#include <USB.h>
#include <USBCDC.h>
#include <driver/uart.h>
#include <tusb.h>
#include "RelayBuffer.h"

#if !CONFIG_IDF_TARGET_ESP32S3 || ARDUINO_USB_MODE || ARDUINO_USB_CDC_ON_BOOT
#error Select ESP32S3 Dev Module, USB-OTG (TinyUSB), and USB CDC On Boot Disabled.
#endif

USBCDC host;
RelayBuffer toHost;
RelayBuffer toBus;
constexpr int rxPin = 5;
constexpr int txPin = 4;
constexpr uart_port_t busPort = UART_NUM_1;  // Serial1
cdc_line_coding_t activeCoding = {};
bool configured = false;

bool applyCoding(const cdc_line_coding_t& c) {
  if (c.bit_rate < 300 || c.bit_rate > 1000000 || c.data_bits < 5 ||
      c.data_bits > 8 || c.stop_bits > 2 || c.parity > 2) return false;
  constexpr uart_word_length_t widths[] = {
    UART_DATA_5_BITS, UART_DATA_6_BITS, UART_DATA_7_BITS, UART_DATA_8_BITS
  };
  constexpr uart_parity_t parities[] = {
    UART_PARITY_DISABLE, UART_PARITY_ODD, UART_PARITY_EVEN
  };
  constexpr uart_stop_bits_t stops[] = {
    UART_STOP_BITS_1, UART_STOP_BITS_1_5, UART_STOP_BITS_2
  };
  // Complete any old frame before applying new host settings.
  Serial1.flush();
  return uart_set_baudrate(busPort, c.bit_rate) == ESP_OK &&
         uart_set_word_length(busPort, widths[c.data_bits - 5]) == ESP_OK &&
         uart_set_parity(busPort, parities[c.parity]) == ESP_OK &&
         uart_set_stop_bits(busPort, stops[c.stop_bits]) == ESP_OK;
}

template <typename Port>
void discardInput(Port& port) {
  uint8_t unused[128];
  int remaining = port.available();
  while (remaining > 0) {
    const size_t chunk = size_t(remaining) < sizeof(unused) ? size_t(remaining) : sizeof(unused);
    const size_t count = port.read(unused, chunk);
    if (!count || count > chunk) break;
    remaining -= count;
  }
}

void discardQueuedData() {
  toHost.clear();
  toBus.clear();
  discardInput(host);
  discardInput(Serial1);
}

void setup() {
  Serial1.setRxBufferSize(4096);
  Serial1.setTxBufferSize(1024);
  Serial1.begin(230400, SERIAL_8N1, rxPin, txPin);
  host.setRxBufferSize(4096);
  host.enableReboot(false); // A serial program may toggle DTR/RTS or select 1200 baud.
  host.begin();
  USB.productName("Gearotons RS2 RS485 Bridge");
  USB.begin();
}

void loop() {
  // CDC DTR indicates an open port. Discard stale traffic after close or unplug.
  if (!tud_cdc_n_connected(0)) {
    discardQueuedData();
    activeCoding.bit_rate = 0;
    configured = false;
    delay(1);
    return;
  }

  cdc_line_coding_t requested;
  tud_cdc_n_get_line_coding(0, &requested);
  if (memcmp(&requested, &activeCoding, sizeof(requested)) != 0) {
    configured = applyCoding(requested);
    activeCoding = requested;
  }
  if (configured) {
    toBus.pump(host, Serial1);
    toHost.pump(Serial1, host);
  } else {
    discardQueuedData();
  }
  delay(1);
}
