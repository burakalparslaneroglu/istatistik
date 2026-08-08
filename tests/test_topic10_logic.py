import numpy as np
import pytest

from core.topic10_logic import (
    empirical_rule_bounds, from_z, normal_density, normal_interval_probability,
    uniform_density, uniform_mean_var, uniform_probability, z_score,
)


def test_uniform_reference_example_matches_notes():
    assert uniform_density(120,140) == pytest.approx(.05)
    assert uniform_probability(120,140,128,136) == pytest.approx(.40)
    mean,var = uniform_mean_var(120,140)
    assert mean == pytest.approx(130)
    assert var == pytest.approx(100/3)
    assert np.sqrt(var) == pytest.approx(5.77350269)


def test_density_can_exceed_one_while_total_area_is_one():
    assert uniform_density(0,.5) == pytest.approx(2)
    assert uniform_probability(0,.5,0,.5) == pytest.approx(1)


def test_normal_reference_z_examples_match_notes():
    assert z_score(85,70,10) == pytest.approx(1.5)
    assert z_score(55,70,10) == pytest.approx(-1.5)
    assert from_z(-2,70,10) == pytest.approx(50)
    assert from_z(1,500,10) == pytest.approx(510)


def test_empirical_rule_and_area_preservation():
    assert empirical_rule_bounds(70,10,1) == pytest.approx((60,80,68.3))
    assert empirical_rule_bounds(70,10,2) == pytest.approx((50,90,95.4))
    exact = normal_interval_probability(60,80,70,10)
    assert exact == pytest.approx(.68268949, rel=1e-6)


def test_normal_density_peak_decreases_when_sigma_grows():
    assert normal_density([0],0,1)[0] > normal_density([0],0,2)[0]
