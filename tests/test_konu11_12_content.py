"""Konu 11–12: notlarla uyum, tablo kuralı ve sezgi deneylerinin istatistiksel doğruluğu.

Deneylerin DGP'si bilindiği için sonuçlar bilinen gerçekle karşılaştırılabilir. Notlarda simülasyonla üretilmiş tek
şekil Şekil 12.13'tür: Konu 12 Deney 1'in varsayılan ayarları şekildeki yolu birebir verir.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats

from core.codegen.base import render_script
from core.labs.konu11 import KONU11_LAB
from core.labs.konu12 import KONU12_LAB
from core.labs.runner import LabState, execute, run_lab
from core.labs.sezgi_konu11 import BINOMIAL_NORMAL, EXPONENTIAL_WAIT, NORMAL_AREA, binomial_window, wait_axis
from core.labs.sezgi_konu12 import (
    CENTRAL_LIMIT,
    CONSISTENCY,
    SAMPLE_PROPORTION,
    gamma_tails,
    proportion_bins,
    two_se_probability,
)

TABLE_11_1 = {  # satır: sütun 0,00–0,05
    0.5: (0.6915, 0.6950, 0.6985, 0.7019, 0.7054, 0.7088),
    1.0: (0.8413, 0.8438, 0.8461, 0.8485, 0.8508, 0.8531),
    1.2: (0.8849, 0.8869, 0.8888, 0.8907, 0.8925, 0.8944),
    1.5: (0.9332, 0.9345, 0.9357, 0.9370, 0.9382, 0.9394),
}
FIGURE_11_7 = (0.000001, 0.000019, 0.000181, 0.001087, 0.004621, 0.014786, 0.036964, 0.073929, 0.120134, 0.160179,
               0.176197, 0.160179, 0.120134, 0.073929, 0.036964, 0.014786, 0.004621, 0.001087, 0.000181, 0.000019,
               0.000001)
FIGURE_12_13 = (  # n = 5, 6, …, 100: tohum 217 ile N(50, 20²) örnekleminin birikimli ortalaması
    44.34, 46.61, 46.04, 48.72, 48.32, 48.41, 47.03, 50.01, 47.74, 50.35, 49.93, 48.35,
    48.82, 48.25, 48.89, 48.94, 47.45, 46.93, 46.99, 48.14, 48.06, 47.15, 47.39, 47.69,
    47.80, 46.70, 47.19, 47.77, 46.70, 47.42, 46.45, 46.07, 46.42, 46.81, 46.93, 47.92,
    47.67, 48.55, 48.23, 47.83, 47.36, 46.97, 47.20, 47.58, 47.79, 47.51, 47.63, 47.54,
    47.54, 47.53, 46.84, 46.97, 46.81, 46.49, 46.53, 46.96, 46.91, 47.08, 46.95, 47.39,
    47.19, 46.98, 46.40, 46.67, 46.67, 46.73, 46.70, 46.55, 46.23, 46.59, 46.94, 46.87,
    46.81, 47.24, 47.30, 47.07, 46.89, 46.72, 46.73, 46.97, 46.99, 46.65, 46.75, 46.75,
    46.58, 47.02, 47.28, 47.47, 47.55, 47.33, 47.34, 47.56, 47.64, 47.52, 47.69, 47.78,
)


def _run(experiment, **overrides) -> LabState:
    parameters = experiment.defaults() | overrides
    state = LabState()
    for op in experiment.build(parameters):
        execute(op, state)
    return state


# --- Konu 11: notlarla uyum ----------------------------------------------------------------

def test_lab_rebuilds_every_cell_of_table_11_1_and_table_11_2() -> None:
    frames = run_lab(KONU11_LAB).state.frames
    table = frames["ztablo"].set_index("z_satir")
    for row, printed in TABLE_11_1.items():
        assert [table.loc[row, f"s0{column}"] for column in range(6)] == pytest.approx(printed, abs=1e-12), row
    z = list(frames["yuzdelik"]["z"])
    assert z == pytest.approx([-1.96, -1.645, -1.282, -0.674, 0.0, 0.674, 1.282, 1.645], abs=1e-12)


def test_table_rule_and_the_unrounded_value_are_both_shown() -> None:
    s = run_lab(KONU11_LAB).state.scalars
    assert (s["P_arasi"], s["P_arasi_yuvarlamasiz"]) == pytest.approx((0.5859, 0.585813), abs=1e-6)
    assert (s["P_12_yaklasik"], s["P_12_yuvarlamasiz"], s["P_12_binom"]) == pytest.approx(
        (0.1052, 0.106209, 0.098788), abs=1e-6)
    python, r = render_script(KONU11_LAB, "Python"), render_script(KONU11_LAB, "R")
    assert "np.round(stats.norm.cdf(" in python and "round(pnorm(" in r


def test_lab_reproduces_the_printed_coordinates_of_figure_11_7() -> None:
    frame = run_lab(KONU11_LAB).state.frames["bin20"]
    assert list(frame["f"].round(6)) == pytest.approx(FIGURE_11_7, abs=1e-12)
    assert frame["g"].max() == pytest.approx(0.17841, abs=5e-6)


# --- Konu 12: notlarla uyum ----------------------------------------------------------------

def test_lab_standard_errors_and_the_integrated_example() -> None:
    s = run_lab(KONU12_LAB).state.scalars
    assert (s["se_4"], s["se_25"], s["se_dolum"], s["se_harcama"]) == pytest.approx((7.5, 3, 10, 12))
    table = run_lab(KONU12_LAB).state.frames["se_tablo"]
    assert list(table["se"]) == pytest.approx([10, 4, 2, 1])


def test_consistency_experiment_defaults_reproduce_figure_12_13() -> None:
    path = _run(CONSISTENCY).frames["orneklem"].set_index("n")
    assert list(path.loc[5:100, "ortalama"].round(2)) == pytest.approx(FIGURE_12_13, abs=1e-12)
    inside = (path["ortalama"] - 50).abs() <= 2 * 20 / np.sqrt(path.index.to_numpy())
    assert inside.loc[5:100].all()  # notlar: n = 5–100 arasındaki bütün değerler bandın içindedir
    expected = np.cumsum(np.random.default_rng(217).normal(50, 20, 100)) / np.arange(1, 101)
    assert list(path["ortalama"]) == pytest.approx(list(expected), abs=1e-12)


def test_consistency_path_extends_and_scales_the_same_sample() -> None:
    base = _run(CONSISTENCY).frames["orneklem"]["ortalama"].to_numpy()
    longer = _run(CONSISTENCY, n=300).frames["orneklem"]["ortalama"].to_numpy()
    assert longer[:100] == pytest.approx(base, abs=1e-12)  # daha uzun yol aynı örneklemin devamıdır
    wider = _run(CONSISTENCY, sigma=40).frames["orneklem"]["ortalama"].to_numpy()
    assert wider - 50 == pytest.approx(2 * (base - 50), abs=1e-9)  # X = 50 + σZ: σ yalnız ölçeği değiştirir


@pytest.mark.parametrize(("sigma", "eps"), [(20, 5), (10, 1), (40, 7.5)])
def test_consistency_probabilities_are_exact_and_go_to_zero(sigma: int, eps: float) -> None:
    table = _run(CONSISTENCY, sigma=sigma, eps=eps).tables["tutarlilik"]
    for label, n in zip(table.index, (10, 25, 100, 400)):
        assert table.loc[label, "Standart hata σ/√n"] == pytest.approx(sigma / math.sqrt(n))
        z = eps * math.sqrt(n) / sigma
        assert table.loc[label, "P(|X̄ₙ − μ| > ε)"] == pytest.approx(2 * stats.norm.sf(z))
    assert list(table["P(|X̄ₙ − μ| > ε)"]) == sorted(table["P(|X̄ₙ − μ| > ε)"], reverse=True)


# --- Konu 11 deneyleri ------------------------------------------------------------------------

@pytest.mark.parametrize(("a", "b"), [(60, 80), (30, 85), (85, 110), (90, 40), (72, 72)])
def test_normal_area_experiment_matches_phi_and_the_simulated_share(a: int, b: int) -> None:
    state = _run(NORMAL_AREA, a=a, b=b, n=20000)
    s = state.scalars
    low, high = sorted((a, b))
    exact = stats.norm.cdf((high - 70) / 10) - stats.norm.cdf((low - 70) / 10)
    assert s["P_tam"] == pytest.approx(exact)
    assert s["P_tablo"] == pytest.approx(round(stats.norm.cdf(round((high - 70) / 10, 2)), 4)
                                         - round(stats.norm.cdf(round((low - 70) / 10, 2)), 4), abs=1e-12)
    assert s["pay"] == pytest.approx(exact, abs=4 * math.sqrt(0.25 / 20000))
    if (a, b) == (60, 80):
        assert s["P_tablo"] == pytest.approx(0.6826, abs=1e-12)
    if (a, b) == (30, 85):
        assert s["P_tablo"] == pytest.approx(0.9332, abs=1e-12)  # a = μ − 4σ: pratikte sol kuyruk


@pytest.mark.parametrize(("n", "p", "x"), [(100, 0.10, 12), (20, 0.5, 10), (10, 0.05, 3), (200, 0.95, 250)])
def test_binomial_normal_experiment_columns(n: int, p: float, x: int) -> None:
    state = _run(BINOMIAL_NORMAL, n=n, p=p, x=x)
    x = min(x, n)
    table = state.tables["karsilastirma"]
    single, cumulative = table[f"P(X = {x})"], table[f"P(X ≤ {x})"]
    mu, sigma = n * p, math.sqrt(n * p * (1 - p))
    assert single["Binom (tam)"] == pytest.approx(stats.binom.pmf(x, n, p))
    assert single["Normal, süreklilik düzeltmeli"] == pytest.approx(
        stats.norm.cdf((x + 0.5 - mu) / sigma) - stats.norm.cdf((x - 0.5 - mu) / sigma))
    assert single["Normal, düzeltmesiz"] == 0  # tek bir noktanın alanı
    assert cumulative["Binom (tam)"] == pytest.approx(stats.binom.cdf(x, n, p))
    assert cumulative["Normal, düzeltmesiz"] == pytest.approx(stats.norm.cdf((x - mu) / sigma))
    reps = 10000
    assert single["Simülasyon payı"] == pytest.approx(stats.binom.pmf(x, n, p), abs=4 * math.sqrt(0.25 / reps))
    low, high = binomial_window(n, p, x)
    assert low <= x <= high and stats.binom.pmf(np.arange(low, high + 1), n, p).sum() > 1 - 2e-7


def test_binomial_default_is_the_invoice_example_of_the_notes() -> None:
    table = _run(BINOMIAL_NORMAL).tables["karsilastirma"]["P(X = 12)"]
    assert (table["Binom (tam)"], table["Normal, süreklilik düzeltmeli"]) == pytest.approx((0.0988, 0.1062), abs=5e-5)


@pytest.mark.parametrize(("mu", "t"), [(5, 10), (7.5, 10), (15, 18), (1, 60), (30, 1)])
def test_exponential_wait_experiment(mu: float, t: int) -> None:
    s = _run(EXPONENTIAL_WAIT, mu=mu, t=t, n=20000).scalars
    assert s["P_uzun"] == pytest.approx(math.exp(-t / mu)) and s["lam"] == pytest.approx(60 / mu)
    assert s["pay"] == pytest.approx(math.exp(-t / mu), abs=4 * math.sqrt(0.25 / 20000))
    assert s["ortalama"] == pytest.approx(mu, rel=0.03) and s["s"] == pytest.approx(mu, rel=0.05)
    assert wait_axis(mu, t) >= max(6 * mu, t)
    if (mu, t) == (5, 10):
        assert s["P_uzun"] == pytest.approx(0.1353, abs=5e-5)


# --- Konu 12 deneyleri ------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 5, 30])
def test_central_limit_experiment_center_spread_and_exact_tails(n: int) -> None:
    table = _run(CENTRAL_LIMIT, n=n, tekrar=5000).tables["tekrarlar"]
    assert table["xbar"].mean() == pytest.approx(1, abs=4 / math.sqrt(n * 5000))
    # Gamma(n, n) basıklığı 3 + 6/n: örneklem standart sapmasının standart hatası ≈ σ_X̄ √((2 + 6/n)/(4 × tekrar))
    assert table["xbar"].std() == pytest.approx(1 / math.sqrt(n), abs=4 * math.sqrt((2 + 6 / n) / 20000) / math.sqrt(n))
    right, left = gamma_tails(n)
    exact_right = stats.gamma.sf(1 + 2 / math.sqrt(n), n, scale=1 / n)
    assert right == pytest.approx(exact_right)
    assert table["sag_kuyruk"].mean() == pytest.approx(right, abs=4 * math.sqrt(right / 5000) + 1e-3)
    assert table["sol_kuyruk"].mean() == pytest.approx(left, abs=4 * math.sqrt(max(left, 1e-4) / 5000) + 1e-3)
    if n <= 4:
        assert left == 0.0  # 1 − 2/√n ≤ 0: ortalama negatif olamaz


@pytest.mark.parametrize(("p", "n"), [(0.40, 100), (0.40, 25), (0.05, 10), (0.5, 400)])
def test_sample_proportion_experiment(p: float, n: int) -> None:
    state = _run(SAMPLE_PROPORTION, p=p, n=n)
    s = state.scalars
    se = math.sqrt(p * (1 - p) / n)
    assert s["se"] == pytest.approx(se)
    assert s["ortalama"] == pytest.approx(p, abs=4 * se / math.sqrt(5000))
    assert s["s"] == pytest.approx(se, rel=0.05)
    assert s["pay"] == pytest.approx(two_se_probability(n, p), abs=4 * math.sqrt(0.25 / 5000))
    bins, lower, upper = proportion_bins(n)
    counts, _ = np.histogram(state.frames["orneklemler"]["p_sapka"], bins=np.linspace(lower, upper, bins + 1))
    assert list(counts) == [int((state.frames["orneklemler"]["x"] == k).sum()) for k in range(n + 1)]


def test_sample_proportion_defaults_are_the_panels_of_figure_12_10() -> None:
    assert _run(SAMPLE_PROPORTION).scalars["se"] == pytest.approx(0.049, abs=5e-4)
    assert _run(SAMPLE_PROPORTION, n=25).scalars["se"] == pytest.approx(0.098, abs=5e-4)
