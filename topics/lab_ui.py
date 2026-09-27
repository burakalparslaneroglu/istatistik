"""Ders notu uygulamalarının ortak "Uygulama" sekmesi.

Her uygulama ``core.labs`` altındaki tek bir tanımdan beslenir: adım metni, uygulamanın hesabı,
Python ve R kodu ve notlarla karşılaştırma aynı kaynaktan gelir. Veriler notlardaki küçük veri
setleridir ve tanımın içinde yazılıdır; indirme veya yükleme gerekmez.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
import streamlit as st

from core.charts import CHART_TYPES, figure_for, show_figure, tr_number
from core.codegen.base import LANGUAGE_INFO, LANGUAGES, render_script, render_step, script_filename
from core.labs.registry import get_lab
from core.labs.runner import LabRun, LabState, run_lab, run_operations
from core.labs.spec import (
    REPRO_DESCRIPTIONS,
    TOTAL,
    Count,
    CrossTab,
    FrequencyTable,
    FromCounts,
    GroupSummary,
    InlineData,
    LabSpec,
    LabStep,
    MapCodes,
    PieChart,
    Scalar,
    ScalarTable,
    Shape,
    Statistic,
    VariableTypes,
)

CODE_LANGUAGE_KEY = "code_language"
_COLUMN_LABELS = {
    "frekans": "Frekans",
    "goreli": "Göreli frekans",
    "yuzde": "Yüzde frekans",
    "aci": "Dilim açısı (°)",
    "sayi": "Sayı",
    TOTAL: TOTAL,
}


# --- Tablo biçimleme ---------------------------------------------------------------

def _count(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def _formatted(table: pd.DataFrame, formats: dict[str, Callable[[float], str]], index_label: str,
               label: Callable[[str], str]) -> pd.DataFrame:
    """Sayıları Türkçe biçimde metne çevirir; satır adları ilk sütun olur."""

    shown = pd.DataFrame(index=table.index)
    for column in table.columns:
        formatter = formats.get(str(column))
        values = table[column]
        shown[column] = [formatter(value) for value in values] if formatter else values
    shown = shown.rename(columns=lambda name: _COLUMN_LABELS.get(str(name), label(str(name))))
    shown.index = [str(item) for item in shown.index]
    return shown.rename_axis(index_label).reset_index()


def display_table(op, table: pd.DataFrame, label: Callable[[str], str] = lambda name: name) -> pd.DataFrame:
    """Bir sonuç tablosunun ekranda gösterilecek biçimi."""

    if isinstance(op, FrequencyTable):
        formats = {"frekans": _count, "goreli": lambda v: tr_number(v, 3), "yuzde": lambda v: tr_number(v, 1, True)}
        return _formatted(table, formats, label(op.variable), label)
    if isinstance(op, CrossTab):
        if op.percent is None:
            formatter = _count
        else:
            def formatter(value: float) -> str:
                return tr_number(value, op.decimals, True)
        formats = {str(column): formatter for column in table.columns}
        return _formatted(table, formats, f"{label(op.row)} \\ {label(op.column)}", label)
    if isinstance(op, PieChart):
        formats = {op.column: lambda v: tr_number(v, 3), "aci": lambda v: tr_number(v, 1)}
        return _formatted(table, formats, "Kategori", label)
    if isinstance(op, ScalarTable):
        return pd.DataFrame({"Büyüklük": table.index, "Değer": [tr_number(v, op.decimals) for v in table["deger"]]})
    if isinstance(op, GroupSummary):
        formats = {name: (lambda v: tr_number(v, 3)) for name, _, _ in op.columns}
        return _formatted(table, formats, label(op.by), label)
    if isinstance(op, VariableTypes):
        shown = table.reset_index()
        shown.insert(0, "Değişken", [label(name) for name in shown["degisken"]])
        return shown.rename(columns={"degisken": "Koddaki adı", "saklama": "Yazılımda saklama",
                                     "tur": "İstatistiksel tür", "ayrinti": "Ayrıntı"})
    raise TypeError(f"Tablo türü tanınmıyor: {type(op).__name__}")


def crosstab_caption(op: CrossTab, label: Callable[[str], str] = lambda name: name) -> str:
    """Çapraz tablonun ne gösterdiği: sayılar mı, hangi paydayla yüzdeler mi, hangi alt grupta mı."""

    kind = {
        None: "**Çapraz tablo: sayılar**",
        "satir": "**Satır yüzdeleri** (payda: satır toplamı)",
        "sutun": "**Sütun yüzdeleri** (payda: sütun toplamı)",
    }[op.percent]
    if op.where is not None:
        column, value = op.where
        kind += f" · yalnız {label(column).lower()}: {value}"
    return kind


def show_table(shown: pd.DataFrame) -> None:
    height = min(35 * (len(shown) + 1) + 3, 458)
    st.dataframe(shown, hide_index=True, width="stretch", height=height)


def _frame(frame: pd.DataFrame, label: Callable[[str], str]) -> pd.DataFrame:
    shown = frame.copy()
    for column in shown.columns:
        if shown[column].dtype.kind == "f" and np.allclose(shown[column], np.round(shown[column])):
            shown[column] = shown[column].round().astype(int)
    return shown.rename(columns=lambda name: _COLUMN_LABELS.get(str(name), label(str(name))))


# --- Adım gezinimi -----------------------------------------------------------------

def _step_key(spec: LabSpec) -> str:
    return f"{spec.topic_key}_lab_step"


def _shift(spec: LabSpec, delta: int) -> None:
    key = _step_key(spec)
    numbers = [step.number for step in spec.steps]
    current = st.session_state.get(key) or numbers[0]
    index = min(max(numbers.index(current) + delta, 0), len(numbers) - 1)
    st.session_state[key] = numbers[index]


def _render_navigation(spec: LabSpec) -> LabStep:
    key = _step_key(spec)
    numbers = [step.number for step in spec.steps]
    if st.session_state.get(key) not in numbers:
        st.session_state[key] = numbers[0]
    left, middle, right = st.columns([1, 6, 1], vertical_alignment="bottom")
    left.button("‹ Önceki", key=f"{spec.topic_key}_lab_prev", on_click=_shift, args=(spec, -1), width="stretch")
    middle.segmented_control(
        "Adım", options=numbers, format_func=lambda number: f"Adım {number}", key=key,
        label_visibility="collapsed", width="stretch",
    )
    right.button("Sonraki ›", key=f"{spec.topic_key}_lab_next", on_click=_shift, args=(spec, 1), width="stretch")
    return spec.step(st.session_state.get(key) or numbers[0])


# --- Sonuçlar ----------------------------------------------------------------------

_METRICS = (Shape, Count, Statistic, Scalar)


def _metrics(op, state: LabState) -> list[tuple[str, str]]:
    if isinstance(op, Shape):
        return [("Gözlem sayısı n", _count(state.scalars[op.observations])),
                ("Değişken sayısı", _count(state.scalars[op.variables]))]
    if isinstance(op, Count):
        return [(op.comment, _count(state.scalars[op.name]))]
    if isinstance(op, Statistic):
        return [(op.comment, tr_number(state.scalars[op.name], op.decimals))]
    return [(op.comment, tr_number(state.scalars[op.name], op.decimals, op.percent))]


def _show_metrics(items: list[tuple[str, str]]) -> None:
    for start in range(0, len(items), 4):
        chunk = items[start:start + 4]
        for column, (title, value) in zip(st.columns(len(chunk)), chunk):
            column.metric(title, value)


def render_operations(operations, state: LabState, label: Callable[[str], str], key_prefix: str) -> None:
    """İşlemlerin sonuçlarını sırayla gösterir; art arda gelen tek sayılar tek satırda toplanır."""

    pending: list[tuple[str, str]] = []
    for index, op in enumerate(operations):
        if isinstance(op, _METRICS):
            pending.extend(_metrics(op, state))
            continue
        if pending:
            _show_metrics(pending)
            pending = []
        if isinstance(op, InlineData):
            frame = state.frames[op.frame]
            st.markdown(f"**{op.comment}**")
            if op.layout and len(op.columns) == 1 and len(frame) > 12:
                values = frame[op.columns[0]].to_numpy()
                grid = pd.DataFrame(values.reshape(-1, op.layout), columns=[str(i) for i in range(1, op.layout + 1)])
                show_table(grid)
            else:
                show_table(_frame(frame, label))
        elif isinstance(op, FromCounts):
            counts = pd.DataFrame([tuple(row) for row in op.rows], columns=[*op.columns, "sayi"])
            st.markdown(f"**{op.comment}**")
            show_table(_frame(counts, label))
            st.caption(f"Her satır sayısı kadar tekrarlanır: toplam {_count(len(state.frames[op.frame]))} gözlem.")
        elif isinstance(op, MapCodes):
            frame = state.frames[op.frame][[op.source, op.name]].head(8)
            st.markdown(f"**{op.comment}**")
            show_table(_frame(frame, label))
        elif isinstance(op, CrossTab):
            st.markdown(crosstab_caption(op, label))
            show_table(display_table(op, state.tables[op.result], label))
        elif isinstance(op, (VariableTypes, FrequencyTable, ScalarTable, GroupSummary)):
            show_table(display_table(op, state.tables[op.result], label))
        if isinstance(op, PieChart):
            show_figure(figure_for(op, state, label), key=f"{key_prefix}_grafik_{index}")
            show_table(display_table(op, state.tables[op.result], label))
        elif isinstance(op, CHART_TYPES):
            show_figure(figure_for(op, state, label), key=f"{key_prefix}_grafik_{index}")
    if pending:
        _show_metrics(pending)


def _render_checks(step: LabStep, run: LabRun) -> None:
    results = run.step_checks(step.number)
    if not results:
        return
    passed = sum(item.passed for item in results)
    title = f"Notlarla karşılaştırma: {passed}/{len(results)} değer aynı"
    with st.expander(title, icon=":material/fact_check:" if passed == len(results) else ":material/error:"):
        rows = [
            {
                "Değer": item.check.label,
                "Uygulama": tr_number(item.value, item.check.decimals),
                "Notlar": tr_number(item.check.expected, item.check.decimals),
                "Durum": "✓" if item.passed else "✗",
            }
            for item in results
        ]
        show_table(pd.DataFrame(rows))


def _render_code(spec: LabSpec, step: LabStep) -> None:
    if not step.operations:
        return
    language = st.session_state.get(CODE_LANGUAGE_KEY) or LANGUAGES[0]
    info = LANGUAGE_INFO[language]
    title, description = REPRO_DESCRIPTIONS[step.reproducibility]
    st.markdown(f"**{language} kodu**")
    st.caption(f"İki dilde sonuç: **{title}**. {description}")
    st.code(render_step(spec, step.number, language), language=info.highlight, line_numbers=True)
    if step.code_note:
        st.caption(step.code_note)


def _render_downloads(spec: LabSpec) -> None:
    st.markdown("**Bütün uygulamayı indirin**")
    st.caption(
        "Her dosya bütün adımları çalıştırır ve sonunda sonuçları ders notlarındaki sayılarla karşılaştırır. "
        "Bir sayı tutmazsa hangisinin tutmadığını söyleyerek durur."
    )
    for column, language in zip(st.columns(len(LANGUAGES)), LANGUAGES):
        info = LANGUAGE_INFO[language]
        column.download_button(
            f"{language} (.{info.extension})",
            data=render_script(spec, language),
            file_name=script_filename(spec, language),
            mime=info.mime,
            key=f"{spec.topic_key}_lab_download_{language}",
            icon=":material/download:",
            width="stretch",
        )


@st.cache_resource(show_spinner=False)
def _run(topic_key: str) -> LabRun:
    return run_lab(get_lab(topic_key))


@st.cache_resource(show_spinner=False)
def _state_through(topic_key: str, number: int) -> LabState:
    """Adımın sonundaki durum: sonraki adımların eklediği sütunlar bu adımda görünmez."""

    return run_operations(get_lab(topic_key).operations_through(number))


def render_lab(spec: LabSpec) -> None:
    st.markdown(
        f"Bu sekme ders notlarındaki çözümlü örnekleri (**{spec.title}**) adım adım yeniden üretir. "
        "Tablolar notlardaki sayıların aynısını verir; kod dilini kenar çubuğundan seçin."
    )
    run = _run(spec.topic_key)
    step = _render_navigation(spec)
    st.subheader(f"Adım {step.number}: {step.title}")
    st.caption(step.note.label())
    st.markdown(step.explanation)
    if step.operations:
        state = _state_through(spec.topic_key, step.number)
        render_operations(step.operations, state, spec.label, f"{spec.topic_key}_adim{step.number}")
        _render_checks(step, run)
    if step.takeaway:
        st.info(step.takeaway, icon=":material/lightbulb:")
    _render_code(spec, step)
    if step.number == spec.steps[-1].number:
        _render_downloads(spec)
