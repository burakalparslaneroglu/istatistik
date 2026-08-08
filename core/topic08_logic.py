from __future__ import annotations

import numpy as np

ADDON_VALUES = np.array([0, 1, 2, 3, 4], dtype=float)
ADDON_PROBS = np.array([0.10, 0.30, 0.35, 0.20, 0.05], dtype=float)

JOINT_PROBS = np.array(
    [
        [0.25, 0.10, 0.05],
        [0.00, 0.25, 0.10],
        [0.00, 0.00, 0.25],
    ],
    dtype=float,
)


def validate_pmf(values, probs) -> bool:
    values = np.asarray(values, dtype=float)
    probs = np.asarray(probs, dtype=float)
    return bool(values.size == probs.size and values.size > 0 and np.all(probs >= 0) and np.isclose(probs.sum(), 1.0))


def event_probability(values, probs, *, lower=None, upper=None, inclusive_lower=True, inclusive_upper=True) -> float:
    values = np.asarray(values, dtype=float)
    probs = np.asarray(probs, dtype=float)
    if not validate_pmf(values, probs):
        raise ValueError("Geçerli bir olasılık dağılımı gerekir.")
    mask = np.ones(values.shape, dtype=bool)
    if lower is not None:
        mask &= values >= lower if inclusive_lower else values > lower
    if upper is not None:
        mask &= values <= upper if inclusive_upper else values < upper
    return float(probs[mask].sum())


def expected_value(values, probs) -> float:
    values = np.asarray(values, dtype=float)
    probs = np.asarray(probs, dtype=float)
    if not validate_pmf(values, probs):
        raise ValueError("Geçerli bir olasılık dağılımı gerekir.")
    return float(np.sum(values * probs))


def distribution_variance(values, probs) -> float:
    mu = expected_value(values, probs)
    values = np.asarray(values, dtype=float)
    probs = np.asarray(probs, dtype=float)
    return float(np.sum((values - mu) ** 2 * probs))


def distribution_sd(values, probs) -> float:
    return float(np.sqrt(distribution_variance(values, probs)))


def running_mean_simulation(values, probs, repetitions: int, seed: int = 207) -> np.ndarray:
    if repetitions < 1:
        raise ValueError("Tekrar sayısı en az 1 olmalıdır.")
    values = np.asarray(values, dtype=float)
    probs = np.asarray(probs, dtype=float)
    if not validate_pmf(values, probs):
        raise ValueError("Geçerli bir olasılık dağılımı gerekir.")
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=repetitions, p=probs)
    return np.cumsum(draws) / np.arange(1, repetitions + 1)


def marginals(joint: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    joint = np.asarray(joint, dtype=float)
    if joint.ndim != 2 or np.any(joint < 0) or not np.isclose(joint.sum(), 1.0):
        raise ValueError("Ortak olasılık tablosu negatif olmayan ve toplamı 1 olan bir matris olmalıdır.")
    # rows are Y, columns are X
    return joint.sum(axis=0), joint.sum(axis=1)


def joint_moments(joint: np.ndarray, x_values=None, y_values=None) -> dict[str, float]:
    joint = np.asarray(joint, dtype=float)
    px, py = marginals(joint)
    if x_values is None:
        x_values = np.arange(joint.shape[1], dtype=float)
    if y_values is None:
        y_values = np.arange(joint.shape[0], dtype=float)
    x_values = np.asarray(x_values, dtype=float)
    y_values = np.asarray(y_values, dtype=float)
    ex = float(np.sum(x_values * px))
    ey = float(np.sum(y_values * py))
    ex2 = float(np.sum((x_values ** 2) * px))
    ey2 = float(np.sum((y_values ** 2) * py))
    exy = float(sum(x * y * joint[i, j] for i, y in enumerate(y_values) for j, x in enumerate(x_values)))
    var_x = ex2 - ex**2
    var_y = ey2 - ey**2
    cov = exy - ex * ey
    corr = cov / np.sqrt(var_x * var_y) if var_x > 0 and var_y > 0 else np.nan
    return {"E_X": ex, "E_Y": ey, "E_XY": exy, "Var_X": var_x, "Var_Y": var_y, "Cov": cov, "Corr": float(corr)}


def independent_joint(joint: np.ndarray, tol: float = 1e-10) -> bool:
    joint = np.asarray(joint, dtype=float)
    px, py = marginals(joint)
    expected = np.outer(py, px)
    return bool(np.allclose(joint, expected, atol=tol, rtol=0.0))


def profit_distribution(unit_contribution: float = 300.0, fixed_cost: float = 250.0):
    profits = unit_contribution * ADDON_VALUES - fixed_cost
    return profits, ADDON_PROBS.copy()
