"""Konu 1–2 alternatif örnekleri: değerler motordan bağımsız bir hesapla doğrulanır; metin kuralları denetlenir."""

from __future__ import annotations

import re
from collections import Counter

import pandas as pd
import pytest

from core.labs import kendi_veri as K
from core.labs import ornek_konu01 as O1
from core.labs import ornek_konu02 as O2
from core.labs.ornek import CustomChoices, custom_case, default_pick

ALLOWED_SUFFIXES = {"%100'e", "1'in", "0'dan", "3'teki", "4'te"}
"""Metinlerde rakamdan sonra gelen ekler yalnız sabit ifadelerde olabilir (değişken sayılara ek getirilmez)."""


def _values(spec) -> dict[str, float]:
    return {check.label: check.expected for step in spec.steps for check in step.checks}


def _texts(spec) -> list[str]:
    return [text for step in spec.steps for text in (step.explanation, step.takeaway)]


# --- Konu 2 ---------------------------------------------------------------------------------

def test_konu02_frequencies_and_shares_match_a_direct_count() -> None:
    values = _values(O2.alternative())
    counts = Counter(row[0] for row in O2.ALT_ROWS)
    assert dict(counts) == {"Kredi kartı": 32, "Banka kartı": 25, "Nakit": 18, "Mobil ödeme": 15, "Yemek kartı": 10}
    for category, count in counts.items():
        assert values[f"{category} frekansı"] == count
        assert values[f"{category} göreli frekansı"] == pytest.approx(count / 100)
        assert values[f"{category} yüzde frekansı"] == pytest.approx(count)
    assert values["Kredi kartı dilim açısı (derece)"] == pytest.approx(360 * 0.32)
    assert values["Fark (yüzde puan)"] == pytest.approx(7)
    assert values["Göreli fark (%)"] == pytest.approx(28)


def test_konu02_crosstab_and_denominators_match_a_direct_count() -> None:
    values = _values(O2.alternative())
    cells = Counter((row[1], row[0]) for row in O2.ALT_ROWS)
    assert values["Merkez ∩ Kredi kartı"] == cells[("Merkez", "Kredi kartı")] == 20
    assert values["Merkez satır toplamı"] == 60 and values["Sahil satır toplamı"] == 40
    assert values["Merkez: Kredi kartı (satır %)"] == pytest.approx(100 * 20 / 60)
    assert values["Kredi kartı içinde Merkez (sütun %)"] == pytest.approx(100 * 20 / 32)
    assert values["Kredi kartı içinde Sahil (sütun %)"] == pytest.approx(100 * 12 / 32)


def test_konu02_alternative_contains_a_simpson_reversal() -> None:
    frame = pd.DataFrame(list(O2.ALT_ROWS), columns=list(O2.ALT_COLUMNS))
    happy = frame["memnuniyet"] == "Memnun"
    rates = 100 * happy.groupby([frame["siparis_turu"], frame["sube"]]).mean()
    overall = 100 * happy.groupby(frame["sube"]).mean()
    assert rates["Masada", "Sahil"] > rates["Masada", "Merkez"]
    assert rates["Paket", "Sahil"] > rates["Paket", "Merkez"]
    assert overall["Merkez"] > overall["Sahil"]
    values = _values(O2.alternative())
    assert values["Masada: Merkez (%)"] == pytest.approx(90) and values["Masada: Sahil (%)"] == pytest.approx(95)
    assert values["Paket: Merkez (%)"] == pytest.approx(50) and values["Paket: Sahil (%)"] == pytest.approx(55)
    assert values["Tüm gruplarda Merkez (%)"] == pytest.approx(overall["Merkez"])
    assert values["Tüm gruplarda Sahil (%)"] == pytest.approx(75)
    assert "Simpson paradoksudur" in O2.alternative().step(11).explanation


# --- Konu 2: kesilmiş eksen, Simpson metinleri, eşitlikler ------------------------------------

@pytest.mark.parametrize("larger, smaller", [(78, 72), (32, 25), (27, 20), (60, 1.5), (95, 94.5), (99.5, 40), (3, 1),
                                             (50.5, 50), (100 * 7 / 9, 100 * 2 / 9)])
def test_truncated_axis_starts_just_below_the_smaller_bar(larger: float, smaller: float) -> None:
    low, high = O2._truncated_axis(larger, smaller)
    assert 0 < low < smaller < larger < high
    assert (larger - low) / (smaller - low) > larger / smaller  # fark olduğundan büyük görünür
    assert O2._zero_axis(larger) > larger or O2._zero_axis(larger) == 100


def _konu02(rows: list[tuple], roles: dict, picks: dict | None = None, columns: tuple = ("Ana",)):
    table = K.UploadedTable("veri.csv", "csv", pd.DataFrame(rows, columns=list(columns)))
    return O2.build(custom_case(O2.CUSTOM, table, CustomChoices(roles=roles, picks=picks or {}))[0])


def test_konu02_step10_compares_the_top_category_with_the_next_smaller_one() -> None:
    rows = [("A",)] * 30 + [("B",)] * 30 + [("C",)] * 20 + [("D",)] * 20
    spec = _konu02(rows, {"ana": "Ana"})
    charts = [op for op in spec.step(10).operations if type(op).__name__ == "BarChart"]
    assert [chart.rows for chart in charts] == [("A", "C"), ("A", "C")]
    low, high = charts[0].y_range
    assert 0 < low < 20 and high > 30 and charts[1].y_range[0] == 0
    assert "Fark 10 **yüzde puandır**" in spec.step(10).explanation
    equal = _konu02([("A",)] * 10 + [("B",)] * 10, {"ana": "Ana"})
    assert not equal.step(10).operations and "frekansı eşit" in equal.step(10).explanation


def test_konu02_step12_names_every_most_common_category() -> None:
    spec = _konu02([("A",)] * 4 + [("B",)] * 4 + [("C",)] * 2, {"ana": "Ana"})
    assert "en yaygın: A ve B, her biri %40" in spec.step(12).takeaway
    assert "(her biri 2)" not in spec.step(2).takeaway and "en az gözlenen: C (2)" in spec.step(2).takeaway


@pytest.mark.parametrize("within, overall, expected", [
    ([5.0, 3.0], -2.0, "Bu, Simpson paradoksudur."),
    ([5.0, 3.0], 4.0, "yön değişmiyor"),
    ([5.0, 3.0], 0.0, "Gruplar birleştirilince oranlar eşit. Toplamdaki karşılaştırma alt gruplardaki yönü "
                      "göstermiyor"),
    ([0.0, 0.0], 4.0, "Her alt grupta iki seçeneğin oranı eşit. Gruplar birleştirilince daha yüksek oran: A. "
                      "Toplamdaki fark alt gruplardan değil"),
    ([0.0, 0.0], 0.0, "Her alt grupta iki seçeneğin oranı eşit. Gruplar birleştirilince oranlar eşit."),
    ([5.0, -3.0], 1.0, "Alt gruplarda yön aynı değil"),
    ([5.0, 0.0], -1.0, "Alt grupların bir kısmında A daha yüksek orana sahip; diğerlerinde oranlar eşit."),
    ([0.0, 30.0], 15.0, "Gruplar birleştirilince daha yüksek oran: A. Bu veride yön değişmiyor"),
    ([0.0, 30.0], -5.0, "Gruplar birleştirilince yön tersine dönüyor"),
])
def test_simpson_texts_cover_ties_and_mixed_directions(within, overall, expected) -> None:
    text = O2._simpson_text("A", "B", within, overall)
    assert expected in text
    assert ("Simpson paradoksudur" in text) == (expected == "Bu, Simpson paradoksudur.")


def test_konu02_simpson_takeaway_matches_the_composition() -> None:
    same = [("x", "A", "g1", "Evet")] * 6 + [("x", "A", "g1", "Hayır")] * 4 + [("y", "B", "g1", "Evet")] * 3
    same += [("y", "B", "g1", "Hayır")] * 7 + [("x", "A", "g2", "Evet")] * 2 + [("x", "A", "g2", "Hayır")] * 8
    same += [("y", "B", "g2", "Evet")] * 1 + [("y", "B", "g2", "Hayır")] * 9
    roles = {"ana": "Ana", "secenek": "Seçenek", "altgrup": "Grup", "sonuc": "Sonuç"}
    spec = _konu02(same, roles, {"sonuc": "Evet"}, columns=("Ana", "Seçenek", "Grup", "Sonuç"))
    assert "dağılımı aynı" in spec.step(11).takeaway and "eşit dağılmamıştır" not in spec.step(11).takeaway
    assert "yön değişmiyor" in spec.step(11).explanation


def test_konu02_custom_steps_explain_what_is_missing() -> None:
    table = K.read_upload("ornek.xlsx", K.sample_excel(O2.sample()))
    case, _ = custom_case(O2.CUSTOM, table, CustomChoices(roles={"ana": "Ödeme yöntemi"}))
    spec = O2.build(case)
    for number in (7, 8, 9, 11):
        assert not spec.step(number).operations
        assert "sütun seçin" in spec.step(number).explanation
    assert spec.step(12).operations and spec.step(10).checks


def test_konu02_simpson_step_reports_no_reversal_when_there_is_none() -> None:
    rows = [("A", "x", "Evet")] * 8 + [("A", "x", "Hayır")] * 2 + [("B", "x", "Evet")] * 5 + [("B", "x", "Hayır")] * 5
    rows += [("A", "y", "Evet")] * 6 + [("A", "y", "Hayır")] * 4 + [("B", "y", "Evet")] * 3 + [("B", "y", "Hayır")] * 7
    frame = pd.DataFrame(rows, columns=["Seçenek", "Grup", "Sonuç"])
    table = K.UploadedTable("veri.csv", "csv", frame)
    choices = CustomChoices(roles={"ana": "Grup", "secenek": "Seçenek", "altgrup": "Grup", "sonuc": "Sonuç"},
                            picks={"sonuc": "Evet"})
    spec = O2.build(custom_case(O2.CUSTOM, table, choices)[0])
    assert "yön değişmiyor" in spec.step(11).explanation


def test_konu02_close_shares_are_written_with_enough_decimals() -> None:
    rows = [("A",)] * 1801 + [("B",)] * 1800 + [("C",)] * 1399
    spec = _konu02(rows, {"ana": "Ana"})
    text = spec.step(10).explanation
    assert "(%36,02)" in text and "(%36)" in text and "Fark 0,02 **yüzde puandır**" in text
    assert "(36{,}02 - 36)/36" in text
    tiny = _konu02([("A",)] * 9999 + [("B",)], {"ana": "Ana"})
    assert "(%99,99)" in tiny.step(10).explanation and "(%0,01)" in tiny.step(10).explanation
    assert "/0 " not in tiny.step(10).explanation
    tie = _konu02([("A",)] * 5 + [("B",)] * 5 + [("C",)] * 2, {"ana": "Ana"})
    assert tie.step(10).explanation.startswith("En yaygın kategorilerden A")


@pytest.mark.parametrize("categories, expected", [
    (("0", "1"), "1"), (("Evet", "Hayır"), "Evet"), (("Hayır", "Evet"), "Evet"), (("Memnun", "Memnun değil"), "Memnun"),
    (("Memnun değil", "Memnun"), "Memnun"), (("Kaldı", "Geçti"), "Geçti"), (("A", "B"), "A"), (("VAR", "YOK"), "VAR"),
])
def test_default_pick_prefers_the_positive_category(categories, expected) -> None:
    assert default_pick(categories) == expected


# --- Konu 1 ---------------------------------------------------------------------------------

def test_konu01_values_match_the_table() -> None:
    values = _values(O1.alternative())
    revenue = [row[3] for row in O1.ALT_ROWS]
    reached = sum(row[4] == "Tuttu" for row in O1.ALT_ROWS)
    assert values["Gözlem sayısı n"] == 8 and values["Analitik değişken sayısı"] == 4
    assert values["x₁: 1. gözlemin değeri"] == revenue[0] and values["x₈: son gözlemin değeri"] == revenue[-1]
    assert values["Tuttu sayısı"] == reached == 3
    assert values["Tuttu oranı"] == pytest.approx(3 / 8)
    assert values["Günlük ciro (bin TL) toplamı"] == pytest.approx(sum(revenue))
    assert values["Günlük ciro (bin TL) ortalaması"] == pytest.approx(sum(revenue) / 8)
    assert all((row[3] >= 25) == (row[4] == "Tuttu") for row in O1.ALT_ROWS)  # hedef: 25 bin TL


def _konu01(frame: pd.DataFrame, roles: dict, extra=(), types=None, picks=None):
    table = K.UploadedTable("veri.csv", "csv", frame)
    choices = CustomChoices(roles=roles, extra=tuple(extra), types=types or {}, picks=picks or {})
    return custom_case(O1.CUSTOM, table, choices)[0]


def test_konu01_custom_types_follow_the_students_choice() -> None:
    table = K.read_upload("ornek.xlsx", K.sample_excel(O1.sample()))
    choices = CustomChoices(roles={"sayisal": "Personel sayısı", "kimlik": "Kafe"}, extra=("İlçe",),
                            types={"Personel sayısı": "Nicel: sürekli", "Kafe": "Kategorik: nominal"})
    case, _ = custom_case(O1.CUSTOM, table, choices)
    assert case.extra["types"]["personel_sayisi"] == O1.TYPE_CHOICES["Nicel: sürekli"]
    assert case.extra["types"]["kafe"] == O1.TYPE_CHOICES["Kimlik etiketi"]  # kimlik rolünün türü sabit
    assert case.extra["types"]["ilce"] == O1.TYPE_CHOICES["Kategorik: nominal"]
    spec = O1.build(case)
    assert spec.step(3).operations and not spec.step(5).operations
    assert "Nicel değişken | Personel sayısı" in spec.step(5).explanation
    with pytest.raises(K.UploadError, match="türü"):
        custom_case(O1.CUSTOM, table, CustomChoices(roles={"sayisal": "Personel sayısı"},
                                                    types={"Personel sayısı": "Kategorik: sıralı"}))


def test_konu01_identity_columns_are_counted_once() -> None:
    frame = pd.DataFrame({"No": [1, 2, 3, 4], "Ad": ["a", "b", "c", "d"], "Puan": [50, 60, 70, 80],
                          "Sınıf": ["1", "2", "2", "1"]})
    case = _konu01(frame, {"sayisal": "Puan", "kimlik": "Ad"}, extra=("No", "Sınıf"),
                   types={"No": "Kimlik etiketi", "Sınıf": "Kategorik: sıralı"})
    spec = O1.build(case)
    assert _values(spec)["Analitik değişken sayısı"] == 2
    assert "“Ad” ve “No” sütunları yalnızca kimlik etiketidir" in spec.step(1).explanation
    assert "| Ordinal değişken | Sınıf |" in spec.step(5).explanation
    assert "No" not in spec.step(5).explanation.split("| Değişken |")[1].split("\n")[0]


@pytest.mark.parametrize("values, message", [(["a", "b", "a", "c"], "tekrar eden"),
                                             (["a", None, "b", "c"], "boş hücre")])
def test_konu01_identity_column_must_be_unique_and_complete(values, message) -> None:
    frame = pd.DataFrame({"Ad": values, "Puan": [50, 60, 70, 80]})
    with pytest.raises(K.UploadError, match=message):
        _konu01(frame, {"sayisal": "Puan", "kimlik": "Ad"})


def test_konu01_time_column_makes_a_time_series() -> None:
    frame = pd.DataFrame({"Yıl": range(2001, 2051), "Gelir": [100 + index for index in range(50)]})
    spec = O1.build(_konu01(frame, {"sayisal": "Gelir", "zaman": "Yıl"}))
    kinds = [type(op).__name__ for op in spec.step(3).operations]
    assert kinds == ["LineChart"] and "zaman serisidir" in spec.step(3).explanation
    with pytest.raises(K.UploadError, match="artan sırada"):
        _konu01(frame.iloc[::-1].reset_index(drop=True), {"sayisal": "Gelir", "zaman": "Yıl"})


def test_konu01_many_observations_explain_the_missing_chart() -> None:
    frame = pd.DataFrame({"Gelir": [100 + index for index in range(50)]})
    spec = O1.build(_konu01(frame, {"sayisal": "Gelir"}))
    assert not spec.step(3).operations
    assert "40 değerinden büyük" in spec.step(3).explanation and spec.step(3).takeaway
    assert "yalnız yatay kesit gösterilir" not in spec.step(3).explanation


def test_konu01_derived_columns_do_not_overwrite_file_columns(tmp_path) -> None:
    frame = pd.DataFrame({"Puan": [55, 61, 72, 80, 47], "Durum": ["Geçti", "Geçti", "Geçti", "Geçti", "Kaldı"],
                          "Durum kod": [7, 8, 9, 5, 6], "Gözlem no": [101, 102, 103, 104, 105]})
    case = _konu01(frame, {"sayisal": "Puan", "ikili": "Durum"}, extra=("Durum kod", "Gözlem no"))
    spec = O1.build(case)
    code = next(op for op in spec.step(2).operations if type(op).__name__ == "MapCodes")
    assert code.name == "durum_kod_2"
    derived = next(op for op in spec.step(3).operations if type(op).__name__ == "Derive")
    assert derived.name == "gozlem_no_2"
    rows = next(op for op in spec.step(2).operations if type(op).__name__ == "VariableTypes").rows
    assert len({row[0] for row in rows}) == len(rows)


# --- Metin kuralları ---------------------------------------------------------------------------

NASTY = {
    "Fiyat ($)": ["1. sınıf", "*yıldız*", "a|b", "x_y", "Ç&Ş #1", "<b>", "50$ indirim"],
    "Grup [A]": ["Merkez $", "Sahil"],
}


def _nasty_specs() -> list:
    rng = __import__("numpy").random.default_rng(3)
    n = 120
    frame = pd.DataFrame({
        "Fiyat ($)": rng.choice(NASTY["Fiyat ($)"], n),
        "Grup [A]": rng.choice(NASTY["Grup [A]"], n),
        "Tasarım `x`": rng.choice(["A_1", "B*2"], n),
        "Kanal": rng.choice(["Web|1", "Mağaza~"], n),
        "Sonuç": rng.choice(["Evet", "Hayır"], n),
        "Puan $x$": rng.integers(10, 99, n),
    })
    table = K.UploadedTable("nasty.csv", "csv", frame)
    second = custom_case(O2.CUSTOM, table, CustomChoices(roles={
        "ana": "Fiyat ($)", "satir": "Grup [A]", "secenek": "Tasarım `x`", "altgrup": "Kanal", "sonuc": "Sonuç"}))[0]
    first = custom_case(O1.CUSTOM, table, CustomChoices(roles={"sayisal": "Puan $x$", "ikili": "Grup [A]"},
                                                        extra=("Fiyat ($)", "Kanal")))[0]
    return [O1.build(first), O2.build(second)]


def _custom_specs() -> list:
    first = custom_case(O1.CUSTOM, K.read_upload("a.xlsx", K.sample_excel(O1.sample())),
                        CustomChoices(roles={"sayisal": "Günlük ciro (bin TL)", "ikili": "Hedef durumu"}))[0]
    second = custom_case(O2.CUSTOM, K.read_upload("b.xlsx", K.sample_excel(O2.sample())),
                         CustomChoices(roles={"ana": "Ödeme yöntemi", "satir": "Şube", "secenek": "Şube",
                                              "altgrup": "Sipariş türü", "sonuc": "Memnuniyet"}))[0]
    return [O1.build(first), O2.build(second), *_nasty_specs()]


@pytest.mark.parametrize("spec", [O1.alternative(), O2.alternative(), *_custom_specs()],
                         ids=["konu01-alternatif", "konu02-alternatif", "konu01-kendi", "konu02-kendi",
                              "konu01-isaretler", "konu02-isaretler"])
def test_texts_attach_no_suffix_to_numbers_and_do_not_start_like_a_list(spec) -> None:
    for text in _texts(spec):
        found = set(re.findall(r"\S*\d[\)\]]*['’][a-zçğıöşü]+", text))
        assert found <= ALLOWED_SUFFIXES, found
        for line in text.splitlines():
            assert not re.match(r"\s*\d+\.\s", line), line  # Markdown numaralı liste sanmasın


@pytest.mark.parametrize("spec", _nasty_specs(), ids=["konu01", "konu02"])
def test_user_labels_cannot_break_markdown_or_math(spec) -> None:
    """Kullanıcının adları Markdown işaretleri kaçırılarak yazılır ve hiçbir zaman matematik ifadesine girmez."""

    labels = [label for values in NASTY.values() for label in values] + list(NASTY)
    for text in _texts(spec):
        dollars = re.findall(r"(?<!\\)\$", text)
        assert len(dollars) % 2 == 0, text
        for segment in re.findall(r"(?<!\\)\$(.*?)(?<!\\)\$", text):
            assert not any(word in segment for word in ("sınıf", "yıldız", "Merkez", "Fiyat", "indirim")), segment
        for label in labels:
            assert label not in text or not any(mark in label for mark in "*_|[]<>$#&`~"), (label, text)
        for line in text.splitlines():
            if line.startswith("| ") and not line.startswith("|---"):
                assert len(re.findall(r"(?<!\\)\|", line)) == 3, line
