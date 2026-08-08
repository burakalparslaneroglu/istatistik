from __future__ import annotations

import math
import numpy as np


def uniform_density(a: float, b: float) -> float:
    if b <= a:
        raise ValueError("Üst sınır alt sınırdan büyük olmalıdır.")
    return 1.0 / (b - a)


def uniform_probability(a: float, b: float, c: float, d: float) -> float:
    if b <= a:
        raise ValueError("Üst sınır alt sınırdan büyük olmalıdır.")
    lo = max(a, min(c, d))
    hi = min(b, max(c, d))
    return max(0.0, hi - lo) / (b - a)


def uniform_mean_var(a: float, b: float) -> tuple[float, float]:
    if b <= a:
        raise ValueError("Üst sınır alt sınırdan büyük olmalıdır.")
    return (a + b) / 2.0, ((b - a) ** 2) / 12.0


def normal_density(x, mu: float = 0.0, sigma: float = 1.0):
    if sigma <= 0:
        raise ValueError("Standart sapma pozitif olmalıdır.")
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def z_score(x: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("Standart sapma pozitif olmalıdır.")
    return (x - mu) / sigma


def from_z(z: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("Standart sapma pozitif olmalıdır.")
    return mu + z * sigma


def normal_interval_probability(lower: float, upper: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("Standart sapma pozitif olmalıdır.")
    lo, hi = sorted((lower, upper))
    def cdf(v: float) -> float:
        return 0.5 * (1 + math.erf((v - mu) / (sigma * math.sqrt(2))))
    return cdf(hi) - cdf(lo)


def empirical_rule_bounds(mu: float, sigma: float, k: int) -> tuple[float, float, float]:
    if sigma <= 0 or k not in (1, 2, 3):
        raise ValueError("sigma pozitif ve k 1, 2 veya 3 olmalıdır.")
    percentages = {1: 68.3, 2: 95.4, 3: 99.7}
    return mu - k * sigma, mu + k * sigma, percentages[k]
