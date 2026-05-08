#pragma once
#include <vector>

struct Note {
    float time;
    int lane;
};

std::vector<Note> generate_test_notes() {
    std::vector<Note> notes;
    for (int i = 0; i < 64; i++) {
        notes.push_back({i * 0.5f, i % 4});
    }
    return notes;
}
