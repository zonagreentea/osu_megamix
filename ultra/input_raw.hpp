#pragma once
#include <cstdint>
#include <cstddef>

enum class InputEventType : uint8_t {
  KeyDown, KeyUp,
  MouseDown, MouseUp,
  MouseMove,
  Scroll,
  TextUtf32
};

enum class MouseButton : uint8_t { Left=0, Right=1, Middle=2, X1=3, X2=4, Unknown=255 };

struct InputEvent {
  InputEventType type{};
  uint64_t t_us = 0; // monotonic timestamp (microseconds)

  // union-ish payload (kept simple/pod)
  int32_t key = 0;        // platform keycode (raw)
  uint32_t mods = 0;      // raw modifier bits (backend-defined)
  MouseButton mb = MouseButton::Unknown;

  double x = 0.0;         // mouse pos
  double y = 0.0;

  double dx = 0.0;        // mouse delta
  double dy = 0.0;

  double scroll_x = 0.0;
  double scroll_y = 0.0;

  char32_t text = U'\0';  // text input as utf32 codepoint
};

struct InputSnapshot {
  // simple “raw state” view (not filtered, just last-known)
  double mouse_x = 0.0, mouse_y = 0.0;
  double mouse_dx = 0.0, mouse_dy = 0.0;   // accumulated this frame
  double scroll_x = 0.0, scroll_y = 0.0;   // accumulated this frame

  // raw button/key state (backend keycodes map into this via adapter later)
  // kept small + backend-agnostic: we store “recently seen” in event queue for now.
};

class InputRaw {
public:
  static constexpr size_t kMaxEvents = 4096;

  void begin_frame(uint64_t t_us_now);
  void push(const InputEvent& e);

  // returns pointer to internal array + count (valid until next begin_frame)
  const InputEvent* events() const { return m_events; }
  size_t event_count() const { return m_count; }

  const InputSnapshot& snapshot() const { return m_snap; }

  // helpers for adapters
  void on_mouse_move(uint64_t t_us, double x, double y);
  void on_scroll(uint64_t t_us, double sx, double sy);

private:
  InputEvent m_events[kMaxEvents]{};
  size_t m_count = 0;
  InputSnapshot m_snap{};
  uint64_t m_frame_t_us = 0;
  double m_last_x = 0.0, m_last_y = 0.0;
  bool m_has_last = false;
};
