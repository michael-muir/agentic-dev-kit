"""Acceptance tests for the demo package."""

from demo import add


def test_demo_ac_1_adds_two_integers() -> None:
    """DEMO-AC-1: the sum of 2 and 3 is 5."""
    assert add(2, 3) == 5
