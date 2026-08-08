import pytest

from core.topic04_logic import (
    PERCENTILE_DATA,
    SALES,
    SALES_WITH_OUTLIER,
    arithmetic_mean,
    geometric_mean_growth,
    median,
    modes,
    percentile_course_rule,
    weighted_mean,
)


def test_arithmetic_mean_examples_match_notes():
    assert arithmetic_mean(SALES) == pytest.approx(21.25)
    assert arithmetic_mean(SALES_WITH_OUTLIER) == pytest.approx(25.0)


def test_median_resists_course_outlier_example():
    assert median(SALES) == pytest.approx(22.0)
    assert median(SALES_WITH_OUTLIER) == pytest.approx(22.0)


def test_weighted_mean_example_matches_notes():
    assert weighted_mean([70, 80, 90], [0.25, 0.25, 0.50]) == pytest.approx(82.5)
    assert arithmetic_mean([70, 80, 90]) == pytest.approx(80.0)


def test_mode_supports_unimodal_multimodal_and_no_mode():
    assert modes([1, 2, 2, 3, 4]) == [2.0]
    assert modes([1, 1, 2, 2, 3]) == [1.0, 2.0]
    assert modes([1, 2, 3, 4]) == []


def test_percentile_rule_matches_p60_example():
    location, value = percentile_course_rule(PERCENTILE_DATA, 60)
    assert location == pytest.approx(7.8)
    assert value == pytest.approx(54.8)


def test_quartiles_match_notes():
    _, q1 = percentile_course_rule(PERCENTILE_DATA, 25)
    _, q2 = percentile_course_rule(PERCENTILE_DATA, 50)
    _, q3 = percentile_course_rule(PERCENTILE_DATA, 75)
    assert q1 == pytest.approx(45.5)
    assert q2 == pytest.approx(53.0)
    assert q3 == pytest.approx(59.5)


def test_geometric_growth_explains_plus_ten_minus_ten():
    assert geometric_mean_growth([10, -10]) == pytest.approx((0.99 ** 0.5 - 1) * 100)
