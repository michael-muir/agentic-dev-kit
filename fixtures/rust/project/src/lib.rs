//! Demo crate used by the agentic-dev-kit fixture tests.

/// Returns the sum of two integers.
///
/// # Examples
///
/// ```
/// assert_eq!(demo::add(2, 3), 5);
/// ```
#[must_use]
pub fn add(left: i64, right: i64) -> i64 {
    left + right
}
