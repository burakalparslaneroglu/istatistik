import numpy as np
import pytest

from core.topic08_logic import (
    ADDON_PROBS, ADDON_VALUES, JOINT_PROBS,
    distribution_sd, distribution_variance, event_probability, expected_value,
    independent_joint, joint_moments, marginals, profit_distribution,
    running_mean_simulation, validate_pmf,
)


def test_addon_distribution_matches_notes():
    assert validate_pmf(ADDON_VALUES, ADDON_PROBS)
    assert event_probability(ADDON_VALUES, ADDON_PROBS, lower=2) == pytest.approx(0.60)
    assert expected_value(ADDON_VALUES, ADDON_PROBS) == pytest.approx(1.80)
    assert distribution_variance(ADDON_VALUES, ADDON_PROBS) == pytest.approx(1.06)
    assert distribution_sd(ADDON_VALUES, ADDON_PROBS) == pytest.approx(np.sqrt(1.06))


def test_same_mean_different_variance_example():
    a_v, a_p = np.array([0,2,4]), np.array([.25,.5,.25])
    b_v, b_p = np.array([1,2,3]), np.array([.25,.5,.25])
    assert expected_value(a_v,a_p) == pytest.approx(2)
    assert expected_value(b_v,b_p) == pytest.approx(2)
    assert distribution_variance(a_v,a_p) == pytest.approx(2)
    assert distribution_variance(b_v,b_p) == pytest.approx(.5)


def test_joint_distribution_moments_match_notes():
    px, py = marginals(JOINT_PROBS)
    assert px.tolist() == pytest.approx([.25,.35,.40])
    assert py.tolist() == pytest.approx([.40,.35,.25])
    m = joint_moments(JOINT_PROBS)
    assert m['E_X'] == pytest.approx(1.15)
    assert m['E_Y'] == pytest.approx(.85)
    assert m['E_XY'] == pytest.approx(1.45)
    assert m['Var_X'] == pytest.approx(.6275)
    assert m['Var_Y'] == pytest.approx(.6275)
    assert m['Cov'] == pytest.approx(.4725)
    assert m['Corr'] == pytest.approx(.4725/.6275)
    assert not independent_joint(JOINT_PROBS)


def test_profit_transform_and_deterministic_simulation():
    profits, probs = profit_distribution()
    assert profits.tolist() == pytest.approx([-250,50,350,650,950])
    assert expected_value(profits,probs) == pytest.approx(290)
    r1 = running_mean_simulation(ADDON_VALUES,ADDON_PROBS,100,seed=207)
    r2 = running_mean_simulation(ADDON_VALUES,ADDON_PROBS,100,seed=207)
    assert np.allclose(r1,r2)
