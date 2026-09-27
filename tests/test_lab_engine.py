"""Tanım şeması, tablo hesapları, kategorik çekiliş ve kod üreticisi yardımcıları."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core.codegen.base import text, wrapped
from core.labs import expr as E
from core.labs import tables as T
from core.labs.runner import LabState, execute, run_operations
from core.labs.spec import TOTAL, Check, CrossTab, DrawCategory, FrequencyTable, FromCounts, NewSample


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
