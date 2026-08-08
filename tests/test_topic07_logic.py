import pytest

from core.topic07_logic import (
    DEVICE_PURCHASE_COUNTS,
    bayes_posteriors,
    conditional_probability,
    fraud_alarm_posterior,
    independent_from_conditional,
    joint_probability_table,
    multiplication_rule,
    natural_frequencies,
    shipping_tree_paths,
)


def test_device_purchase_probabilities_match_notes():
    probs = joint_probability_table(DEVICE_PURCHASE_COUNTS)
    assert probs.loc["Mobil", "Satın aldı"] == pytest.approx(0.18)
    assert probs.loc["Masaüstü", "Satın aldı"] == pytest.approx(0.08)
    assert conditional_probability(0.18, 0.60) == pytest.approx(0.30)
    assert conditional_probability(0.18, 0.26) == pytest.approx(180 / 260)


def test_independence_and_multiplication():
    assert independent_from_conditional(0.30, 0.30)
    assert not independent_from_conditional(0.30, 0.45)
    assert multiplication_rule(0.80, 0.90) == pytest.approx(0.72)


def test_probability_tree_matches_notes():
    paths = shipping_tree_paths()
    assert paths["Standart × aynı gün"] == pytest.approx(0.56)
    assert paths["Standart × daha geç"] == pytest.approx(0.14)
    assert paths["Öncelikli × aynı gün"] == pytest.approx(0.285)
    assert paths["Öncelikli × daha geç"] == pytest.approx(0.015)
    assert sum(paths.values()) == pytest.approx(1.0)


def test_bayes_supplier_example_matches_notes():
    post = bayes_posteriors([0.70, 0.30], [0.02, 0.06])
    assert post[0] == pytest.approx(0.4375)
    assert post[1] == pytest.approx(0.5625)


def test_base_rate_example_matches_notes():
    posterior = fraud_alarm_posterior(0.02, 0.90, 0.05)
    assert posterior == pytest.approx(0.018 / 0.067)
    freq = natural_frequencies(10_000, 0.02, 0.90, 0.05)
    assert freq["Gerçek sahte + alarm"] == 180
    assert freq["Gerçek sahte + alarm yok"] == 20
    assert freq["Sahte değil + alarm"] == 490
    assert freq["Sahte değil + alarm yok"] == 9310
