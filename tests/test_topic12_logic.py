import numpy as np

from core.topic12_logic import (
    finite_population_correction,
    repeated_sample_means,
    sample_mean_se,
    sample_proportion_se,
    standardized_sample_proportion,
)


def test_sample_mean_standard_error_references():
    assert sample_mean_se(60, 36) == 10
    assert sample_mean_se(20, 100) == 2
    assert sample_mean_se(120, 100) == 12


def test_finite_population_reference():
    fpc = finite_population_correction(400, 100)
    assert abs(fpc - 0.8671) < 0.0002
    assert abs(sample_mean_se(20, 100, population_size=400) - 1.734) < 0.002


def test_sample_proportion_reference():
    assert abs(sample_proportion_se(0.40, 100) - 0.04899) < 1e-5
    assert abs(sample_proportion_se(0.64, 100) - 0.048) < 1e-10
    assert abs(standardized_sample_proportion(0.70, 0.64, 100) - 1.25) < 1e-10


def test_repeated_sample_means_are_deterministic():
    population = np.arange(100, dtype=float)
    a = repeated_sample_means(population, 10, 50, seed=207)
    b = repeated_sample_means(population, 10, 50, seed=207)
    assert np.array_equal(a, b)
