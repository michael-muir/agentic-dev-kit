#ifndef DEMO_INCLUDE_DEMO_DEMO_HPP_
#define DEMO_INCLUDE_DEMO_DEMO_HPP_

#include <cstdint>

namespace demo {

/// Returns the sum of two integers.
[[nodiscard]] std::int64_t Add(std::int64_t left, std::int64_t right) noexcept;

}  // namespace demo

#endif  // DEMO_INCLUDE_DEMO_DEMO_HPP_
