import pytest

from core.topic06_logic import (
    addition_rule,
    combinations,
    complement,
    event_probability,
    factorial,
    permutations,
    product_count,
    relative_frequency,
    shipment_metrics,
)


def test_counting_examples():
    assert product_count([4, 3, 2]) == 24
    assert factorial(5) == 120
    assert combinations(5, 3) == 10
    assert permutations(5, 3) == 60


def test_probability_assignment_and_events():
    assert relative_frequency(30, 200) == pytest.approx(0.15)
    assert complement(0.12) == pytest.approx(0.88)
    assert event_probability(set(range(1, 7)), {1, 3, 5}) == pytest.approx(0.5)


def test_addition_rule_course_example():
    assert addition_rule(0.40, 0.35, 0.15) == pytest.approx(0.60)
    assert addition_rule(0.45, 0.30, 0.18) == pytest.approx(0.57)


def test_shipment_application_matches_notes():
    m = shipment_metrics()
    assert m["p_on_time"] == pytest.approx(0.78)
    assert m["p_late"] == pytest.approx(0.22)
    assert m["p_error"] == pytest.approx(0.13)
    assert m["p_late_or_error"] == pytest.approx(0.30)
    assert m["p_on_time_and_error_free"] == pytest.approx(0.70)
