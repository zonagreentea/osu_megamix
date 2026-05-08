#pragma once
#include <chrono>
#include <thread>
#include <iostream>

void run_game() {
    using namespace std::chrono;
    auto start = high_resolution_clock::now();

    while (true) {
        auto now = high_resolution_clock::now();
        float t = duration<float>(now - start).count();

        std::cout << "tick: " << t << "\\r";
        std::this_thread::sleep_for(milliseconds(16)); // ~60fps
    }
}
