"""Konu 9–10: notlarla uyum, yeni işlemler ve sezgi deneylerinin istatistiksel doğruluğu.

Deneylerin DGP'si bilindiği için sonuçlar bilinen gerçekle karşılaştırılabilir. Notlarda simülasyonla üretilmiş
bir şekil yoktur; varsayılan ayarların olasılık sütunları notlardaki şekillerin basılı değerleridir.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats

from core.codegen.base import render_script, render_step
from core.labs.konu09 import KONU09_LAB
from core.labs.konu10 import KONU10_LAB
from core.labs.runner import LabState, execute, run_lab
from core.labs.sezgi_konu09 import BINOMIAL_SHAPE, POISSON_INTERVAL, WITHOUT_REPLACEMENT, poisson_upper
from core.labs.sezgi_konu10 import NORMAL_SHAPE, STANDARDIZATION, UNIFORM_INTERVAL, Y_MAX

FIGURE_9_6 = {  # p = 0,20 paneli; p = 0,80 bunun aynadaki görüntüsüdür
    "f_020": (0.1074, 0.2684, 0.3020, 0.2013, 0.0881, 0.0264, 0.0055, 0.0008, 0.0001, 0.0, 0.0),
    "f_050": (0.0010, 0.0098, 0.0439, 0.1172, 0.2051, 0.2461, 0.2051, 0.1172, 0.0439, 0.0098, 0.0010),
}
FIGURE_9_8 = {
    "f_1": (0.3679, 0.3679, 0.1839, 0.0613, 0.0153, 0.0031, 0.0005, 0.0001, 0.0, 0.0, 0.0, 0.0, 0.0),
    "f_3": (0.0498, 0.1494, 0.2240, 0.2240, 0.1680, 0.1008, 0.0504, 0.0216, 0.0081, 0.0027, 0.0008, 0.0002, 0.0001),
    "f_6": (0.0025, 0.0149, 0.0446, 0.0892, 0.1339, 0.1606, 0.1606, 0.1377, 0.1033, 0.0688, 0.0413, 0.0225, 0.0113),
}


def _run(experiment, **overrides) -> LabState:
    parameters = experiment.defaults() | overrides
    state = LabState()
    for op in experiment.build(parameters):
        execute(op, state)
    return state


# --- Konu 9: notlarla uyum ----------------------------------------------------------------

def test_lab_reproduces_the_printed_coordinates_of_figures_9_6_and_9_8() -> None:
    frames = run_lab(KONU09_LAB).state.frames
    for column, printed in FIGURE_9_6.items():
        assert list(frames["bin10"][column].round(4)) == pytest.approx(printed, abs=1e-12), column
    assert list(frames["bin10"]["f_080"]) == pytest.approx(list(frames["bin10"]["f_020"])[::-1])
    for column, printed in FIGURE_9_8.items():
        assert list(frames["pois12"][column].round(4)) == pytest.approx(printed, abs=1e-12), column


def test_bernoulli_sequences_add_up_to_the_binomial_distribution() -> None:
    state = run_lab(KONU09_LAB).state
    sequences = state.frames["diziler"]
    assert len(sequences) == 2 ** 8 and sequences["olasilik"].sum() == pytest.approx(1.0)
    table = state.tables["binom_dizi"]
    assert list(table["dizi_sayisi"]) == [math.comb(8, x) for x in range(9)]
    assert list(table["olasilik"]) == pytest.approx(stats.binom.pmf(range(9), 8, 0.25))


def test_hypergeometric_argument_order_in_both_languages() -> None:
    python, r = render_step(KONU09_LAB, 7, "Python"), render_step(KONU09_LAB, 7, "R")
    assert "stats.hypergeom.pmf(1, 20, 5, 4)" in python  # (x, N, r, n)
    assert "dhyper(1, 5, 20 - 5, 4)" in r  # (x, r, N − r, n)
    assert run_lab(KONU09_LAB).state.scalars["P1_hiper"] == pytest.approx(
        math.comb(5, 1) * math.comb(15, 3) / math.comb(20, 4))


def test_numeric_groups_are_selected_by_name_in_r() -> None:
    assert 'tapply(diziler$olasilik, diziler$x, sum)[c("0", "1", "2", "3", "4", "5", "6", "7", "8")]' in (
        render_step(KONU09_LAB, 1, "R"))


# --- Konu 10: notlarla uyum ----------------------------------------------------------------

def test_rectangle_sums_match_the_empirical_rule_without_a_normal_table() -> None:
    s = run_lab(KONU10_LAB).state.scalars
    for name, k in (("alan_bir", 1), ("alan_iki", 2), ("alan_uc", 3)):
        assert s[name] == pytest.approx(stats.norm.cdf(k) - stats.norm.cdf(-k), abs=1e-6), name
    assert s["alan_toplam"] == pytest.approx(1.0, abs=1e-6) and s["alan_sol"] == pytest.approx(0.5, abs=1e-6)
    assert s["alan_z"] == pytest.approx(s["alan_bir"], abs=1e-6)
    assert s["alan_dolum"] == pytest.approx(s["alan_iki"], abs=1e-6)


def test_uniform_and_z_numbers_of_the_notes() -> None:
    s = run_lab(KONU10_LAB).state.scalars
    assert (s["f_ucus"], s["P_ucus"], s["mu_ucus"]) == pytest.approx((0.05, 0.40, 130))
    assert s["var_ucus"] == pytest.approx(400 / 12) and s["sd_ucus"] == pytest.approx(5.7735, abs=1e-4)
    assert (s["z_85"], s["z_55"], s["x_eksi_2"], s["z_510"], s["z_480"]) == pytest.approx((1.5, -1.5, 50, 1, -2))
    exams = run_lab(KONU10_LAB).state.frames["sinavlar"]
    assert list(exams["z"]) == pytest.approx([2.0, 1.0])


def test_unary_minus_and_fixed_density_axis_in_generated_code() -> None:
    python, r = render_script(KONU10_LAB, "Python"), render_script(KONU10_LAB, "R")
    assert "x_eksi_2 = 70 + (-2) * 10" in python and "x_eksi_2 <- 70 + (-2) * 10" in r
    spec = NORMAL_SHAPE.spec(NORMAL_SHAPE.defaults())
    assert "ax.set_ylim(0, 0.1)" in render_script(spec, "Python")
    assert "ylim = c(0, 0.1)," in render_script(spec, "R")


# --- Konu 9 deneyleri ------------------------------------------------------------------------

def test_binomial_experiment_defaults_are_the_first_panel_of_figure_9_6() -> None:
    table = _run(BINOMIAL_SHAPE).tables["karsilastirma"]
    assert list(table["Binom olasılığı"].round(4)) == pytest.approx(FIGURE_9_6["f_020"], abs=1e-12)
    assert table["Simülasyon oranı"].sum() == pytest.approx(1.0)


@pytest.mark.parametrize(("n", "p"), [(10, 0.2), (10, 0.5), (30, 0.9), (5, 0.35)])
def test_binomial_draws_have_mean_np_and_variance_npq(n: int, p: float) -> None:
    s = _run(BINOMIAL_SHAPE, n=n, p=p, tekrar=10000).scalars
    assert s["E_X"] == pytest.approx(n * p) and s["Var_X"] == pytest.approx(n * p * (1 - p))
    assert s["ortalama"] == pytest.approx(n * p, abs=4 * math.sqrt(n * p * (1 - p) / 10000))
    assert s["varyans"] == pytest.approx(n * p * (1 - p), rel=0.06)


def test_poisson_support_leaves_a_negligible_tail_for_every_slider_value() -> None:
    assert poisson_upper(1.0) == 12  # Şekil 9.8'in ekseni
    for minutes in range(5, 65, 5):
        lam = 12 * minutes / 60
        assert stats.poisson.sf(poisson_upper(lam), lam) < 1e-10, minutes
        draws = _run(POISSON_INTERVAL, t=minutes, tekrar=10000).frames["aralik"]["x"]
        assert draws.max() <= poisson_upper(lam)


def test_poisson_experiment_defaults_and_equal_mean_and_variance() -> None:
    state = _run(POISSON_INTERVAL)
    assert state.scalars["lam"] == 3
    assert list(state.tables["karsilastirma"]["Poisson olasılığı"].round(4))[:13] == pytest.approx(
        FIGURE_9_8["f_3"], abs=1e-12)
    for minutes in (5, 30, 60):
        s = _run(POISSON_INTERVAL, t=minutes, tekrar=10000).scalars
        assert s["ortalama"] == pytest.approx(s["lam"], rel=0.03)
        assert s["varyans"] == pytest.approx(s["lam"], rel=0.06)
        assert s["oran_sifir"] == pytest.approx(math.exp(-s["lam"]), abs=0.012)


def test_without_replacement_experiment_matches_table_9_1_and_the_correction() -> None:
    state = _run(WITHOUT_REPLACEMENT)
    s = state.scalars
    assert (s["E_X"], s["Var_binom"]) == pytest.approx((0.8, 0.72))
    assert s["duzeltme"] == pytest.approx(32 / 39) and s["Var_hiper"] == pytest.approx(0.72 * 32 / 39)
    table = state.tables["karsilastirma"]
    assert list(table["Hipergeometrik olasılık"]) == pytest.approx(stats.hypergeom.pmf(range(9), 40, 4, 8))
    small = _run(WITHOUT_REPLACEMENT, N=10, tekrar=10000)
    assert set(small.frames["secim"]["x"].unique()) <= {0.0, 1.0}  # r = 1: en fazla bir kusurlu
    assert small.scalars["varyans"] == pytest.approx(0.72 * 2 / 9, rel=0.1)
    gaps = [(_run(WITHOUT_REPLACEMENT, N=N).tables["karsilastirma"]["Hipergeometrik olasılık"]
             - _run(WITHOUT_REPLACEMENT, N=N).tables["karsilastirma"]["Binom olasılığı"]).abs().max()
            for N in (20, 40, 100, 400)]
    assert gaps == sorted(gaps, reverse=True) and gaps[-1] < 0.01


# --- Konu 10 deneyleri -----------------------------------------------------------------------

def test_normal_experiment_keeps_the_rule_shares_and_its_fixed_axes_fit() -> None:
    assert 1 / (4 * math.sqrt(2 * math.pi)) < Y_MAX  # σ = 4'te tepe yüksekliği ekseni aşmaz
    for mu, sigma in ((50, 4), (70, 10), (90, 15)):
        s = _run(NORMAL_SHAPE, mu=mu, sigma=sigma, n=10000).scalars
        assert s["pay_1"] == pytest.approx(0.683, abs=0.015) and s["pay_2"] == pytest.approx(0.954, abs=0.008)
        assert 0 <= mu - 3 * sigma and mu + 3 * sigma <= 140


@pytest.mark.parametrize(("c", "h"), [(132, 4.0), (125, 5.0), (135, 2.5), (130, 0.0)])
def test_uniform_share_is_proportional_to_the_interval_length(c: int, h: float) -> None:
    s = _run(UNIFORM_INTERVAL, c=c, h=h, n=10000).scalars
    assert 120 <= c - h and c + h <= 140
    assert s["P_aralik"] == pytest.approx(2 * h / 20)
    assert s["pay"] == pytest.approx(2 * h / 20, abs=0.015)
    assert s["tam_c_sayisi"] == 0


@pytest.mark.parametrize(("mu", "sigma"), [(70, 10), (40, 2), (100, 20)])
def test_standardization_keeps_every_share_and_gives_mean_zero_sd_one(mu: int, sigma: int) -> None:
    state = _run(STANDARDIZATION, mu=mu, sigma=sigma, n=10000)
    table = state.tables["paylar"]
    assert list(table["Özgün ölçek: μ ± kσ"]) == list(table["Standart ölçek: |z| ≤ k"])
    assert list(table["Özgün ölçek: μ ± kσ"]) == pytest.approx([0.683, 0.954, 0.997], abs=0.015)
    assert state.scalars["z_ortalama"] == pytest.approx(0, abs=0.03)
    assert state.scalars["z_s"] == pytest.approx(1, abs=0.02)
    z = state.frames["puan"]["z"].to_numpy()
    assert np.abs(z).max() < 5  # standart ölçeğin histogram aralığı [−5, 5]
