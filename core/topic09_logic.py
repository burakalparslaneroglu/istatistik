from __future__ import annotations

import math
import numpy as np


def binomial_pmf(n: int, p: float, x: int) -> float:
    if n < 0 or x < 0 or x > n or not (0 <= p <= 1):
        return 0.0
    return math.comb(n, x) * (p**x) * ((1 - p) ** (n - x))


def binomial_distribution(n: int, p: float) -> tuple[np.ndarray, np.ndarray]:
    xs = np.arange(n + 1, dtype=int)
    ps = np.array([binomial_pmf(n, p, int(x)) for x in xs], dtype=float)
    return xs, ps


def binomial_mean_var(n: int, p: float) -> tuple[float, float]:
    return n * p, n * p * (1 - p)


def poisson_pmf(lam: float, x: int) -> float:
    if lam < 0 or x < 0:
        return 0.0
    return math.exp(-lam) * (lam**x) / math.factorial(x)


def poisson_distribution(lam: float, max_x: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    if lam < 0:
        raise ValueError("lambda negatif olamaz.")
    if max_x is None:
        max_x = max(8, int(math.ceil(lam + 4 * math.sqrt(max(lam, 1e-9)))))
    xs = np.arange(max_x + 1, dtype=int)
    ps = np.array([poisson_pmf(lam, int(x)) for x in xs], dtype=float)
    return xs, ps


def convert_poisson_rate(rate: float, base_minutes: float, target_minutes: float) -> float:
    if rate < 0 or base_minutes <= 0 or target_minutes <= 0:
        raise ValueError("Geçerli hız ve zaman aralığı gerekir.")
    return rate * target_minutes / base_minutes


def hypergeometric_support(N: int, r: int, n: int) -> np.ndarray:
    if not (0 <= r <= N and 0 <= n <= N):
        raise ValueError("0<=r<=N ve 0<=n<=N olmalıdır.")
    lower = max(0, n - (N - r))
    upper = min(n, r)
    return np.arange(lower, upper + 1, dtype=int)


def hypergeometric_pmf(N: int, r: int, n: int, x: int) -> float:
    if not (0 <= r <= N and 0 <= n <= N):
        return 0.0
    if x not in set(hypergeometric_support(N, r, n).tolist()):
        return 0.0
    return math.comb(r, x) * math.comb(N - r, n - x) / math.comb(N, n)


def hypergeometric_distribution(N: int, r: int, n: int) -> tuple[np.ndarray, np.ndarray]:
    xs = hypergeometric_support(N, r, n)
    ps = np.array([hypergeometric_pmf(N, r, n, int(x)) for x in xs], dtype=float)
    return xs, ps


def hypergeometric_mean_var(N: int, r: int, n: int) -> tuple[float, float]:
    if N <= 1:
        raise ValueError("Varyans için N>1 olmalıdır.")
    p = r / N
    return n * p, n * p * (1 - p) * ((N - n) / (N - 1))


def choose_distribution(*, fixed_trials: bool, two_outcomes: bool, constant_p_independent: bool, fixed_interval_count: bool, finite_population_without_replacement: bool) -> str:
    if finite_population_without_replacement:
        return "Hipergeometrik"
    if fixed_trials and two_outcomes and constant_p_independent:
        return "Binom"
    if fixed_interval_count:
        return "Poisson"
    return "Bu üç modelden biri olduğu söylenemez"
