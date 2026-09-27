"""Tanım şeması, tablo hesapları, kategorik çekiliş ve kod üreticisi yardımcıları."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core.codegen.base import render_step, text, wrapped
from core.labs import expr as E
from core.labs import tables as T
from core.labs.runner import LabState, execute, run_operations
from core.labs.spec import (
    TOTAL,
    BoxPlot,
    Check,
    CrossTab,
    DotPlot,
    DrawCategory,
    FrequencyTable,
    FromCounts,
    Histogram,
    InlineData,
    JoinColumns,
    LineChart,
    NewSample,
    Scalar,
    ShowFrame,
    Statistic,
)


def test_frequency_table_follows_the_given_order_and_adds_totals() -> None:
    values = pd.Series(["b", "a", "b", "c", "b"], name="x")
    table = T.frequency_table(values, ("c", "b", "a"), relative=True, totals=True)
    assert list(table.index) == ["c", "b", "a", TOTAL]
    assert list(table["frekans"]) == [1, 3, 1, 5]
    assert table.loc["b", "goreli"] == pytest.approx(0.6)
    assert table.loc[TOTAL, "yuzde"] == pytest.approx(100.0)


def test_frequency_table_rejects_categories_missing_from_the_order() -> None:
    with pytest.raises(ValueError, match="Sırada olmayan"):
        T.frequency_table(pd.Series(["a", "z"]), ("a",))


def test_zero_frequency_categories_are_kept() -> None:
    table = T.frequency_table(pd.Series(["a", "a"]), ("a", "b"), relative=False)
    assert list(table["frekans"]) == [2, 0]


def test_from_counts_repeats_each_row_its_count_times() -> None:
    frame = T.from_counts(("g", "h"), (("x", "p", 2), ("y", "q", 0), ("y", "p", 3)))
    assert len(frame) == 5
    assert frame.groupby(["g", "h"]).size().to_dict() == {("x", "p"): 2, ("y", "p"): 3}


def test_crosstab_denominators() -> None:
    frame = T.from_counts(("r", "c"), (("A", "u", 1), ("A", "v", 3), ("B", "u", 2), ("B", "v", 2)))
    counts = T.crosstab(frame, "r", "c", ("A", "B"), ("u", "v"), margins=True)
    assert counts.loc[TOTAL, TOTAL] == 8 and counts.loc["A", TOTAL] == 4 and counts.loc[TOTAL, "u"] == 3
    rows = T.crosstab(frame, "r", "c", ("A", "B"), ("u", "v"), percent="satir", margins=True)
    assert rows.loc["A", "v"] == pytest.approx(75.0) and rows.loc["B", TOTAL] == pytest.approx(100.0)
    columns = T.crosstab(frame, "r", "c", ("A", "B"), ("u", "v"), percent="sutun", margins=True)
    assert columns.loc["B", "u"] == pytest.approx(200 / 3) and columns.loc[TOTAL, "v"] == pytest.approx(100.0)


def test_class_table_puts_boundary_values_in_the_upper_class_and_adds_totals() -> None:
    values = pd.Series([10.0, 19.0, 20.0, 29.0, 30.0])
    edges = T.class_edges(values, 10)
    assert list(edges) == [10.0, 20.0, 30.0, 40.0]
    table = T.class_table(values, edges, ("frekans", "yuzde", "kumulatif_frekans"), totals=True)
    assert list(table.index) == ["10 ≤ x < 20", "20 ≤ x < 30", "30 ≤ x < 40", TOTAL]
    assert list(table["frekans"]) == [2, 2, 1, 5]
    assert table.loc[TOTAL, "yuzde"] == pytest.approx(100.0)
    assert np.isnan(table.loc[TOTAL, "kumulatif_frekans"])
    cumulative = T.class_table(values, edges, ("kumulatif_yuzde",), row_labels="ust")
    assert list(cumulative.index) == ["x < 20", "x < 30", "x < 40"]
    assert list(cumulative["kumulatif_yuzde"]) == pytest.approx([40.0, 80.0, 100.0])


def test_class_table_rejects_unknown_columns_and_needs_a_class_count_with_a_lower_edge() -> None:
    with pytest.raises(ValueError, match="Tanınmayan"):
        T.class_table(pd.Series([1.0]), np.array([0.0, 10.0]), ("medyan",))
    with pytest.raises(ValueError, match="sınıf sayısı"):
        T.class_edges(pd.Series([1.0]), 10, lower=0)


def test_boundary_labels_use_a_decimal_comma_without_padding() -> None:
    assert T.boundary_label(12.5) == "12,5" and T.boundary_label(20.0) == "20"


def test_stem_leaf_keeps_empty_stems() -> None:
    stems = T.stem_leaf(pd.Series([12.0, 15.0, 31.0]))
    assert list(stems.index) == ["1", "2", "3"]
    assert list(stems["yapraklar"]) == ["2 5", "", "1"]
    assert list(stems["yaprak_sayisi"]) == [2, 0, 1]
    with pytest.raises(ValueError):
        T.stem_leaf(pd.Series([1.5]))


def test_percentile_locations_of_both_rules() -> None:
    assert T.percentile_location(12, 60) == pytest.approx(7.8)
    assert T.percentile_location(12, 60, "yazilim") == pytest.approx(7.6)
    with pytest.raises(ValueError):
        T.percentile_location(12, 60, "tip9")


def test_dot_plot_axis_range_is_shared_by_all_three_renderers() -> None:
    from core.charts import figure_for
    from core.labs.konu04 import KONU04_LAB, SPREAD_RANGE

    step = KONU04_LAB.step(10)
    plots = [op for op in step.operations if isinstance(op, DotPlot)]
    assert len(plots) == 2 and all(op.x_range == SPREAD_RANGE for op in plots)
    state = run_operations(KONU04_LAB.operations_through(10))
    assert all(tuple(figure_for(op, state).layout.xaxis.range) == SPREAD_RANGE for op in plots)
    assert render_step(KONU04_LAB, 10, "Python").count("ax.set_xlim(5, 55)") == 2
    assert render_step(KONU04_LAB, 10, "R").count("xlim = c(5, 55)") == 2


def test_dot_plot_axis_range_must_cover_the_data() -> None:
    state = LabState()
    execute(FromCounts("f", ("x",), ((10.0, 1), (50.0, 1)), "iki gözlem"), state)
    with pytest.raises(ValueError, match="kapsamıyor"):
        execute(DotPlot("f", "x", "Değer", "Dar eksen", x_range=(20, 60)), state)


def test_thresholds_end_exactly_at_one_and_validate() -> None:
    edges = T.thresholds((0.1, 0.2, 0.7))
    assert edges[-1] == 1.0
    with pytest.raises(ValueError):
        T.thresholds((0.5, 0.6))


def test_category_draw_is_the_first_category_whose_cumulative_probability_exceeds_u() -> None:
    frame = pd.DataFrame({"g": ["a"] * 5})
    u = np.array([0.0, 0.0999, 0.1, 0.2999, 0.9999])
    drawn = T.draw_categories(frame, u, ("x", "y", "z"), (((), (0.1, 0.2, 0.7)),), ())
    assert list(drawn) == ["x", "x", "y", "y", "z"]


def test_conditional_category_draws_follow_their_own_probabilities() -> None:
    state = LabState()
    for op in (
        NewSample("s", 20000, 1),
        DrawCategory("s", "g", ("a", "b"), (((), (0.5, 0.5)),), "grup"),
        DrawCategory("s", "y", ("1", "0"), ((("a",), (0.9, 0.1)), (("b",), (0.2, 0.8))), "sonuç", by=("g",)),
    ):
        execute(op, state)
    frame = state.frames["s"]
    shares = frame.groupby("g")["y"].apply(lambda values: (values == "1").mean())
    assert shares["a"] == pytest.approx(0.9, abs=0.01) and shares["b"] == pytest.approx(0.2, abs=0.01)


def test_run_operations_matches_hand_counts() -> None:
    state = run_operations((
        FromCounts("f", ("k",), (("x", 3), ("y", 1)), "sayım"),
        FrequencyTable("f", "k", "t", ("x", "y"), totals=True),
        CrossTab("f", "k", "k", "c", ("x", "y"), ("x", "y"), margins=True),
    ))
    assert state.tables["t"].loc["x", "yuzde"] == pytest.approx(75.0)
    assert state.tables["c"].loc["x", "y"] == 0


def test_check_tolerance_is_half_the_last_printed_digit() -> None:
    assert Check("a", None, 0.625, 3).tolerance == pytest.approx(0.0005, abs=1e-11)
    assert Check("a", None, 64, 0).tolerance == 0.5


def test_expression_rendering_uses_minimal_parentheses() -> None:
    expression = E.mul(100, E.div(E.sub(E.ref("b"), E.ref("a")), E.ref("a")))
    dialect = E.Dialect(variable=lambda name: name, functions={}, power="^")
    assert E.render(expression, dialect) == "100 * (b - a) / a"
    assert E.evaluate(expression, scalar={"a": 72.0, "b": 78.0}.__getitem__) == pytest.approx(8.3333333)


def test_string_literals_are_escaped_for_both_languages() -> None:
    assert text('a "b" \\ c') == '"a \\"b\\" \\\\ c"'
    assert text(0.125) == "0.125" and text(3.0) == "3"


def test_wrapped_lists_keep_the_requested_items_per_line() -> None:
    lines = wrapped("x = [", [str(i) for i in range(7)], "]", per_line=3)
    assert lines == ["x = [", "    0, 1, 2,", "    3, 4, 5,", "    6", "]"]


# --- Konu 5–6 ile eklenen işlemler ----------------------------------------------------

def test_counting_functions_and_new_statistics() -> None:
    assert E.evaluate(E.comb(5, 2)) == 10 and E.evaluate(E.perm(5, 2)) == 20 and E.evaluate(E.factorial(5)) == 120
    frame = pd.DataFrame({"g": [0.0, 1.0, 0.0, 1.0]})
    assert list(E.evaluate(E.cummean(E.var("g")), frame)) == [0.0, 0.5, 1 / 3, 0.5]
    assert list(E.evaluate(E.seq(E.var("g")), frame)) == [1.0, 2.0, 3.0, 4.0]
    state = run_operations((
        InlineData("d", ("x",), ((4,), (6,), (8,), (10,), (12,)), "Tablo 5.1"),
        Statistic("d", "x", "var", "s2", "s²"),
        Statistic("d", "x", "nunique", "k", "farklı değer"),
    ))
    assert state.scalars["s2"] == 10 and state.scalars["k"] == 5
    python, r = render_step(_one_step(E.comb(5, 2)), 1, "Python"), render_step(_one_step(E.comb(5, 2)), 1, "R")
    assert "math.comb(5, 2)" in python and "import math" in python and "choose(5, 2)" in r


def _one_step(expression):
    from core.labs.spec import LabSpec, LabStep, NoteRef

    step = LabStep(1, "t", NoteRef("6.4"), "t", operations=(Scalar("c", expression, "C"),))
    return LabSpec("konu06", "t", "6", (step,))


def test_join_columns_keeps_the_first_table_order() -> None:
    state = run_operations((
        InlineData("d", ("x",), (("b",), ("a",), ("b",)), "veri"),
        FrequencyTable("d", "x", "f1", ("b", "a")),
        FrequencyTable("d", "x", "f2", ("b", "a"), relative=False),
        JoinColumns("j", (("oran", "f1", "goreli"), ("sayi", "f2", "frekans"))),
    ))
    joined = state.tables["j"]
    assert list(joined.index) == ["b", "a"] and list(joined["sayi"]) == [2, 1]
    assert joined.loc["a", "oran"] == pytest.approx(1 / 3)


def test_show_frame_requires_existing_columns() -> None:
    state = run_operations((InlineData("d", ("x",), ((1,),), "veri"),))
    execute(ShowFrame("d", ("x",), "göster"), state)
    with pytest.raises(ValueError, match="gösterilecek sütun yok"):
        execute(ShowFrame("d", ("x", "y"), "göster"), state)


def test_new_charts_use_state_values_and_course_quartiles() -> None:
    from core.charts import figure_for

    operations = (
        InlineData("d", ("k", "y"), tuple((k, 0.1 * (k % 3)) for k in range(1, 61)), "seri"),
        Scalar("p", E.const(0.1), "p"),
        Statistic("d", "y", "mean", "m", "ortalama"),
        LineChart("d", "k", "y", "k", "oran", "Uzun seri", references=(("p", "Gerçek p"),), markers=False),
        Histogram("d", (("y", "Değer"),), 5, 0, 0.5, "Histogram", "Değer", references=(("m", "Ortalama"),),
                  y_label="Gözlem sayısı"),
        BoxPlot((("d", "y", "Seri"),), "Değer", "Veri seti", "Kutu"),
    )
    state = run_operations(operations)
    line, histogram, box = (figure_for(op, state) for op in operations[3:])
    assert line.data[0].mode == "lines" and list(line.data[1].y) == [0.1, 0.1]
    assert line.layout.xaxis.dtick is None  # 60 farklı değer: her değere işaret konmaz
    assert histogram.data[-1].x[0] == pytest.approx(state.scalars["m"])
    assert histogram.layout.yaxis.title.text == "Gözlem sayısı"
    summary = T.box_summary(state.frames["d"]["y"])
    assert (box.data[0].q1[0], box.data[0].median[0], box.data[0].q3[0]) == (summary["q1"], summary["medyan"],
                                                                                summary["q3"])
