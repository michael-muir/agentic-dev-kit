cmake_minimum_required(VERSION 3.20)
project(demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(demo src/demo.cpp)
target_include_directories(demo PUBLIC include)

enable_testing()
add_executable(demo_tests tests/demo_test.cpp)
target_link_libraries(demo_tests PRIVATE demo)
add_test(NAME demo_ac_1_adds_two_integers COMMAND demo_tests)
