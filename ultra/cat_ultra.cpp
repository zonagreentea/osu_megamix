/*  cat_ultra.cpp — SDL2 no-JS test: continuous audio + 3-2-1-go + tap spawns + HP->bust->mix  */
#include <SDL.h>
#include <cmath>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>

#include <cstdlib>
#include <cstdio>
static bool ultra_builder_mode() {
  const char* v = std::getenv("OSU_MEGAMIX_BUILDER");
  return v && v[0] && v[0] != '0';
}

static constexpr int   WIN_W = 960;
static constexpr int   WIN_H = 540;
static constexpr int   COUNTDOWN_MS = 3000;
static constexpr int   GO_FLASH_MS  = 500;

static constexpr int   SEED = 1337;
static constexpr int   N_PER_SEC = 4;
static constexpr float HIT_WINDOW_MS = 90.0f;
static constexpr float CIRCLE_R = 40.0f;

static constexpr float HP_GAIN_HIT   = 0.04f;
static constexpr float HP_DRAIN_MISS = 0.10f;

static constexpr int   AUDIO_SR = 48000;

static inline uint32_t mix32(uint32_t x) {
  x ^= x << 13; x ^= x >> 17; x ^= x << 5;
  return x;
}
static inline float hashUnit(uint32_t seed, uint32_t a, uint32_t b) {
  uint32_t x = (seed ^ (a * 374761393u) ^ (b * 668265263u)) >> 0;
  x = mix32(x);
  return (x / 4294967296.0f);
}

struct Cat {
  bool running = false;
  uint64_t t0_ticks = 0;
  double ticks_per_s = 0.0;
  int t_go_ms = COUNTDOWN_MS;

  struct Marker { int t_ms; int n; bool is_go; };
  std::vector<Marker> markers;

  struct Spawn { int t_hit; float x,y,r; uint32_t id; };
  std::vector<Spawn> spawns;

  struct Input { int t_ms; int kind; float x,y; }; // kind 1=down 2=up
  std::vector<Input> inputs;

  struct Bust { int t_ms; };
  std::vector<Bust> busts;

  int last_bin = -1;
};

static inline int nowMs(const Cat& cat) {
  uint64_t now = SDL_GetPerformanceCounter();
  double dt = (double)(now - cat.t0_ticks) / cat.ticks_per_s;
  return (int)std::floor(dt * 1000.0);
}

struct AudioState {
  double phase1 = 0.0;
  double phase2 = 0.0;
  double t_s = 0.0;
  double bpm = 120.0;
};
static AudioState g_audio;

static void audioCallback(void*, Uint8* stream, int len) {
  float* out = (float*)stream;
  int frames = len / (int)(sizeof(float) * 2);

  const double beat = 60.0 / g_audio.bpm;

  for (int i=0;i<frames;i++) {
    double t = g_audio.t_s;
    double bt  = std::fmod(t, beat);
    double eighth = beat / 2.0;
    double bt8 = std::fmod(t, eighth);

    double kickEnv = std::exp(-bt * 18.0);
    double kickFreq = 90.0 * std::exp(-bt * 10.0) + 35.0;
    g_audio.phase1 += (2.0 * M_PI * kickFreq) / AUDIO_SR;
    double kick = std::sin(g_audio.phase1) * kickEnv;

    double hatEnv = std::exp(-bt8 * 80.0);
    double noise = std::sin(g_audio.phase2 * 12.345) * std::sin(g_audio.phase2 * 7.89);
    g_audio.phase2 += (2.0 * M_PI * 6000.0) / AUDIO_SR;
    double hat = noise * hatEnv * 0.4;

    double bassEnv = std::exp(-bt * 10.0);
    double bassFreq = 55.0;
    static double bassPhase = 0.0;
    bassPhase += (2.0 * M_PI * bassFreq) / AUDIO_SR;
    double bass = (std::sin(bassPhase) * 0.35 + std::sin(bassPhase*0.5)*0.15) * bassEnv;

    double mix = 0.35*kick + 0.18*hat + 0.35*bass;
    float s = (float)std::clamp(mix * 0.35, -1.0, 1.0);

    out[i*2+0] = s;
    out[i*2+1] = s;

    g_audio.t_s += 1.0 / AUDIO_SR;
  }
}

enum class Mode { OSU, MIX };

struct Game {
  Mode mode = Mode::OSU;
  bool busted = false;
  float hp = 1.0f;
  int combo = 0;
  int score = 0;

  float mx = WIN_W/2.0f;
  float my = WIN_H/2.0f;
  bool mouseDown = false;

  std::vector<uint32_t> judged;
};

static bool hasJudged(const Game& g, uint32_t id) {
  return std::find(g.judged.begin(), g.judged.end(), id) != g.judged.end();
}
static void markJudged(Game& g, uint32_t id) { g.judged.push_back(id); }

static const Cat::Input* findClickDown(const Cat& cat, int tTarget, float windowMs) {
  int lo = (int)std::floor(tTarget - windowMs);
  int hi = (int)std::ceil (tTarget + windowMs);
  for (int i=(int)cat.inputs.size()-1;i>=0;i--) {
    const auto& ev = cat.inputs[i];
    if (ev.kind != 1) continue;
    if (ev.t_ms < lo) break;
    if (ev.t_ms >= lo && ev.t_ms <= hi) return &ev;
  }
  return nullptr;
}

static void generateBin(Cat& cat, int binIdx, int w, int h) {
  for (int i=0;i<N_PER_SEC;i++) {
    float uT = hashUnit(SEED, (uint32_t)binIdx, (uint32_t)i);
    int tHit = cat.t_go_ms + binIdx*1000 + (int)std::floor(uT * 1000.0f);

    float uX = hashUnit(SEED + 17, (uint32_t)binIdx, (uint32_t)i);
    float uY = hashUnit(SEED + 29, (uint32_t)binIdx, (uint32_t)i);

    float margin = 70.0f;
    float x = margin + (w - 2*margin) * uX;
    float y = margin + (h - 2*margin) * uY;

    uint32_t id = mix32((uint32_t)SEED ^ (uint32_t)(binIdx*100 + i));
    cat.spawns.push_back({tHit, x, y, CIRCLE_R, id});
  }
}

static void generatorTick(Cat& cat, int t_ms, int w, int h) {
  if (t_ms < cat.t_go_ms) return;
  int bin = (t_ms - cat.t_go_ms) / 1000;
  for (int b=cat.last_bin+1; b<=bin; b++) {
    generateBin(cat, b, w, h);
    cat.last_bin = b;
  }
}

static void osuTick(Cat& cat, Game& g, int t_ms) {
  if (t_ms < cat.t_go_ms) return;
  if (g.busted) return;

  for (const auto& sp : cat.spawns) {
    if (hasJudged(g, sp.id)) continue;
    if (t_ms < sp.t_hit + (int)std::ceil(HIT_WINDOW_MS)) continue;

    const auto* click = findClickDown(cat, sp.t_hit, HIT_WINDOW_MS);
    bool hit = false;
    if (click) {
      float dx = click->x - sp.x;
      float dy = click->y - sp.y;
      hit = (dx*dx + dy*dy) <= sp.r*sp.r;
    }

    markJudged(g, sp.id);

    if (hit) {
      g.combo += 1;
      g.score += 300 + std::min(200, g.combo);
      g.hp = std::clamp(g.hp + HP_GAIN_HIT, 0.0f, 1.0f);
    } else {
      g.combo = 0;
      g.hp = std::clamp(g.hp - HP_DRAIN_MISS, 0.0f, 1.0f);
      if (g.hp <= 0.0f && !g.busted) {
        cat.busts.push_back({t_ms});
        g.busted = true;
        g.mode = Mode::MIX; // ROUTE TO MIX
      }
    }
  }
}

static void mixTick(Cat&, Game&, int) {}

static void drawCircle(SDL_Renderer* r, float cx, float cy, float rad) {
  const int seg = 64;
  for (int i=0;i<seg;i++) {
    float a0 = (float)(i * 2.0*M_PI / seg);
    float a1 = (float)((i+1) * 2.0*M_PI / seg);
    int x0 = (int)std::lround(cx + std::cos(a0)*rad);
    int y0 = (int)std::lround(cy + std::sin(a0)*rad);
    int x1 = (int)std::lround(cx + std::cos(a1)*rad);
    int y1 = (int)std::lround(cy + std::sin(a1)*rad);
    SDL_RenderDrawLine(r, x0,y0,x1,y1);
  }
}

static int countdownLabel(int t_ms) {
  if (t_ms < 1000) return 3;
  if (t_ms < 2000) return 2;
  if (t_ms < 3000) return 1;
  return 0;
}

int main(int, char**) {
  if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER) != 0) {
    SDL_Log("SDL_Init failed: %s", SDL_GetError());
    return 1;
  }

  SDL_AudioSpec want{};
  want.freq = AUDIO_SR;
  want.format = AUDIO_F32SYS;
  want.channels = 2;
  want.samples = 1024;
  want.callback = audioCallback;

  SDL_AudioSpec got{};
  SDL_AudioDeviceID dev = SDL_OpenAudioDevice(nullptr, 0, &want, &got, 0);
  if (!dev) {
    SDL_Log("Audio open failed: %s", SDL_GetError());
    return 1;
  }
  SDL_PauseAudioDevice(dev, 0);

  SDL_Window* win = SDL_CreateWindow("cat ultra (no JS) — bust to mix",
    SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
    WIN_W, WIN_H, SDL_WINDOW_SHOWN);

  SDL_Renderer* ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);

  Cat cat;
  Game game;

  cat.running = true;
  cat.ticks_per_s = (double)SDL_GetPerformanceFrequency();
  cat.t0_ticks = SDL_GetPerformanceCounter();
  cat.t_go_ms = COUNTDOWN_MS;
  cat.last_bin = -1;

  cat.markers.push_back({0, 3, false});
  cat.markers.push_back({1000, 2, false});
  cat.markers.push_back({2000, 1, false});
  cat.markers.push_back({3000, 0, true});

  bool quit = false;
  while (!quit) {
    SDL_Event e;
    while (SDL_PollEvent(&e)) {
      if (e.type == SDL_QUIT) quit = true;

      if (e.type == SDL_MOUSEMOTION) {
        game.mx = (float)e.motion.x;
        game.my = (float)e.motion.y;
      }
      if (e.type == SDL_MOUSEBUTTONDOWN) {
        int t_ms = nowMs(cat);
        cat.inputs.push_back({t_ms, 1, game.mx, game.my});
        game.mouseDown = true;
      }
      if (e.type == SDL_MOUSEBUTTONUP) {
        int t_ms = nowMs(cat);
        cat.inputs.push_back({t_ms, 2, game.mx, game.my});
        game.mouseDown = false;
      }
      if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_r) {
        cat.spawns.clear();
        cat.inputs.clear();
        cat.busts.clear();
        game.judged.clear();
        game.mode = Mode::OSU;
        game.busted = false;
        game.hp = 1.0f;
        game.combo = 0;
        game.score = 0;
        cat.t0_ticks = SDL_GetPerformanceCounter();
        cat.last_bin = -1;
      }
    }

    int t_ms = nowMs(cat);
    generatorTick(cat, t_ms, WIN_W, WIN_H);

    if (game.mode == Mode::OSU) osuTick(cat, game, t_ms);
    else mixTick(cat, game, t_ms);

    SDL_SetRenderDrawColor(ren, 11, 11, 15, 255);
    SDL_RenderClear(ren);

    for (const auto& sp : cat.spawns) {
      int dt = sp.t_hit - t_ms;
      if (dt < -500) continue;
      if (dt > 700) continue;

      float life = 1.0f - std::clamp(dt / 700.0f, 0.0f, 1.0f);
      float ringR = sp.r + (1.0f - life) * 90.0f;

      SDL_SetRenderDrawColor(ren, 255,255,255, 255);
      drawCircle(ren, sp.x, sp.y, ringR);

      bool judged = hasJudged(game, sp.id);
      Uint8 a = judged ? 50 : 230;
      SDL_SetRenderDrawColor(ren, 255,255,255, a);
      drawCircle(ren, sp.x, sp.y, sp.r);
    }

    SDL_SetRenderDrawColor(ren, 255,255,255, 255);
    drawCircle(ren, game.mx, game.my, 6.0f);

    int cd = countdownLabel(t_ms);
    if (cd != 0) {
      SDL_SetRenderDrawColor(ren, 255,255,255, 255);
      drawCircle(ren, WIN_W/2.0f, WIN_H/2.0f, 90.0f + cd*10.0f);
    } else if (t_ms < cat.t_go_ms + GO_FLASH_MS) {
      SDL_SetRenderDrawColor(ren, 255,255,255, 255);
      drawCircle(ren, WIN_W/2.0f, WIN_H/2.0f, 120.0f);
    }

    if (game.mode == Mode::MIX) {
      SDL_SetRenderDrawColor(ren, 255,255,255, 25);
      SDL_Rect r{0,0,WIN_W,WIN_H};
      SDL_RenderFillRect(ren, &r);
    }

    SDL_RenderPresent(ren);
  }

  SDL_CloseAudioDevice(dev);
  SDL_DestroyRenderer(ren);
  SDL_DestroyWindow(win);
  SDL_Quit();
  return 0;
}
