#include "input_raw.hpp"

void InputRaw::begin_frame(uint64_t t_us_now) {
  m_frame_t_us = t_us_now;
  m_count = 0;

  // reset per-frame accumulators (raw, but per-frame)
  m_snap.mouse_dx = 0.0;
  m_snap.mouse_dy = 0.0;
  m_snap.scroll_x = 0.0;
  m_snap.scroll_y = 0.0;
}

void InputRaw::push(const InputEvent& e) {
  if (m_count < kMaxEvents) {
    m_events[m_count++] = e;
  }
}

void InputRaw::on_mouse_move(uint64_t t_us, double x, double y) {
  InputEvent e{};
  e.type = InputEventType::MouseMove;
  e.t_us = t_us;
  e.x = x; e.y = y;

  if (m_has_last) {
    e.dx = x - m_last_x;
    e.dy = y - m_last_y;
    m_snap.mouse_dx += e.dx;
    m_snap.mouse_dy += e.dy;
  } else {
    m_has_last = true;
  }

  m_last_x = x;
  m_last_y = y;

  m_snap.mouse_x = x;
  m_snap.mouse_y = y;

  push(e);
}

void InputRaw::on_scroll(uint64_t t_us, double sx, double sy) {
  InputEvent e{};
  e.type = InputEventType::Scroll;
  e.t_us = t_us;
  e.scroll_x = sx;
  e.scroll_y = sy;

  m_snap.scroll_x += sx;
  m_snap.scroll_y += sy;

  push(e);
}
