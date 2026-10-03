"""Konu 5–6 alternatif örnekleri ve kendi verini yükle: değerler motordan bağımsız bir hesapla doğrulanır; iki grubun
karşılaştırması, sapmalar, Chebyshev payları, aykırı değer sınırları, kovaryans ve korelasyon; olaylar, sayma kuralları,
öğrencinin seçtiği değerler (kaydırıcılar) ve ortak olasılık tablosu ile metin kuralları denetlenir."""

from __future__ import annotations

import math
import re
from collections import Counter
from itertools import product

import numpy as np
import pandas as pd
import pytest

from core.codegen.base import render_step
from core.labs import kendi_veri as K
from core.labs import ornek_konu05 as O5
from core.labs import ornek_konu06 as O6
from core.labs.ornek import CustomChoices, custom_case
from core.labs.registry import get_lab
from core.labs.runner import run_lab
from core.labs.spec import BoxSummary, CompleteCases, DotPlot, Histogram, Selections, Subset

ALLOWED_SUFFIXES = {"%88,9'dan", "1'e", "0'dır", "1'dir", "8'de", "4'teki", "%50'ye", "0,25'lik"}
"""Rakamdan sonra ek yalnız sabit ifadelerde (ör. "%88,9'dan küçük değildir", "|r| 1'e yaklaştıkça"); değişken
sayılara ek getirilmez."""


def _values(spec) -> dict[str, float]:
    return {check.label: check.expected for step in spec.steps for check in step.checks}


def _texts(spec) -> list[str]:
    return [text for step in spec.steps for text in (step.explanation, step.takeaway, step.code_note)]


def _ops(spec, number: int, kind) -> list:
    return [op for op in spec.step(number).operations if isinstance(op, kind)]


def _ders(values, p: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=float), p, method="weibull"))


def _konu05(frame: pd.DataFrame, roles: dict):
    table = K.UploadedTable("veri.csv", "csv", frame)
    case, notes = custom_case(O5.CUSTOM, table, CustomChoices(roles=roles))
    return O5.build(case), notes


def _konu06(frame: pd.DataFrame, roles: dict, picks: dict | None = None, settings: dict | None = None):
    table = K.UploadedTable("veri.csv", "csv", frame)
    case, _ = custom_case(O6.CUSTOM, table, CustomChoices(roles=roles, picks=picks or {}, settings=settings or {}))
    return O6.build(case)


# --- Konu 5: alternatif örnek ------------------------------------------------------------------

def test_konu05_alternative_matches_a_direct_calculation() -> None:
    values = _values(O5.alternative())
    depot = np.array([row[0] for row in O5.ALT_ROWS])
    x = np.array([row[1] for row in O5.ALT_ROWS], dtype=float)
    y = np.array([row[2] for row in O5.ALT_ROWS], dtype=float)
    north, south = x[depot == "Kuzey"], x[depot == "Güney"]
    assert values["Kuzey: ortalama"] == values["Güney: ortalama"] == pytest.approx(40)
    assert values["Kuzey: değişim aralığı R"] == np.ptp(north) == 14
    assert values["Güney: değişim aralığı R"] == np.ptp(south) == 123
    mean, deviations = x.mean(), x - x.mean()
    assert values["Ortalama x̄"] == pytest.approx(mean)
    assert values["İlk gözlemin sapması"] == pytest.approx(deviations[0])
    assert values["İlk gözlemin kareli sapması"] == pytest.approx(deviations[0] ** 2)
    assert values["Sapmaların toplamı"] == pytest.approx(0, abs=1e-9)
    assert values["Kareli sapmalar toplamı"] == pytest.approx((deviations ** 2).sum())
    assert values["Örneklem varyansı s²"] == pytest.approx(np.var(x, ddof=1)) == values["Yazılımla varyans"]
    s = np.std(x, ddof=1)
    assert values["Standart sapma s"] == pytest.approx(s)
    assert values["Kuzey: s"] == pytest.approx(np.std(north, ddof=1))
    assert values["Güney: s"] == pytest.approx(np.std(south, ddof=1))
    assert values["Teslimat mesafesi (km): CV (%)"] == pytest.approx(100 * s / mean)
    assert values["Teslim süresi (saat): CV (%)"] == pytest.approx(100 * np.std(y, ddof=1) / y.mean())
    assert values["En büyük gözlemin z-skoru"] == pytest.approx((x.max() - mean) / s)
    assert values["En küçük gözlemin z-skoru"] == pytest.approx((x.min() - mean) / s)
    assert values["Güney: en büyük gözlemin z-skoru"] == pytest.approx((135 - 40) / np.std(south, ddof=1))
    for k in (2, 3):
        share = np.mean(np.abs(x - mean) <= k * s)
        assert values[f"k = {k}: x̄ ± {k}s içindeki gözlemlerin payı"] == pytest.approx(share) == pytest.approx(23 / 24)
        assert share >= 1 - 1 / k ** 2  # Chebyshev her veri setinde sağlanır
    q1, q3 = _ders(x, 25), _ders(x, 75)
    assert (values["Q₁"], values["Q₃"]) == (q1, q3) == (30.75, 43.5)
    lower, upper = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    assert (values["Alt sınır Q₁ − 1,5·IQR"], values["Üst sınır Q₃ + 1,5·IQR"]) == (lower, upper)
    assert values["Aykırı değer adayı sayısı"] == ((x < lower) | (x > upper)).sum() == 1
    assert values["Medyan"] == np.median(x) and values["Sağ bıyık ucu"] == x[x <= upper].max() == 58
    assert values["Kuzey: medyan"] == np.median(north) and values["Güney: medyan"] == np.median(south)
    assert values["Kovaryans s_xy"] == pytest.approx(np.cov(x, y)[0, 1]) == values["Yazılımla kovaryans"]
    assert values["Korelasyon r"] == pytest.approx(np.corrcoef(x, y)[0, 1]) == values["Yazılımla korelasyon"]
    assert values["s_y"] == pytest.approx(np.std(y, ddof=1))


def test_konu05_alternative_tells_the_story_of_the_notes() -> None:
    spec = O5.alternative()
    assert "İki grubun ortalaması da 40" in spec.step(1).takeaway
    assert "Güney grubunun gözlemleri daha geniş" in spec.step(2).takeaway
    assert "yaklaşık 7,96 katıdır" in spec.step(4).takeaway
    assert "|z| > 3 olan gözlem sayısı: 1" in spec.step(6).takeaway
    assert "Sınırların dışındaki gözlem (135) aykırı değer adayıdır" in spec.step(8).takeaway
    assert "sağ bıyık 58" in spec.step(9).takeaway and "Beş sayı özeti 12; 30,75; 38,5; 43,5 ve 135" in \
        spec.step(9).takeaway
    assert "doğrusal ilişkinin yönü pozitif" in spec.step(11).takeaway
    assert "medyan ve IQR" in spec.step(12).takeaway
    boxes = _ops(spec, 9, BoxSummary)[0]
    assert [label for _, _, label in boxes.series] == ["Tümü", "Kuzey", "Güney"]
    assert [op.value for op in _ops(spec, 1, Subset)] == ["Kuzey", "Güney"]


# --- Konu 5: kendi verini yükle ---------------------------------------------------------------

INCOME = pd.DataFrame({
    "Gelir": [12.5, 14.0, 13.25, 18.0, 11.75, 15.5, 40.0, 13.0],
    "Şube": ["A", "B", None, "A", "B", "A", "B", "A"],
    "Harcama": [3.1, None, 2.8, 4.0, 2.5, 3.6, 6.9, 3.0],
})


def test_konu05_without_optional_columns_asks_for_them() -> None:
    spec, _ = _konu05(INCOME, {"sayisal": "Gelir"})
    assert run_lab(spec).all_passed
    for number in (1, 2, 10, 11):
        assert "sütun seçin" in spec.step(number).explanation and not spec.step(number).checks
    assert spec.step(1).operations  # veri yine Adım 1'de okunur
    assert "İkinci bir sayısal sütun seçerseniz" in spec.step(5).explanation
    assert [check.label for check in spec.step(5).checks] == ["Gelir: CV (%)"]
    snippet = render_step(spec, 4, "Python")  # yalnız önceki adımın varyansını kullanır
    assert "Önceki adımlar çalıştırılmış olmalıdır" in snippet


def test_konu05_blank_cells_in_optional_columns_are_handled_per_step() -> None:
    spec, notes = _konu05(INCOME, {"sayisal": "Gelir", "grup": "Şube", "ikinci": "Harcama"})
    assert run_lab(spec).all_passed and len(notes) == 2
    assert "Grup sütunu boş olan 1 gözlem" in spec.step(1).explanation
    values = _values(spec)
    assert values["A: ortalama"] == pytest.approx(np.mean([12.5, 18.0, 15.5, 13.0]))
    assert values["B: ortalama"] == pytest.approx(np.mean([14.0, 11.75, 40.0]))
    first = spec.step(5).operations[0]
    assert isinstance(first, CompleteCases) and first.columns == ("gelir", "harcama")
    assert not _ops(spec, 10, CompleteCases)  # iki sütunun tam gözlemleri Adım 5'te seçildi
    assert "1 gözlem bu adımda kullanılmaz; 7 gözlem kalır" in spec.step(10).explanation
    paired = INCOME.dropna(subset=["Harcama"])
    assert values["Kovaryans s_xy"] == pytest.approx(np.cov(paired["Gelir"], paired["Harcama"])[0, 1])
    assert "negatif çarpım yok" in spec.step(10).takeaway


def test_konu05_cv_needs_a_positive_mean_and_no_negative_values() -> None:
    frame = pd.DataFrame({"Büyüme": [-2.5, 1.0, 3.5, 0.5, 2.0, -1.0], "Satış": [10, 12, 15, 11, 14, 9]})
    spec, _ = _konu05(frame, {"sayisal": "Büyüme", "ikinci": "Satış"})
    assert run_lab(spec).all_passed
    assert [check.label for check in spec.step(5).checks] == ["Satış: CV (%)"]
    assert "negatif değer var" in spec.step(5).explanation
    only, _ = _konu05(frame, {"sayisal": "Büyüme"})
    assert not only.step(5).operations and "oran ölçekli" in only.step(5).explanation


def test_konu05_constant_or_short_second_column_blocks_correlation() -> None:
    frame = pd.DataFrame({"x": [1, 2, 3, 4, 5, 6], "y": [7, 7, 7, 7, 7, 7], "z": [1, None, None, None, None, 2]})
    constant, _ = _konu05(frame, {"sayisal": "x", "ikinci": "y"})
    assert "korelasyon tanımsızdır" in constant.step(11).explanation and not constant.step(11).checks
    short, _ = _konu05(frame, {"sayisal": "x", "ikinci": "z"})
    assert "en az üç gözlem" in short.step(10).explanation and run_lab(short).all_passed


@pytest.mark.parametrize("frame, roles, message", [
    (pd.DataFrame({"x": [5.0] * 6}), {"sayisal": "x"}, "bütün değerler aynı"),
    (pd.DataFrame({"x": [1e9 + step * 1e-3 for step in range(6)]}), {"sayisal": "x"}, "birbirine çok yakın"),
    (pd.DataFrame({"x": [1, 2, 3, 4, 5, 6], "g": ["A", "A", "A", "A", "A", "B"]}), {"sayisal": "x", "grup": "g"},
     "en az iki gözlem"),
])
def test_konu05_unusable_data_is_rejected(frame, roles, message) -> None:
    with pytest.raises(K.UploadError, match=message):
        _konu05(frame, roles)


def test_konu05_boundary_observations_count_inside_the_chebyshev_interval() -> None:
    """x̄ ± 2s sınırındaki gözlem (|x − x̄| = 2s) içeride sayılır; ondalıklı veride kayan nokta yuvarlaması bu eşitliği
    bozmaz (göreli 10⁻⁹ pay)."""

    for values in ([10, 6, 8, 8, 8, 8, 8, 8, 8], [1.0, 0.6, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]):
        spec, _ = _konu05(pd.DataFrame({"x": values}), {"sayisal": "x"})
        assert _values(spec)["k = 2: x̄ ± 2s içindeki gözlemlerin payı"] == 1.0
        assert "9 gözlemin 9 tanesi" in spec.step(7).explanation
    plain = np.array([1.0, 0.6] + [0.8] * 7)
    assert (np.abs(plain - plain.mean()) <= 2 * plain.std(ddof=1)).sum() < 9  # payı olmadan sınırdakiler dışarıda


def test_konu05_large_data_uses_histograms_and_large_values_keep_safe_digits() -> None:
    rng = np.random.default_rng(11)
    frame = pd.DataFrame({"Süre": np.round(rng.gamma(2, 9, 400), 1), "Grup": rng.choice(["A", "B"], 400)})
    spec, _ = _konu05(frame, {"sayisal": "Süre", "grup": "Grup"})
    assert run_lab(spec).all_passed
    assert _ops(spec, 8, Histogram) and not _ops(spec, 8, DotPlot)
    large, _ = _konu05(pd.DataFrame({"x": [123456789012.5 + step * 1000.25 for step in range(40)]}),
                       {"sayisal": "x"})
    decimals = {check.label: check.decimals for check in large.step(3).checks}
    # Ortalamanın kesin değeri …517,375; 40 değerin kayan noktalı toplamı üçüncü basamağı güvenilir vermez. Basamak
    # farkın içinde kalacak kadar sınırlanır (iki basamakta …517,375 tam yarım olduğu için bir basamak).
    assert decimals["Ortalama x̄"] == 1 and decimals["Sapmaların toplamı"] <= 1
    assert "\\bar{x} \\approx 123456808517{,}4$" in large.step(3).explanation
    assert run_lab(large).all_passed


# --- Konu 6: alternatif örnek ------------------------------------------------------------------

def test_konu06_alternative_matches_a_direct_count() -> None:
    values = _values(O6.alternative())
    sums = Counter(a + b for a, b in product(range(1, 9), repeat=2))
    assert values["Bir zarda örnek nokta sayısı"] == 8 and values["Farklı toplam sayısı (2, …, 16)"] == len(sums) == 15
    assert values["Toplam 2: yalnız (1, 1)"] == sums[2] == 1 and values["Toplam 9: en sık toplam"] == sums[9] == 8
    assert values["Listelenen sonuç sayısı"] == values["3 × 2"] == 6 and values["8 × 8"] == 64
    assert values["6!"] == math.factorial(6)
    assert values["C(6, 3) = 6!/(3! 3!)"] == values["Listelenen grup sayısı"] == math.comb(6, 3) == 20
    assert values["P(6, 3) = 6!/3!"] == values["Listelenen görev dağılımı sayısı"] == math.perm(6, 3) == 120
    rows = [(odeme, tur) for odeme, tur, count in O6.ALT_COUNTS for _ in range(count)]
    n = len(rows)
    mobile = sum(odeme == "Mobil" for odeme, _ in rows)
    package = sum(tur == "Paket" for _, tur in rows)
    both = sum(odeme == "Mobil" and tur == "Paket" for odeme, tur in rows)
    assert n == 200 and (mobile, package, both) == (60, 80, 35)
    assert values["Klasik yöntem: P(1) = 1/8"] == pytest.approx(1 / 8)
    assert values["Göreli frekans: Mobil"] == pytest.approx(mobile / n) == values["P(E)"]
    assert values["A'daki örnek nokta sayısı"] == 4 and values["P(A) = 4/8"] == pytest.approx(0.5)
    assert values["P(Eᶜ) = 1 − P(E)"] == pytest.approx(1 - mobile / n) \
        == values["P(Eᶜ): E'de olmayan gözlemlerin oranı"]
    assert values["P(A ∪ B) = 5/8"] == pytest.approx(5 / 8) and values["P(A ∩ B) = 1/8"] == pytest.approx(1 / 8)
    union = (mobile + package - both) / n
    assert values["P(E ∪ F) = P(E) + P(F) − P(E ∩ F)"] == pytest.approx(union) == pytest.approx(0.525)
    assert values["P(E ∪ F): en az birinin gerçekleştiği gözlemlerin oranı"] == pytest.approx(union)
    assert values["P(E ∩ F): ortak hücre"] == pytest.approx(both / n)
    assert values["P(F): Paket sütununun toplamı"] == pytest.approx(package / n)
    assert values["Ne E ne F: 1 − P(E ∪ F)"] == pytest.approx(1 - union) == \
        values["Ne E ne F: iki olayın da dışındaki gözlemlerin oranı"]
    assert values["Örnek nokta olasılıklarının toplamı"] == pytest.approx(1)


def test_konu06_alternative_uses_its_story_and_lists_every_selection() -> None:
    spec = O6.alternative()
    assert "Kafenin altı çalışanı" in spec.step(3).explanation and "3! farklı sırayla" in spec.step(3).takeaway
    roles = [op.columns for op in _ops(spec, 3, Selections) if op.ordered]
    assert roles == [("sef", "kasiyer", "barista")]
    assert "“Ödeme yöntemi: Mobil”" in spec.step(6).explanation and "(Kart ve Nakit)" in spec.step(6).explanation
    assert "%52,5 kadarında" in spec.step(9).takeaway


# --- Konu 6: kendi verini yükle ve kaydırıcılar --------------------------------------------------

CODES = pd.DataFrame({"Kod": [1, 2, 3, 1, 2, 2, 1, 3, 3, 1], "Durum": ["Evet", "Hayır"] * 5})


def test_konu06_settings_change_the_die_and_the_team() -> None:
    spec = _konu06(CODES, {"olay_e": "Kod", "olay_f": "Durum"}, settings={"zar": 20, "ekip": 10, "secim": 5})
    assert run_lab(spec).all_passed
    values = _values(spec)
    assert values["Farklı toplam sayısı (2, …, 40)"] == 39 and values["Toplam 21: en sık toplam"] == 20
    assert "\\{1, 2, \\ldots, 20\\}" in spec.step(1).explanation
    assert "\\{2, 4, \\ldots, 20\\}" in spec.step(5).explanation
    listed = _ops(spec, 3, Selections)  # C(10, 5) = 252 listelenir, P(10, 5) = 30240 listelenmez
    assert [op.ordered for op in listed] == [False]
    assert "Permütasyon listesi 720 satırı aşacağı" in spec.step(3).takeaway
    assert values["C(10, 5) = 10!/(5! 5!)"] == 252 and values["P(10, 5) = 10!/5!"] == 30240
    assert values["P(A ∩ B) = 1/20"] == pytest.approx(0.05)
    one = _konu06(CODES, {"olay_e": "Kod", "olay_f": "Durum"}, settings={"zar": 4, "ekip": 3, "secim": 1})
    assert "Tek kişi seçilirken" in one.step(3).takeaway and _values(one)["P(A ∪ B) = 3/4"] == pytest.approx(0.75)
    with pytest.raises(K.UploadError, match="büyük olamaz"):
        _konu06(CODES, {"olay_e": "Kod", "olay_f": "Durum"}, settings={"ekip": 4, "secim": 5})


def test_konu06_default_settings_match_the_alternative() -> None:
    assert {setting.key: setting.default(pd.DataFrame(), {}) for setting in O6.CUSTOM.settings} == O6.ALT_SETTINGS


def test_konu06_disjoint_events_and_unobserved_combinations() -> None:
    frame = pd.DataFrame({"Teslim": ["Geç", "Geç", "Zamanında", "Zamanında", "Zamanında", "Geç"],
                          "Hasar": ["Yok", "Yok", "Var", "Var", "Yok", "Yok"]})
    spec = _konu06(frame, {"olay_e": "Teslim", "olay_f": "Hasar"}, picks={"olay_e": "Geç", "olay_f": "Var"})
    assert run_lab(spec).all_passed
    assert "ayrıktır (ortak gözlem yok)" in spec.step(8).takeaway
    assert _values(spec)["P(E ∩ F)"] == 0
    assert "1 tanesi veride hiç gözlenmemiştir" in spec.step(2).explanation  # (Geç, Var)


def test_konu06_needs_two_different_columns() -> None:
    with pytest.raises(K.UploadError, match="iki farklı sütun"):
        _konu06(CODES, {"olay_e": "Durum", "olay_f": "Durum"})


def test_konu06_category_names_never_enter_math() -> None:
    frame = pd.DataFrame({"Ödeme": ["Kart $", "Nakit_1", "Kart $", "Mobil", "Nakit_1", "Mobil"],
                          "Tür": ["A", "B", "B", "A", "A", "B"]})
    spec = _konu06(frame, {"olay_e": "Ödeme", "olay_f": "Tür"}, picks={"olay_e": "Kart $"})
    for text in _texts(spec):
        for formula in re.findall(r"\$[^$]*\$", text.replace("\\$", "")):
            assert "Kart" not in formula and "Nakit" not in formula, formula


# --- Metin kuralları -------------------------------------------------------------------------

def _own_specs():
    yield _konu05(INCOME, {"sayisal": "Gelir", "grup": "Şube", "ikinci": "Harcama"})[0]
    yield _konu06(CODES, {"olay_e": "Kod", "olay_f": "Durum"}, settings={"zar": 6, "ekip": 5, "secim": 2})


def test_texts_add_no_suffix_to_runtime_numbers() -> None:
    specs = [O5.alternative(), O6.alternative(), *_own_specs()]
    for spec in specs:
        for text in _texts(spec):
            plain = re.sub(r"\$[^$]*\$", "", text)  # matematik ifadelerindeki ekler (ör. $(x_i - \bar{x})^2$'dir) değil
            for word in re.findall(r"%?\d[\d,]*'[a-zçğıöşü]+", plain):
                assert word in ALLOWED_SUFFIXES, (spec.topic_key, word, text)


def test_notes_step_snippets_are_unchanged_by_the_scalar_rule() -> None:
    """Önceki adımın skalerini kullanan adımın kodu notlar dışındaki kaynaklarda bunu söyler; notların adım kodları
    değişmez."""

    assert "Önceki adımlar çalıştırılmış olmalıdır" not in render_step(get_lab("konu03"), 2, "Python")
    from core.labs.ornekler import VARIANTS

    assert "Önceki adımlar çalıştırılmış olmalıdır" in render_step(VARIANTS["konu03"].alternative(), 2, "Python")


def test_signless_zero_and_exact_box_values_in_other_sources() -> None:
    from topics.lab_ui import _signless_zero, display_table

    assert _signless_zero("−0,00") == "0,00" and _signless_zero("%−0,0") == "%0,0"
    assert _signless_zero("−0,01") == "−0,01" and _signless_zero("−10") == "−10"
    spec = O5.alternative()
    state = run_lab(spec).state
    box = _ops(spec, 9, BoxSummary)[0]
    shown = display_table(box, state.tables["kutu"], spec.label, small=True)
    row = shown[shown["Özet"] == "Alt sınır Q₁ − 1,5·IQR"].iloc[0]
    assert row["Tümü"] == "11,625" and row["Kuzey"] == "26"
    notes = display_table(box, state.tables["kutu"], spec.label)
    assert notes[notes["Özet"] == "Alt sınır Q₁ − 1,5·IQR"].iloc[0]["Tümü"] == "11,62"


def test_reference_lines_show_the_digits_of_their_metric() -> None:
    """Nokta grafiğinin açıklamasındaki başvuru değeri metrikle aynı basamakla yazılır (11,625; iki basamakla 11,62
    olurdu). Notların grafikleri değişmez (iki basamak)."""

    from core.charts import figure_for

    spec = O5.alternative()
    state = run_lab(spec).state
    plot = _ops(spec, 8, DotPlot)[0]
    assert plot.reference_decimals == (3, 3)
    names = [trace.name for trace in figure_for(plot, state, spec.label).data if trace.name]
    assert "Alt sınır: 11,625" in names and "Üst sınır: 62,625" in names
    notes = get_lab("konu05")
    assert all(op.reference_decimals == () for step in notes.steps for op in step.operations
               if isinstance(op, DotPlot))


def test_konu06_rounded_terms_are_not_written_with_an_equals_sign() -> None:
    """P(E) = 1/3 gibi yuvarlanan terimlerle toplama kuralı "≈" ile yazılır (0,3333 + 0,5 − 0,1667 = 0,6667
    değildir); örnek uzay kümesine ek getirilmez (zarın yüz sayısı değişkendir)."""

    frame = pd.DataFrame({"Tür": ["a", "a", "b", "b", "c", "c"], "Durum": ["x", "y", "x", "y", "x", "y"]})
    spec = _konu06(frame, {"olay_e": "Tür", "olay_f": "Durum"}, picks={"olay_e": "a", "olay_f": "x"},
                   settings={"zar": 6})
    assert run_lab(spec).all_passed
    assert "0{,}3333 + 0{,}5 - 0{,}1667 \\approx 0{,}6667$" in spec.step(8).explanation
    assert "P(E) + P(F) ≈ 0,8333 ortak kısmı" in spec.step(8).takeaway
    assert "çıkarınca yaklaşık 0,6667 bulunur" in spec.step(8).takeaway
    assert "$'" not in spec.step(1).explanation and "kümesidir" in spec.step(1).explanation
    assert "“a” satırı ile “x” sütunu dışında kalan hücrelerin" in spec.step(9).takeaway


def test_konu05_products_that_are_zero_are_counted() -> None:
    """Ortalamadaki gözlemin (x = x̄) sapma çarpımı sıfırdır; metin üç durumu da sayar."""

    takeaway = O5.alternative().step(10).takeaway
    assert "24 gözlemin 18 tanesinde pozitif, 4 tanesinde negatif ve 2 tanesinde sıfır" in takeaway


def test_metric_titles_fit_their_columns() -> None:
    """Metrik başlıkları 1280 piksel genişlikte kesilmez: aynı satırdaki metrik sayısına göre en çok 28 (dört
    metrik), 38, 57 ya da 110 karakter. Notlardaki uzun başlıklar (ör. "Kovaryans s_xy = toplam/(n − 1)") değişmez."""

    from topics.lab_ui import _METRICS, _metrics

    limit = {4: 28, 3: 38, 2: 57, 1: 110}
    for spec in (O5.alternative(), O6.alternative()):
        state = run_lab(spec).state
        for step in spec.steps:
            rows, pending = [], []
            for op in step.operations:
                if isinstance(op, _METRICS):
                    pending.extend(_metrics(op, state))
                    continue
                if pending:
                    rows.append(pending)
                    pending = []
            if pending:
                rows.append(pending)
            for row in rows:
                for start in range(0, len(row), 4):
                    chunk = row[start:start + 4]
                    for title, _ in chunk:
                        assert len(title) <= limit[len(chunk)], (spec.topic_key, step.number, title)


# --- Bağımsız inceleme (1. tur) bulguları ------------------------------------------------------

def test_konu05_rejects_the_same_column_for_x_and_y() -> None:
    """x ve y aynı sütun olunca kovaryans ve korelasyon anlamsızdır (r = 1); seçim açık bir iletiyle reddedilir."""

    with pytest.raises(K.UploadError, match="hem x hem y için seçildi"):
        _konu05(INCOME, {"sayisal": "Gelir", "ikinci": "Gelir"})


def test_konu05_chebyshev_slack_grows_with_the_magnitude_of_the_data() -> None:
    """Büyük değerlerde tam sınırdaki gözlem (|x − x̄| = 3s) iki dilde de içeride sayılsın diye göreli pay verinin
    kayan nokta farkına göre büyür; olağan veride 10⁻⁹ kalır."""

    frame = pd.DataFrame({"Tutar": [86349475.7, 86349463.98] + [86349469.84] * 17})
    spec, _ = _konu05(frame, {"sayisal": "Tutar"})
    assert run_lab(spec).all_passed
    assert _values(spec)["k = 3: x̄ ± 3s içindeki gözlemlerin payı"] == 1.0
    assert "10⁻⁶ göreli payla (ks × 1,000001)" in spec.step(7).code_note
    assert "10⁻⁹ göreli payla (ks × 1,000000001)" in O5.alternative().step(7).code_note


def test_konu05_an_observation_on_the_fence_is_not_an_outlier() -> None:
    """Q₃ + 1,5·IQR = 1,91 ve x = 1,91: kesin hesapta sınırın üzerindedir, aykırı değer değildir. Sınırlar d + 3
    basamağa yuvarlanarak sınıflanır (kayan noktalı hesap 1,91'i sınırın dışına düşürebilirdi)."""

    spec, _ = _konu05(pd.DataFrame({"Süre": [0.05, 0.33, 0.4, 0.58, 0.59, 1.91]}), {"sayisal": "Süre"})
    run = run_lab(spec)
    assert run.all_passed
    assert run.state.scalars["aykiri_sayisi"] == 0 and run.state.tables["kutu"].loc["aykiri_sayisi", "Süre"] == 0
    assert "Sınırların dışında gözlem yok" in spec.step(8).takeaway and "1{,}91" in spec.step(8).explanation
    assert _ops(spec, 9, BoxSummary)[0].fence_decimals == 5 and "5 basamağa yuvarlar" in spec.step(8).code_note
    assert "bıyıklar en küçük ve en büyük gözleme uzanır" in spec.step(9).takeaway


def test_konu05_exact_linear_relation_gives_r_exactly_minus_one() -> None:
    """Tam doğrusal ilişkide r kesin olarak −1'dir ("≈ −1" değil); varyanslar sonsuz ondalıklı olsa bile."""

    x = [15, 41, 5, 30, 36, 9, 3, 14, 33, 28, 8, 22, 33]
    spec, _ = _konu05(pd.DataFrame({"x": x, "y": [-value - 1 for value in x]}), {"sayisal": "x", "ikinci": "y"})
    assert run_lab(spec).all_passed
    assert spec.step(11).takeaway.startswith("r = −1: noktaların hepsi bir doğrunun üzerindedir")
    assert spec.step(11).explanation.endswith("$r = −1$.")


def test_konu05_rounded_substitutions_are_written_with_approx() -> None:
    """Yerine konan değer yuvarlanmışsa zincirdeki eşitlik "≈" olur: z ≈ (135 − 40)/23,06 ≈ 4,12; kareli sapmalar
    toplamı yuvarlanmışsa varyans da "≈" ile yazılır."""

    assert "$z \\approx (135 - 40)/23{,}06 \\approx 4{,}12$" in O5.alternative().step(6).explanation
    frame = pd.DataFrame({"x": [0, 0, 1, 1, 1, 2, 4]})  # Σ(x − x̄)² = 80/7 sonsuz ondalıklı
    spec, _ = _konu05(frame, {"sayisal": "x"})
    assert "\\approx 11{,}43/(7 - 1) \\approx 1{,}9$" in spec.step(3).explanation


def test_konu05_values_too_close_within_a_group_or_the_pairs_are_reported() -> None:
    """Grubun ya da eşleşen gözlemlerin değerleri büyüklüklerine göre çok yakınsa (göreli fark 10⁻⁷'den küçük)
    standart sapma ve korelasyon güvenilir basamakla hesaplanamaz: grup reddedilir, kovaryans adımları açıklanır."""

    big = [987654321.123451, 987654321.123456, 987654321.123458, 987654321.123453, 987654321.123459]
    frame = pd.DataFrame({"x": big + [1.5, 2.5, 3.5, 4.75], "g": list("AAAAABBBB"),
                          "y": [1.25, 2.5, 3.75, 2.0, 3.0, None, None, None, None]})
    with pytest.raises(K.UploadError, match="“A” grubundaki “x” değerleri"):
        _konu05(frame, {"sayisal": "x", "grup": "g"})
    spec, _ = _konu05(frame, {"sayisal": "x", "ikinci": "y"})
    assert "büyüklüklerine göre birbirine çok yakın" in spec.step(10).explanation and not spec.step(11).operations
    assert "İkinci sütunun CV'si bu adımda hesaplanmaz" in spec.step(5).explanation


def test_konu05_constant_second_column_keeps_the_covariance() -> None:
    """y sabitse kovaryans tanımlıdır (0) ve hesaplanır; korelasyon tanımsızdır ve nedeni yazılır."""

    spec, _ = _konu05(pd.DataFrame({"x": [1, 2, 3, 4, 5.5], "y": [2, 2, 2, 2, 2]}), {"sayisal": "x", "ikinci": "y"})
    assert run_lab(spec).all_passed and _values(spec)["Kovaryans s_xy"] == 0
    assert spec.step(10).takeaway.startswith("Sapmaların çarpımı 5 gözlemin hepsinde sıfır; kovaryans sıfır.")
    assert not spec.step(11).operations and "korelasyon tanımsızdır" in spec.step(11).explanation


def test_konu06_set_notation_keeps_the_irregular_elements() -> None:
    """A ∪ B kümesinde düzeni bozan öğeler (m − 1) açıkça yazılır: {2, 4, …, 18, 19, 20}."""

    frame = pd.DataFrame({"E": ["a"] + ["b"] * 6, "F": ["x", "y", "x", "y", "x", "y", "y"]})
    expected = {12: "A \\cup B = \\{2, 4, \\ldots, 10, 11, 12\\}", 13: "A \\cup B = \\{2, 4, \\ldots, 12, 13\\}",
                20: "A \\cup B = \\{2, 4, \\ldots, 18, 19, 20\\}"}
    for m, text in expected.items():
        spec = _konu06(frame, {"olay_e": "E", "olay_f": "F"}, picks={"olay_e": "a", "olay_f": "x"},
                       settings={"zar": m})
        assert text in spec.step(7).explanation, m


def test_konu06_complement_chains_use_approx_when_rounded() -> None:
    """P(E) = 1/7 yuvarlanır: "P(Eᶜ) = 1 − P(E) ≈ 1 − 0,1429 ≈ 0,8571" ve "1 − P(E ∪ F) ≈ 1 − 0,4286 ≈ 0,5714"."""

    frame = pd.DataFrame({"E": ["a"] + ["b"] * 6, "F": ["x", "y", "x", "y", "x", "y", "y"]})
    spec = _konu06(frame, {"olay_e": "E", "olay_f": "F"}, picks={"olay_e": "a", "olay_f": "x"})
    assert spec.step(6).takeaway.startswith("P(Eᶜ) = 1 − P(E) ≈ 1 − 0,1429 ≈ 0,8571")
    assert "$1 - P(E \\cup F) \\approx 1 - 0{,}4286 \\approx 0{,}5714$" in spec.step(9).explanation


def test_signless_zero_in_legends_and_profile_tables() -> None:
    """Ortalaması kesin olarak 0 olan veride kayan noktalı ortalama −1e-17 olabilir: grafik açıklaması ve profil
    tablosu "−0,00" göstermez (notlar dışındaki kaynaklar)."""

    from core.charts import figure_for
    from topics.lab_ui import display_table

    frame = pd.DataFrame({"x": [0.2, 0.7, -0.9, 0.2, 0.7, -0.9], "g": list("ABABAB")})
    spec, _ = _konu05(frame, {"sayisal": "x", "grup": "g"})
    state = run_lab(spec).state
    names = [trace.name for plot in _ops(spec, 1, DotPlot) for trace in figure_for(plot, state, spec.label).data
             if trace.name]
    assert names and all("−" not in name for name in names)
    profile = [op for op in spec.step(12).operations if type(op).__name__ == "ScalarTable"][0]
    shown = display_table(profile, state.tables[profile.result], spec.label, small=True)
    assert not shown["Değer"].str.startswith("−0").any()


def test_box_summary_columns_are_series_labels_in_other_sources() -> None:
    """Grup adı koddaki bir sütunun adıyla aynı olsa da (ör. "sapma", "z") kutu özetinin başlığı grup adıdır."""

    from topics.lab_ui import display_table

    frame = pd.DataFrame({"x": [1.5, 2.5, 3.0, 4.25, 5.0, 6.5], "g": ["sapma", "z"] * 3})
    spec, _ = _konu05(frame, {"sayisal": "x", "grup": "g"})
    box = _ops(spec, 9, BoxSummary)[0]
    shown = display_table(box, run_lab(spec).state.tables["kutu"], spec.label, small=True)
    assert list(shown.columns) == ["Özet", "Tümü", "sapma", "z"]


# --- Bağımsız inceleme (2. tur) bulguları ------------------------------------------------------

def _csv_konu05(frame: pd.DataFrame, roles: dict):
    """Dosya yolu (CSV): okuma, temizleme ve üretilen R okuyucusu da sınanır."""

    table = K.read_upload("veri.csv", frame.to_csv(index=False).encode("utf-8"))
    case, _ = custom_case(O5.CUSTOM, table, CustomChoices(roles=roles))
    return O5.build(case)


def test_expected_values_keep_two_more_digits_in_other_sources() -> None:
    """Kontrol satırındaki beklenen değer notlarda basılı değerdir; diğer kaynaklarda uygulamanın değeri iki basamak
    fazlasıyla yazılır (yarım noktaya yakın değerde iki dilin küçük farkı toleransı aşmasın)."""

    from core.codegen.base import expected_text, render_script

    assert expected_text(25.566666, 2, "notlar") == "25.57" and expected_text(25.566666, 2, "kendi") == "25.5667"
    assert expected_text(0.18, 3, "alternatif") == "0.18" and expected_text(-1e-17, 2, "kendi") == "0"
    assert expected_text(1542781970.5004, 0, "kendi") == "1542781970.5"
    assert 'kontrol_et("Ortalama x̄", ortalama, 40, 2)' in render_script(O5.alternative(), "Python")


def test_konu05_unreliable_checks_are_skipped_for_huge_values() -> None:
    """1,5·10¹¹ dolayındaki değerlerde ilk gözlemin kareli sapması iki dilde tam kısımda ayrılabilir: kontrol edilmez
    ve kod notu bunu söyler; öbür kontroller kalır."""

    spec = _csv_konu05(pd.DataFrame({"x": [150000153920.88, 150000094822.75, 150000184223.36, 150000097995.95,
                                           150000051684.85, 150000028393.93]}), {"sayisal": "x"})
    labels = [check.label for check in spec.step(3).checks]
    assert "İlk gözlemin kareli sapması" not in labels and "Örneklem varyansı s²" in labels
    assert "ilk gözlemin kareli sapması kontrol edilmez" in spec.step(3).code_note
    assert sum(len(step.checks) for step in O5.alternative().steps) == 47  # olağan veride hiçbiri atlanmaz


def test_konu05_quartile_digits_avoid_exact_halves() -> None:
    """IQR = 299999,875 iki basamakla tam yarım: metin ve tablo aynı sayıyı göstersin diye bir basamak yazılır."""

    spec = _csv_konu05(pd.DataFrame({"x": [999999999000, 1000000000000, 1000000000000.5, 1000000001000,
                                           1000000002000, 1000000300000, 1000000300000, 1000000300001]}),
                       {"sayisal": "x"})
    decimals = {check.label: check.decimals for check in spec.step(8).checks}
    assert decimals["IQR = Q₃ − Q₁"] == 1 and "$IQR \\approx 299999{,}9$" in spec.step(8).explanation


def test_konu05_fence_note_when_fences_cannot_be_rounded() -> None:
    """Çok büyük değerlerde sınırlar yuvarlanamaz; tam sınırdaki gözlem kayan noktalı hesapta dışarıda kalırsa metin
    bunu açıkça söyler (uygulama ve kod aynı sonucu verir)."""

    values = [1e12 - 300000, 1e12, 1e12 + 1, 1e12 + 2, 1e12 + 3, 1e12 + 100000.2, 1e12 + 250000.5]
    spec = _csv_konu05(pd.DataFrame({"x": values}), {"sayisal": "x"})
    assert _ops(spec, 9, BoxSummary)[0].fence_decimals is None
    assert "Not: 1000000250000,5 kesin hesapta sınırların içindedir ama kayan noktalı hesapta dışında kalır" in \
        spec.step(8).takeaway


def test_konu05_proportional_columns_have_the_same_cv() -> None:
    """y = 2x ya da y = 0,3x: iki CV kesin olarak eşittir (birim değişikliği, §5.5); karşılaştırma kesin yapılır."""

    for x, y in (([1, 2, 3, 4, 5, 6], [0.3, 0.6, 0.9, 1.2, 1.5, 1.8]), ([2, 3, 5, 7, 11], [4, 6, 10, 14, 22])):
        spec = _csv_konu05(pd.DataFrame({"x": x, "y": y}), {"sayisal": "x", "ikinci": "y"})
        assert spec.step(5).takeaway.startswith("İki değişkenin göreli değişkenliği aynıdır.")


def test_r_reads_six_or_more_decimals_through_rounding() -> None:
    """R'nin metinden sayı okuması altı ve daha çok ondalıkta son ikili basamakta ayrılabilir: üretilen R kodu sütunu
    kendi basamağına yuvarlar; daha az basamakta kod değişmez."""

    from core.codegen.base import render_script

    spec = _csv_konu05(pd.DataFrame({"x": [0.1, 0.3, 0.35, 0.4, 0.45, 0.4674112, 0.718528]}), {"sayisal": "x"})
    assert "veri$x <- round(as.numeric(veri$x), 7)  # sayı" in render_script(spec, "R")
    plain = _csv_konu05(pd.DataFrame({"x": [1.5, 2.25, 3.125, 4.0, 5.5]}), {"sayisal": "x"})
    assert "veri$x <- as.numeric(veri$x)  # sayı" in render_script(plain, "R")


def test_konu05_metric_titles_start_with_the_measure() -> None:
    """Grup ya da sütun adı uzun olsa da metrik başlığının başı ölçüyü söyler (sonu kesilebilir)."""

    from topics.lab_ui import _METRICS, _metrics

    spec = O5.alternative()
    state = run_lab(spec).state
    titles = [title for step in spec.steps for op in step.operations if isinstance(op, _METRICS)
              for title, _ in _metrics(op, state)]
    assert {"Ortalama · Kuzey", "R · Güney", "s · Kuzey", "En büyük z · Güney", "CV · Teslim süresi (saat)"} <= \
        set(titles)


def test_konu05_wording_for_edge_cases() -> None:
    """Neredeyse eşit standart sapmalar, aynı basamaklı z-skorları ve boş ikinci sütun."""

    frame = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 10.0, 11.0, 12.0, 13.001], "g": ["A"] * 4 + ["B"] * 4,
                          "y": [None] * 8})
    spec = _csv_konu05(frame, {"sayisal": "x", "grup": "g", "ikinci": "y"})
    assert "standart sapmaları birbirine çok yakındır" in spec.step(4).takeaway
    assert "ikinci sütunda değeri olan gözlem yok" in spec.step(5).explanation
    decimals = {check.label: check.decimals for check in O5.alternative().step(6).checks}
    assert decimals["En büyük gözlemin z-skoru"] == decimals["En küçük gözlemin z-skoru"]


def test_konu06_wording_for_empty_intersection_full_union_and_table_digits() -> None:
    frame = pd.DataFrame({"E": ["a", "a", "b", "b", "c", "c"], "F": ["x", "x", "y", "y", "y", "y"]})
    spec = _konu06(frame, {"olay_e": "E", "olay_f": "F"}, picks={"olay_e": "a", "olay_f": "y"})
    assert "ikisinde birden olan gözlem yok" in spec.step(8).explanation
    assert spec.step(9).takeaway.startswith("Bütün gözlemlerde E ya da F (ya da ikisi) gerçekleşir.")
    assert "$\\approx 2/6 \\approx 0{,}333$" in spec.step(4).explanation
    assert {check.label: check.decimals for check in spec.step(4).checks}["Göreli frekans: a"] == 3


def test_konu05_noisy_sum_of_deviations_is_explained_on_the_page() -> None:
    """10 000 değer, 10¹² dolayında: kayan noktalı toplam birkaç birim çıkar. Kontrol atlanır, metin bunu söyler ve
    metrik ondalıkla gösterilir ("2" değil "1,75" gibi)."""

    rng = np.random.default_rng(3)
    frame = pd.DataFrame({"x": np.round(1e12 + rng.uniform(0, 1e7, 10000), 1)})
    spec, _ = _konu05(frame, {"sayisal": "x"})
    step = spec.step(3)
    assert "Sapmaların toplamı" not in [check.label for check in step.checks]
    assert "sapmaların toplamı 0 yerine birkaç birimlik bir sayı olarak görünebilir" in step.explanation
    assert next(op for op in step.operations if getattr(op, "name", "") == "sapma_toplami").decimals == 2
