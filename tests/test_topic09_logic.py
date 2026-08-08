import pytest

from core.topic09_logic import (
    binomial_mean_var, binomial_pmf, choose_distribution, convert_poisson_rate,
    hypergeometric_mean_var, hypergeometric_pmf, poisson_pmf,
)


def test_binomial_reference_example_matches_notes():
    assert binomial_pmf(8,.25,2) == pytest.approx(.3114624, rel=1e-5)
    assert 1-binomial_pmf(8,.25,0) == pytest.approx(.8998871, rel=1e-5)
    mean,var = binomial_mean_var(8,.25)
    assert mean == pytest.approx(2)
    assert var == pytest.approx(1.5)


def test_poisson_reference_example_and_rate_conversion():
    assert convert_poisson_rate(12,60,15) == pytest.approx(3)
    assert poisson_pmf(3,2) == pytest.approx(.2240418, rel=1e-5)


def test_hypergeometric_reference_example_matches_notes():
    assert hypergeometric_pmf(20,5,4,1) == pytest.approx(.4695562, rel=1e-5)
    mean,var = hypergeometric_mean_var(20,5,4)
    assert mean == pytest.approx(1)
    assert var == pytest.approx(.6315789474)


def test_distribution_choice_logic():
    assert choose_distribution(fixed_trials=True,two_outcomes=True,constant_p_independent=True,fixed_interval_count=False,finite_population_without_replacement=False) == 'Binom'
    assert choose_distribution(fixed_trials=False,two_outcomes=False,constant_p_independent=False,fixed_interval_count=True,finite_population_without_replacement=False) == 'Poisson'
    assert choose_distribution(fixed_trials=False,two_outcomes=True,constant_p_independent=False,fixed_interval_count=False,finite_population_without_replacement=True) == 'Hipergeometrik'
