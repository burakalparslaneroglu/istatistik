from __future__ import annotations

from collections import Counter
from math import prod
from typing import Iterable

import numpy as np


SALES = np.array([16, 18, 20, 22, 22, 22, 24, 26], dtype=float)
SALES_WITH_OUTLIER = np.array([16, 18, 20, 22, 22, 22, 24, 56], dtype=float)
PERCENTILE_DATA = np.array([40, 42, 45, 47, 50, 52, 54, 55, 58, 60, 65, 70], dtype=float)


def arithmetic_mean(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        raise ValueError("Veri seti boş olamaz.")
    return float(arr.mean())


def weighted_mean(values: Iterable[float], weights: Iterable[float]) -> float:
    x = np.asarray(list(values), dtype=float)
    w = np.asarray(list(weights), dtype=float)
    if x.size == 0 or x.size != w.size:
        raise ValueError("Değerler ve ağırlıklar aynı uzunlukta ve boş olmayan diziler olmalıdır.")
    if float(w.sum()) <= 0:
        raise ValueError("Ağırlıkların toplamı pozitif olmalıdır.")
    return float(np.average(x, weights=w))


def median(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        raise ValueError("Veri seti boş olamaz.")
    return float(np.median(arr))


def modes(values: Iterable[float]) -> list[float]:
    vals = list(values)
    if not vals:
        raise ValueError("Veri seti boş olamaz.")
    counts = Counter(vals)
    max_count = max(counts.values())
    if max_count == 1:
        return []
    return sorted(float(k) for k, v in counts.items() if v == max_count)


def percentile_course_rule(values: Iterable[float], p: float) -> tuple[float, float]:
    """Return (L_p, P_p) using the course rule L_p = p(n+1)/100."""
    arr = np.sort(np.asarray(list(values), dtype=float))
    if arr.size == 0:
        raise ValueError("Veri seti boş olamaz.")
    if not 0 < p < 100:
        raise ValueError("p, 0 ile 100 arasında olmalıdır.")

    location = p * (arr.size + 1) / 100
    if location <= 1:
        return float(location), float(arr[0])
    if location >= arr.size:
        return float(location), float(arr[-1])

    lower_position = int(np.floor(location))
    fraction = location - lower_position
    lower_value = arr[lower_position - 1]
    upper_value = arr[lower_position]
    value = lower_value + fraction * (upper_value - lower_value)
    return float(location), float(value)


def geometric_mean_growth(rates_percent: Iterable[float]) -> float:
    rates = list(rates_percent)
    if not rates:
        raise ValueError("Büyüme oranı listesi boş olamaz.")
    factors = [1 + r / 100 for r in rates]
    if any(f <= 0 for f in factors):
        raise ValueError("Geometrik ortalama için büyüme faktörleri pozitif olmalıdır.")
    g = prod(factors) ** (1 / len(factors))
    return 100 * (g - 1)
