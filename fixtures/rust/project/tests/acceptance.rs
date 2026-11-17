//! Acceptance tests for the demo crate.

#[test]
fn demo_ac_1_adds_two_integers() {
    assert_eq!(demo::add(2, 3), 5);
}
