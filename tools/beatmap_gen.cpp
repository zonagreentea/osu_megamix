#pragma once
#include <vector>

std::vector<float> generate_pattern(float bpm) {
    std::vector<float> pattern;
    float interval = 60.0f / bpm;
    for (int i = 0; i < 32; i++) {
        pattern.push_back(i * interval);
    }
    return pattern;
}
