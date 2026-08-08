import pytest

from core.topic05_logic import (
    AD_COUNTS,
    OUTLIER_INCOME,
    SALES,
    SUPPLIER_A,
    SUPPLIER_B,
    VARIANCE_EXAMPLE,
    chebyshev_min_percent,
    coefficient_of_variation,
    iqr_summary,
    outlier_candidates,
    sample_correlation,
    sample_covariance,
    sample_range,
    sample_sd,
    sample_variance,
    z_score,
)


def test_supplier_spread_matches_notes():
    assert SUPPLIER_A.mean() == pytest.approx(10)
    assert SUPPLIER_B.mean() == pytest.approx(10)
    assert sample_range(SUPPLIER_A) == pytest.approx(2)
    assert sample_range(SUPPLIER_B) == pytest.approx(6)
    assert sample_sd(SUPPLIER_A) == pytest.approx(0.70710678)
    assert sample_sd(SUPPLIER_B) == pytest.approx(2.54950976)


def test_variance_example_matches_notes():
    assert VARIANCE_EXAMPLE.mean() == pytest.approx(8)
    assert sample_variance(VARIANCE_EXAMPLE) == pytest.approx(10)
    assert sample_sd(VARIANCE_EXAMPLE) == pytest.approx(10 ** 0.5)


def test_cv_and_z_examples_match_notes():
    assert coefficient_of_variation(80, 8) == pytest.approx(10)
    assert coefficient_of_variation(10, 2) == pytest.approx(20)
    assert z_score(85, 70, 10) == pytest.approx(1.5)
    assert z_score(45, 30, 10) == pytest.approx(1.5)


def test_chebyshev_examples_match_notes():
    assert chebyshev_min_percent(2) == pytest.approx(75)
    assert chebyshev_min_percent(3) == pytest.approx(100 * 8 / 9)


def test_iqr_outlier_example_matches_notes():
    summary = iqr_summary(OUTLIER_INCOME)
    assert summary["q1"] == pytest.approx(23)
    assert summary["median"] == pytest.approx(26)
    assert summary["q3"] == pytest.approx(29)
    assert summary["iqr"] == pytest.approx(6)
    assert summary["lower_fence"] == pytest.approx(14)
    assert summary["upper_fence"] == pytest.approx(38)
    assert outlier_candidates(OUTLIER_INCOME) == [65.0]


def test_covariance_and_correlation_example():
    assert sample_covariance(AD_COUNTS, SALES) == pytest.approx(6.75)
    assert sample_correlation(AD_COUNTS, SALES) > 0.99
