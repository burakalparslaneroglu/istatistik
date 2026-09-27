"""Uygulama tanımını çalıştırır ve notlardaki sayılarla karşılaştırır.

Veriler ders notlarındaki küçük veri setleridir ve tanımın içinde yazılıdır; dış kaynak yoktur.
Simülasyonlarda tek bir ``np.random.default_rng(seed)`` üreteci vardır ve bütün çekilişler işlem
sırasıyla ondan yapılır. Üretilen Python kodu aynı sırayla çektiği için aynı sayıları verir.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from core.labs import expr as E
from core.labs import tables as T
from core.labs.spec import (
    TOTAL,
    BarChart,
    CellTarget,
    Check,
    CompareBarChart,
    Count,
    CrossTab,
    Derive,
    Draw,
    DrawCategory,
    FrequencyTable,
    FromCounts,
    GroupedBarChart,
    Groups,
    GroupSummary,
    Histogram,
    InlineData,
    LabSpec,
    LineChart,
    MapCodes,
    MonteCarlo,
    NewSample,
    Operation,
    PieChart,
    Scalar,
    ScalarTable,
    ScalarTarget,
    Shape,
    Statistic,
    StatTarget,
    TableTarget,
    VariableTypes,
)


@dataclass
class CheckResult:
    check: Check
    value: float
    passed: bool

    @property
    def difference(self) -> float:
        return self.value - self.check.expected


@dataclass
class LabState:
    frames: dict[str, pd.DataFrame] = field(default_factory=dict)
    tables: dict[str, pd.DataFrame] = field(default_factory=dict)
    scalars: dict[str, float] = field(default_factory=dict)
    plots: dict[str, object] = field(default_factory=dict)
    rng: np.random.Generator | None = None


@dataclass
class LabRun:
    state: LabState
    checks: dict[int, list[CheckResult]]

    @property
    def all_passed(self) -> bool:
        return all(result.passed for items in self.checks.values() for result in items)

    def step_checks(self, number: int) -> list[CheckResult]:
        return self.checks.get(number, [])


# --- Yardımcılar ------------------------------------------------------------------

def plot_key(op) -> str:
    """Grafiğin uygulama durumundaki anahtarı; başlıklar bir tanım içinde tekildir."""

    return f"{type(op).__name__}:{op.title}"


def _subset(frame: pd.DataFrame, where: tuple[str, object] | None) -> pd.DataFrame:
    if where is None:
        return frame
    column, value = where
    return frame[frame[column] == value]


def statistic(series: pd.Series, stat: str) -> float:
    if stat == "count":
        return float(series.count())
    if stat == "sum":
        return float(series.sum())
    if stat == "mean":
        return float(series.mean())
    if stat == "min":
        return float(series.min())
    if stat == "max":
        return float(series.max())
    if stat == "value":
        if len(series) != 1:
            raise ValueError(f"Tek değer beklenirken {len(series)} gözlem bulundu.")
        return float(series.iloc[0])
    raise ValueError(f"Desteklenmeyen istatistik: {stat}")


def _scalar(state: LabState):
    def lookup(name: str) -> float:
        return float(state.scalars[name])

    return lookup


def evaluate_scalar(expression: E.Expr, state: LabState) -> float:
    return float(E.evaluate(expression, scalar=_scalar(state)))


def without_total(table: pd.DataFrame) -> pd.DataFrame:
    """Grafiklerde ``Toplam`` satırı ve sütunu çizilmez."""

    return table.drop(index=TOTAL, columns=TOTAL, errors="ignore")


def _bar_data(op: BarChart, state: LabState) -> pd.DataFrame:
    if op.x is None:
        table = without_total(state.tables[op.source])
        data = pd.DataFrame({"kategori": table.index.astype(str), "deger": table[op.y].to_numpy(dtype=float)})
    else:
        frame = state.frames[op.source]
        data = pd.DataFrame(
            {"kategori": frame[op.x].astype(str).to_numpy(), "deger": frame[op.y].to_numpy(dtype=float)}
        )
    if op.sort == "azalan":
        data = data.sort_values("deger", ascending=False, kind="stable")
    elif op.sort is not None:
        raise ValueError(f"Desteklenmeyen sıralama: {op.sort}")
    return data.reset_index(drop=True)


# --- İşlemler -----------------------------------------------------------------------

def execute(op: Operation, state: LabState) -> None:
    if isinstance(op, InlineData):
        state.frames[op.frame] = T.inline_frame(op.columns, op.rows)
    elif isinstance(op, FromCounts):
        state.frames[op.frame] = T.from_counts(op.columns, op.rows)
    elif isinstance(op, VariableTypes):
        frame = state.frames[op.frame]
        rows = []
        for variable, kind, detail in op.rows:
            stored = "sayı" if pd.api.types.is_numeric_dtype(frame[variable]) else "metin"
            rows.append({"degisken": variable, "saklama": stored, "tur": kind, "ayrinti": detail})
        state.tables[op.result] = pd.DataFrame(rows).set_index("degisken")
    elif isinstance(op, MapCodes):
        frame = state.frames[op.frame]
        frame[op.name] = T.map_codes(frame[op.source], op.mapping)
    elif isinstance(op, Groups):
        frame = state.frames[op.frame]
        if sum(op.sizes) != len(frame) or len(op.sizes) != len(op.labels):
            raise ValueError("Grup büyüklüklerinin toplamı gözlem sayısına eşit olmalıdır.")
        frame[op.name] = np.repeat(np.asarray(op.labels, dtype=object), op.sizes)
    elif isinstance(op, Derive):
        frame = state.frames[op.frame]
        frame[op.name] = E.evaluate(op.expr, frame, scalar=_scalar(state))
    elif isinstance(op, NewSample):
        state.frames[op.frame] = pd.DataFrame({"id": np.arange(1, op.nobs + 1)})
        if op.seed is not None:
            state.rng = np.random.default_rng(op.seed)
        elif state.rng is None:
            raise ValueError("Tohumsuz örneklem yalnız Monte Carlo döngüsü içinde kullanılabilir.")
    elif isinstance(op, Draw):
        frame, rng = state.frames[op.frame], state.rng
        if op.distribution == "normal":
            frame[op.name] = rng.normal(op.first, op.second, size=len(frame))
        elif op.distribution == "uniform":
            frame[op.name] = rng.uniform(op.first, op.second, size=len(frame))
        else:
            raise ValueError(f"Desteklenmeyen dağılım: {op.distribution}")
    elif isinstance(op, DrawCategory):
        frame = state.frames[op.frame]
        u = state.rng.random(len(frame))
        frame[op.name] = T.draw_categories(frame, u, op.categories, op.probabilities, op.by)
    elif isinstance(op, Shape):
        frame = state.frames[op.frame]
        state.scalars[op.observations] = float(len(frame))
        state.scalars[op.variables] = float(frame.drop(columns=list(op.exclude)).shape[1])
    elif isinstance(op, Count):
        frame = state.frames[op.frame]
        state.scalars[op.name] = float((frame[op.column] == op.value).sum())
    elif isinstance(op, Statistic):
        series = _subset(state.frames[op.frame], op.where)[op.variable]
        state.scalars[op.name] = statistic(series, op.stat)
    elif isinstance(op, Scalar):
        state.scalars[op.name] = evaluate_scalar(op.expr, state)
    elif isinstance(op, ScalarTable):
        state.tables[op.result] = pd.DataFrame(
            {"deger": [evaluate_scalar(expression, state) for _, expression in op.rows]},
            index=pd.Index([label for label, _ in op.rows], name="nicelik"),
        )
    elif isinstance(op, GroupSummary):
        grouped = state.frames[op.frame].groupby(op.by)
        table = pd.DataFrame({name: grouped[variable].agg(stat) for name, variable, stat in op.columns})
        state.tables[op.result] = table.reindex(list(op.order))
    elif isinstance(op, FrequencyTable):
        values = state.frames[op.frame][op.variable]
        state.tables[op.result] = T.frequency_table(values, op.order, relative=op.relative, totals=op.totals)
    elif isinstance(op, CrossTab):
        frame = _subset(state.frames[op.frame], op.where)
        state.tables[op.result] = T.crosstab(
            frame, op.row, op.column, op.row_order, op.column_order, percent=op.percent, margins=op.margins
        )
    elif isinstance(op, BarChart):
        state.plots[plot_key(op)] = _bar_data(op, state)
    elif isinstance(op, GroupedBarChart):
        table = without_total(state.tables[op.table])
        state.plots[plot_key(op)] = table if op.series == "satir" else table.T
    elif isinstance(op, CompareBarChart):
        state.plots[plot_key(op)] = pd.DataFrame(
            {label: state.tables[name][op.column] for label, name in op.tables}
        )
    elif isinstance(op, PieChart):
        values = state.tables[op.table].loc[list(op.order), op.column].astype(float)
        table = pd.DataFrame({op.column: values, "aci": 360 * values})
        state.tables[op.result] = table
        state.plots[plot_key(op)] = table
    elif isinstance(op, LineChart):
        frame = state.frames[op.frame]
        state.plots[plot_key(op)] = frame[[op.x, op.y]].copy()
    elif isinstance(op, Histogram):
        state.plots[plot_key(op)] = state.tables[op.table][[column for column, _ in op.columns]].copy()
    elif isinstance(op, MonteCarlo):
        _monte_carlo(op, state)
    else:
        raise TypeError(f"Tanınmayan işlem: {type(op).__name__}")


def _monte_carlo(op: MonteCarlo, state: LabState) -> None:
    """Tekrar döngüsü: üreteç bir kez tohumlanır; her tekrar aynı üreteçten yeni çekiliş yapar."""

    rng = np.random.default_rng(op.seed)
    rows: list[list[float]] = []
    for _ in range(op.reps):
        local = LabState(rng=rng)
        for inner in op.body:
            execute(inner, local)
        rows.append([evaluate_scalar(expression, local) for _, expression in op.collect])
    state.rng = rng
    state.tables[op.result] = pd.DataFrame(rows, columns=[name for name, _ in op.collect])


# --- Notlarla karşılaştırma ---------------------------------------------------------

def evaluate_target(target, state: LabState) -> float:
    if isinstance(target, StatTarget):
        series = _subset(state.frames[target.frame], target.where)[target.variable]
        return statistic(series, target.stat)
    if isinstance(target, ScalarTarget):
        return float(state.scalars[target.name])
    if isinstance(target, TableTarget):
        return float(state.tables[target.table].loc[target.row, target.column])
    if isinstance(target, CellTarget):
        return float(state.frames[target.frame][target.column].iloc[target.row - 1])
    raise TypeError(f"Tanınmayan hedef: {type(target).__name__}")


def run_operations(operations) -> LabState:
    state = LabState()
    for op in operations:
        execute(op, state)
    return state


def run_lab(spec: LabSpec) -> LabRun:
    state = LabState()
    checks: dict[int, list[CheckResult]] = {}
    for step in spec.steps:
        for op in step.operations:
            execute(op, state)
        results = []
        for check in step.checks:
            value = evaluate_target(check.target, state)
            passed = bool(np.isfinite(value)) and abs(value - check.expected) <= check.tolerance
            results.append(CheckResult(check=check, value=value, passed=passed))
        checks[step.number] = results
    return LabRun(state=state, checks=checks)
