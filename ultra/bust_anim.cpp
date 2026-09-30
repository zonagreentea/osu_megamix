#include "bust_anim.hpp"
#include <SDL.h>
#include <cmath>

static void fill_rect(SDL_Renderer* r, int x, int y, int w, int h, Uint8 a){
  SDL_SetRenderDrawBlendMode(r, SDL_BLENDMODE_BLEND);
  SDL_SetRenderDrawColor(r, 0, 0, 0, a);
  SDL_Rect rc{ x, y, w, h };
  SDL_RenderFillRect(r, &rc);
}

void BustAnim::draw(SDL_Renderer* r, int w, int h, uint64_t now_us){
  if(!active) return;

  const double t = (now_us - start_us) / 1e6; // seconds since bust
  // 0.00-0.12: white flash (alpha up then down)
  // 0.12-0.90: blackout ramp + shutter bars
  // 0.90-1.20: settle (leave a soft dark overlay)
  float flash = 0.f;
  if(t < 0.12){
    float u = (float)(t / 0.12);
    // triangle pulse
    flash = (u < 0.5f) ? (u*2.f) : (2.f - u*2.f);
  }

  // base darkness ramps in
  float dark = 0.f;
  if(t < 0.9) dark = (float)(t / 0.9);
  else dark = 1.f;

  // settle to 0.85 darkness after 1.2s
  float settle = 1.f;
  if(t > 0.9){
    float u = (float)((t - 0.9) / 0.3);
    settle = 1.f - 0.15f * clamp01(u);
  }
  float base = clamp01(dark * settle);

  // If the animation runs long, we keep a dim overlay, but stop the “motion”
  bool motion = (t < 1.2);

  // flash: draw white fullscreen briefly (by drawing black with negative logic: easiest is draw white rect)
  if(flash > 0.f){
    SDL_SetRenderDrawBlendMode(r, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(r, 255, 255, 255, (Uint8)(flash * 220));
    SDL_Rect rc{0,0,w,h};
    SDL_RenderFillRect(r, &rc);
  }

  // base blackout
  fill_rect(r, 0, 0, w, h, (Uint8)(base * 220));

  if(motion){
    // shutter bars sliding in (pure vibe, no text/font)
    // bars count
    const int bars = 9;
    const float u = clamp01((float)(t / 1.2));
    const float ease = 1.f - std::pow(1.f - u, 3.f); // cubic out
    for(int i=0;i<bars;i++){
      float phase = (float)i / (bars - 1);
      // each bar has slight offset
      float v = clamp01(ease*1.15f - phase*0.25f);
      int bar_w = (int)(w * 0.08);
      int x = (int)((phase * (w - bar_w)) + std::sin((phase*6.283f) + (float)t*20.f) * 2.0f);
      int hh = (int)(h * v);
      int y = (h - hh) / 2;
      SDL_SetRenderDrawBlendMode(r, SDL_BLENDMODE_BLEND);
      SDL_SetRenderDrawColor(r, 120, 180, 255, (Uint8)(90 + 90*v));
      SDL_Rect rc{ x, y, bar_w, hh };
      SDL_RenderFillRect(r, &rc);
    }

    // tiny scanline shimmer
    SDL_SetRenderDrawBlendMode(r, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(r, 160, 220, 255, 22);
    for(int y=0; y<h; y+=4){
      SDL_RenderDrawLine(r, 0, y, w, y);
    }
  }

  // stop “active” after 2s (keep dim overlay by leaving base rect, but the caller can decide)
  if(t > 2.0){
    // keep it active if you want persistent dim; otherwise:
    active = false;
  }
}
