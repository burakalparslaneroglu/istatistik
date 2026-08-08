from core.topic11_logic import (
    binomial_normal_approx_probability,
    continuity_bounds,
    exponential_cdf,
    exponential_interval_probability,
    normal_quantile,
    normal_approximation_suitable,
    std_normal_cdf,
    std_normal_probability,
)


def test_standard_normal_reference_values():
    assert abs(std_normal_cdf(1.0) - 0.8413) < 5e-5
    assert abs(std_normal_probability("Sol kuyruk", 1.5) - 0.9332) < 5e-5
    assert abs(std_normal_probability("İki değer arası", -0.5, 1.25) - 0.5859) < 2e-4


def test_inverse_normal_reference_cutoff():
    assert abs(normal_quantile(0.90, 70, 10) - 82.8155) < 0.01


def test_continuity_correction_reference():
    assert continuity_bounds("X = x", 12) == (11.5, 12.5)
    assert normal_approximation_suitable(100, 0.10)
    approx = binomial_normal_approx_probability(100, 0.10, "X = x", 12)
    approx_table = binomial_normal_approx_probability(100, 0.10, "X = x", 12, z_decimals=2)
    assert abs(approx - 0.1062) < 0.0001
    assert abs(approx_table - 0.1052) < 0.0001


def test_exponential_reference_values():
    assert abs(exponential_cdf(6, 15) - 0.3297) < 1e-4
    assert abs(exponential_cdf(18, 15) - 0.6988) < 1e-4
    assert abs(exponential_interval_probability(6, 18, 15) - 0.3691) < 1e-4
