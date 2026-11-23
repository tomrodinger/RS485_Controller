#pragma once
#include <stddef.h>
#include <stdint.h>

// Keep unwritten bytes when either port temporarily accepts only part of a chunk.
class RelayBuffer {
 public:
  template <typename Input, typename Output>
  void pump(Input& input, Output& output) {
    const int space = output.availableForWrite();
    if (space <= 0) return;
    if (offset == count) {
      const int ready = input.available();
      if (ready <= 0) return;
      const size_t request = size_t(ready) < sizeof(data) ? size_t(ready) : sizeof(data);
      count = input.read(data, request);
      offset = 0;
    }
    const size_t remaining = count - offset;
    const size_t request = remaining < size_t(space) ? remaining : size_t(space);
    if (request) offset += output.write(data + offset, request);
  }

  void clear() { offset = count = 0; }

 private:
  uint8_t data[256];
  size_t offset = 0;
  size_t count = 0;
};
