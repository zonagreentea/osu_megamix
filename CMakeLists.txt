cmake_minimum_required(VERSION 3.16)
project(cat_ultra LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(SDL2 REQUIRED)

add_executable(cat_ultra

  cat_ultra.cpp
  timing.cpp
  input_raw.cpp
)
target_include_directories(cat_ultra PRIVATE ${SDL2_INCLUDE_DIRS})
target_link_libraries(cat_ultra PRIVATE ${SDL2_LIBRARIES})
