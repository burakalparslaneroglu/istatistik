"""Ders notu uygulamalarının ortak "Uygulama" sekmesi.

Her uygulama ``core.labs`` altındaki tek bir tanımdan beslenir: adım metni, uygulamanın hesabı,
Python ve R kodu ve notlarla karşılaştırma aynı kaynaktan gelir. Varsayılan veri notlardaki küçük veri
setleridir. Ek kaynakları olan konularda (``core.labs.ornekler``) sekmenin üstünde veri kaynağı seçilir:
notlardaki örnek, kurgusal alternatif örnek ya da öğrencinin kendi dosyası (``topics.kendi_veri_ui``).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Callable

import numpy as np
import pandas as pd
import streamlit as st

from core.charts import CHART_TYPES, figure_for, show_figure, tr_number
from core.codegen.base import LANGUAGE_INFO, LANGUAGES, render_script, render_step, script_filename
from core.labs.ornek import SOURCE_LABELS, kesin, md, ondalik
from core.labs.ornekler import get_variants
from core.labs.registry import get_lab
from core.labs.runner import LabRun, LabState, run_lab, run_operations
from core.labs.spec import (
    REPRO_DESCRIPTIONS,
    SOURCES,
    TOTAL,
    BoxSummary,
    ClassTable,
    CompleteCases,
    Count,
    CrossTab,
    FrequencyTable,
    FromCounts,
    GroupSummary,
    InlineData,
    JoinColumns,
    LabSpec,
    LabStep,
    MapCodes,
    Outcomes,
    PairStatistic,
    Percentile,
    PieChart,
    ReadFile,
    ReplaceMax,
    Scalar,
    ScalarTable,
    Selections,
    Shape,
    ShowFrame,
    Statistic,
    StemLeaf,
    VariableTypes,
)
from topics.kendi_veri_ui import render_custom

CODE_LANGUAGE_KEY = "code_language"
_COLUMN_LABELS = {
    "frekans": "Frekans",
    "goreli": "Göreli frekans",
    "yuzde": "Yüzde frekans",
    "aci": "Dilim açısı (°)",
    "sayi": "Sayı",
    "alt": "Alt sınır",
    "ust": "Üst sınır",
    "orta_nokta": "Orta nokta",
    "kumulatif_frekans": "Kümülatif frekans",
    "kumulatif_goreli": "Kümülatif göreli frekans",
    "kumulatif_yuzde": "Kümülatif yüzde",
    "yapraklar": "Yapraklar",
    "yaprak_sayisi": "Yaprak sayısı",
    "nicelik": "Büyüklük",
    TOTAL: TOTAL,
}
_BOX_LABELS = {
    "en_kucuk": "En küçük değer",
    "q1": "Q₁ (birinci çeyrek)",
    "medyan": "Medyan",
    "q3": "Q₃ (üçüncü çeyrek)",
    "en_buyuk": "En büyük değer",
    "iqr": "IQR = Q₃ − Q₁",
    "alt_sinir": "Alt sınır Q₁ − 1,5·IQR",
    "ust_sinir": "Üst sınır Q₃ + 1,5·IQR",
    "alt_biyik": "Sol bıyık ucu",
    "ust_biyik": "Sağ bıyık ucu",
    "aykiri_sayisi": "Aykırı değer sayısı",
}


# --- Tablo biçimleme ---------------------------------------------------------------

def _count(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def _blank_if_missing(formatter: Callable[[float], str]) -> Callable[[float], str]:
    """Toplam satırında toplanmayan hücreler (ör. sınıf sınırları) boş gösterilir."""

    return lambda value: "" if pd.isna(value) else formatter(value)


def _boundary(value: float) -> str:
    return tr_number(value, 0 if float(value).is_integer() else 2)


def _short(value: float) -> Decimal:
    """Sayının 15 anlamlı basamaklı kısa yazımı: kayan nokta gürültüsü (0,0011250000000000001) atılır."""

    return Decimal(f"{float(value):.15g}").normalize()


def _places(value: float) -> int:
    return max(0, -_short(value).as_tuple().exponent)


def _midpoint(value: float) -> str:
    """Sınıf orta noktası: tam sayıysa ondalıksız, değilse en az 2 basamak; 0,0125 gibi değerler tam yazılır."""

    if float(value).is_integer():
        return tr_number(value, 0)
    return tr_number(value, max(2, _places(value)))


def _value_text(value: float) -> str:
    """Altyazıdaki tek bir sayı: üstel gösterim yok (8,79e+14 değil); kayan nokta gürültüsü atılır."""

    return ondalik(kesin(value), _places(value))


def _index_text(item) -> str:
    """Satır adı: ondalık sayılar Türkçe yazımla (1,5; −1); ondalıksız değerde ",0" yazılmaz."""

    if isinstance(item, (float, np.floating)) and np.isfinite(item):
        return f"{float(item):.10g}".replace(".", ",").replace("-", "−")
    return str(item)


def _formatted(table: pd.DataFrame, formats: dict[str, Callable[[float], str]], index_label: str,
               label: Callable[[str], str], rename: bool = True) -> pd.DataFrame:
    """Sayıları Türkçe biçimde metne çevirir; satır adları ilk sütun olur. ``rename=False``: sütunlar kategori
    adlarıdır (çapraz tablo) ve olduğu gibi yazılır."""

    shown = pd.DataFrame(index=table.index)
    for column in table.columns:
        formatter = formats.get(str(column))
        values = table[column]
        shown[column] = [formatter(value) for value in values] if formatter else values
    if rename:
        shown = shown.rename(columns=lambda name: _COLUMN_LABELS.get(str(name), label(str(name))))
    else:
        shown.columns = [str(name) for name in shown.columns]
    shown.index = [_index_text(item) for item in shown.index]
    return shown.rename_axis(index_label).reset_index()


def display_table(op, table: pd.DataFrame, label: Callable[[str], str] = lambda name: name) -> pd.DataFrame:
    """Bir sonuç tablosunun ekranda gösterilecek biçimi."""

    if isinstance(op, FrequencyTable):
        formats = {"frekans": _count, "goreli": lambda v: tr_number(v, 3), "yuzde": lambda v: tr_number(v, 1, True)}
        return _formatted(table, formats, label(op.variable), label)
    if isinstance(op, CrossTab):
        if op.weights is not None:
            def formatter(value: float) -> str:
                return tr_number(value, op.decimals)
        elif op.percent is None:
            formatter = _count
        else:
            def formatter(value: float) -> str:
                return tr_number(value, op.decimals, True)
        formats = {str(column): formatter for column in table.columns}
        return _formatted(table, formats, f"{label(op.row)} \\ {label(op.column)}", label, rename=False)
    if isinstance(op, PieChart):
        formats = {op.column: lambda v: tr_number(v, 3), "aci": lambda v: tr_number(v, 1)}
        return _formatted(table, formats, "Kategori", label)
    if isinstance(op, ClassTable):
        formats = {
            "orta_nokta": _midpoint, "frekans": _count, "goreli": lambda v: tr_number(v, 3),
            "yuzde": lambda v: tr_number(v, 1, True), "kumulatif_frekans": _count,
            "kumulatif_goreli": lambda v: tr_number(v, 3), "kumulatif_yuzde": lambda v: tr_number(v, 1, True),
        }
        shown = table.drop(columns=["alt", "ust"])  # sınıf sınırları satır adında yazılı
        heading = "Sınıf" if op.row_labels == "sinif" else "Sınır"
        return _formatted(shown, {k: _blank_if_missing(f) for k, f in formats.items()}, heading, label)
    if isinstance(op, StemLeaf):
        return _formatted(table, {"yaprak_sayisi": _count}, "Gövde", label)
    if isinstance(op, ScalarTable):
        return pd.DataFrame({"Büyüklük": table.index, "Değer": [tr_number(v, op.decimals) for v in table["deger"]]})
    if isinstance(op, GroupSummary):
        formats = {name: _count if stat == "count" else (lambda v: tr_number(v, op.decimals))
                   for name, _, stat in op.columns}
        return _formatted(table, formats, label(op.by), label)
    if isinstance(op, JoinColumns):
        formats = {name: (lambda v: tr_number(v, op.decimals, op.percent)) for name, _, _ in op.columns}
        index = str(table.index.name or "")
        return _formatted(table, formats, _COLUMN_LABELS.get(index, label(index)) or "Kategori", label)
    if isinstance(op, BoxSummary):
        shown = table.rename(index=_BOX_LABELS)
        formats = {str(column): _boundary for column in shown.columns}
        return _formatted(shown, formats, "Özet", label)
    if isinstance(op, VariableTypes):
        shown = table.reset_index()
        shown.insert(0, "Değişken", [label(name) for name in shown["degisken"]])
        return shown.rename(columns={"degisken": "Koddaki adı", "saklama": "Yazılımda saklama",
                                     "tur": "İstatistiksel tür", "ayrinti": "Ayrıntı"})
    raise TypeError(f"Tablo türü tanınmıyor: {type(op).__name__}")


def _plain(text: str) -> str:
    return text


def crosstab_caption(op: CrossTab, label: Callable[[str], str] = lambda name: name,
                     escape: Callable[[str], str] = _plain) -> str:
    """Çapraz tablonun ne gösterdiği: sayılar mı, hangi paydayla yüzdeler mi, hangi alt grupta mı. ``escape``:
    kullanıcının adlarını Markdown'a güvenli yazan fonksiyon (kendi verini yükle)."""

    if op.weights is not None:
        kind = (f"**Çapraz tablo — toplanan sütun: {escape(label(op.weights))}** (her hücre, o hücreye düşen "
                "satırlardaki değerlerin toplamıdır)")
    else:
        kind = {
            None: "**Çapraz tablo: sayılar**",
            "satir": "**Satır yüzdeleri** (payda: satır toplamı)",
            "sutun": "**Sütun yüzdeleri** (payda: sütun toplamı)",
        }[op.percent]
    if op.where is not None:
        column, value = op.where
        kind += f" · yalnız {escape(label(column))}: {escape(str(value))}"
    return kind


def show_table(shown) -> None:
    """Tabloyu gösterir; ``shown`` bir DataFrame ya da Türkçe sayı biçimli Styler'dır (bkz. ``_frame``)."""

    rows = len(shown) if isinstance(shown, pd.DataFrame) else len(shown.data)
    # 16 satıra kadar (ör. 5 dakikalık 14 sınıf ve Toplam) tablo kaydırmadan görünür; daha uzun ham veri kayar.
    height = min(35 * (rows + 1) + 3, 598)
    st.dataframe(shown, hide_index=True, width="stretch", height=height)


def _decimals(values: pd.Series, small: bool = False) -> int:
    """Kesirli bir sütunun gösterim basamağı: en az 2 (notlardaki 0,25 ve 17,50 gibi), en çok 4.

    ``small`` (notlar dışındaki kaynaklar; notların ekranı değişmez): veri gibi kısa değerler (15'ten az anlamlı
    basamak, ör. 0,345678 ya da 0,000056) tam yazılır; bölmeyle bulunan uzun değerler (25,3333…) en az 4 basamak ve en
    küçük değerin 3 anlamlı basamağıyla (en çok 15)."""

    if small:
        nonzero = [_short(value) for value in values if value != 0 and np.isfinite(value)]
        if not nonzero:
            return 2
        if max(len(item.as_tuple().digits) for item in nonzero) < 15:
            return min(15, max(2, max(-item.as_tuple().exponent for item in nonzero)))
        smallest = min(abs(float(item)) for item in nonzero)
        return min(15, max(4, 2 - int(np.floor(np.log10(smallest)))))
    for decimals in (2, 3):
        if np.allclose(values, np.round(values, decimals), rtol=0, atol=1e-9):
            return decimals
    return 4


def _whole(values: pd.Series, small: bool = False) -> bool:
    """Sütunun bütün değerleri tam sayı mı. Notlarda 10⁻⁹ toleransla; diğer kaynaklarda tam olarak (1e-11 gibi çok
    küçük değerler 0 görünmesin)."""

    if small:
        return bool((values == np.round(values)).all())
    return bool(np.allclose(values, np.round(values), rtol=0, atol=1e-9))


def _with_blanks(values: pd.Series, small: bool = False) -> pd.Series:
    """Boş hücresi olan sütunun ekran biçimi: değerler metin, boş hücre boş metin; sayılar Türkçe yazımla."""

    present = values.dropna()
    if pd.api.types.is_numeric_dtype(values) and not pd.api.types.is_bool_dtype(values):
        numbers = present.astype(float)
        decimals = 0 if _whole(numbers, small) else _decimals(numbers, small)
        return values.map(lambda value: "" if pd.isna(value) else tr_number(value, decimals))
    return values.map(lambda value: "" if pd.isna(value) else value)


def _frame_label(name: str, label: Callable[[str], str]) -> str:
    """Veri çerçevesi sütununun başlığı: tanımdaki etiket önce (öğrencinin "Yüzde" adlı sütunu "Yüzde frekans"
    olmaz), yoksa sonuç tablolarının ortak başlıkları."""

    own = label(name)
    return own if own != name else _COLUMN_LABELS.get(name, name)


def _frame(frame: pd.DataFrame, label: Callable[[str], str], small: bool = False):
    """Veri çerçevesinin ekran biçimi: tam sayı değerli sütunlar tam sayı, kesirli sütunlar ondalık virgülle.

    Kesirli sütunlar Styler ile biçimlenir; sütun sayısal kaldığı için sağa hizalı görünür. ``small``: bkz.
    ``_decimals``.
    """

    shown = frame.copy()
    formats: dict[str, Callable[[float], str]] = {}
    for column in shown.columns:
        if shown[column].isna().any():  # kendi verindeki boş hücreler boş görünür ("None" ya da "nan" değil)
            shown[column] = _with_blanks(shown[column], small)
            continue
        if shown[column].dtype.kind != "f":
            continue
        if _whole(shown[column], small):
            shown[column] = shown[column].round().astype(int)
            if (shown[column] < 0).any():  # tipografik eksi: −10
                formats[column] = lambda value: tr_number(value, 0)
        else:
            formats[column] = lambda value, decimals=_decimals(shown[column], small): tr_number(value, decimals)
    rename = {column: _frame_label(str(column), label) for column in shown.columns}
    shown = shown.rename(columns=rename)
    if not formats:
        return shown
    return shown.style.format({rename[column]: formatter for column, formatter in formats.items()})


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

_METRICS = (Shape, Count, Statistic, PairStatistic, Scalar, Percentile)
_SUBSCRIPTS = str.maketrans("0123456789,", "₀₁₂₃₄₅₆₇₈₉,")


def _metrics(op, state: LabState) -> list[tuple[str, str]]:
    if isinstance(op, Percentile):
        items = []
        if op.location is not None:
            index = tr_number(op.p, 0 if float(op.p).is_integer() else 1).translate(_SUBSCRIPTS)
            location = tr_number(state.scalars[op.location], 2).rstrip("0").rstrip(",")  # 7,80 → 7,8
            items.append((f"Konum L{index}", location))
        return items + [(op.comment, tr_number(state.scalars[op.name], op.decimals))]
    if isinstance(op, Shape):
        return [("Gözlem sayısı n", _count(state.scalars[op.observations])),
                ("Değişken sayısı", _count(state.scalars[op.variables]))]
    if isinstance(op, Count):
        return [(op.comment, _count(state.scalars[op.name]))]
    if isinstance(op, (Statistic, PairStatistic)):
        return [(op.comment, tr_number(state.scalars[op.name], op.decimals))]
    return [(op.comment, tr_number(state.scalars[op.name], op.decimals, op.percent))]


def _show_metrics(items: list[tuple[str, str]]) -> None:
    for start in range(0, len(items), 4):
        chunk = items[start:start + 4]
        for column, (title, value) in zip(st.columns(len(chunk)), chunk):
            column.metric(title, value)


def _input_only(operations, index: int, state: LabState) -> bool:
    """Satır içi veri, aynı adımda aynı çerçevenin bütün sütunlarını gösteren bir ``ShowFrame`` ile sonuçlanıyorsa
    yalnız girdi sütunlarıyla gösterilir: aynı tablo iki kez görünmez."""

    op = operations[index]
    columns = set(state.frames[op.frame].columns)
    return any(isinstance(later, ShowFrame) and later.frame == op.frame and columns <= set(later.columns)
               for later in operations[index + 1:])


def render_operations(operations, state: LabState, label: Callable[[str], str], key_prefix: str,
                      escape: Callable[[str], str] = _plain, small: bool = False) -> None:
    """İşlemlerin sonuçlarını sırayla gösterir; art arda gelen tek sayılar tek satırda toplanır. ``escape``: başlık ve
    etiketlerdeki kullanıcı adlarını Markdown'a güvenli yazar (kendi verini yükle; notlardaki metinler olduğu gibi).
    ``small``: çok küçük değerli sütunlar sıfır görünmesin (notlar dışındaki kaynaklar; bkz. ``_decimals``)."""

    pending: list[tuple[str, str]] = []
    for index, op in enumerate(operations):
        if isinstance(op, _METRICS):
            pending.extend((escape(title), value) for title, value in _metrics(op, state))
            continue
        if pending:
            _show_metrics(pending)
            pending = []
        if isinstance(op, InlineData):
            frame = state.frames[op.frame]
            if _input_only(operations, index, state):
                frame = frame[list(op.columns)]
            st.markdown(f"**{escape(op.comment)}**")
            if op.layout and len(op.columns) == 1 and len(frame) % op.layout == 0:
                # Notlardaki gibi satır başına ``layout`` değer; sütun başlıkları satır içindeki sıradır.
                values = frame[op.columns[0]].to_numpy()
                grid = pd.DataFrame(values.reshape(-1, op.layout), columns=[str(i) for i in range(1, op.layout + 1)])
                show_table(_frame(grid, str))
            else:
                show_table(_frame(frame, label, small))
        elif isinstance(op, FromCounts):
            counts = pd.DataFrame([tuple(row) for row in op.rows], columns=[*op.columns, "sayi"])
            st.markdown(f"**{escape(op.comment)}**")
            show_table(_frame(counts, label, small))
            st.caption(f"Her satır sayısı kadar tekrarlanır: toplam {_count(len(state.frames[op.frame]))} gözlem.")
        elif isinstance(op, ReadFile):
            frame = state.frames[op.frame]
            st.markdown(f"**{escape(op.comment)}**")
            show_table(_frame(frame, label, small))
            dropped = f" Temel sütunlarda boş hücre bulunan {_count(op.dropped)} satır çıkarıldı." if op.dropped else ""
            st.caption(f"Analizde {_count(len(frame))} gözlem var.{dropped}")
        elif isinstance(op, CompleteCases):
            st.caption(f"{op.comment}: {_count(len(state.frames[op.frame]))} gözlem.")
        elif isinstance(op, ReplaceMax):
            before = float(state.frames[op.source][op.variable].max())
            after = float(state.frames[op.frame][op.variable].max())
            st.caption(f"{escape(op.comment)}: en büyük gözlem {_value_text(before)} yerine {_value_text(after)}.")
        elif isinstance(op, (Outcomes, Selections)):
            frame = state.frames[op.frame]
            st.markdown(f"**{escape(op.comment)}**")
            show_table(_frame(frame, label, small))
            noun = "Sonuç" if isinstance(op, Outcomes) else "Seçim"
            st.caption(f"{noun} sayısı: {_count(len(frame))}.")
        elif isinstance(op, ShowFrame):
            st.markdown(f"**{escape(op.comment)}**")
            show_table(_frame(state.frames[op.frame][list(op.columns)], label, small))
        elif isinstance(op, MapCodes):
            frame = state.frames[op.frame][[op.source, op.name]].head(8)
            st.markdown(f"**{escape(op.comment)}**")
            show_table(_frame(frame, label, small))
        elif isinstance(op, CrossTab):
            st.markdown(crosstab_caption(op, label, escape))
            show_table(display_table(op, state.tables[op.result], label))
        elif isinstance(op, GroupSummary) and op.as_frame and any(
                isinstance(later, ShowFrame) and later.frame == op.result for later in operations[index + 1:]):
            continue  # grup özeti aynı adımda türetilen sütunlarıyla birlikte bir kez gösterilir
        elif isinstance(op, (VariableTypes, FrequencyTable, ScalarTable, GroupSummary, ClassTable, StemLeaf,
                             JoinColumns, BoxSummary)):
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
    if spec.source == "notlar":
        st.caption(
            "Her dosya bütün adımları çalıştırır ve sonunda sonuçları ders notlarındaki sayılarla karşılaştırır. "
            "Bir sayı tutmazsa hangisinin tutmadığını söyleyerek durur."
        )
    else:
        files = "" if spec.source == "alternatif" else " Veri dosyanızı betikle aynı klasöre koyun."
        st.caption(
            "Her dosya bütün adımları çalıştırır ve sonunda sonuçları uygulamanın bu sayfada gösterdiği sayılarla "
            f"karşılaştırır. Bir sayı tutmazsa hangisinin tutmadığını söyleyerek durur.{files}"
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


def _spec(topic_key: str, source: str) -> LabSpec:
    """Notlardaki ya da alternatif örneğin tanımı (öğrenci verisi içermez)."""

    return get_lab(topic_key) if source == "notlar" else get_variants(topic_key).alternative()


@st.cache_resource(show_spinner=False)
def _run(topic_key: str, source: str = "notlar") -> LabRun:
    return run_lab(_spec(topic_key, source))


@st.cache_resource(show_spinner=False)
def _state_through(topic_key: str, number: int, source: str = "notlar") -> LabState:
    """Adımın sonundaki durum: sonraki adımların eklediği sütunlar bu adımda görünmez."""

    return run_operations(_spec(topic_key, source).operations_through(number))


def _source_key(topic_key: str) -> str:
    return f"{topic_key}_lab_kaynak"


_SOURCE_ICONS = {
    "notlar": ":material/menu_book:",
    "alternatif": ":material/shuffle:",
    "kendi": ":material/upload_file:",
}


def _render_source(topic_key: str) -> str:
    """Sekmenin en üstünde veri kaynağı seçimi; varsayılan notlardaki örnektir."""

    key = _source_key(topic_key)
    if st.session_state.get(key) not in SOURCES:
        st.session_state[key] = SOURCES[0]
    st.segmented_control(
        "Veri kaynağı", options=list(SOURCES), key=key, required=True, width="stretch",
        format_func=lambda source: f"{_SOURCE_ICONS[source]} {SOURCE_LABELS[source]}",
    )
    return st.session_state[key]


def render_lab(spec: LabSpec) -> None:
    variants = get_variants(spec.topic_key)
    source = _render_source(spec.topic_key) if variants else "notlar"
    if source == "notlar":
        st.markdown(
            f"Bu sekme ders notlarındaki çözümlü örnekleri (**{spec.title}**) adım adım yeniden üretir. "
            "Tablolar notlardaki sayıların aynısını verir; kod dilini kenar çubuğundan seçin."
        )
        active = spec
    elif source == "alternatif":
        active = variants.alternative()
        st.markdown(
            f"Bu sekme notlardaki adımları (**{spec.title}**) başka bir veriyle yeniden yapar. {variants.story} "
            "Sayılar notlardakinden farklıdır; yöntem ve kod aynıdır."
        )
    else:
        active = render_custom(spec.topic_key, variants.custom)
        if active is None:
            return
    step = _render_navigation(active)
    st.subheader(f"Adım {step.number}: {step.title}")
    st.caption(step.note.label())
    st.markdown(step.explanation)
    if step.operations:
        if source == "kendi":
            state = run_operations(active.operations_through(step.number))
        else:
            state = _state_through(spec.topic_key, step.number, source)
        render_operations(step.operations, state, active.label, f"{spec.topic_key}_{source}_adim{step.number}",
                          md if source == "kendi" else _plain, small=source != "notlar")
        if source == "notlar":
            _render_checks(step, _run(spec.topic_key))
    if step.takeaway:
        st.info(step.takeaway, icon=":material/lightbulb:")
    _render_code(active, step)
    if step.number == active.steps[-1].number:
        _render_downloads(active)
