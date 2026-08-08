from __future__ import annotations

import math
from typing import Iterable


SHIPMENT_PROBABILITIES = {
    "Zamanında ve hatasız": 0.70,
    "Zamanında ve hatalı": 0.08,
    "Geç ve hatasız": 0.17,
    "Geç ve hatalı": 0.05,
}


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Faktöriyel negatif sayılar için tanımlı değildir.")
    return math.factorial(n)


def combinations(n: int, r: int) -> int:
    if n < 0 or r < 0 or r > n:
        raise ValueError("0 <= r <= n olmalıdır.")
    return math.comb(n, r)


def permutations(n: int, r: int) -> int:
    if n < 0 or r < 0 or r > n:
        raise ValueError("0 <= r <= n olmalıdır.")
    return math.perm(n, r)


def product_count(stage_sizes: Iterable[int]) -> int:
    sizes = list(stage_sizes)
    if not sizes or any(s <= 0 for s in sizes):
        raise ValueError("Aşama seçenek sayıları pozitif olmalıdır.")
    return math.prod(sizes)


def classical_probability(favorable: int, total: int) -> float:
    if total <= 0 or favorable < 0 or favorable > total:
        raise ValueError("0 <= elverişli sonuç <= toplam sonuç ve toplam > 0 olmalıdır.")
    return favorable / total


def relative_frequency(successes: int, trials: int) -> float:
    return classical_probability(successes, trials)


def complement(probability: float) -> float:
    if not 0 <= probability <= 1:
        raise ValueError("Olasılık 0 ile 1 arasında olmalıdır.")
    return 1 - probability


def addition_rule(p_a: float, p_b: float, p_intersection: float) -> float:
    for p in (p_a, p_b, p_intersection):
        if not 0 <= p <= 1:
            raise ValueError("Olasılıklar 0 ile 1 arasında olmalıdır.")
    if p_intersection > min(p_a, p_b):
        raise ValueError("Kesişim olasılığı tekil olasılıklardan büyük olamaz.")
    result = p_a + p_b - p_intersection
    if not 0 <= result <= 1:
        raise ValueError("Verilen olasılıklar tutarlı değildir.")
    return result


def event_probability(sample_space: set[int], event: set[int]) -> float:
    if not sample_space or not event.issubset(sample_space):
        raise ValueError("Olay örnek uzayın alt kümesi olmalıdır.")
    return len(event) / len(sample_space)


def shipment_metrics() -> dict[str, float]:
    p_late = SHIPMENT_PROBABILITIES["Geç ve hatasız"] + SHIPMENT_PROBABILITIES["Geç ve hatalı"]
    p_error = SHIPMENT_PROBABILITIES["Zamanında ve hatalı"] + SHIPMENT_PROBABILITIES["Geç ve hatalı"]
    p_late_or_error = addition_rule(p_late, p_error, SHIPMENT_PROBABILITIES["Geç ve hatalı"])
    return {
        "p_on_time": 1 - p_late,
        "p_late": p_late,
        "p_error": p_error,
        "p_late_or_error": p_late_or_error,
        "p_on_time_and_error_free": 1 - p_late_or_error,
    }
