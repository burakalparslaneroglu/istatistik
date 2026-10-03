"""Konu 3–4 alternatif örnekleri ve kendi verini yükle: değerler motordan bağımsız bir hesapla doğrulanır; sınıf
kuralı, gövde–yaprak birimi, mod durumları, grup ağırlıkları ve metin kuralları denetlenir."""

from __future__ import annotations

import math
import re
from collections import Counter
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from core.labs import kendi_veri as K
from core.labs import ornek_konu03 as O3
from core.labs import ornek_konu04 as O4
from core.labs import tables as T
from core.labs.konu03 import TRAVEL_TIMES
from core.labs.konu04 import SALES
from core.labs.ornek import CustomChoices, custom_case
from core.labs.runner import run_lab
from core.labs.spec import ClassTable, CompleteCases, Count, DotPlot, GroupSummary, Histogram, ReadFile, StemLeaf

ALLOWED_SUFFIXES = {"%100'dür", "%10'dur", "%50", "%80'inin", "%60'ı", "1'dir", "100'e", "1'deki", "3'teki",
                    "7'deki", "§3.9'daki", "5'in", "10'un"}
"""Rakamdan sonra ek yalnız sabit ifadelerde (ör. "payda 1'dir", "Adım 3'teki"); değişken sayılara ek getirilmez."""


def _values(spec) -> dict[str, float]:
    return {check.label: check.expected for step in spec.steps for check in step.checks}


def _texts(spec) -> list[str]:
    return [text for step in spec.steps for text in (step.explanation, step.takeaway, step.code_note)]


def _ops(spec, number: int, kind) -> list:
    return [op for op in spec.step(number).operations if isinstance(op, kind)]


def _konu03(values, label: str = "Değer", k: int | None = None):
    table = K.UploadedTable("veri.csv", "csv", pd.DataFrame({label: values}))
    settings = {} if k is None else {"k": k}
    case, _ = custom_case(O3.CUSTOM, table, CustomChoices(roles={"sayisal": label}, settings=settings))
    return O3.build(case)


def _konu04(frame: pd.DataFrame, roles: dict):
    table = K.UploadedTable("veri.csv", "csv", frame)
    case, _ = custom_case(O4.CUSTOM, table, CustomChoices(roles=roles))
    return O4.build(case)


# --- Konu 3: alternatif örnek ------------------------------------------------------------------

def test_konu03_alternative_matches_a_direct_count() -> None:
    values = _values(O3.alternative())
    scores = np.array(O3.ALT_SCORES)
    assert len(scores) == 50 and values["Gözlem sayısı"] == 50
    assert values["En küçük değer"] == 38 and values["En büyük değer"] == 99
    assert values["Yaklaşık sınıf genişliği"] == pytest.approx(61 / 7)
    for lower in range(30, 100, 10):
        label = f"{lower} ≤ x < {lower + 10}"
        count = int(((scores >= lower) & (scores < lower + 10)).sum())
        assert values[f"Frekans: {label}"] == count
        assert values[f"Yüzde frekans: {label}"] == pytest.approx(2 * count)
        assert values[f"Orta nokta: {label}"] == lower + 5
        assert values[f"Yaprak sayısı, gövde: {lower // 10}"] == count
    assert values["Frekans: 80 ≤ x < 90"] == 20
    for lower in range(30, 100, 5):
        assert values[f"Genişlik 5: {lower} ≤ x < {lower + 5}"] == ((scores >= lower) & (scores < lower + 5)).sum()
    for lower in range(30, 110, 20):
        assert values[f"Genişlik 20: {lower} ≤ x < {lower + 20}"] == ((scores >= lower) & (scores < lower + 20)).sum()
    assert values["Kümülatif yüzde: x < 90"] == pytest.approx(80)
    counts = Counter(O3.ALT_SCORES)
    for value in (85, 88, 89):
        assert values[f"{value} değerindeki gözlem sayısı"] == counts[value] == 3
    assert max(counts.values()) == 3
    assert "sola çarpık" in O3.alternative().step(11).explanation


def test_konu03_class_rule_reproduces_the_notes() -> None:
    classes = O3.classes_for(pd.Series(TRAVEL_TIMES, dtype=float), 7)
    assert (classes.width, classes.lower, classes.count) == (Decimal(10), Decimal(10), 7)
    assert O3.suggested_classes(40) == 7 and O3.suggested_classes(10) == 5 and O3.suggested_classes(10_000) == 15


@pytest.mark.parametrize("raw, unit, expected", [
    ("9.142857", "1", "10"), ("10", "1", "10"), ("10.0001", "1", "20"), ("2.4", "1", "2.5"), ("0.26", "0.01", "0.5"),
    ("0.57", "1", "1"), ("0.0303", "0.001", "0.05"), ("9722.2", "1", "10000"), ("4.2", "1", "5"),
])
def test_nice_width_rounds_up_to_an_easy_value(raw: str, unit: str, expected: str) -> None:
    assert O3.nice_width(Decimal(raw), Decimal(unit)) == Decimal(expected)


def test_decimal_class_edges_are_exact_and_boundary_values_go_up() -> None:
    values = pd.Series([0.2, 0.3, 0.3, 0.45, 0.7, 0.8, 0.9, 1.1, 1.2, 1.3], dtype=float)
    spec = _konu03(values, k=10)
    classes = O3.classes_for(values, 10)
    assert classes.width == Decimal("0.2") and classes.lower == Decimal("0.2")
    edges = classes.edges()
    assert [repr(float(edge)) for edge in edges[:4]] == ["0.2", "0.4", "0.6", "0.8"]
    values_by_label = _values(spec)
    assert values_by_label["Frekans: 0,2 ≤ x < 0,4"] == 3 and values_by_label["Frekans: 0,8 ≤ x < 1"] == 2
    assert sum(value for label, value in values_by_label.items() if label.startswith("Frekans: ")) == 10
    tenth = T.class_edges(None, 0.1, 0.2, 3)
    assert [repr(float(edge)) for edge in tenth] == ["0.2", "0.3", "0.4", "0.5"]


def test_integer_data_never_gets_a_width_below_one() -> None:
    spec = _konu03([1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 1, 2], label="Likert", k=8)
    classes = O3.classes_for(pd.Series([1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 1, 2], dtype=float), 8)
    assert classes.width == Decimal(1) and classes.count == 5
    assert "biriminde kaydedildiği için" in spec.step(2).explanation
    assert "dar sınıf kullanılmaz" in spec.step(8).explanation
    widths = [op.width for op in spec.step(8).operations if type(op).__name__ == "ClassTable"]
    assert widths == [2.0, 4.0]  # h = 1 ile birlikte 1, 2 ve 4 genişlikleri


def test_the_class_count_setting_changes_the_width() -> None:
    values = [12 + (index * 37) % 65 for index in range(60)]  # 12–76
    coarse, fine = _konu03(values, k=5), _konu03(values, k=20)
    assert _ops(coarse, 3, ClassTable)[0].width == 20 and _ops(fine, 3, ClassTable)[0].width == 5  # 12,8 → 20; 3,2 → 5
    assert "/5 = 12{,}8$" in coarse.step(2).explanation and "/20 = 3{,}2$" in fine.step(2).explanation
    for spec, width in ((coarse, 20), (fine, 5)):
        edges = np.arange(0, 80 + width, width)
        expected = np.histogram(values, bins=edges)[0]  # son kutu kapalı; 80 veride olmadığı için [a, b) ile aynı
        frequencies = [check.expected for check in spec.step(3).checks if check.label.startswith("Frekans: ")]
        assert frequencies == list(expected[expected.cumsum() > 0][: len(frequencies)])
    assert O3.CUSTOM.settings[0].default(pd.DataFrame({"x": values}), {}) == O3.suggested_classes(60)


@pytest.mark.parametrize("values, decimals, unit, stem, leaf", [
    (list(TRAVEL_TIMES), 0, 0, 3, 5),
    ([1565, 1852, 1644, 1766, 1888, 1912, 2044, 1812, 1790, 1679, 2008, 1852, 1967, 1954, 1733], 0, 1, 15, 6),
    ([2.37, 2.15, 3.98, 1.85, 3.02, 2.66, 3.41, 2.95, 3.5, 2.2, 1.9, 3.75], 2, -1, 2, 3),
])
def test_stem_leaf_unit_keeps_at_most_twenty_stems_and_truncates(values, decimals, unit, stem, leaf) -> None:
    series = pd.Series(values, dtype=float)
    assert O3.data_decimals(series) == decimals
    assert O3.stem_unit(series, decimals) == unit
    whole = T.stem_leaf_units(pd.Series([values[0] if unit else 35.0]), decimals, unit)[0]
    assert (whole // 10, whole % 10) == (stem, leaf)
    stems = T.stem_leaf(series, decimals, unit)
    assert len(stems) <= O3.MAX_STEMS and stems["yaprak_sayisi"].sum() == len(values)


def test_konu03_stem_leaf_with_a_leaf_unit_of_ten() -> None:
    values = [1565, 1852, 1644, 1766, 1888, 1912, 2044, 1812, 1790, 1679, 2008, 1852, 1967, 1954, 1733]
    spec = _konu03(values, label="Satış")
    op = _ops(spec, 10, StemLeaf)[0]
    assert (op.decimals, op.unit) == (0, 1)
    assert "kesilir, yuvarlanmaz" in spec.step(10).explanation
    table = run_lab(spec).state.tables["govde_yaprak"]
    assert table.loc["16", "yapraklar"] == "4 7" and table.loc["18", "yapraklar"] == "1 5 5 8"


def test_konu03_large_or_negative_data_skips_dot_plot_and_stem_leaf() -> None:
    rng = np.random.default_rng(5)
    large = _konu03(list(rng.integers(100, 999, 400)), label="Tutar")
    assert not _ops(large, 6, DotPlot) and "en çok 300 gözlem" in large.step(6).explanation
    assert not large.step(10).operations and "en çok 300 gözlem" in large.step(10).explanation
    negative = _konu03([-3.5, -1.2, 0.4, 2.8, 1.1, -0.6, 3.9, 2.2, -2.7, 0.9, 1.6], label="Büyüme")
    assert not negative.step(10).operations and "negatif" in negative.step(10).explanation
    assert run_lab(negative).all_passed and "(−" in negative.step(2).explanation


def test_konu03_identical_values_are_rejected() -> None:
    with pytest.raises(K.UploadError, match="bütün değerler aynı"):
        _konu03([5] * 12)


# --- Konu 4: alternatif örnek ------------------------------------------------------------------

def test_konu04_alternative_matches_a_direct_calculation() -> None:
    values = _values(O4.alternative())
    rent = np.array([row[0] for row in O4.ALT_ROWS], dtype=float)
    rooms = [row[1] for row in O4.ALT_ROWS]
    assert values["Değerlerin toplamı"] == pytest.approx(rent.sum()) == pytest.approx(383.5)
    assert values["Ortalama"] == pytest.approx(rent.mean())
    outlier = rent.max() + 3 * (rent.max() - rent.min())
    assert values["Yeni en büyük değer"] == outlier == 123
    assert values["Uç değerli ortalama"] == pytest.approx((rent.sum() - rent.max() + outlier) / 15)
    means = pd.Series(rent).groupby(rooms).mean()
    sizes = pd.Series(rent).groupby(rooms).size()
    for room in ("1+1", "2+1", "3+1"):
        assert values[f"{room}: grup ortalaması"] == pytest.approx(means[room])
        assert values[f"{room}: katkı wⱼ x̄ⱼ"] == pytest.approx(sizes[room] / 15 * means[room])
    assert values["Ağırlıklı ortalama"] == pytest.approx(rent.mean())
    assert values["Grup ortalamalarının basit ortalaması"] == pytest.approx(means.mean())
    assert values["Medyan"] == 25 and values["Uç değerli medyan"] == 25
    assert values["Mod"] == 25 and values["En yüksek frekans"] == 3
    assert values["Konum L₆₀"] == pytest.approx(9.6) and values["60. yüzdelik P₆₀"] == pytest.approx(26.2)
    assert values["Birinci çeyrek Q₁"] == 20 and values["Üçüncü çeyrek Q₃"] == 30
    assert np.percentile(rent, 60, method="weibull") == pytest.approx(26.2)
    rates = np.array([45, 30, 18, 12], dtype=float)
    product = np.prod(1 + rates / 100)
    assert values["Yüzde değişimlerin aritmetik ortalaması"] == pytest.approx(26.25)
    assert values["100 birimin dönem sonundaki değeri"] == pytest.approx(100 * product)
    assert values["Geometrik ortalama G"] == pytest.approx(product ** 0.25)
    assert values["Ortalama bileşik büyüme (%)"] == pytest.approx(100 * (product ** 0.25 - 1))
    assert values["Türetilen set: ortalama"] == pytest.approx(rent.mean())
    assert values["Türetilen set: medyan"] == pytest.approx(rent.mean() + 0.5 * (25 - rent.mean()))


def test_konu04_outlier_rule_reproduces_the_notes() -> None:
    sales = np.array(SALES, dtype=float)
    assert sales.max() + O4.OUTLIER * (sales.max() - sales.min()) == 56


@pytest.mark.parametrize("values, expected, kind", [
    ([3, 4, 4, 5, 6, 7], "Mod 4.", "mode"),
    ([2, 2, 3, 4, 4, 5], "iki modludur", "count"),
    ([1, 1, 2, 2, 3, 3, 4, 5], "çok modludur (3 mod)", "count"),
    ([10, 11, 12, 13, 14], "ayırt edici bir mod yoktur", None),
    ([1, 1, 2, 2, 3, 3], "ayırt edici bir mod yoktur", None),
])
def test_konu04_mode_cases_follow_the_notes(values, expected, kind) -> None:
    spec = _konu04(pd.DataFrame({"x": values}), {"sayisal": "x"})
    assert expected in spec.step(6).explanation
    names = [getattr(op, "stat", None) for op in spec.step(6).operations]
    assert ("mode" in names) == (kind == "mode")
    assert bool(_ops(spec, 6, Count)) == (kind == "count")
    assert run_lab(spec).all_passed


def test_konu04_group_weights_handle_blanks_and_missing_roles() -> None:
    frame = pd.DataFrame({"Puan": [55, 61, 72, 80, 47, 66, 90, 58], "Bölüm": ["A", "A", "B", None, "B", "A", "B", "C"]})
    spec = _konu04(frame, {"sayisal": "Puan", "grup": "Bölüm"})
    assert _ops(spec, 3, CompleteCases) and "1 gözlemde grup sütunu boş" in spec.step(3).takeaway
    summary = _ops(spec, 3, GroupSummary)[0]
    assert summary.as_frame and summary.order == ("A", "B", "C")
    complete = frame.dropna()
    assert _values(spec)["Ağırlıklı ortalama"] == pytest.approx(complete["Puan"].mean())
    alone = _konu04(frame[["Puan"]], {"sayisal": "Puan"})
    assert not alone.step(3).operations and "Grup sütunu" in alone.step(3).explanation
    assert not alone.step(9).operations and "Yüzde değişim" in alone.step(9).explanation


def test_konu04_growth_column_is_checked() -> None:
    frame = pd.DataFrame({"x": [3, 5, 8, 9, 12], "r": [10, -120, None, None, None]})
    blocked = _konu04(frame, {"sayisal": "x", "buyume": "r"})
    assert not blocked.step(9).operations and "−100" in blocked.step(9).explanation
    single = _konu04(pd.DataFrame({"x": [3, 5, 8, 9, 12], "r": [10, None, None, None, None]}),
                     {"sayisal": "x", "buyume": "r"})
    assert "en az iki dönemin" in single.step(9).explanation
    fine = _konu04(pd.DataFrame({"x": [3, 5, 8, 9, 12], "r": [10, -10, None, None, None]}),
                   {"sayisal": "x", "buyume": "r"})
    values = _values(fine)
    assert values["100 birimin dönem sonundaki değeri"] == pytest.approx(99)
    assert values["Ortalama bileşik büyüme (%)"] == pytest.approx(100 * (math.sqrt(0.99) - 1))


def test_konu04_large_data_uses_histograms_and_even_n_median() -> None:
    rng = np.random.default_rng(11)
    spec = _konu04(pd.DataFrame({"Gelir": rng.integers(1000, 9000, 500)}), {"sayisal": "Gelir"})
    for number in (1, 2, 5, 8, 10):
        assert not _ops(spec, number, DotPlot) and _ops(spec, number, Histogram)
    assert "çift olduğu için" in spec.step(4).explanation and "Sıralı veri" not in spec.step(4).explanation
    assert run_lab(spec).all_passed


def test_konu04_derived_names_do_not_overwrite_file_columns() -> None:
    frame = pd.DataFrame({"n": [3, 5, 8, 9, 12, 7], "katki": ["a", "a", "b", "b", "b", "a"],
                          "n dar": [10, -5, 4, None, None, None]})
    table = K.UploadedTable("veri.csv", "csv", frame)
    case, _ = custom_case(O4.CUSTOM, table, CustomChoices(roles={"sayisal": "n", "grup": "katki", "buyume": "n dar"}))
    names = O4.group_names(case)
    assert names["n"] == "n_2" and names["katki"] == "katki_2"
    spec = O4.build(case)
    derived = [op.name for op in spec.step(10).operations if type(op).__name__ == "Derive"]
    assert derived == ["n_dar_2"]
    assert dict(spec.labels)["n"] == "n" and dict(spec.labels)["n_2"] == "Gözlem sayısı nⱼ"
    assert run_lab(spec).all_passed


# --- Metin kuralları ---------------------------------------------------------------------------

NASTY = ("Fiyat ($)", "a|b", "x_y", "*yıldız*", "<b>", "Grup [A]")


def _nasty_specs() -> list:
    rng = np.random.default_rng(4)
    frame = pd.DataFrame({"Puan $x$": rng.integers(20, 99, 60), "Grup [A]": rng.choice(["Merkez $", "a|b", "x_y"], 60),
                          "Artış *%*": [12.5, -3.0, 8.25, 4.0] + [None] * 56})
    table = K.UploadedTable("nasty.csv", "csv", frame)
    third = custom_case(O3.CUSTOM, table, CustomChoices(roles={"sayisal": "Puan $x$"}))[0]
    fourth = custom_case(O4.CUSTOM, table, CustomChoices(roles={"sayisal": "Puan $x$", "grup": "Grup [A]",
                                                                "buyume": "Artış *%*"}))[0]
    return [O3.build(third), O4.build(fourth)]


def _all_specs() -> list:
    decimals = _konu03([2.37, 2.15, 3.98, 1.85, 3.02, 2.66, 3.41, 2.95, 3.5, 2.2, 1.9, 3.75], label="Not ortalaması")
    negative = _konu04(pd.DataFrame({"x": [-3.5, -1.2, 0.4, 2.8, 1.1, -0.6]}), {"sayisal": "x"})
    return [O3.alternative(), O4.alternative(), decimals, negative, *_nasty_specs()]


@pytest.mark.parametrize("spec", _all_specs(), ids=["konu03-alternatif", "konu04-alternatif", "konu03-ondalik",
                                                    "konu04-negatif", "konu03-isaretler", "konu04-isaretler"])
def test_texts_attach_no_suffix_to_numbers_and_do_not_start_like_a_list(spec) -> None:
    for text in _texts(spec):
        found = set(re.findall(r"\S*\d[\)\]]*['’][a-zçğıöşü]+", text))
        assert found <= ALLOWED_SUFFIXES, found
        for line in text.splitlines():
            assert not re.match(r"\s*\d+\.\s", line), line
    assert run_lab(spec).all_passed


@pytest.mark.parametrize("spec", _nasty_specs(), ids=["konu03", "konu04"])
def test_user_labels_cannot_break_markdown_or_math(spec) -> None:
    for text in _texts(spec):
        dollars = re.findall(r"(?<!\\)\$", text)
        assert len(dollars) % 2 == 0, text
        for segment in re.findall(r"(?<!\\)\$(.*?)(?<!\\)\$", text):
            assert not any(word in segment for word in ("Puan", "Merkez", "Grup", "Artış")), segment
        for label in NASTY:
            assert label not in text, (label, text)


# --- Bağımsız inceleme bulguları: büyüklük, kesinlik ve metin -----------------------------------

def test_konu03_long_decimals_and_large_values_keep_every_digit() -> None:
    assert O3.data_decimals(pd.Series([1234.567891, 1000.000001])) == 6
    assert O3.data_decimals(pd.Series([12345.678901, 2.5])) == 6
    spec = _konu03([150000000.1, 210000000.2, 260000000.1, 330000000.3, 410000000.2, 480000000.1, 520000000.4,
                    600000000.2, 710000000.3, 850000000.1])
    assert "(850000000{,}1 - 150000000{,}1)/5 = 700000000/5 = 140000000$" in spec.step(2).explanation
    assert "480000000,1 değeri böyle gösterilir" in spec.step(10).explanation
    assert run_lab(spec).all_passed


def test_konu03_texts_have_no_float_noise_and_use_the_typographic_minus() -> None:
    assert "= 0{,}075$" in _konu03([0.01, 0.06, 0.07, 0.08, 0.12, 0.13, 0.15, 0.18, 0.2, 0.22]).step(5).explanation
    assert "= 0{,}0003$" in _konu03([0.0001 * index for index in range(1, 11)]).step(5).explanation
    for values in ([-12, -7, -9, -3, 1, 4, -11, -8, -6, -2], [-3.5, -1.2, 0.4, 2.8, 1.1, -0.6, 0.9, -2.2, 3.3, 1.7]):
        for text in _texts(_konu03(values)):
            assert not re.search(r"(?<![\w{])-\d", text or ""), text
    assert "$−10 \\leq x < −5$ sınıfı için $m = (−10 + (−5))/2 = −7{,}5$" in \
        _konu03([-12, -7, -9, -3, 1, 4, -11, -8, -6, -2]).step(5).explanation


def test_konu03_width_sentences_follow_the_rule() -> None:
    forced = _konu03([1] * 5 + [2] * 5)
    assert "1 biriminde olduğu için 0,2 genişliğindeki" in forced.step(2).takeaway
    assert "kullanılabilir" not in forced.step(2).takeaway
    likert = _konu03([1, 1, 2, 2, 3, 3, 4, 4, 5, 5])  # yaklaşık genişlik 0,8 < birim 1 = kolay genişlik
    assert "1 biriminde olduğu için 0,8 genişliğindeki" in likert.step(2).takeaway
    assert "kullanılabilir" not in likert.step(2).takeaway and "dar sınıf kullanılmaz" in likert.step(8).explanation
    assert "payı yaklaşık %91,7" in _konu03(list(range(1, 12)) + [30]).step(9).takeaway
    easy = _konu03([0, 10, 20, 25, 30, 35, 40, 45, 50, 12], k=5)
    assert "zaten kolay okunan bir değerdir" in easy.step(2).takeaway
    rounded = O3.alternative()
    assert "Yaklaşık 8,71 genişliğindeki sınıflar da kullanılabilir" in rounded.step(2).takeaway
    assert "\\approx 8{,}71$" in rounded.step(2).explanation
    ties = _konu03([1, 1, 2, 2, 3, 3, 4, 4, 5, 5])
    assert "1, 2 ve 3 (her biri 2 gözlem); aynı sıklıkta 2 değer daha var" in ties.step(6).explanation


def test_konu03_unwritable_class_labels_are_reported_for_the_chosen_count() -> None:
    values = [0, 1e9, 2e9, 3e9, 4e9, 5e9, 6e9, 7e9, 8e9, 8.9e9]
    with pytest.raises(K.UploadError, match="Şu sınıf sayılarından birini seçin: 18, 19 ve 20"):
        _konu03(values)  # önerilen k = 5: h = 2·10⁹, sınırlar 10¹⁰'a ulaşır
    assert run_lab(_konu03(values, k=18)).all_passed


@pytest.mark.parametrize("values, message", [
    ([0.000012, 0.000034, 0.000021, 0.000045, 0.000018, 0.00003, 0.000027, 0.000039, 0.000016, 0.000041],
     "Değerleri 100000 ile çarpın"),
    ([1234567.0001234, 1234567.0002345, 1234567.0003456, 1234567.0004567, 1234567.0005678, 1234567.0006789,
      1234567.0001111, 1234567.0002222, 1234567.0003333, 1234567.0004444], "Değerlerden ortak bir sayı çıkarın"),
])
def test_konu03_data_that_no_class_count_can_label_is_rejected_before_the_slider(values, message) -> None:
    table = K.UploadedTable("veri.csv", "csv", pd.DataFrame({"Değer": values}))
    with pytest.raises(K.UploadError, match=message):
        custom_case(O3.CUSTOM, table, CustomChoices(roles={"sayisal": "Değer"}))  # validate: k'dan bağımsız


def test_konu03_generated_code_prints_class_limits_without_exponents() -> None:
    from core.codegen.base import render_script
    from core.labs.registry import get_lab

    spec = _konu03([0.0001 * index for index in range(1, 11)])
    assert _ops(spec, 3, ClassTable)[0].width == pytest.approx(0.0002)
    assert 'print(frekans_dagilimi.round(5).to_string(float_format=lambda deger: f"{deger:.5f}"' in \
        render_script(spec, "Python")
    assert ("print(format(round(frekans_dagilimi, 5), digits = 15, scientific = FALSE, drop0trailing = TRUE))"
            in render_script(spec, "R"))
    notes = get_lab("konu03")  # notlardaki kod değişmez
    assert "print(frekans_dagilimi.round(3))" in render_script(notes, "Python")
    assert "print(round(frekans_dagilimi, 3))" in render_script(notes, "R")


def test_the_check_tolerance_catches_the_wrong_percentile_rule(tmp_path) -> None:
    """Uygulamayla karşılaştırma göreli 10⁻¹² düzeyindedir: yazılımın varsayılan yüzdelik kuralı (tip 7) büyük
    değerlerde de yakalanır (10⁹ ölçeğinde fark 0,2)."""

    import subprocess
    import sys

    from core.codegen.base import render_script

    data = ("x\n" + "\n".join(str(1000000000 + value) for value in range(11)) + "\n").encode("utf-8")
    case, _ = custom_case(O4.CUSTOM, K.read_upload("veri.csv", data), CustomChoices(roles={"sayisal": "x"}))
    spec = O4.build(case)
    (tmp_path / "veri.csv").write_bytes(data)
    script = render_script(spec, "Python")
    assert "1e-12 * abs(beklenen)" in script and "1e-12 * abs(beklenen)" in render_script(spec, "R")
    marker = "def yuzdelik("
    assert marker in script
    wrong = script.replace(marker, "def yuzdelik(degerler, p):\n    return float(np.percentile(degerler, p))\n\n\n"
                                   "def _ders_yuzdeligi(", 1)
    path = tmp_path / "yanlis_kural.py"
    path.write_text(wrong, encoding="utf-8")
    result = subprocess.run([sys.executable, path.name], cwd=tmp_path, capture_output=True, encoding="utf-8",
                            errors="replace", env={**__import__("os").environ, "MPLBACKEND": "Agg"}, timeout=300)
    assert result.returncode != 0 and "HATA 60. yüzdelik" in result.stdout


def test_konu04_exact_equalities_hold_for_large_values() -> None:
    spec = _konu04(pd.DataFrame({"x": [500000000.5, 510000000.25, 520000000.75, 530000000.5, 540000000.5]}),
                   {"sayisal": "x"})
    assert "= 2600000002{,}5/5 = 520000000{,}5$" in spec.step(1).explanation
    assert "gözlemler arasında yoktur" in spec.step(1).takeaway
    assert "verinin 3. değeridir: $520000000{,}75$" in spec.step(4).explanation
    assert "türetilen sette 520000000,625" in spec.step(10).explanation
    rounded = _konu04(pd.DataFrame({"x": [10000000, 10000000, 10000000, 10000001, 10000001, 10000000]}),
                      {"sayisal": "x"})
    assert "60000002/6 \\approx 10000000{,}33$" in rounded.step(1).explanation
    assert "60000005/6 \\approx 10000000{,}83$" in rounded.step(2).explanation
    assert "Ortalama yaklaşık 10000000,33;" in rounded.step(1).takeaway


def test_more_than_six_decimals_are_written_exactly() -> None:
    assert O3.data_decimals(pd.Series([0.1000001, 0.3000001])) == 7
    assert O3.data_decimals(pd.Series([1e-11, 6e-11])) == 11
    assert O3.data_decimals(pd.Series([0.1 + 0.2, 0.5])) == 1  # kayan nokta gürültüsü basamak saymaz
    spec = _konu04(pd.DataFrame({"x": [0.1000001, 0.3000001, 0.2000001, 0.2000001, 0.2000001]}), {"sayisal": "x"})
    assert "0{,}1000001 + 0{,}3000001" in spec.step(1).explanation and "= 1{,}0000005/5 = 0{,}2000001$" in \
        spec.step(1).explanation
    tiny = _konu04(pd.DataFrame({"x": [0.0000012, 0.0000034, 0.0000021, 0.0000045, 0.0000018]}), {"sayisal": "x"})
    assert "\\boxed{0{,}0000021}" in tiny.step(4).explanation
    smaller = _konu04(pd.DataFrame({"x": [1e-11, 2e-11, 3e-11, 4e-11, 6e-11]}), {"sayisal": "x"})
    assert "(0{,}00000000001 + 0{,}00000000002" in smaller.step(1).explanation
    modes = _konu04(pd.DataFrame({"x": [0.1000001, 0.1000001, 0.3000007, 0.3000007, 0.2, -0.5]}), {"sayisal": "x"})
    assert "0,1000001 ve 0,3000007 değerlerinin her biri 2 kez" in modes.step(6).explanation
    noise = _konu04(pd.DataFrame({"x": [0.1 + 0.2, 0.5, 0.7, 0.9, 1.1]}), {"sayisal": "x"})
    assert "(0{,}3 + 0{,}5 + 0{,}7 + 0{,}9 + 1{,}1)/5 = 3{,}5/5 = 0{,}7$" in noise.step(1).explanation
    assert all(run_lab(item).all_passed for item in (spec, tiny, smaller, modes, noise))


def test_konu04_tiny_values_keep_three_significant_digits() -> None:
    spec = _konu04(pd.DataFrame({"x": [0.000012, 0.000034, 0.000021, 0.000045, 0.000018]}), {"sayisal": "x"})
    assert "Ortalama 0,000026;" in spec.step(1).takeaway
    assert "değeridir: $0{,}000021$" in spec.step(4).explanation
    assert "P₆₀ = 0,0000288" in spec.step(7).takeaway
    assert "Q₁ ile Q₂ arası 0,000006, Q₂ ile Q₃ arası 0,0000185" in spec.step(8).takeaway
    mean = next(check for check in spec.step(1).checks if check.label == "Ortalama")
    assert mean.decimals >= 7 and mean.expected == pytest.approx(0.000026)
    six = _konu04(pd.DataFrame({"x": [0.123456, 0.234567, 0.345678, 0.456789, 0.567891]}), {"sayisal": "x"})
    assert "değeridir: $0{,}345678$" in six.step(4).explanation


def test_konu04_rounded_values_are_marked_and_shown_the_same_everywhere() -> None:
    even = _konu04(pd.DataFrame({"x": [0.1234, 0.2345, 0.3456, 0.4567, 0.5678, 0.0123]}), {"sayisal": "x"})
    assert "/2 = 0{,}29005$" in even.step(4).explanation and "P₆₀ = 0,36782" in even.step(7).takeaway
    alternative = O4.alternative()
    assert "Ortalama yaklaşık 25,57;" in alternative.step(1).takeaway
    assert "yaklaşık 249,12 olur" in alternative.step(9).takeaway
    x = [5, 89, 66, 58, 25, 47, 19, 77, 47, 4, 26, 70, 52, 38, 26, 9, 61, 66, 52, 93,
         92, 21, 61, 63, 25, 30, 49, 74, 29, 72, 65, 22, 39, 83, 84, 66, 1, 68, 23, 82]
    spec = _konu04(pd.DataFrame({"x": x, "g": [f"G{index % 10}" for index in range(40)]}),
                   {"sayisal": "x", "grup": "g"})
    assert "1979/40 = 49{,}475$" in spec.step(1).explanation  # tam yarım: bir basamak daha, "=" ile
    assert "Ağırlıklı ortalama (49,475) Adım 1'deki ortalamaya eşittir" in spec.step(3).takeaway
    assert {check.decimals for check in spec.step(1).checks if check.label == "Ortalama"} == {3}


def test_konu04_growth_uses_its_own_filled_cells() -> None:
    frame = pd.DataFrame({"Kira": [20, 25, 22, 30, 28, None, None, None], "Artış": [45, 30, 18, 12, 9, 7, 5, 3]})
    table = K.UploadedTable("veri.csv", "csv", frame)
    case, notes = custom_case(O4.CUSTOM, table, CustomChoices(roles={"sayisal": "Kira", "buyume": "Artış"}))
    assert len(case.data) == 5 and len(notes) == 1 and "“Kira”" in notes[0] and "Artış" not in notes[0]
    spec = O4.build(case)
    values = _values(spec)
    rates = np.array([45, 30, 18, 12, 9, 7, 5, 3], dtype=float)
    assert values["Yüzde değişimlerin aritmetik ortalaması"] == pytest.approx(rates.mean())
    assert values["100 birimin dönem sonundaki değeri"] == pytest.approx(100 * np.prod(1 + rates / 100))
    assert "(8 dönem)" in spec.step(9).explanation
    read = spec.step(9).operations[0]
    assert isinstance(read, ReadFile) and read.frame == "veri_buyume" and read.dropped == 0 and len(read.rows) == 8
    with pytest.raises(K.UploadError, match="dolu hücre yok"):
        custom_case(O4.CUSTOM, K.UploadedTable("v.csv", "csv", pd.DataFrame({"x": [1, 2, 3, 4, 5], "r": [None] * 5})),
                    CustomChoices(roles={"sayisal": "x", "buyume": "r"}))


def test_konu04_extreme_magnitudes_build_and_axes_cover_the_data() -> None:
    close = [999000000000000, 999000000000001, 999000000000000, 999000000000001, 999000000000000]
    with pytest.raises(K.UploadError, match="birbirine çok yakın"):
        _konu04(pd.DataFrame({"x": close}), {"sayisal": "x"})
    lower, upper = O4._axis(999000000000000.0, 999000000000001.0)
    assert lower < 999000000000000.0 and upper > 999000000000001.0
    values = [999000000000000 + step * 1000003 for step in (0, 4, 1, 9, 6)]
    spec = _konu04(pd.DataFrame({"x": values}), {"sayisal": "x"})
    assert run_lab(spec).all_passed
    assert "4995000020000060/5 = 999000004000012$" in spec.step(1).explanation


def test_konu04_sentences_for_many_modes_short_series_and_large_data() -> None:
    modes = _konu04(pd.DataFrame({"x": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9]}), {"sayisal": "x"})
    assert "1, 2, 3, 4, 5 ve diğer 3 değerin her biri 2 kez gözlenir. Veri çok modludur (8 mod)." in \
        modes.step(6).explanation
    two = _konu04(pd.DataFrame({"x": [3, 5, 8, 9, 12], "r": [10, -10, None, None, None]}),
                  {"sayisal": "x", "buyume": "r"})
    assert "$100 \\times g_1 g_2$" in two.step(9).explanation and "\\cdots" not in two.step(9).explanation
    assert "%10 ve %−10" in two.step(9).explanation and "aritmetik ortalaması %0," in two.step(9).takeaway
    rng = np.random.default_rng(3)
    large = _konu04(pd.DataFrame({"x": rng.integers(10, 99, 320)}), {"sayisal": "x"})
    assert "Histogramda ortalama" in large.step(1).explanation
    histogram = _ops(large, 1, Histogram)[0]
    assert histogram.hover_unit == "gözlem" and Histogram.__dataclass_fields__["hover_unit"].default == "tekrar"
    frame = pd.DataFrame({"Puan": [55, 61, 72, 80, 47, 66, 90, 58], "Bölüm": ["A", "A", "B", None, "B", "A", "B", "C"]})
    blanks = _konu04(frame, {"sayisal": "Puan", "grup": "Bölüm"})
    assert "bu gözlemlerin ortalaması geri gelir" in blanks.step(3).takeaway


@pytest.mark.parametrize("seed", range(6))
def test_konu04_own_data_matches_an_independent_calculation(seed: int) -> None:
    rng = np.random.default_rng(seed)
    n = int(rng.integers(5, 60))
    x = np.round(rng.normal(50, 15, n), int(rng.integers(0, 3)))
    groups = rng.choice(["a", "b", "c"], n).astype(object)
    groups[rng.random(n) < 0.15] = None
    spec = _konu04(pd.DataFrame({"x": x, "g": groups}), {"sayisal": "x", "grup": "g"})
    values = _values(spec)
    outlier = x.max() + 3 * (x.max() - x.min())
    replaced = x.copy()
    replaced[np.argmax(x)] = outlier
    expected = {
        "Ortalama": x.mean(), "Uç değerli ortalama": replaced.mean(), "Medyan": np.median(x),
        "Uç değerli medyan": np.median(replaced), "60. yüzdelik P₆₀": np.percentile(x, 60, method="weibull"),
        "Birinci çeyrek Q₁": np.percentile(x, 25, method="weibull"),
        "Üçüncü çeyrek Q₃": np.percentile(x, 75, method="weibull"),
        "Türetilen set: medyan": x.mean() + 0.5 * (np.median(x) - x.mean()),
        "En yüksek frekans": pd.Series(x).value_counts().max(),
        "Ağırlıklı ortalama": x[pd.notna(groups)].mean(),
    }
    for label, value in expected.items():
        assert values[label] == pytest.approx(value, rel=1e-12, abs=1e-12), label


def test_ui_number_formats_for_small_and_large_values() -> None:
    from topics import lab_ui

    assert lab_ui._midpoint(0.0125) == "0,0125" and lab_ui._midpoint(12.5) == "12,50" and lab_ui._midpoint(15.0) == "15"
    assert lab_ui._value_text(878768219800000.0) == "878768219800000" and lab_ui._value_text(2e-05) == "0,00002"
    assert lab_ui._value_text(0.1 + 0.2) == "0,3" and lab_ui._value_text(-56.0) == "−56"
    tiny = pd.Series([0.000026, 0.0000458])
    assert lab_ui._decimals(tiny) == 4 and lab_ui._decimals(tiny, small=True) == 7
    assert lab_ui._decimals(pd.Series([0.123456, 0.5]), small=True) == 6
    assert lab_ui._decimals(pd.Series([0.000056, 0.000078]), small=True) == 6
    assert lab_ui._decimals(pd.Series([25 + 1 / 3, 18.5]), small=True) == 4  # bölmeyle bulunan uzun değer
    assert lab_ui._decimals(pd.Series([17.5, 25.0]), small=True) == 2 == lab_ui._decimals(pd.Series([17.5, 25.0]))
    assert not lab_ui._whole(pd.Series([1e-11, 2e-11]), small=True) and lab_ui._whole(pd.Series([1e-11, 2e-11]))
    assert lab_ui._midpoint(1234567.0025) == "1234567,0025" and lab_ui._value_text(6e-11) == "0,00000000006"


def _rule_classes(values: list[float], k: int) -> tuple[Decimal, list[Decimal]]:
    """Notlardaki sınıf kuralının motordan bağımsız yazımı: kolay genişlik, h katı alt sınır, en büyüğü kapsayan
    sınıflar."""

    exact = [Decimal(repr(float(value))) for value in values]
    places = max(max(0, -value.normalize().as_tuple().exponent) for value in exact)
    unit = Decimal(1).scaleb(-places)
    raw = (max(exact) - min(exact)) / k
    easy = sorted(factor * Decimal(10) ** power for factor in (Decimal(1), Decimal(2), Decimal("2.5"), Decimal(5))
                  for power in range(-8, 12))
    width = max(next(item for item in easy if item >= raw), unit)
    lower = (min(exact) / width).to_integral_value(rounding="ROUND_FLOOR") * width
    count = int(((max(exact) - lower) / width).to_integral_value(rounding="ROUND_FLOOR")) + 1
    return width, [lower + index * width for index in range(count + 1)]


@pytest.mark.parametrize("seed", range(6))
def test_konu03_own_data_matches_an_independent_class_rule(seed: int) -> None:
    rng = np.random.default_rng(100 + seed)
    n = int(rng.integers(10, 120))
    values = list(np.round(rng.gamma(3, 7, n) - rng.integers(0, 10), int(rng.integers(0, 3))))
    k = int(rng.integers(5, 21))
    width, edges = _rule_classes(values, k)
    spec = _konu03(values, k=k)
    table = _ops(spec, 3, ClassTable)[0]
    assert Decimal(repr(table.width)) == width and Decimal(repr(table.lower)) == edges[0]
    exact = [Decimal(repr(float(value))) for value in values]
    expected = [sum(1 for value in exact if a <= value < b) for a, b in zip(edges[:-1], edges[1:])]
    frequencies = [check.expected for check in spec.step(3).checks if check.label.startswith("Frekans: ")]
    assert frequencies == expected and sum(expected) == n
    midpoints = [check.expected for check in spec.step(5).checks if check.label.startswith("Orta nokta: ")]
    assert midpoints == pytest.approx([float((a + b) / 2) for a, b in zip(edges[:-1], edges[1:])], abs=1e-12)
