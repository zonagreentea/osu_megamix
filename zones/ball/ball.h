#pragma once
#include <stdint.h>

typedef uint32_t ball_tick_t;

typedef struct {
  ball_tick_t tick;
  uint32_t buttons;
  int16_t ax0, ay0;
} ball_input_t;

typedef struct {
  ball_tick_t tick;
  uint32_t rng;
} ball_state_t;

typedef struct {
  ball_state_t s;
} ball_world_t;

void ball_init(ball_world_t* w, uint32_t seed);
void ball_step(ball_world_t* w);
const ball_state_t* ball_state(const ball_world_t* w);
