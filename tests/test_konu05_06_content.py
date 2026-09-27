"""Konu 5–6: notlarla uyum, kutu grafiği ve sayma kuralları, sezgi deneylerinin istatistiksel doğruluğu.

Deneylerin DGP'si bilindiği için sonuçlar bilinen gerçekle karşılaştırılabilir. Konu 6 Deney 1'in varsayılan
ayarları notlardaki Şekil 6.6'nın veri üretim sürecidir; şeklin basılı özellikleri burada denetlenir.
"""

from __future__ import annotations

import math
from itertools import combinations, permutations, product

import numpy as np
import pandas as pd
import pytest

from core.codegen.base import render_step
from core.labs import tables as T
from core.labs.konu05 import ADVERTISING, INCOME, KONU05_LAB, SUPPLIER_A, SUPPLIER_B
from core.labs.konu06 import KONU06_LAB, SHIPMENTS
from core.labs.runner import LabState, execute, run_operations
from core.labs.sezgi_konu05 import CURVATURE, EMPIRICAL_RULE, OUTLIER_SPREAD, _true_correlation
from core.labs.sezgi_konu06 import ADDITION_RULE, RELATIVE_FREQUENCY, TWO_DICE, _feasible
from core.labs.spec import CrossTab, Event, InlineData


def _run(experiment, **overrides) -> LabState:
    parameters = experiment.defaults() | overrides
    state = LabState()
    for op in experiment.build(parameters):
        execute(op, state)
    return state


# --- Konu 5: notlarla uyum -------------------------------------------------------------

def test_suppliers_share_the_centre_but_not_the_spread() -> None:
    a, b = np.asarray(SUPPLIER_A, dtype=float), np.asarray(SUPPLIER_B, dtype=float)
    assert a.mean() == b.mean() == 10
    assert (np.ptp(a), np.ptp(b)) == (2, 6)
    assert round(a.std(ddof=1), 2) == 0.71 and round(b.std(ddof=1), 2) == 2.55


def test_income_box_summary_matches_the_notes() -> None:
    """§5.9–5.10: beş sayı özeti 20, 23, 26, 29, 65; sınırlar 14 ve 38; üst bıyık 30; tek aykırı değer 65."""

    summary = T.box_summary(INCOME)
    assert tuple(summary[["en_kucuk", "q1", "medyan", "q3", "en_buyuk"]]) == (20, 23, 26, 29, 65)
    assert (summary["iqr"], summary["alt_sinir"], summary["ust_sinir"]) == (6, 14, 38)
    assert (summary["alt_biyik"], summary["ust_biyik"], summary["aykiri_sayisi"]) == (20, 30, 1)
    assert list(T.outliers(INCOME, summary)) == [65]


def test_box_summary_uses_the_course_quartiles_and_fences() -> None:
    rng = np.random.default_rng(5)
    for n in (7, 12, 31, 200):
        x = rng.gamma(1.5, 2.0, size=n)
        summary = T.box_summary(x)
        q1, q3 = np.percentile(x, (25, 75), method="weibull")
        assert summary["q1"] == pytest.approx(q1) and summary["q3"] == pytest.approx(q3)
        low, high = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
        inside = x[(x >= low) & (x <= high)]
        assert summary["alt_biyik"] == inside.min() and summary["ust_biyik"] == inside.max()
        assert summary["aykiri_sayisi"] == ((x < low) | (x > high)).sum()


def test_covariance_and_correlation_of_the_advertising_table() -> None:
    frame = pd.DataFrame(ADVERTISING, columns=["hafta", "reklam", "satis"])
    assert frame["reklam"].cov(frame["satis"]) == pytest.approx(6.75)
    assert frame["reklam"].corr(frame["satis"]) == pytest.approx(np.corrcoef(frame["reklam"], frame["satis"])[0, 1])
    assert round(frame["reklam"].corr(frame["satis"]), 2) == 0.99


def test_box_plots_are_drawn_from_the_course_summary_in_both_languages() -> None:
    """matplotlib ve R'nin boxplot fonksiyonları çeyrekleri kendi kurallarıyla bulur; kod kullanmaz."""

    python, r = render_step(KONU05_LAB, 9, "Python"), render_step(KONU05_LAB, 9, "R")
    assert "kutu_ozeti" in python and ".boxplot(" not in python
    code = [line for line in r.splitlines() if not line.lstrip().startswith("#")]
    assert any("bxp(" in line for line in code) and not any("boxplot(" in line for line in code)


# --- Konu 5 deneyleri --------------------------------------------------------------

def test_one_outlier_inflates_range_and_sd_but_not_the_iqr() -> None:
    state = _run(OUTLIER_SPREAD, n=50, delta=60)
    s = state.scalars
    assert s["aralik_uc"] - s["aralik_ozgun"] > 40
    assert s["s_uc"] > 1.5 * s["s_ozgun"]
    assert abs(s["iqr_uc"] - s["iqr_ozgun"]) < 0.25 * s["iqr_ozgun"]
    unchanged = _run(OUTLIER_SPREAD, n=50, delta=0).tables["olculer"]
    assert np.allclose(unchanged["Değişim"], 0.0)


@pytest.mark.parametrize("alpha", [0.5, 1.0, 4.0, 30.0])
def test_chebyshev_bounds_hold_in_every_sample(alpha: float) -> None:
    table = _run(EMPIRICAL_RULE, alpha=alpha, n=2000).tables["kurallar"]
    observed, bound = table["Gözlenen oran"].to_numpy(), table["Chebyshev (en az)"].to_numpy()
    assert np.all(observed >= bound - 1e-12)
    assert bound == pytest.approx((0.0, 0.75, 8 / 9))


def test_empirical_rule_fits_only_near_bell_shape() -> None:
    near_bell = _run(EMPIRICAL_RULE, alpha=30.0, n=5000).tables["kurallar"]
    assert np.allclose(near_bell["Gözlenen oran"], near_bell["Ampirik kural (yaklaşık)"], atol=0.02)
    skewed = _run(EMPIRICAL_RULE, alpha=0.5, n=5000).tables["kurallar"]
    assert skewed.loc["k = 1", "Gözlenen oran"] > 0.80  # χ²₁ ölçeğinde P(|X − μ| ≤ σ) ≈ 0,88


def test_true_correlation_formula_matches_a_large_sample() -> None:
    rng = np.random.default_rng(3)
    x = rng.uniform(-3, 3, 400_000)
    e = rng.normal(0, 1, x.size)
    for c in (0.0, 0.3, 0.7, 1.0):
        y = 2 * (1 - c) * x + c * x**2 + e
        assert np.corrcoef(x, y)[0, 1] == pytest.approx(_true_correlation(c), abs=0.005)


def test_curvature_hides_a_strong_relation_from_the_correlation() -> None:
    linear = _run(CURVATURE, c=0.0, n=500).scalars
    curved = _run(CURVATURE, c=1.0, n=500).scalars
    assert linear["r"] == pytest.approx(linear["rho"], abs=0.03) and linear["r"] > 0.9
    assert curved["rho"] == 0.0 and abs(curved["r"]) < 0.15


# --- Konu 6: sayma kuralları ve olaylar -------------------------------------------------

def test_outcomes_follow_the_tree_order_and_the_product_rule() -> None:
    orders = T.outcomes((("teslimat", ("Standart", "Hızlı")), ("odeme", ("Kart", "Havale", "Kapıda"))))
    assert list(orders.itertuples(index=False, name=None)) == list(product(("Standart", "Hızlı"),
                                                                            ("Kart", "Havale", "Kapıda")))
    dice = T.outcomes((("birinci", range(1, 7)), ("ikinci", range(1, 7))))
    counts = (dice["birinci"] + dice["ikinci"]).value_counts().sort_index()
    assert len(dice) == 36 and list(counts) == [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]


def test_selections_list_combinations_and_permutations_in_order() -> None:
    items = ("A", "B", "C", "D", "E")
    chosen = T.selections(items, 2, False, ("birinci", "ikinci"))
    ordered = T.selections(items, 2, True, ("baskan", "raportor"))
    assert list(chosen.itertuples(index=False, name=None)) == list(combinations(items, 2))
    assert list(ordered.itertuples(index=False, name=None)) == list(permutations(items, 2))
    assert (len(chosen), len(ordered)) == (math.comb(5, 2), math.perm(5, 2))


def test_event_indicator_and_weighted_joint_table() -> None:
    state = run_operations((
        InlineData("sevkiyat", ("nokta", "zaman", "kalite", "olasilik"), SHIPMENTS, "Tablo 6.2"),
        Event("sevkiyat", "Z", "zaman", ("Zamanında",), "Z"),
        CrossTab("sevkiyat", "zaman", "kalite", "ortak", ("Zamanında", "Geç"), ("Hatasız", "Hatalı"),
                 margins=True, weights="olasilik", decimals=2),
    ))
    assert list(state.frames["sevkiyat"]["Z"]) == [1, 1, 0, 0]
    table = state.tables["ortak"]
    assert table.loc["Zamanında", "Toplam"] == pytest.approx(0.78)
    assert table.loc["Toplam", "Hatalı"] == pytest.approx(0.13)
    assert table.loc["Toplam", "Toplam"] == pytest.approx(1.0)


def test_generated_code_writes_events_as_sets_and_weighted_tables_as_sums() -> None:
    python, r = render_step(KONU06_LAB, 9, "Python"), render_step(KONU06_LAB, 9, "R")
    assert '.isin(["Zamanında"]).astype(int)' in python and 'aggfunc="sum"' in python
    assert '%in% c("Zamanında")' in r and "xtabs(sevkiyat$olasilik ~" in r
    assert "levels = c(\"Zamanında\", \"Geç\")) +" in r  # formülde terimler + ile birleşir


# --- Konu 6 deneyleri --------------------------------------------------------------

def test_default_relative_frequency_experiment_is_figure_6_6() -> None:
    """Şekil 6.6: ilk dokuz işlemde gecikme yok; 20–30 arasında 0,20 civarı; 100 işlemin 16'sı gecikmiş."""

    frame = _run(RELATIVE_FREQUENCY).frames["islem"]
    delays = list(frame.loc[frame["gecikme"] == 1, "k"].astype(int))
    assert delays == [10, 15, 19, 20, 25, 29, 54, 58, 59, 68, 77, 83, 87, 89, 95, 100]
    ratios = frame["oran"].to_numpy()
    assert np.all(ratios[:9] == 0) and ratios[-1] == pytest.approx(0.16)
    assert ratios.max() == pytest.approx(6 / 29) and int(np.argmax(ratios)) + 1 == 29
    assert round(ratios[19], 4) == 0.2 and round(ratios[29], 4) == 0.2


def test_relative_frequency_settles_near_p() -> None:
    frame = _run(RELATIVE_FREQUENCY, p=0.4, n=2000).frames["islem"]
    assert frame["oran"].iloc[-1] == pytest.approx(0.4, abs=0.035)


def test_simulated_dice_sums_approach_the_classical_probabilities() -> None:
    table = _run(TWO_DICE, n=7200).tables["karsilastirma"]
    assert table["Klasik olasılık"].to_numpy() == pytest.approx(np.array([1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]) / 36)
    assert np.allclose(table["Simülasyon oranı"], table["Klasik olasılık"], atol=0.015)
    assert table["Simülasyon oranı"].sum() == pytest.approx(1.0)


def test_addition_rule_is_an_identity_of_counts_and_infeasible_overlaps_are_clamped() -> None:
    for overlap in (0.0, 0.15, 0.35):
        s = _run(ADDITION_RULE, pAB=overlap).scalars
        assert s["kural"] == pytest.approx(s["oran_birlesim"], abs=1e-12)
        assert s["cift_sayim"] >= s["oran_birlesim"]
    assert _feasible({"pA": 0.4, "pB": 0.35, "pAB": 0.6})[2] == pytest.approx(0.35)
    assert _feasible({"pA": 0.7, "pB": 0.6, "pAB": 0.0})[2] == pytest.approx(0.3)
    s = _run(ADDITION_RULE, n=10000).scalars
    assert s["oran_birlesim"] == pytest.approx(0.60, abs=0.02)
