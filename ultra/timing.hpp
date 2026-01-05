#pragma once
#include <chrono>
#include <cstdint>

struct UltraTiming {
  using clock = std::chrono::steady_clock;

  clock::time_point last = clock::now();
  double dt_sec = 0.0;
  double raw_dt_sec = 0.0;
  uint64_t frame = 0;

  double clamp_max_sec = 0.050; // 50ms

  void tick() {
    auto now = clock::now();
    std::chrono::duration<double> d = now - last;
    last = now;

    raw_dt_sec = d.count();
    dt_sec = raw_dt_sec;

    if (dt_sec < 0.0) dt_sec = 0.0;
    if (dt_sec > clamp_max_sec) dt_sec = clamp_max_sec;

    frame++;
  }
};
