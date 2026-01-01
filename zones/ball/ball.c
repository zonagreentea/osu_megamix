#include "ball.h"

static inline uint32_t ball_xorshift32(uint32_t x){
  x ^= x << 13; x ^= x >> 17; x ^= x << 5; return x;
}

void ball_init(ball_world_t* w, uint32_t seed){
  w->s.tick = 0;
  w->s.rng  = seed ? seed : 1;
}

void ball_step(ball_world_t* w){
  w->s.tick += 1;
  w->s.rng = ball_xorshift32(w->s.rng);
}

const ball_state_t* ball_state(const ball_world_t* w){
  return &w->s;
}
