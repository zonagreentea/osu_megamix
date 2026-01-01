#include "ballhard.h"

static inline uint32_t xorshift32(uint32_t x){
  x ^= x << 13; x ^= x >> 17; x ^= x << 5; return x;
}

void bh_init(bh_world_t* w, uint32_t seed){
  w->s.tick = 0;
  w->s.rng  = seed ? seed : 1;
}

void bh_submit_input(bh_world_t* w, bh_input_t in){
  // material truth: only accept input for "now or future".
  // no rollback: late evidence is recorded by caller if desired, but sim won't rewind here.
  (void)w; (void)in;
  // For Ball 1 we keep it simple. Next ball: per-tick input log ring.
}

void bh_step(bh_world_t* w){
  // deterministic tick
  w->s.tick += 1;
  w->s.rng = xorshift32(w->s.rng);
}

const bh_state_t* bh_state(const bh_world_t* w){
  return &w->s;
}
