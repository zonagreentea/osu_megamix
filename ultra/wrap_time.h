#pragma once
#include <cstdint>

// wrap-safe signed delta in u32 space (works across overflow)
static inline int32_t wrap_delta_u32(uint32_t a, uint32_t b) {
  return (int32_t)(a - b);
}

// unwrap u32 timestamp stream into monotonic u64 (for logs/replay)
static inline uint64_t unwrap_u32(uint32_t t, uint32_t &last_t, uint64_t &base) {
  if ((int32_t)(t - last_t) < 0) base += (1ULL << 32); // forward wrap
  last_t = t;
  return base + t;
}
