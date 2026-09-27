"""Konu 3–4: notlarla uyum, yüzdelik kuralı ve sezgi deneylerinin istatistiksel doğruluğu.

Deneylerin DGP'si bilindiği için sonuçlar bilinen gerçekle karşılaştırılabilir.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from core.labs import tables as T
from core.labs.konu03 import FREQUENCIES, STEM_LEAVES, TRAVEL_TIMES
from core.labs.konu04 import ORDERED
from core.labs.runner import LabState, execute
from core.labs.sezgi_konu03 import CLASS_WIDTH, CUMULATIVE_SHARE, DISTRIBUTION_SHAPE, _peak_count, _tails
from core.labs.sezgi_konu04 import COMPOUND_GROWTH, OUTLIER, PERCENTILE_RULE, _equal_years_growth


def _run(experiment, **overrides) -> LabState:
    parameters = experiment.defaults() | overrides
    state = LabState()
    for op in experiment.build(parameters):
        execute(op, state)
    return state


# --- Notlarla uyum ------------------------------------------------------------------

def test_raw_travel_times_give_the_printed_frequency_table_and_stem_leaf() -> None:
    """Tablo 3.1'in 40 değeri Tablo 3.2'nin frekanslarını ve §3.11'deki yaprakları verir."""

    values = pd.Series(TRAVEL_TIMES, dtype=float)
    assert len(values) == 40 and values.is_monotonic_increasing
    table = T.class_table(values, T.class_edges(values, 10, 10, 7), ("frekans",))
    assert tuple(table["frekans"]) == FREQUENCIES
    stems = T.stem_leaf(values)
    assert tuple(zip(stems.index, stems["yapraklar"])) == STEM_LEAVES
    assert tuple(stems["yaprak_sayisi"]) == FREQUENCIES


def test_course_rule_is_hyndman_fan_type_6_and_differs_from_the_default() -> None:
    """L_p = (p/100)(n + 1) numpy'de method="weibull", R'de type = 6'dır; varsayılan (tip 7) farklıdır."""

    rng = np.random.default_rng(1)
    for n in (5, 9, 12, 40):
        sample = rng.normal(size=n)
        for p in (5, 10, 25, 50, 60, 75, 90, 95):
            assert T.percentile(sample, p) == pytest.approx(np.percentile(sample, p, method="weibull"), abs=1e-12)
            assert T.percentile(sample, p, "yazilim") == pytest.approx(np.percentile(sample, p), abs=1e-12)
    assert T.percentile(ORDERED, 25) == pytest.approx(45.5)
    assert T.percentile(ORDERED, 25, "yazilim") == pytest.approx(46.5)


def test_course_rule_uses_the_extremes_outside_the_data_range() -> None:
    assert T.percentile_location(4, 10) == pytest.approx(0.5)
    assert T.percentile((3, 1, 2, 4), 10) == 1.0
    assert T.percentile((3, 1, 2, 4), 95) == 4.0


# --- Konu 3 deneyleri ---------------------------------------------------------------

def test_narrow_and_wide_classes_hide_the_true_two_peaks() -> None:
    assert _peak_count(_run(CLASS_WIDTH, n=2000, h=10).tables["siniflar"]["frekans"]) == 2
    assert _peak_count(_run(CLASS_WIDTH, n=2000, h=20).tables["siniflar"]["frekans"]) == 1
    assert _peak_count(_run(CLASS_WIDTH, n=100, h=2).tables["siniflar"]["frekans"]) > 2


def test_peak_count_treats_plateaus_as_one_peak() -> None:
    assert _peak_count((1, 3, 3, 1, 4, 2)) == 2
    assert _peak_count((5,)) == 1
    assert _peak_count((1, 2, 3)) == 1


def test_class_edges_cover_every_draw() -> None:
    state = _run(CLASS_WIDTH, n=2000, h=7)
    table = state.tables["siniflar"]
    assert table["frekans"].sum() == 2000
    assert table["alt"].iloc[0] <= state.frames["ogrenci"]["sure"].min()
    assert table["ust"].iloc[-1] > state.frames["ogrenci"]["sure"].max()


@pytest.mark.parametrize("shift, longer", [(-1.0, "sag"), (1.0, "sol")])
def test_tail_direction_follows_the_beta_parameters(shift: float, longer: str) -> None:
    _, left, right = _tails(_run(DISTRIBUTION_SHAPE, n=5000, s=shift))
    assert (right > left) if longer == "sag" else (left > right)


def test_symmetric_scores_have_similar_class_shares_on_both_sides() -> None:
    table = _run(DISTRIBUTION_SHAPE, n=5000, s=0.0).tables["siniflar"].drop(index="Toplam", errors="ignore")
    shares = table["yuzde"].to_numpy()
    assert shares[:5].sum() == pytest.approx(50.0, abs=2.5)


def test_sample_cumulative_share_approaches_the_dgp_probability() -> None:
    for threshold in (20, 40, 60):
        state = _run(CUMULATIVE_SHARE, n=2000, t=threshold)
        expected = 100 * stats.norm.cdf((threshold - 35) / 12)
        assert state.scalars["dgp_yuzde"] == pytest.approx(expected)
        assert state.scalars["orneklem_yuzde"] == pytest.approx(expected, abs=2.5)


def test_cumulative_percent_never_decreases_and_ends_at_100() -> None:
    cumulative = _run(CUMULATIVE_SHARE, n=200).tables["kumulatif"]["kumulatif_yuzde"].to_numpy()
    assert np.all(np.diff(cumulative) >= 0) and cumulative[-1] == pytest.approx(100.0)


# --- Konu 4 deneyleri ---------------------------------------------------------------

def test_outliers_move_the_mean_by_about_k_delta_over_n_but_not_the_median() -> None:
    base = _run(OUTLIER, n=200, k=0, delta=0)
    shifted = _run(OUTLIER, n=200, k=10, delta=100)
    assert shifted.scalars["ortalama"] - base.scalars["ortalama"] == pytest.approx(10 * 100 / 200, abs=0.5)
    assert abs(shifted.scalars["medyan"] - base.scalars["medyan"]) <= 1.0


def test_median_follows_the_outliers_once_they_are_half_of_the_days() -> None:
    state = _run(OUTLIER, n=20, k=10, delta=100)
    assert state.scalars["medyan"] > 30


def test_both_percentile_rules_agree_at_the_median_and_converge() -> None:
    at_median = _run(PERCENTILE_RULE, p=50, n=13)
    assert at_median.scalars["P_ders"] == pytest.approx(at_median.scalars["P_yazilim"])
    small = np.mean([abs(_run(PERCENTILE_RULE, p=p, n=10).scalars["fark"]) for p in (10, 20, 80, 90)])
    large = np.mean([abs(_run(PERCENTILE_RULE, p=p, n=60).scalars["fark"]) for p in (10, 20, 80, 90)])
    assert large < small


def test_location_gap_between_the_rules_is_2p_over_100_minus_1() -> None:
    for p, n in ((10, 9), (60, 12), (90, 40)):
        state = _run(PERCENTILE_RULE, p=p, n=n)
        assert state.scalars["L_ders"] - state.scalars["L_yazilim"] == pytest.approx(2 * p / 100 - 1)


def test_equal_ups_and_downs_lose_money_like_the_notes_example() -> None:
    assert _equal_years_growth(10) == pytest.approx(100 * (0.99 ** 0.5 - 1))
    table = _run(COMPOUND_GROWTH, x=10, T=20).tables["yatirimcilar"]
    assert table["aritmetik"].mean() == pytest.approx(0.0, abs=0.3)
    assert table["geometrik"].mean() == pytest.approx(_equal_years_growth(10), abs=0.2)
    assert np.all(table["geometrik"] <= table["aritmetik"] + 1e-9)
    # Son değer 100'ün altında ⇔ 20 yılda en çok 10 artış: P(Bin(20; 0,5) ≤ 10) ≈ 0,588
    assert table["kayip"].mean() == pytest.approx(stats.binom.cdf(10, 20, 0.5), abs=0.06)


def test_without_change_both_means_are_zero() -> None:
    table = _run(COMPOUND_GROWTH, x=0, T=10).tables["yatirimcilar"]
    assert np.allclose(table[["aritmetik", "geometrik"]], 0.0)
    assert not table["kayip"].any()
