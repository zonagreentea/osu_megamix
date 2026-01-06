#pragma once
#include <vector>
#include <cstdint>
#include <algorithm>
#include <chrono>

static inline uint64_t aux_now_ms() {
  using namespace std::chrono;
  return (uint64_t)duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
}

struct AuxContribution {
  uint64_t player_id = 0;
  float gain = 0.0f;             // 0..1
  uint64_t last_touch_ms = 0;    // monotonic ms
  bool opt_in = false;
};

struct AuxBus {
  static constexpr float AUX_MAX_GAIN_PER_PLAYER = 0.25f; // roamers help, cannot hijack
  static constexpr float AUX_TOTAL_MAX_GAIN      = 1.0f;  // clamp total
  static constexpr uint64_t AUX_DECAY_MS         = 2500;  // fades quickly if not touching
  static constexpr uint64_t AUX_GRACE_MS         = 350;   // prevents jitter
  static constexpr uint32_t AUX_MAX_ROAMERS      = 8;     // safety cap

  std::vector<AuxContribution> c;

  void touch(uint64_t player_id, float gain01, uint64_t now_ms) {
    gain01 = std::clamp(gain01, 0.0f, 1.0f);
    auto it = std::find_if(c.begin(), c.end(),
      [&](const AuxContribution& x){ return x.player_id == player_id; });

    if (it == c.end()) {
      if (c.size() >= AUX_MAX_ROAMERS) return;
      AuxContribution x;
      x.player_id = player_id;
      x.gain = gain01;
      x.last_touch_ms = now_ms;
      x.opt_in = true;
      c.push_back(x);
    } else {
      it->gain = gain01;
      it->last_touch_ms = now_ms;
      it->opt_in = true;
    }
  }

  void update(uint64_t now_ms) {
    for (auto &x : c) {
      if (!x.opt_in) { x.gain = 0.0f; continue; }
      uint64_t age = (now_ms > x.last_touch_ms) ? (now_ms - x.last_touch_ms) : 0;

      if (age <= AUX_GRACE_MS) continue;

      if (age >= AUX_DECAY_MS) {
        x.gain = 0.0f;
        x.opt_in = false;
      } else {
        float t = float(age - AUX_GRACE_MS) / float(AUX_DECAY_MS - AUX_GRACE_MS);
        float decay = 1.0f - std::clamp(t, 0.0f, 1.0f);
        x.gain *= decay;
      }
    }
    c.erase(std::remove_if(c.begin(), c.end(),
      [](const AuxContribution& x){ return x.gain <= 0.0001f; }), c.end());
  }

  float total_gain() const {
    float sum = 0.0f;
    for (auto &x : c) sum += std::clamp(x.gain, 0.0f, AUX_MAX_GAIN_PER_PLAYER);
    return std::min(sum, AUX_TOTAL_MAX_GAIN);
  }
};
