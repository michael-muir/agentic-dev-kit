// Acceptance test for DEMO-AC-1: the sum of two integers.
#include <cstdlib>
#include <iostream>

#include "demo/demo.hpp"

int main() {
  if (demo::Add(2, 3) != 5) {
    std::cerr << "DEMO-AC-1 failed: Add(2, 3) != 5\n";
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
