#include "../usb_rs485_bridge/RelayBuffer.h"
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <vector>

struct Input {
  std::vector<uint8_t> bytes;
  size_t pos = 0;
  int available() const { return static_cast<int>(bytes.size() - pos); }
  size_t read(uint8_t* out, size_t count) {
    count = std::min(count, bytes.size() - pos);
    std::copy_n(bytes.begin() + pos, count, out);
    pos += count;
    return count;
  }
};

struct Output {
  std::vector<uint8_t> bytes;
  int space = 0;
  size_t accepted = 0;
  int availableForWrite() const { return space; }
  size_t write(const uint8_t* data, size_t count) {
    assert(count <= static_cast<size_t>(space));
    count = std::min(count, accepted);
    bytes.insert(bytes.end(), data, data + count);
    return count;
  }
};

int main() {
  Input host, bus;
  for (unsigned i = 0; i < 8192; i++) {
    host.bytes.push_back(static_cast<uint8_t>(i));
    bus.bytes.push_back(static_cast<uint8_t>(255 - i));
  }
  Output busOut, hostOut;
  RelayBuffer outbound, inbound;
  for (int i = 0; i < 6000; ++i) {
    busOut.space = i % 121;
    busOut.accepted = i % 25;
    hostOut.space = i % 41;
    hostOut.accepted = i % 17;
    outbound.pump(host, busOut);
    inbound.pump(bus, hostOut);
  }
  assert(busOut.bytes == host.bytes && hostOut.bytes == bus.bytes);

  Input session;
  session.bytes = {1, 2, 3};
  Output port;
  port.space = 3;
  port.accepted = 1;
  outbound.pump(session, port);
  outbound.clear(); // Dropped connection must not send the previous chunk's tail.
  session.bytes.push_back(9);
  outbound.pump(session, port);
  assert((port.bytes == std::vector<uint8_t>{1, 9}));
}
