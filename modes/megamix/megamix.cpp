#pragma once
#include <iostream>

void update_megamix(float t) {
    if ((int)t % 8 < 2) std::cout << "[osu]";
    else if ((int)t % 8 < 4) std::cout << "[taiko]";
    else if ((int)t % 8 < 6) std::cout << "[catch]";
    else std::cout << "[mania]";
}
