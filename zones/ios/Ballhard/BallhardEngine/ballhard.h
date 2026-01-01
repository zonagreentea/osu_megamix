#pragma once
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t bh_tick_t;

typedef struct {
  bh_tick_t tick;
  uint32_t buttons;   // bitfield
  int16_t ax0, ay0;   // simple axes
} bh_input_t;

typedef struct {
  bh_tick_t tick;
  uint32_t rng;
  // add your sim truth state here (scores, objects, etc.)
} bh_state_t;

typedef struct {
  bh_state_t s;
} bh_world_t;

void bh_init(bh_world_t* w, uint32_t seed);
void bh_submit_input(bh_world_t* w, bh_input_t in);   // evidence only (observed frame)
void bh_step(bh_world_t* w);                          // deterministic step: tick++
const bh_state_t* bh_state(const bh_world_t* w);

#ifdef __cplusplus
}
#endif
