#include "ballhard.h"

static inline uint32_t xorshift32(uint32_t x){
  x ^= x << 13; x ^= x >> 17; x ^= x << 5; return x;
}

void bh_init(bh_world_t* w, uint32_t seed){
  w->s.tick = 0;
  w->s.rng  = seed ? seed : 1;
}

void bh_submit_input(bh_world_t* w, bh_input_t in){
  (void)w; (void)in;
  // evidence-only intake lives here later (ring/log); rollback stays OFF.
}

void bh_step(bh_world_t* w){
  w->s.tick += 1;
  w->s.rng = xorshift32(w->s.rng);
}

const bh_state_t* bh_state(const bh_world_t* w){
  return &w->s;
}
