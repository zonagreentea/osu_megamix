#include <cstdio>
#include <cstdint>
#include "../ultra/wrap_time.h"

int main() {
  // simulate overflow boundary: ... FFFFFF00, FFFFFF80, 00000010, 00000050
  uint32_t seq[] = {0xFFFFFF00u, 0xFFFFFF80u, 0x00000010u, 0x00000050u};

  // ordering check via wrap delta
  for (int i=1;i<4;i++){
    int32_t d = wrap_delta_u32(seq[i], seq[i-1]);
    std::printf("delta(%08x - %08x) = %+d => %s\n",
      seq[i], seq[i-1], d, (d>0?"after":"before-or-same"));
  }

  // unwrap to u64
  uint32_t last = seq[0];
  uint64_t base = 0;
  uint64_t u0 = unwrap_u32(seq[0], last, base);
  std::printf("unwrap %08x -> %llu\n", seq[0], (unsigned long long)u0);
  for (int i=1;i<4;i++){
    uint64_t u = unwrap_u32(seq[i], last, base);
    std::printf("unwrap %08x -> %llu\n", seq[i], (unsigned long long)u);
  }
  return 0;
}
