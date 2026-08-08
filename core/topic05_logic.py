from __future__ import annotations

from typing import Iterable

import numpy as np

from core.topic04_logic import percentile_course_rule


SUPPLIER_A = np.array([9, 10, 10, 10, 11], dtype=float)
SUPPLIER_B = np.array([7, 8, 10, 12, 13], dtype=float)
VARIANCE_EXAMPLE = np.array([4, 6, 8, 10, 12], dtype=float)
OUTLIER_INCOME = np.array([20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 65], dtype=float)
AD_COUNTS = np.array([1, 2, 3, 4, 5], dtype=float)
SALES = np.array([20, 22, 25, 27, 31], dtype=float)


def sample_range(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        raise ValueError("Veri seti boş olamaz.")
    return float(arr.max() - arr.min())


def sample_variance(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    if arr.size < 2:
        raise ValueError("Örneklem varyansı için en az iki gözlem gerekir.")
    return float(np.var(arr, ddof=1))


def sample_sd(values: Iterable[float]) -> float:
    return float(np.sqrt(sample_variance(values)))


def coefficient_of_variation(mean: float, sd: float) -> float:
    if mean <= 0:
        raise ValueError("CV için ortalama pozitif ve anlamlı olmalıdır.")
    if sd < 0:
        raise ValueError("Standart sapma negatif olamaz.")
    return 100 * sd / mean


def z_score(value: float, mean: float, sd: float) -> float:
    if sd <= 0:
        raise ValueError("Standart sapma pozitif olmalıdır.")
    return (value - mean) / sd


def chebyshev_min_percent(k: float) -> float:
    if k <= 1:
        raise ValueError("Chebyshev eşitsizliği için k > 1 olmalıdır.")
    return 100 * (1 - 1 / (k**2))


def iqr_summary(values: Iterable[float]) -> dict[str, float]:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        raise ValueError("Veri seti boş olamaz.")
    _, q1 = percentile_course_rule(arr, 25)
    _, median = percentile_course_rule(arr, 50)
    _, q3 = percentile_course_rule(arr, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return {
        "min": float(arr.min()),
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "max": float(arr.max()),
        "iqr": float(iqr),
        "lower_fence": float(lower),
        "upper_fence": float(upper),
    }


def outlier_candidates(values: Iterable[float]) -> list[float]:
    arr = np.asarray(list(values), dtype=float)
    summary = iqr_summary(arr)
    mask = (arr < summary["lower_fence"]) | (arr > summary["upper_fence"])
    return [float(x) for x in arr[mask]]


def sample_covariance(x: Iterable[float], y: Iterable[float]) -> float:
    xa = np.asarray(list(x), dtype=float)
    ya = np.asarray(list(y), dtype=float)
    if xa.size < 2 or xa.size != ya.size:
        raise ValueError("İki dizi aynı uzunlukta ve en az iki gözlemli olmalıdır.")
    return float(np.cov(xa, ya, ddof=1)[0, 1])


def sample_correlation(x: Iterable[float], y: Iterable[float]) -> float:
    xa = np.asarray(list(x), dtype=float)
    ya = np.asarray(list(y), dtype=float)
    if xa.size < 2 or xa.size != ya.size:
        raise ValueError("İki dizi aynı uzunlukta ve en az iki gözlemli olmalıdır.")
    if np.std(xa, ddof=1) == 0 or np.std(ya, ddof=1) == 0:
        raise ValueError("Korelasyon için her iki değişkende de değişkenlik olmalıdır.")
    return float(np.corrcoef(xa, ya)[0, 1])
