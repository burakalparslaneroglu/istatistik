from __future__ import annotations

from math import sqrt
import numpy as np


def sample_mean_se(sigma: float, n: int, *, population_size: int | None = None) -> float:
    if sigma < 0 or n <= 0:
        raise ValueError("sigma negatif olamaz ve n pozitif olmalıdır.")
    se = sigma / sqrt(n)
    if population_size is not None:
        se *= finite_population_correction(population_size, n)
    return se


def finite_population_correction(population_size: int, n: int) -> float:
    if population_size <= 1 or n <= 0 or n > population_size:
        raise ValueError("0 < n ≤ N ve N > 1 olmalıdır.")
    return sqrt((population_size - n) / (population_size - 1))


def sample_proportion_se(p: float, n: int, *, population_size: int | None = None) -> float:
    if not 0 <= p <= 1 or n <= 0:
        raise ValueError("p [0,1] aralığında ve n pozitif olmalıdır.")
    se = sqrt(p * (1 - p) / n)
    if population_size is not None:
        se *= finite_population_correction(population_size, n)
    return se


def repeated_sample_means(
    population: np.ndarray,
    n: int,
    repetitions: int,
    *,
    seed: int = 207,
    replace: bool = True,
) -> np.ndarray:
    values = np.asarray(population, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("Anakütle tek boyutlu ve boş olmayan bir dizi olmalıdır.")
    if n <= 0 or repetitions <= 0:
        raise ValueError("n ve tekrar sayısı pozitif olmalıdır.")
    if not replace and n > values.size:
        raise ValueError("Yerine koymadan örneklemede n anakütleyi aşamaz.")
    rng = np.random.default_rng(seed)
    if replace:
        draws = rng.choice(values, size=(repetitions, n), replace=True)
        return draws.mean(axis=1)
    return np.array([rng.choice(values, size=n, replace=False).mean() for _ in range(repetitions)])


def clt_exponential_sample_means(n: int, repetitions: int, *, mean: float = 1.0, seed: int = 207) -> np.ndarray:
    if n <= 0 or repetitions <= 0 or mean <= 0:
        raise ValueError("Parametreler pozitif olmalıdır.")
    rng = np.random.default_rng(seed)
    return rng.exponential(scale=mean, size=(repetitions, n)).mean(axis=1)


def standardized_sample_mean(xbar: float, mu: float, sigma: float, n: int) -> float:
    se = sample_mean_se(sigma, n)
    if se == 0:
        raise ValueError("Standart hata sıfır olamaz.")
    return (xbar - mu) / se


def standardized_sample_proportion(phat: float, p: float, n: int) -> float:
    se = sample_proportion_se(p, n)
    if se == 0:
        raise ValueError("Standart hata sıfır olamaz.")
    return (phat - p) / se
