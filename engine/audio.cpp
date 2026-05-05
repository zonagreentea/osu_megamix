#pragma once
#include <iostream>

void play_audio_tick(float t) {
    if (((int)(t * 2)) % 2 == 0) {
        std::cout << "[kick]";
    } else {
        std::cout << "[snare]";
    }
}
