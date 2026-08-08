from __future__ import annotations

from math import comb, exp, sqrt
from statistics import NormalDist

_STD_NORMAL = NormalDist()


def std_normal_cdf(z: float) -> float:
    return float(_STD_NORMAL.cdf(z))


def std_normal_probability(event: str, a: float, b: float | None = None) -> float:
    if event == "Sol kuyruk":
        return std_normal_cdf(a)
    if event == "Sağ kuyruk":
        return 1.0 - std_normal_cdf(a)
    if event == "İki değer arası":
        if b is None:
            raise ValueError("İki değer arası olayında ikinci sınır gereklidir.")
        lo, hi = sorted((a, b))
        return std_normal_cdf(hi) - std_normal_cdf(lo)
    raise ValueError("Bilinmeyen standart normal olay türü.")


def normal_probability(event: str, a: float, mu: float, sigma: float, b: float | None = None) -> float:
    if sigma <= 0:
        raise ValueError("Standart sapma pozitif olmalıdır.")
    za = (a - mu) / sigma
    zb = None if b is None else (b - mu) / sigma
    return std_normal_probability(event, za, zb)


def normal_quantile(probability: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if not 0.0 < probability < 1.0:
        raise ValueError("Olasılık 0 ile 1 arasında olmalıdır.")
    if sigma <= 0:
        raise ValueError("Standart sapma pozitif olmalıdır.")
    return float(mu + sigma * _STD_NORMAL.inv_cdf(probability))


def binomial_pmf(n: int, p: float, x: int) -> float:
    if x < 0 or x > n:
        return 0.0
    return comb(n, x) * (p**x) * ((1 - p) ** (n - x))


def binomial_normal_params(n: int, p: float) -> tuple[float, float]:
    return n * p, sqrt(n * p * (1 - p))


def normal_approximation_suitable(n: int, p: float) -> bool:
    return n * p >= 5 and n * (1 - p) >= 5


def continuity_bounds(event: str, x: int, upper: int | None = None) -> tuple[float | None, float | None]:
    if event == "X = x":
        return x - 0.5, x + 0.5
    if event == "X ≤ x":
        return None, x + 0.5
    if event == "X ≥ x":
        return x - 0.5, None
    if event == "a ≤ X ≤ b":
        if upper is None:
            raise ValueError("Aralık olayında üst sınır gereklidir.")
        lo, hi = sorted((x, upper))
        return lo - 0.5, hi + 0.5
    raise ValueError("Bilinmeyen binom olay türü.")


def binomial_exact_probability(n: int, p: float, event: str, x: int, upper: int | None = None) -> float:
    if event == "X = x":
        return binomial_pmf(n, p, x)
    if event == "X ≤ x":
        return sum(binomial_pmf(n, p, k) for k in range(0, min(x, n) + 1))
    if event == "X ≥ x":
        return sum(binomial_pmf(n, p, k) for k in range(max(x, 0), n + 1))
    if event == "a ≤ X ≤ b":
        if upper is None:
            raise ValueError("Aralık olayında üst sınır gereklidir.")
        lo, hi = sorted((x, upper))
        return sum(binomial_pmf(n, p, k) for k in range(max(lo, 0), min(hi, n) + 1))
    raise ValueError("Bilinmeyen binom olay türü.")


def binomial_normal_approx_probability(
    n: int,
    p: float,
    event: str,
    x: int,
    upper: int | None = None,
    *,
    z_decimals: int | None = None,
) -> float:
    mu, sigma = binomial_normal_params(n, p)
    if sigma == 0:
        return float("nan")
    lo, hi = continuity_bounds(event, x, upper)

    def z_value(bound: float) -> float:
        z = (bound - mu) / sigma
        return round(z, z_decimals) if z_decimals is not None else z

    if lo is None:
        return std_normal_cdf(z_value(hi))
    if hi is None:
        return 1 - std_normal_cdf(z_value(lo))
    return std_normal_cdf(z_value(hi)) - std_normal_cdf(z_value(lo))


def exponential_plot_bounds(event: str, x: float, mean: float, b: float | None = None) -> tuple[float, float, float]:
    """Return a safe finite plotting interval (lo, hi, xmax) for exponential-event shading."""
    if mean <= 0:
        raise ValueError("Ortalama süre pozitif olmalıdır.")
    if x < 0 or (b is not None and b < 0):
        raise ValueError("Süre sınırları negatif olamaz.")

    candidate_upper = max(60.0, 5 * mean, x, b if b is not None else 0.0)
    if event == "X ≤ x":
        return 0.0, x, candidate_upper
    if event == "X > x":
        right_tail_upper = max(candidate_upper, x + 5 * mean)
        return x, right_tail_upper, right_tail_upper
    if event == "a < X ≤ b":
        if b is None:
            raise ValueError("Aralık olayında ikinci sınır gereklidir.")
        lo, hi = sorted((x, b))
        return lo, hi, candidate_upper
    raise ValueError("Bilinmeyen üstel dağılım olay türü.")

def exponential_cdf(x: float, mean: float) -> float:
    if mean <= 0:
        raise ValueError("Ortalama süre pozitif olmalıdır.")
    if x <= 0:
        return 0.0
    return 1 - exp(-x / mean)


def exponential_survival(x: float, mean: float) -> float:
    if mean <= 0:
        raise ValueError("Ortalama süre pozitif olmalıdır.")
    if x <= 0:
        return 1.0
    return exp(-x / mean)


def exponential_interval_probability(a: float, b: float, mean: float) -> float:
    lo, hi = sorted((a, b))
    return exponential_cdf(hi, mean) - exponential_cdf(lo, mean)
