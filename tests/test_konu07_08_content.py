"""Konu 7–8: notlarla uyum, yeni grafik ve çekiliş işlemleri, sezgi deneylerinin istatistiksel doğruluğu.

Deneylerin DGP'si bilindiği için sonuçlar bilinen gerçekle karşılaştırılabilir. Konu 8 Deney 1'in varsayılan
ayarları notlardaki Şekil 8.8'in veri üretim sürecidir; şeklin basılı özellikleri burada denetlenir.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core.codegen.base import render_script, render_step
from core.labs import tables as T
from core.labs.konu07 import KONU07_LAB, ORDER_TREE, VISITS
from core.labs.konu08 import JOINT as JOINT_PMF
from core.labs.konu08 import KONU08_LAB
from core.labs.runner import LabState, execute, run_lab
from core.labs.sezgi_konu07 import BASE_RATE, DIRECTION, INDEPENDENCE, _posterior
from core.labs.sezgi_konu08 import JOINT, LONG_RUN, SPREAD, _joint_truth


def _run(experiment, **overrides) -> LabState:
    parameters = experiment.defaults() | overrides
    state = LabState()
    for op in experiment.build(parameters):
        execute(op, state)
    return state


# --- Konu 7: notlarla uyum ----------------------------------------------------------------

def test_store_counts_rebuild_tables_7_1_and_7_2() -> None:
    frame = T.from_counts(("cihaz", "satin"), VISITS)
    counts = T.crosstab(frame, "cihaz", "satin", ("Mobil", "Masaüstü"), ("Satın aldı", "Satın almadı"),
                        margins=True)
    assert counts.loc["Toplam", "Satın aldı"] == 260 and counts.loc["Mobil", "Toplam"] == 600
    frame["pay"] = 1 / len(frame)
    joint = T.crosstab(frame, "cihaz", "satin", ("Mobil", "Masaüstü"), ("Satın aldı", "Satın almadı"),
                       margins=True, weights="pay")
    assert joint.loc["Mobil", "Satın aldı"] == pytest.approx(0.18)
    assert joint.loc["Toplam", "Toplam"] == pytest.approx(1.0)


def test_mosaic_areas_are_the_joint_probabilities() -> None:
    """Sütun genişliği satırın marjinali, yükseklik satır içindeki pay: alan = ortak olasılık (Şekil 7.2)."""

    table = run_lab(KONU07_LAB).state.plots["MosaicChart:Ortak ve marjinal olasılıklar: mozaik"]
    widths = table.sum(axis=1) / table.to_numpy().sum()
    shares = table.div(table.sum(axis=1), axis=0)
    assert list(widths) == pytest.approx([0.60, 0.40])
    assert shares.loc["Mobil", "Satın aldı"] == pytest.approx(0.30)
    assert (shares.mul(widths, axis=0)).to_numpy() == pytest.approx(table.to_numpy())


def test_tree_layout_puts_the_first_path_on_top_and_rejects_inconsistent_branches() -> None:
    frame = pd.DataFrame(ORDER_TREE, columns=["sinif", "kargo", "p_sinif", "p_kargo"])
    paths = T.tree_layout(frame, "sinif", "kargo", "p_sinif", "p_kargo")
    assert list(paths["y_yol"]) == [3, 2, 1, 0]
    assert list(paths["y_ilk"]) == [2.5, 2.5, 0.5, 0.5]
    assert list(paths["ortak"]) == pytest.approx([0.56, 0.14, 0.285, 0.015])
    broken = frame.copy()
    broken.loc[1, "p_sinif"] = 0.6
    with pytest.raises(ValueError, match="dalının olasılığı"):
        T.tree_layout(broken, "sinif", "kargo", "p_sinif", "p_kargo")


def test_generated_code_draws_the_mosaic_and_the_tree_from_the_same_rules() -> None:
    python, r = render_step(KONU07_LAB, 2, "Python"), render_step(KONU07_LAB, 2, "R")
    assert "genislik = cizim.sum(axis=1) / cizim.to_numpy().sum()" in python
    assert "for (j in rev(seq_len(ncol(cizim))))" in r
    python_tree, r_tree = render_step(KONU07_LAB, 7, "Python"), render_step(KONU07_LAB, 7, "R")
    assert "y_yol = np.arange(len(yollar))[::-1]" in python_tree
    assert "kutu <- function" in r_tree


# --- Konu 8: notlarla uyum ve yeni işlemler -------------------------------------------------

def test_joint_table_marginals_and_moments_match_table_8_6() -> None:
    frame = pd.DataFrame(JOINT_PMF, columns=["x", "y", "f"])
    assert frame["f"].sum() == pytest.approx(1.0)
    assert (frame.loc[frame["y"] > frame["x"], "f"] == 0).all()  # satış talebi aşamaz
    ex, ey = (frame["x"] * frame["f"]).sum(), (frame["y"] * frame["f"]).sum()
    exy = (frame["x"] * frame["y"] * frame["f"]).sum()
    assert (ex, ey, exy) == pytest.approx((1.15, 0.85, 1.45))
    assert exy - ex * ey == pytest.approx(0.4725)


def test_discrete_draws_follow_the_inverse_distribution_function() -> None:
    values, probabilities = (0, 1, 2, 3, 4), (0.10, 0.30, 0.35, 0.20, 0.05)
    u = np.array([0.0, 0.0999, 0.10, 0.3999, 0.40, 0.7499, 0.75, 0.9499, 0.95, 0.99999])
    assert list(T.draw_discrete(u, values, probabilities)) == [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
    draws = T.draw_discrete(np.random.default_rng(1).random(200_000), values, probabilities)
    shares = np.bincount(draws.astype(int), minlength=5) / draws.size
    assert shares == pytest.approx(probabilities, abs=0.004)
    with pytest.raises(ValueError):
        T.draw_discrete(u, values, (0.5, 0.5, 0.1, -0.1, 0.0))


def test_numeric_categories_are_labels_in_bar_charts_and_negative_labels_go_below() -> None:
    python, r = render_step(KONU08_LAB, 2, "Python"), render_step(KONU08_LAB, 2, "R")
    assert 'index=gecersiz["x"].astype(str))' in python
    assert "ax.margins(y=0.1)" in python
    assert "pos = ifelse(cizim < 0, 1, 3)" in r and r.count("ifelse(cizim < 0") == 1  # yalnız geçersiz tablo
    labels = run_lab(KONU08_LAB).state.plots["BarChart:Ek ürün sayısının olasılık dağılımı"]["kategori"]
    assert list(labels) == ["0", "1", "2", "3", "4"]


def test_heat_map_shows_zero_cells_in_a_light_tint_in_both_languages() -> None:
    python, r = render_step(KONU08_LAB, 9, "Python"), render_step(KONU08_LAB, 9, "R")
    assert '"#E7F2F3"' in python and 'ax.grid(which="minor", color="white", linewidth=3)' in python
    assert '"#E7F2F3"' in r and 'col = "white", lwd = 3' in r and "par(eski_par)" in r


def test_line_chart_legends_in_r_sit_above_the_series() -> None:
    script = render_script(LONG_RUN.spec(LONG_RUN.defaults()), "R")
    assert "ylim = c(aralik[1], aralik[2] + 0.3 * diff(aralik))" in script
    assert 'legend("top",' in script and 'legend("topright",' not in script


# --- Konu 7 deneyleri ------------------------------------------------------------------------

def test_direction_experiment_separates_the_two_conditional_probabilities() -> None:
    s = _run(DIRECTION, n=20000).scalars
    assert s["oran_S_M"] == pytest.approx(0.30, abs=0.012)
    assert s["oran_M_S"] == pytest.approx(0.18 / 0.26, abs=0.02)
    assert s["oran_S"] == pytest.approx(0.26, abs=0.01)
    table = _run(DIRECTION).tables["yon"]["deger"]
    assert table["P(M | S) = P(M ∩ S)/P(S): DGP"] == pytest.approx(0.6923, abs=1e-4)


def test_independence_experiment_detects_equal_and_unequal_conditionals() -> None:
    same = _run(INDEPENDENCE, n=20000).scalars
    assert abs(same["oran_E_K"] - same["oran_E_D"]) < 0.02
    assert same["oran_EK"] == pytest.approx(same["carpim"], abs=0.01)
    different = _run(INDEPENDENCE, n=20000, pED=0.20).scalars
    assert different["oran_E_K"] - different["oran_E_D"] == pytest.approx(0.20, abs=0.03)


def test_base_rate_experiment_reproduces_bayes_and_the_curve_increases() -> None:
    assert _posterior(BASE_RATE.defaults()) == pytest.approx(0.018 / 0.067)
    state = _run(BASE_RATE, n=100000)
    assert state.scalars["oran_F_A"] == pytest.approx(0.2687, abs=0.02)
    counts = _run(BASE_RATE).tables["dogal"]
    assert counts.loc["Toplam", "Toplam"] == 10000
    assert counts.loc["Sahte", "Alarm"] == pytest.approx(180, abs=30)
    assert counts.loc["Sahte değil", "Alarm"] == pytest.approx(490, abs=60)
    curve = state.frames["egri"]["sonsal"].to_numpy()
    assert np.all(np.diff(curve) > 0)


# --- Konu 8 deneyleri ------------------------------------------------------------------------

def test_default_long_run_experiment_is_figure_8_8() -> None:
    """Şekil 8.8: ilk çekiliş 3; 5. ile 50. çekiliş arasında ortalama 1,8–2,3; toplam 177, son ortalama 1,77."""

    state = _run(LONG_RUN)
    means = state.frames["cekilis"]["ortalama"].to_numpy()
    assert state.frames["cekilis"]["x"].iloc[0] == 3 and means[1] == 2.5
    assert 1.8 <= means[4:50].min() and means[4:50].max() <= 2.3
    assert state.scalars["toplam"] == 177 and means[-1] == pytest.approx(1.77)
    assert [round(means[k - 1], 4) for k in (10, 25, 50, 75, 99)] == [2.0, 1.88, 2.08, 1.8667, 1.7879]


def test_long_run_mean_settles_near_the_expected_value() -> None:
    assert _run(LONG_RUN, n=5000).scalars["son_ortalama"] == pytest.approx(1.80, abs=0.04)


@pytest.mark.parametrize("d", [0.5, 1.0, 2.0, 3.0])
def test_spread_keeps_the_mean_and_scales_the_variance(d: float) -> None:
    s = _run(SPREAD, d=d, n=10000).scalars
    assert s["ortalama"] == pytest.approx(2.0, abs=0.03 * max(d, 1))
    assert s["s2"] == pytest.approx(d * d / 2, rel=0.05)
    assert s["Var_X"] == pytest.approx(d * d / 2)


def test_joint_experiment_covariance_follows_the_conversion_probability() -> None:
    assert _joint_truth(1.0)["rho"] == pytest.approx(1.0)
    assert _joint_truth(0.5)["Cov"] == pytest.approx(0.6275 * 0.5)
    for q in (0.2, 0.6, 1.0):
        state = _run(JOINT, q=q, n=20000)
        assert state.scalars["s_xy"] == pytest.approx(0.6275 * q, abs=0.02)
        frame = state.frames["gun"]
        assert (frame["y"] <= frame["x"]).all()
