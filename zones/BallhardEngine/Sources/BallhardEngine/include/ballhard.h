#pragma once
#include <stdint.h>

typedef uint32_t bh_tick_t;

typedef struct {
  bh_tick_t tick;
  uint32_t buttons;
  int16_t ax0, ay0;
} bh_input_t;

typedef struct {
  bh_tick_t tick;
  uint32_t rng;
} bh_state_t;

typedef struct {
  bh_state_t s;
} bh_world_t;

void bh_init(bh_world_t* w, uint32_t seed);
void bh_submit_input(bh_world_t* w, bh_input_t in);
void bh_step(bh_world_t* w);
const bh_state_t* bh_state(const bh_world_t* w);
