from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


DEVICE_PURCHASE_COUNTS = pd.DataFrame(
    {
        "Satın aldı": [180, 80],
        "Satın almadı": [420, 320],
    },
    index=["Mobil", "Masaüstü"],
)


def joint_probability_table(counts: pd.DataFrame) -> pd.DataFrame:
    total = float(counts.to_numpy().sum())
    if total <= 0:
        raise ValueError("Toplam gözlem sayısı pozitif olmalıdır.")
    return counts / total


def conditional_probability(p_intersection: float, p_condition: float) -> float:
    if not 0 <= p_intersection <= 1 or not 0 < p_condition <= 1:
        raise ValueError("Olasılıklar geçerli aralıkta olmalıdır ve koşul olasılığı pozitif olmalıdır.")
    if p_intersection > p_condition:
        raise ValueError("Kesişim olasılığı koşul olasılığından büyük olamaz.")
    return p_intersection / p_condition


def independent_from_conditional(p_a: float, p_a_given_b: float, tol: float = 1e-12) -> bool:
    return abs(p_a - p_a_given_b) <= tol


def multiplication_rule(p_a: float, p_b_given_a: float) -> float:
    if not 0 <= p_a <= 1 or not 0 <= p_b_given_a <= 1:
        raise ValueError("Olasılıklar 0 ile 1 arasında olmalıdır.")
    return p_a * p_b_given_a


def shipping_tree_paths(
    p_standard: float = 0.70,
    p_same_day_given_standard: float = 0.80,
    p_same_day_given_priority: float = 0.95,
) -> dict[str, float]:
    if not 0 <= p_standard <= 1:
        raise ValueError("Standart sipariş olasılığı geçersiz.")
    for p in (p_same_day_given_standard, p_same_day_given_priority):
        if not 0 <= p <= 1:
            raise ValueError("Koşullu olasılıklar 0 ile 1 arasında olmalıdır.")
    p_priority = 1 - p_standard
    paths = {
        "Standart × aynı gün": p_standard * p_same_day_given_standard,
        "Standart × daha geç": p_standard * (1 - p_same_day_given_standard),
        "Öncelikli × aynı gün": p_priority * p_same_day_given_priority,
        "Öncelikli × daha geç": p_priority * (1 - p_same_day_given_priority),
    }
    return paths


def bayes_posteriors(priors: Iterable[float], likelihoods: Iterable[float]) -> np.ndarray:
    p = np.asarray(list(priors), dtype=float)
    l = np.asarray(list(likelihoods), dtype=float)
    if p.size == 0 or p.size != l.size:
        raise ValueError("Önsel ve koşullu olasılık dizileri aynı uzunlukta ve boş olmamalıdır.")
    if np.any(p < 0) or np.any(l < 0) or np.any(l > 1):
        raise ValueError("Olasılıklar geçersiz.")
    if not np.isclose(p.sum(), 1.0):
        raise ValueError("Önsel olasılıkların toplamı 1 olmalıdır.")
    joint = p * l
    evidence = joint.sum()
    if evidence <= 0:
        raise ValueError("Yeni bilginin toplam olasılığı pozitif olmalıdır.")
    return joint / evidence


def fraud_alarm_posterior(prevalence: float, sensitivity: float, false_positive_rate: float) -> float:
    posterior = bayes_posteriors(
        [prevalence, 1 - prevalence],
        [sensitivity, false_positive_rate],
    )
    return float(posterior[0])


def natural_frequencies(
    total: int,
    prevalence: float,
    sensitivity: float,
    false_positive_rate: float,
) -> dict[str, int]:
    if total <= 0:
        raise ValueError("Toplam gözlem sayısı pozitif olmalıdır.")
    fraud = round(total * prevalence)
    nonfraud = total - fraud
    true_alarm = round(fraud * sensitivity)
    missed = fraud - true_alarm
    false_alarm = round(nonfraud * false_positive_rate)
    true_clear = nonfraud - false_alarm
    return {
        "Gerçek sahte + alarm": true_alarm,
        "Gerçek sahte + alarm yok": missed,
        "Sahte değil + alarm": false_alarm,
        "Sahte değil + alarm yok": true_clear,
    }
