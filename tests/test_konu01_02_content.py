"""Konu 1–2: notlarla uyum ve sezgi deneylerinin istatistiksel doğruluğu.

Deneylerin DGP'si bilindiği için sonuçlar bilinen gerçekle karşılaştırılabilir.
"""

from __future__ import annotations

from collections import Counter

import pytest

from core.labs.konu02 import AD_COUNTS, MATERIAL_COUNTS, RAW_TRANSPORT, SOURCE_COUNTS
from core.labs.runner import LabState, execute
from core.labs.sezgi_konu01 import CROSSING, DESIGN, ORDINAL_CODES, POPULATION_MEAN, REPRESENTATION
from core.labs.sezgi_konu02 import FREQUENCY_OR_PERCENT, ROW_OR_COLUMN, SIMPSON


def _run(experiment, **overrides) -> LabState:
    parameters = experiment.defaults() | overrides
    state = LabState()
    for op in experiment.build(parameters):
        execute(op, state)
    return state


# --- Notlarla uyum ------------------------------------------------------------------

def test_raw_transport_table_matches_the_frequency_table() -> None:
    """Tablo 2.1'in 40 kaydı Tablo 2.2'deki frekansları verir (son hücre Raylı sistem)."""

    assert Counter(RAW_TRANSPORT) == {"Yürüme": 6, "Otobüs": 16, "Özel araç": 5, "Bisiklet": 3, "Raylı sistem": 10}
    assert RAW_TRANSPORT[-1] == "Raylı sistem"


def test_count_tables_match_the_printed_totals() -> None:
    assert sum(row[-1] for row in MATERIAL_COUNTS) == 60
    assert sum(row[-1] for row in SOURCE_COUNTS) == 120
    by_design = Counter()
    for _, design, _, count in AD_COUNTS:
        by_design[design] += count
    assert by_design == {"A": 110, "B": 60}


# --- Konu 1 deneyleri ---------------------------------------------------------------

def test_population_crossing_of_the_ordinal_codes_is_3_75() -> None:
    assert CROSSING == pytest.approx(3.75)


def test_code_ranking_flips_only_through_the_spacing() -> None:
    low, high = _run(ORDINAL_CODES, n=2000, c=3.0), _run(ORDINAL_CODES, n=2000, c=10.0)
    assert low.tables["dagilim"].equals(high.tables["dagilim"])
    means_low, means_high = low.tables["ortalamalar"], high.tables["ortalamalar"]
    assert means_low.loc["A", "ort_12c"] > means_low.loc["B", "ort_12c"]
    assert means_high.loc["A", "ort_12c"] < means_high.loc["B", "ort_12c"]


def test_observational_gap_carries_selection_and_experiment_does_not() -> None:
    state = _run(DESIGN, n=5000, gamma=1.0, tau=5.0)
    rho = 1 / 2 ** 0.5
    expected_gap = 5.0 + 8 * 2 * rho * (2 / 3.141592653589793) ** 0.5
    assert state.scalars["fark_gozlem"] == pytest.approx(expected_gap, abs=0.8)
    assert state.scalars["fark_deney"] == pytest.approx(5.0, abs=0.6)


def test_without_selection_both_designs_estimate_the_effect() -> None:
    state = _run(DESIGN, n=5000, gamma=0.0, tau=5.0)
    assert state.scalars["fark_gozlem"] == pytest.approx(5.0, abs=0.6)


def test_biased_sample_centres_on_the_wrong_value() -> None:
    table = _run(REPRESENTATION).tables["tekrarlar"]
    assert POPULATION_MEAN == pytest.approx(40.0)
    assert table["yanli_ort"].mean() == pytest.approx(0.7 * 20 + 0.3 * 45, abs=0.3)
    assert table["rastgele_ort"].mean() == pytest.approx(40.0, abs=0.5)
    assert table["yanli_ort"].std() < table["rastgele_ort"].std()


# --- Konu 2 deneyleri ---------------------------------------------------------------

def test_percentages_do_not_follow_group_size_but_counts_do() -> None:
    small, large = _run(FREQUENCY_OR_PERCENT, n_merkez=500), _run(FREQUENCY_OR_PERCENT, n_merkez=3000)
    assert large.tables["frekanslar"].loc["Merkez", "Özel araç"] > small.tables["frekanslar"].loc["Merkez", "Özel araç"]
    assert large.tables["yuzdeler"].loc["Merkez", "Özel araç"] == pytest.approx(12.5, abs=1.5)
    assert small.tables["yuzdeler"].loc["Merkez", "Özel araç"] == pytest.approx(12.5, abs=3.5)


def test_row_percentages_are_stable_and_column_percentages_follow_pi() -> None:
    for share in (0.2, 0.8):
        state = _run(ROW_OR_COLUMN, n=5000, pi=share)
        assert state.tables["satir_yuzde"].loc["İktisat", "Dijital"] == pytest.approx(45.0, abs=3.0)
        expected = 100 * share * 0.45 / (share * 0.45 + (1 - share) * 0.40)
        assert state.tables["sutun_yuzde"].loc["İktisat", "Dijital"] == pytest.approx(expected, abs=3.0)


def test_simpson_reversal_appears_only_with_unequal_composition() -> None:
    reversed_state = _run(SIMPSON, n=3000)
    gap = {name: reversed_state.tables[name].loc["B", "Dönüştü"] - reversed_state.tables[name].loc["A", "Dönüştü"]
           for name in ("kolay_oran", "zor_oran", "genel_oran")}
    assert gap["kolay_oran"] > 0 and gap["zor_oran"] > 0 and gap["genel_oran"] < 0
    balanced = _run(SIMPSON, n=3000, a_A=0.5, a_B=0.5)
    assert balanced.tables["genel_oran"].loc["B", "Dönüştü"] > balanced.tables["genel_oran"].loc["A", "Dönüştü"]


def test_pie_starts_at_three_o_clock_and_turns_counterclockwise_like_the_notes() -> None:
    """Şekil 2.5: otobüs dilimi 0°'den 144°'ye. Plotly ilk dilimi ``rotation`` açısında bitirdiği için
    rotation = 90° − 144° = −54° olmalıdır."""

    from core.charts import figure_for
    from core.labs.konu02 import KONU02_LAB
    from core.labs.runner import run_operations
    from core.labs.spec import PieChart

    step = KONU02_LAB.step(6)
    pie = next(op for op in step.operations if isinstance(op, PieChart))
    state = run_operations(KONU02_LAB.operations_through(6))
    trace = figure_for(pie, state).data[0]
    assert trace.direction == "counterclockwise"
    assert trace.rotation == pytest.approx(-54.0)
    assert list(trace.labels) == ["Otobüs", "Raylı sistem", "Yürüme", "Özel araç", "Bisiklet"]
