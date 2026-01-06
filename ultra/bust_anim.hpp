#pragma once
#include <cstdint>

struct SDL_Renderer;

struct BustAnim {
  bool active = false;
  uint64_t start_us = 0;

  // start the animation at a monotonic timestamp
  void start(uint64_t t_us) { active = true; start_us = t_us; }

  // draw overlay (projection only)
  void draw(SDL_Renderer* r, int w, int h, uint64_t now_us);

  // helper
  static float clamp01(float x){ return x < 0.f ? 0.f : (x > 1.f ? 1.f : x); }
};
