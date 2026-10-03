"""Konu 7–9 alternatif örnekleri, kendi verini yükle (Konu 7–8) ve kendi değerlerini gir (Konu 9): değerler motordan
bağımsız bir hesapla doğrulanır; koşullu olasılık, bağımsızlık, ağaç ve Bayes; ampirik dağılım, beklenen değer,
varyans, ortak dağılım; binom, Poisson ve hipergeometrik olasılıklar ile metin kuralları ve iki dilde yeniden üretim
denetlenir."""

from __future__ import annotations

import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from core.codegen.base import render_script, script_filename
from core.labs import kendi_veri as K
from core.labs import ornek_konu07 as O7
from core.labs import ornek_konu08 as O8
from core.labs import ornek_konu09 as O9
from core.labs.ornek import CustomChoices, custom_case, kesir_basamak, parameter_values
from core.labs.runner import run_lab
from core.labs.spec import CompleteCases, CrossTab, GroupSummary, ShowFrame

ALLOWED_SUFFIXES = {"1'dir", "0'dır", "10⁻¹²'den", "1'de", "1'deki", "4'te", "4'teki", "5'te", "5'teki", "7'deki",
                    "8'deki", "0,50'de", "4'ü"}
"""Rakamdan sonra ek yalnız sabit ifadelerde (ör. "toplamı 1'dir", "Adım 4'te", alternatif örneğin "25 paketin 4'ü");
değişken sayılara ek getirilmez."""
CONSTANT_FORMULAS = {"10^{-20}"}


def _values(spec) -> dict[str, float]:
    return {check.label: check.expected for step in spec.steps for check in step.checks}


def _step_values(spec, number: int) -> dict[str, float]:
    return {check.label: check.expected for check in spec.step(number).checks}


def _texts(spec) -> list[str]:
    return [text for step in spec.steps for text in (step.explanation, step.takeaway, step.code_note)]


def _konu07(frame: pd.DataFrame, roles: dict, picks: dict | None = None, settings: dict | None = None):
    table = K.UploadedTable("veri.csv", "csv", frame)
    case, _ = custom_case(O7.CUSTOM, table, CustomChoices(roles=roles, picks=picks or {}, settings=settings or {}))
    return O7.build(case)


def _konu08(frame: pd.DataFrame, roles: dict, settings: dict | None = None):
    table = K.UploadedTable("veri.csv", "csv", frame)
    case, notes = custom_case(O8.CUSTOM, table, CustomChoices(roles=roles, settings=settings or {}))
    return O8.build(case), notes


def _konu09(**changes):
    values = dict(O9.ALT_VALUES)
    values.update(changes)
    return O9.build(values)


# --- Konu 7 ------------------------------------------------------------------------------------

def test_konu07_alternative_matches_a_direct_count() -> None:
    spec = O7.alternative()
    counts = {(kanal, karar): count for kanal, karar, count in O7.ALT_COUNTS}
    n = sum(counts.values())
    s = sum(count for (_, karar), count in counts.items() if karar == "Onaylandı")
    m = counts[("Mobil", "Onaylandı")] + counts[("Mobil", "Reddedildi")]
    ms = counts[("Mobil", "Onaylandı")]
    values = _values(spec)
    assert values["S'deki gözlem sayısı"] == s == 360 and values["M'deki gözlem sayısı"] == m == 450
    assert values[f"P(S) = {s}/{n}"] == pytest.approx(s / n)
    assert values[f"P(S | M) = {ms}/{m}"] == pytest.approx(ms / m)
    assert values["P(S | Mᶜ)"] == pytest.approx((s - ms) / (n - m))
    assert values[f"P(M | S) = {ms}/{s}"] == pytest.approx(ms / s)
    assert values["P(M)P(S)"] == pytest.approx(m / n * s / n)
    assert values["P(M | S) = P(M ∩ S)/P(S)"] == pytest.approx(ms / s)
    posterior = {kanal: counts[(kanal, "Onaylandı")] / s for kanal in O7.ALT_ORDERS["kanal"]}
    for kanal, value in posterior.items():
        assert values[f"Sonsal P({kanal} | S)"] == pytest.approx(value)
    base, hit, false = 0.01, 0.92, 0.03
    assert values["P(F | A) = P(F ∩ A)/P(A)"] == pytest.approx(base * hit / (base * hit + (1 - base) * false))
    assert values["Doğal frekans: alarm alan"] == 92 + 297
    assert sum(len(step.checks) for step in spec.steps) == 48


def test_konu07_texts_follow_the_story_and_exactness() -> None:
    spec = O7.alternative()
    assert "800 kredi kartı başvurusu" in spec.step(1).explanation
    assert "“Diğer”" in spec.step(7).explanation  # üç kanal: M dışındakiler tek dalda
    assert "P(S \\mid M^c) \\approx 0{,}5143" in spec.step(7).explanation
    assert "bağımlıdır" in spec.step(5).takeaway
    assert "“Sahte değil” grubu daha kalabalık olduğu için (9900 işlem)" in spec.step(10).takeaway
    assert "yanlış alarmlar (297) gerçek alarmları (92) sayıca geçer" in spec.step(10).takeaway
    assert "sonsal olasılığı en büyük kaynak: “Mobil”" in spec.step(9).takeaway


def test_konu07_independent_events_and_binary_condition() -> None:
    frame = pd.DataFrame({"Cihaz": ["Mobil"] * 4 + ["Masaüstü"] * 6,
                          "Satın alma": ["Evet", "Evet", "Hayır", "Hayır", "Evet", "Evet", "Evet", "Hayır", "Hayır",
                                         "Hayır"]})
    spec = _konu07(frame, {"kosul": "Cihaz", "sonuc": "Satın alma"}, picks={"kosul": "Mobil", "sonuc": "Evet"})
    assert run_lab(spec).all_passed
    assert "bu veride M ile S bağımsızdır" in spec.step(5).takeaway
    assert "bağımsızdır" in spec.step(6).takeaway and "eşittir" in spec.step(6).takeaway
    assert "“Masaüstü”" in spec.step(7).explanation  # iki kategori: tümleyen diğer kategorinin adı
    assert "Sonsal önsele eşittir" in spec.step(8).takeaway
    assert _step_values(spec, 5)["P(S | M) − P(S)"] == pytest.approx(0)


def test_konu07_disjoint_events_have_zero_posterior() -> None:
    frame = pd.DataFrame({"Kanal": ["A", "A", "B", "B", "C", "C"],
                          "Sonuç": ["Ret", "Ret", "Onay", "Ret", "Onay", "Onay"]})
    spec = _konu07(frame, {"kosul": "Kanal", "sonuc": "Sonuç"}, picks={"kosul": "A", "sonuc": "Onay"})
    assert run_lab(spec).all_passed
    assert "ortak gözlemi yoktur" in spec.step(4).takeaway
    assert _step_values(spec, 8)["P(M | S) = P(M ∩ S)/P(S)"] == 0


def test_konu07_needs_two_different_columns() -> None:
    frame = pd.DataFrame({"Kanal": ["A", "B"] * 4})
    with pytest.raises(K.UploadError, match="iki farklı sütun"):
        _konu07(frame, {"kosul": "Kanal", "sonuc": "Kanal"})


def test_konu07_category_names_never_enter_math() -> None:
    frame = pd.DataFrame({"Kanal": ["Şube $", "Web_1", "Şube $", "Mobil", "Web_1", "Mobil", "Mobil", "Şube $"],
                          "Sonuç": ["Onay", "Ret", "Ret", "Onay", "Onay", "Ret", "Onay", "Onay"]})
    spec = _konu07(frame, {"kosul": "Kanal", "sonuc": "Sonuç"}, picks={"kosul": "Şube $", "sonuc": "Onay"})
    for text in _texts(spec):
        for formula in re.findall(r"\$[^$]*\$", text.replace("\\$", "")):
            assert "Şube" not in formula and "Web" not in formula, formula


def test_konu07_alarm_settings_change_step_10() -> None:
    frame = O7.sample()
    roles = {"kosul": "Başvuru kanalı", "sonuc": "Başvuru sonucu"}
    spec = _konu07(frame, roles, picks={"kosul": "Mobil", "sonuc": "Onaylandı"},
                   settings={"temel": 40, "yakalama": 90, "yanlis": 10})
    values = _step_values(spec, 10)
    assert values["Doğal frekans: durum var ve alarm"] == pytest.approx(3600)
    assert values["Doğal frekans: durum yok ve alarm"] == pytest.approx(600)
    assert values["P(F | A) = P(F ∩ A)/P(A)"] == pytest.approx(3600 / 4200)
    assert "gerçek alarmlar (3600) yanlış alarmlardan (600) çoktur" in spec.step(10).takeaway
    default = _konu07(frame, roles, picks={"kosul": "Mobil", "sonuc": "Onaylandı"})
    assert _values(default) == pytest.approx(_values(O7.alternative()))


def test_konu07_half_point_probabilities_get_one_more_digit() -> None:
    """1/800 = 0,00125: dört basamakta tam yarım. Kayan noktalı değer iki yöne de yuvarlanabileceği için beş basamakla
    yazılır; metin ile tablo aynı sayıyı gösterir."""

    assert kesir_basamak(Fraction(1, 800)) == 5 and kesir_basamak(Fraction(1, 32)) == 5
    assert kesir_basamak(Fraction(1, 8)) == 3 and kesir_basamak(Fraction(1, 3)) == 4
    rows = [("A", "Evet")] + [("A", "Hayır")] * 99 + [("B", "Evet")] * 300 + [("B", "Hayır")] * 400
    frame = pd.DataFrame(rows, columns=["Grup", "Durum"])
    spec = _konu07(frame, {"kosul": "Grup", "sonuc": "Durum"}, picks={"kosul": "A", "sonuc": "Evet"})
    assert run_lab(spec).all_passed
    assert "P(M \\cap S) = 0{,}00125" in spec.step(2).explanation


# --- Konu 8 ------------------------------------------------------------------------------------

def test_konu08_alternative_matches_a_direct_calculation() -> None:
    spec = O8.alternative()
    x = np.array([row[0] for row in O8.ALT_DAYS], dtype=float)
    y = np.array([row[1] for row in O8.ALT_DAYS], dtype=float)
    values = _values(spec)
    mean, variance = x.mean(), x.var()
    assert values["E(X) = Σ x f(x)"] == pytest.approx(mean) == 2.45
    assert values["Var(X) = Σ (x − μ)² f(x)"] == pytest.approx(variance)
    assert values["(n − 1)s²/n = Var(X)"] == pytest.approx(variance)
    assert values["σ = √Var(X)"] == pytest.approx(math.sqrt(variance))
    assert values["İlk 10 gözlemin ortalaması"] == pytest.approx(x[:10].mean())
    assert values["Bütün 100 gözlemin ortalaması = E(X)"] == pytest.approx(mean)
    assert values["Var(B) = (μ − en küçük)(en büyük − μ)"] == pytest.approx((mean - x.min()) * (x.max() - mean))
    assert values["P(X ≥ 2)"] == pytest.approx((x >= 2).mean())
    cov = np.mean((x - mean) * (y - y.mean()))
    assert values["Cov(X, Y) = E(XY) − E(X)E(Y)"] == pytest.approx(cov)
    assert values["ρ = Cov(X, Y)/(σX σY)"] == pytest.approx(np.corrcoef(x, y)[0, 1])
    assert values["P(X = 2, Y = 2)"] == pytest.approx(np.mean((x == 2) & (y == 2)))
    assert values["E(Π)"] == pytest.approx(150 * mean - 200)
    assert values["P(Π < 0)"] == pytest.approx(np.mean(150 * x - 200 < 0))
    assert sum(len(step.checks) for step in spec.steps) == 66


def test_konu08_without_y_asks_for_it_and_blank_y_cells_are_skipped() -> None:
    frame = pd.DataFrame({"Ürün": [0, 1, 1, 2, 2, 2, 3, 3, 4, 1], "İade": [0, 0, 1, None, 1, 2, 1, 0, 2, 1]})
    alone, _ = _konu08(frame, {"kesikli": "Ürün"})
    for number in (9, 10, 11):
        assert "İkinci kesikli değişken Y" in alone.step(number).explanation
        assert not alone.step(number).operations
    both, notes = _konu08(frame, {"kesikli": "Ürün", "ikinci": "İade"})
    assert run_lab(both).all_passed
    first = both.step(9).operations[0]
    assert isinstance(first, CompleteCases) and first.frame == "ciftler"
    assert "Y'si boş olan 1 gözlem" in both.step(9).takeaway
    assert _step_values(both, 1) == _step_values(alone, 1)  # X'in dağılımı Y'nin boş hücrelerinden etkilenmez


@pytest.mark.parametrize("frame, roles, message", [
    (pd.DataFrame({"x": np.arange(25.0)}), {"kesikli": "x"}, "en çok 20"),
    (pd.DataFrame({"x": [3.0] * 6}), {"kesikli": "x"}, "en az iki farklı"),
    (pd.DataFrame({"x": [1.0, 2.0, 2000000.0, 1.0, 2.0]}), {"kesikli": "x"}, "1.000.000"),
    (pd.DataFrame({"x": [1.123456, 2.0, 1.0, 2.0, 1.0]}), {"kesikli": "x"}, "dörtten fazla ondalık"),
    (pd.DataFrame({"x": [1.0, 2.0, 1.0, 2.0, 3.0], "y": [1.0, 2.0, 3.0, 4.0, 5.0]}),
     {"kesikli": "x", "ikinci": "x"}, "iki farklı sütun"),
    (pd.DataFrame({"x": [1.0, 2.0] * 6, "y": np.arange(12.0)}), {"kesikli": "x", "ikinci": "y"}, "en çok 10"),
])
def test_konu08_unusable_columns_are_rejected(frame, roles, message) -> None:
    with pytest.raises(K.UploadError, match=message):
        _konu08(frame, roles)


def test_konu08_two_values_decimals_and_no_loss() -> None:
    frame = pd.DataFrame({"Puan": [0.5, 2.5, 2.5, 0.5, 2.5, 2.5, 0.5, 2.5]})
    spec, _ = _konu08(frame, {"kesikli": "Puan"}, settings={"katki": 100, "sabit": 0})
    assert run_lab(spec).all_passed
    assert "B, A'nın aynısıdır" in spec.step(8).takeaway
    assert "Hiçbir değerde zarar oluşmaz" in spec.step(12).takeaway
    assert "x = 2,5" in spec.step(1).takeaway and "2{,}5" in spec.step(2).explanation
    values = _values(spec)
    assert values["E(B) = E(A)"] == pytest.approx(np.mean(frame["Puan"]))


def test_konu08_threshold_skips_a_certain_event() -> None:
    """En olası değer en küçük değerse "en az" olayı kesin olurdu; eşik bir sonraki değerdir."""

    frame = pd.DataFrame({"Hata": [0, 0, 0, 0, 1, 2, 0, 1]})
    spec, _ = _konu08(frame, {"kesikli": "Hata"})
    assert "P(X ≥ 1)" in _step_values(spec, 3)
    assert _step_values(spec, 3)["P(X ≥ 1)"] == pytest.approx(3 / 8)


def test_konu08_default_settings_match_the_alternative() -> None:
    spec, _ = _konu08(O8.sample(), {"kesikli": "Online sipariş sayısı", "ikinci": "Aynı gün teslim edilen"})
    assert _values(spec) == pytest.approx(_values(O8.alternative()))


def test_konu06_half_points_match_the_table() -> None:
    """Blok D düzeltmesi: 1/800 ve 3/800 dört basamakta tam yarımdır; metin ile metrikler beş basamakla aynı sayıyı
    gösterir. Frekans tablosu üç basamaklıdır: 3/80 metinde tablodaki gibi 0,037 yazılır."""

    from core.labs import ornek_konu06 as O6

    rows = [("A", "Evet")] + [("B", "Evet")] * 2 + [("B", "Hayır")] * 797
    table = K.UploadedTable("veri.csv", "csv", pd.DataFrame(rows, columns=["Grup", "Durum"]))
    case, _ = custom_case(O6.CUSTOM, table, CustomChoices(roles={"olay_e": "Grup", "olay_f": "Durum"},
                                                          picks={"olay_e": "A", "olay_f": "Evet"}))
    spec = O6.build(case)
    assert "0{,}00125 + 0{,}00375 - 0{,}00125 = 0{,}00375" in spec.step(8).explanation
    assert {check.label: check.decimals for check in spec.step(8).checks}["P(E)"] == 5
    rows = [("A", "Evet")] * 3 + [("B", "Hayır")] * 77
    table = K.UploadedTable("veri.csv", "csv", pd.DataFrame(rows, columns=["Grup", "Durum"]))
    case, _ = custom_case(O6.CUSTOM, table, CustomChoices(roles={"olay_e": "Grup", "olay_f": "Durum"},
                                                          picks={"olay_e": "A", "olay_f": "Evet"}))
    assert "3/80 \\approx 0{,}037$" in O6.build(case).step(4).explanation


# --- Konu 9 ------------------------------------------------------------------------------------

def test_konu09_alternative_matches_scipy() -> None:
    spec = O9.alternative()
    values = _values(spec)
    n, p, x = 10, 0.3, 3
    assert values["P(X = 3) formülle"] == pytest.approx(stats.binom.pmf(x, n, p))
    assert values["P(X ≥ 1)"] == pytest.approx(1 - 0.7 ** 10)
    binom = _step_values(spec, 3)
    assert binom["E(X) = Σ x f(x)"] == pytest.approx(3) and binom["Var(X) = Σ (x − μ)² f(x)"] == pytest.approx(2.1)
    assert values["λ = 18(20/60)"] == pytest.approx(6)
    assert values["P(X = 4) formülle"] == pytest.approx(stats.poisson.pmf(4, 6))
    assert values["E(X) = λ"] == pytest.approx(6) and values["Var(X) = λ"] == pytest.approx(6)
    assert values["P(X = 1) formülle"] == pytest.approx(stats.hypergeom.pmf(1, 25, 4, 5))
    assert values["Var(X) formülle"] == pytest.approx(5 * 0.16 * 0.84 * 20 / 24)
    assert values["P(Y = 0)"] == pytest.approx(math.exp(-6))
    assert values["P(Z ≥ 1)"] == pytest.approx(1 - stats.hypergeom.pmf(0, 25, 4, 5))
    assert sum(len(step.checks) for step in O9.alternative().steps) == 35


@pytest.mark.parametrize("changes, message", [
    ({"x": 12}, "n'den"),
    ({"saatlik": 120.0, "dakika": 60}, "en çok 50"),
    ({"r": 30}, "r \\(30\\)"),
    ({"n_h": 26}, "seçilen birim sayısı"),
    ({"x_h": 5}, "en çok 4"),
    ({"N": 6, "r": 4, "n_h": 5, "x_h": 2}, "en az 3"),
])
def test_konu09_invalid_values_are_explained(changes, message) -> None:
    values = dict(O9.ALT_VALUES)
    values.update(changes)
    with pytest.raises(K.UploadError, match=message):
        O9.validate(values)


def test_konu09_large_n_is_not_listed_and_p_half_draws_one_shape() -> None:
    spec = _konu09(n=15, p=0.5, x=7)
    assert run_lab(spec).all_passed
    assert "listelenmez" in spec.step(1).explanation
    assert _step_values(spec, 1)["2^15"] == 2 ** 15
    assert "tek bir dağılım çizilir" in spec.step(4).takeaway
    assert len(spec.step(4).checks) == 1


def test_konu09_small_probabilities_show_significant_digits() -> None:
    spec = _konu09(n=50, p=0.01, x=5)
    assert run_lab(spec).all_passed
    value = stats.binom.pmf(5, 50, 0.01)
    digits = next(check.decimals for check in spec.step(2).checks if check.label == "P(X = 5) yazılımla")
    assert digits > 4 and round(value, digits) != 0
    tiny = _konu09(n=50, p=0.01, x=40)
    assert "10⁻¹²'den küçük" in tiny.step(2).takeaway


def test_konu09_fractional_lambda_and_single_draw() -> None:
    spec = _konu09(saatlik=7.5, dakika=10, x_pois=2, N=10, r=3, n_h=1, x_h=1)
    assert run_lab(spec).all_passed
    assert "\\approx 1{,}25" not in spec.step(5).explanation and "= 1{,}25" in spec.step(5).explanation
    assert "çarpanı 1'dir" in spec.step(7).takeaway
    odd = _konu09(saatlik=7.0, dakika=10)
    assert "\\approx 1{,}1667" in odd.step(5).explanation


def test_konu09_default_values_and_file_name() -> None:
    params = O9.VARIANTS.params
    spec = params.build(parameter_values(params))
    assert spec.source == "kendi" and script_filename(spec, "R") == "ikt217_konu09_kendi_degerlerim.R"
    assert _values(spec) == pytest.approx(_values(O9.alternative()))


def _run(spec, language: str, folder: Path):
    path = folder / script_filename(spec, language)
    path.write_text(render_script(spec, language), encoding="utf-8")
    command = [sys.executable] if language == "Python" else ["Rscript"]
    return subprocess.run(command + [path.name], cwd=folder, capture_output=True, encoding="utf-8", errors="replace",
                          timeout=300, env={**__import__("os").environ, "MPLBACKEND": "Agg", "LANG": "C.UTF-8"})


@pytest.mark.parametrize("changes", [
    {"n": 15, "p": 0.5, "x": 7},
    {"n": 4, "p": 0.07, "x": 0, "saatlik": 7.0, "dakika": 10, "x_pois": 0, "N": 9, "r": 0, "n_h": 3, "x_h": 0},
    {"n": 50, "p": 0.99, "x": 50, "saatlik": 120.0, "dakika": 25, "x_pois": 150, "N": 500, "r": 500, "n_h": 500,
     "x_h": 500},
    {"n": 1, "p": 0.5, "x": 1, "saatlik": 0.5, "dakika": 1, "x_pois": 0, "N": 2, "r": 1, "n_h": 2, "x_h": 1},
], ids=["n15", "kucuk", "uc-degerler", "tek-deneme"])
def test_konu09_own_values_are_reproduced_in_both_languages(changes, tmp_path: Path) -> None:
    spec = _konu09(**changes)
    assert run_lab(spec).all_passed
    checks = sum(len(step.checks) for step in spec.steps)
    for language in ["Python"] + (["R"] if shutil.which("Rscript") else []):
        place = tmp_path / language
        place.mkdir()
        result = _run(spec, language, place)
        assert result.returncode == 0, (language, result.stdout[-1500:] + result.stderr[-1500:])
        assert result.stdout.count("  OK   ") == checks, language


# --- Bağımsız inceleme bulguları (Blok D) ------------------------------------------------------------

NEAR_TIE = pd.DataFrame([("A", "Evet")] * 100 + [("A", "Hayır")] * 101 + [("B", "Evet")] * 299
                        + [("B", "Hayır")] * 302, columns=["Grup", "Durum"])
LONG_VALUES = pd.DataFrame({"x": [-12.75, -3, 5, 5, -12.75, 2.5, 5], "y": [-0.25, 1, 1, -0.25, -0.25, 1, -0.25]})
BASIS_POINTS = pd.DataFrame({"x": [-0.0025, 0, 0.0025, 0, 0, 0.0025, -0.0025, 0.0025], "y": [1, 2, 3, 2, 2, 3, 1, 2]})
MANY_VALUES = pd.DataFrame({"x": [0, 1, 2, 5, 9, 14, 20, 30, 31, 33, 40, 2, 2, 5]})
SCIENTIFIC = pd.DataFrame({"x": [0.0001, 0.0002, 0.0003, 0.0001, 0.0002],
                           "y": [100000, 200000, 100000, 200000, 100000]})


def test_konu07_near_ties_are_written_with_enough_digits() -> None:
    """802 gözlemde P(S) ≈ 0,497506 ile P(S | M) ≈ 0,497512: dört basamakta ikisi de 0,4975 görünürdü."""

    spec = _konu07(NEAR_TIE, {"kosul": "Grup", "sonuc": "Durum"}, picks={"kosul": "A", "sonuc": "Evet"})
    assert run_lab(spec).all_passed
    assert "0,497506" in spec.step(1).takeaway and "0,497512" in spec.step(1).takeaway
    decimals = {check.label: check.decimals for check in spec.step(1).checks}
    assert decimals["P(S) = 399/802"] == decimals["P(S | M) = 100/201"] == 6
    assert "(yaklaşık 0,497512) P(S)'den (yaklaşık 0,497506) büyüktür" in spec.step(5).takeaway
    assert "0,25062" in spec.step(8).takeaway and "0,25063" in spec.step(8).takeaway


@pytest.mark.parametrize("settings, phrase", [
    ({"temel": 30, "yakalama": 90, "yanlis": 45}, "durum varkenkinden küçük olsa da"),
    ({"temel": 40, "yakalama": 50, "yanlis": 50}, "alarm durumu ayırt etmez"),
    ({"temel": 1, "yakalama": 92, "yanlis": 0}, "her alarm gerçektir"),
    ({"temel": 50, "yakalama": 50, "yanlis": 50}, "alarmların yarısı yanlıştır"),
    ({"temel": 40, "yakalama": 90, "yanlis": 10}, "bu sıra tersine dönebilir"),
])
def test_konu07_alarm_wording_follows_the_settings(settings, phrase) -> None:
    spec = _konu07(O7.sample(), {"kosul": "Başvuru kanalı", "sonuc": "Başvuru sonucu"},
                   picks={"kosul": "Mobil", "sonuc": "Onaylandı"}, settings=settings)
    assert run_lab(spec).all_passed
    assert phrase in spec.step(10).takeaway
    assert "nadir" not in spec.step(10).explanation


def test_konu08_break_even_is_not_a_loss() -> None:
    """15 × 8,2 − 123 kayan noktayla −1,4·10⁻¹⁴ çıkar; kâr sıfırdır, zarar değildir."""

    frame = pd.DataFrame({"x": [8.2, 8.2, 9.2, 10.2, 9.2, 10.2, 8.2, 9.2]})
    spec, _ = _konu08(frame, {"kesikli": "x"}, settings={"katki": 15, "sabit": 123})
    assert run_lab(spec).all_passed
    assert _step_values(spec, 12)["P(Π < 0)"] == 0
    assert "Hiçbir değerde zarar oluşmaz" in spec.step(12).takeaway


@pytest.mark.parametrize("settings, formula, phrase", [
    ({"katki": 1, "sabit": 10000}, "\\Pi = X - 10000$", "hiçbir değerde pozitif kâr oluşmaz"),
    ({"katki": 100, "sabit": 500}, "\\Pi = 100X - 500$", "hiçbir değerde pozitif kâr oluşmaz"),
    ({"katki": 1000, "sabit": 0}, "\\Pi = 1000X$", "Zarar olmasa da"),
    ({"katki": 150, "sabit": 200}, "\\Pi = 150X - 200$", "her gözlemde kâr edileceği anlamına gelmez"),
    ({"katki": 50, "sabit": 200}, "\\Pi = 50X - 200$", "tek tek gözlemlerde yine de kâr edilebilir"),
])
def test_konu08_profit_texts_follow_the_values(settings, formula, phrase) -> None:
    roles = {"kesikli": "Online sipariş sayısı", "ikinci": "Aynı gün teslim edilen"}
    spec, _ = _konu08(O8.sample(), roles, settings=settings)
    assert run_lab(spec).all_passed
    assert formula in spec.step(12).explanation and phrase in spec.step(12).takeaway
    assert " − 0" not in spec.step(12).takeaway and "1X" not in spec.step(12).explanation


def test_konu08_variance_ties_and_exact_standard_deviation() -> None:
    spec, _ = _konu08(pd.DataFrame({"x": [0] * 2 + [1] * 4 + [4] * 4}), {"kesikli": "x"})
    assert "x = 0 ve 4 merkezden en uzak değerlerdir, ama en büyük katkı x = 4 değerinden" in spec.step(7).takeaway
    spec, _ = _konu08(pd.DataFrame({"x": [0, 1] * 3}), {"kesikli": "x"})
    assert "σ = 0,5." in spec.step(7).takeaway and "en uzak değerlerden gelir (x = 0 ve 1)" in spec.step(7).takeaway
    spec, _ = _konu08(pd.DataFrame({"x": [0, 0.025] * 3}), {"kesikli": "x"})  # σ = 0,0125: üç basamakta tam yarım
    assert run_lab(spec).all_passed
    assert "σ = 0,0125." in spec.step(7).takeaway
    assert {check.label: check.decimals for check in spec.step(7).checks}["σ = √Var(X)"] == 4


def test_konu08_event_has_more_than_one_value() -> None:
    spec, _ = _konu08(pd.DataFrame({"x": [0, 1, 2, 2, 2]}), {"kesikli": "x"})  # en olası değer en büyük değer
    assert "\\{X \\geq 1\\} = \\{1, 2\\}" in spec.step(3).explanation
    spec, _ = _konu08(pd.DataFrame({"x": [0, 1] * 3}), {"kesikli": "x"})
    assert "yalnız iki farklı değer alır" in spec.step(3).explanation


def test_konu08_sorted_file_and_exact_correlation() -> None:
    spec, _ = _konu08(pd.DataFrame({"x": sorted([0, 1, 1, 2, 2, 2, 3, 3, 4, 5, 2, 1])}), {"kesikli": "x"})
    assert "çizgi dalgalanmaz, E(X)'e aşağıdan" in spec.step(6).takeaway
    frame = pd.DataFrame({"x": [1, 2, 3, 2, 1, 3, 2], "y": [2, 3, 4, 3, 2, 4, 3]})  # Y = X + 1
    spec, _ = _konu08(frame, {"kesikli": "x", "ikinci": "y"})
    assert "ρ = 1." in spec.step(10).takeaway
    assert "f(2) = 3/7 ≈ 0,429." in spec.step(4).takeaway  # sıklık tablosu üç basamaklıdır
    frame = pd.DataFrame({"x": [-1, 0, 1] * 3, "y": [1, 0, 1] * 3})
    spec, _ = _konu08(frame, {"kesikli": "x", "ikinci": "y"})
    assert "Cov(X, Y) = 0; ρ = 0." in spec.step(10).takeaway


def test_konu08_negative_long_and_small_values() -> None:
    spec, _ = _konu08(LONG_VALUES, {"kesikli": "x", "ikinci": "y"})
    assert "(\\mu - (−12{,}75))/(5 - (−12{,}75))" in spec.step(8).explanation
    assert "P(X = x*, Y = y*): ortak" in [op.comment for op in spec.step(11).operations]
    spec, _ = _konu08(BASIS_POINTS, {"kesikli": "x", "ikinci": "y"})
    assert run_lab(spec).all_passed
    assert "E(X) = 0,0003125." in spec.step(5).takeaway and "Var(X) ≈ 0,00000381" in spec.step(7).takeaway
    assert {check.label: check.decimals for check in spec.step(7).checks}["Var(X) = Σ (x − μ)² f(x)"] == 8


def test_konu08_many_values_are_not_listed_with_an_ellipsis() -> None:
    spec, _ = _konu08(MANY_VALUES, {"kesikli": "x"})
    assert "(en küçüğü 0, en büyüğü 40)" in spec.step(1).explanation
    assert "\\sum_{x < 40} f(x)" in spec.step(2).explanation and "en küçük olasılık" in spec.step(2).explanation
    assert "9 değer içerir" in spec.step(3).explanation and "\\sum_{x \\geq 2} f(x)" in spec.step(3).explanation
    assert "…" not in spec.step(1).explanation and "\\ldots" not in spec.step(3).explanation
    shown = [op for op in spec.step(1).operations if isinstance(op, ShowFrame)]
    assert shown and len(shown[0].columns) == 3  # değer, gözlem sayısı ve f(x)


def test_r_scripts_avoid_scientific_names(tmp_path: Path) -> None:
    """R 100000'i "1e+05", 0.0001'i "1e-04" adıyla yazar; tablo satırları koddaki "100000" adıyla seçilemezdi."""

    from core.codegen.r_gen import _exponential

    assert [_exponential(v) for v in (100000, 0.0001, -100000, 120000, 0.00012, 10000, 0.001, "100000")] == [
        True, True, True, False, False, False, False, False]
    spec, _ = _konu08(SCIENTIFIC, {"kesikli": "x", "ikinci": "y"})
    assert "options(scipen = 999)" in render_script(spec, "R")
    assert "scipen" not in render_script(O8.alternative(), "R")
    if shutil.which("Rscript"):
        (tmp_path / "veri.csv").write_text(SCIENTIFIC.to_csv(index=False), encoding="utf-8")
        result = _run(spec, "R", tmp_path)
        assert result.returncode == 0, result.stdout[-1500:] + result.stderr[-1500:]
        assert result.stdout.count("  OK   ") == sum(len(step.checks) for step in spec.steps)


def test_konu09_events_at_the_ends_and_single_trial() -> None:
    spec = _konu09(x=0)
    assert "{X ≤ 0} ile {X = 0} aynı olaydır" in spec.step(2).takeaway
    assert "tek bir dizi vardır" in spec.step(1).takeaway
    assert "x = n iken {X ≥ 10} ile {X = 10} aynı olaydır" in _konu09(x=10).step(2).takeaway
    single = _konu09(n=1, p=0.5, x=1)
    assert "Tek denemede $2^{1} = 2$ olası sonuç vardır" in single.step(1).explanation
    assert "1 bağımsız" not in single.step(1).explanation and "1 deneme bağımsızsa" not in single.step(1).explanation


def test_konu09_half_points_and_fractional_lambda() -> None:
    spec = _konu09(n=5, p=0.05, x=5)  # 0,05⁵ = 0,0000003125: yedi basamakta tam yarım
    assert "P(X = 5) = 0,0000003125" in spec.step(2).takeaway
    assert {check.label: check.decimals for check in spec.step(2).checks}["P(X = 5) formülle"] == 10
    spec = _konu09(saatlik=3.5, dakika=1, x_pois=0)
    assert "\\lambda = 3{,}5(1/60) \\approx 0{,}0583" in spec.step(5).explanation
    assert "(λ ≈ 0,0583)" in spec.step(8).explanation
    table = next(op for op in _konu09(n=10, p=0.3, x=9).step(1).operations if isinstance(op, GroupSummary))
    assert table.decimals >= 6  # P(X = 9) ≈ 0,000138 tabloda da görünür


def test_konu09_degenerate_hypergeometric_wording() -> None:
    assert "iki modelde de varyans sıfırdır" in _konu09(N=9, r=0, n_h=3, x_h=0).step(7).takeaway
    assert "Bütün anakütle seçildiği için" in _konu09(N=25, r=4, n_h=25, x_h=4).step(7).takeaway


def _rows(*groups) -> pd.DataFrame:
    return pd.DataFrame([row for row, count in groups for _ in range(count)], columns=["Grup", "Durum"])


def test_konu07_texts_use_the_digits_of_the_metric_or_table() -> None:
    roles, picks = {"kosul": "Grup", "sonuc": "Durum"}, {"kosul": "A", "sonuc": "Evet"}
    spec = _konu07(_rows((("A", "Evet"), 1), (("A", "Hayır"), 2), (("B", "Hayır"), 29)), roles, picks)
    assert "0,03125 ile yaklaşık 0,3333 " in spec.step(1).takeaway  # metrikler: 0,03125 ve 0,3333
    spec = _konu07(_rows((("A", "Evet"), 1), (("B", "Evet"), 2), (("B", "Hayır"), 29)), roles, picks)
    assert "sonsal P(M | S) ≈ 0,3333 olur" in spec.step(8).takeaway
    spec = _konu07(_rows((("A", "Evet"), 1), (("A", "Hayır"), 3), (("B", "Evet"), 40), (("B", "Hayır"), 52)),
                   roles, picks)  # n = 96: ortak tablo beş basamaklı (3/96 = 0,03125)
    assert "P(M \\cap S) \\approx 0{,}01042" in spec.step(2).explanation and "P(M) ≈ 0,04167" in spec.step(2).takeaway
    spec = _konu07(_rows((("A", "Evet"), 1), (("B", "Evet"), 3999), (("B", "Hayır"), 5999)), roles, picks)
    assert "P(S)'den (yaklaşık 0,40004)" in spec.step(5).takeaway  # tablo: 0,40004
    spec = _konu07(_rows((("A", "Evet"), 2), (("A", "Hayır"), 3), (("B", "Evet"), 3), (("B", "Hayır"), 2)),
                   roles, picks)
    assert "iki grubun büyüklüğü aynıdır (5 gözlem)" in spec.step(4).takeaway


LARGE = pd.DataFrame({"x": [999999, 999998, 999997, 999999, 999998, 999997, 999999],
                      "y": [999999, 999997, 999998, 999998, 999999, 999997, 999997]})


def test_konu08_large_values_use_the_definition_for_covariance(tmp_path: Path) -> None:
    """E(XY) ≈ 10¹² ile E(X)E(Y) birbirini götürür: kısa yol formülü kayan noktada basamak kaybeder (R'de 0,1632,
    Python'da 0,1630; kesin değer 8/49 ≈ 0,1633). Kovaryans ve ρ tanım formülünden gelir."""

    spec, _ = _konu08(LARGE, {"kesikli": "x", "ikinci": "y"})
    assert run_lab(spec).all_passed
    step = spec.step(10)
    assert "Cov_XY" not in [getattr(op, "name", "") for op in step.operations]
    assert "tanım formülüyle hesaplanır: Cov(X, Y) ≈ 0,1633" in step.takeaway and "10¹²" in step.takeaway
    assert _step_values(spec, 10)["Cov(X, Y) tanım formülüyle"] == pytest.approx(8 / 49)
    small, _ = _konu08(pd.DataFrame({"x": [1, 2, 3, 2, 1, 3, 2], "y": [2, 3, 4, 3, 1, 4, 3]}),
                       {"kesikli": "x", "ikinci": "y"})
    assert "Cov_XY" in [getattr(op, "name", "") for op in small.step(10).operations]  # olağan değerlerde iki formül
    if shutil.which("Rscript"):
        (tmp_path / "veri.csv").write_text(LARGE.to_csv(index=False), encoding="utf-8")
        result = _run(spec, "R", tmp_path)
        assert result.returncode == 0, result.stdout[-1500:] + result.stderr[-1500:]


def test_konu08_joint_texts_follow_the_table_and_ties() -> None:
    pairs = [(1, 1)] * 40 + [(1, 2)] * 3 + [(2, 1)] * 23 + [(2, 2)] * 30  # tablo beş basamaklı
    spec, _ = _konu08(pd.DataFrame(pairs, columns=["x", "y"]), {"kesikli": "x", "ikinci": "y"})
    assert "olasılığı yaklaşık 0,41667" in spec.step(9).takeaway
    pairs = [(1, 1)] * 3 + [(1, 0)] + [(0, 1)] + [(0, 0)] * 3
    spec, _ = _konu08(pd.DataFrame(pairs, columns=["x", "y"]), {"kesikli": "x", "ikinci": "y"})
    assert "en olası çiftler (x, y) = (0, 0) ve (1, 1); her birinin olasılığı 0,375" in spec.step(9).takeaway
    assert "Aynı olasılıklı en olası çiftlerden ilkinin hücresinde" in spec.step(11).explanation


def test_konu08_break_even_profit_and_scripts_print_no_negative_zero(tmp_path: Path) -> None:
    frame = pd.DataFrame({"x": [8.2, 8.2, 9.2, 10.2, 9.2, 10.2, 8.2, 9.2]})
    spec, _ = _konu08(frame, {"kesikli": "x"}, settings={"katki": 15, "sabit": 123})
    profits = run_lab(spec).state.frames["dagilim"]["kar"].tolist()
    assert profits == [0, 15, 30]  # kayan nokta artığı (−1,4·10⁻¹⁴) yok
    (tmp_path / "veri.csv").write_text(frame.to_csv(index=False), encoding="utf-8")
    for language in ["Python"] + (["R"] if shutil.which("Rscript") else []):
        place = tmp_path / language
        place.mkdir()
        (place / "veri.csv").write_text(frame.to_csv(index=False), encoding="utf-8")
        result = _run(spec, language, place)
        assert result.returncode == 0, (language, result.stdout[-1500:] + result.stderr[-1500:])
        assert not re.search(r"-0(\.0+)?(?![\d.])", result.stdout), (language, result.stdout[-1500:])


def test_frame_decimals_keep_short_values_and_round_long_ones() -> None:
    from core.labs.tables import frame_decimals

    assert frame_decimals([17 / 21, 4 / 21]) == 4  # 15 basamakta sondaki sıfır atılsa da uzun
    assert frame_decimals([0.03125, 1 / 3]) == 4  # uzun sütun: kısa görünen tek değer basamağı uzatmaz
    assert frame_decimals([0.93082126860974, 2 ** 0.5 / 7, -(3 ** 0.5) / 5]) == 4  # rastlantıyla kısa görünen değer
    assert frame_decimals([0.345678, 2.5]) == 6 and frame_decimals([0.1 + 0.2]) == 2
    assert frame_decimals([0.9830399999999992, 0.5]) == 5  # 12 anlamlı basamakta gürültü atılır: 0,98304
    assert frame_decimals([0.48424328399999, 1.3e-30]) == 9  # 0,484243284; x = μ artığı (1e-30) sıfır sayılır
    assert frame_decimals([61709885016.125, 0.5]) == 3  # yüklenen veri gibi kısa değerler tam
    assert frame_decimals([41.0082376123, 41.5]) == 10 and frame_decimals([12345.6789012, 1.5]) == 7
    assert frame_decimals([123456789.0123 / 7, 2.5]) == 4  # uzun sütun: en çok 13 anlamlı basamak
    spec, _ = _konu08(pd.DataFrame({"x": [0] + [1] * 20}), {"kesikli": "x"})
    assert "yaklaşık 0,04319" in spec.step(7).takeaway  # (x − μ)² f(x) sütunu beş basamaklı


def test_konu09_degenerate_event_clauses_and_short_ranges() -> None:
    assert "0 < x < n değerlerinde" in _konu09(x=10).step(2).takeaway
    single = _konu09(n=1, p=0.5, x=1)
    assert "0 < x < n" not in single.step(2).takeaway and "tek deneme başarılı olur mu" in single.step(8).explanation
    two = _konu09(n=2, p=0.5, x=1)
    assert "x = 1 ve 2 olasılıklarını" in two.step(2).takeaway and "(0, 1 ve 2)" in two.step(4).explanation


def _shown_cells(spec, number: int) -> list[str]:
    """Adımdaki ShowFrame tablolarının ekrandaki hücreleri (uygulamanın biçimiyle)."""

    from topics.lab_ui import _frame

    state = run_lab(spec).state
    cells = []
    for op in spec.step(number).operations:
        if isinstance(op, ShowFrame):
            html = _frame(state.frames[op.frame][list(op.columns)], spec.label, True, dict(op.decimals)).to_html()
            cells += re.findall(r">([−-]?[\d.]+,\d+|[−-]?\d+)</td>", html)
    return cells


def test_tables_and_texts_agree_at_half_points_and_with_float_noise() -> None:
    """n = 1600: 1/1600 = 0,000625 beş basamakta tam yarımdır; tablo ve metin altı basamakla aynı sayıyı gösterir.
    (x − μ)² f(x) sütununda kayan nokta gürültüsü ve x = μ artığı tablonun basamağını değiştirmez."""

    spec = _konu07(_rows((("A", "Evet"), 1), (("A", "Hayır"), 2), (("B", "Evet"), 700), (("B", "Hayır"), 897)),
                   {"kosul": "Grup", "sonuc": "Durum"}, picks={"kosul": "A", "sonuc": "Evet"})
    assert "P(M \\cap S) = 0{,}000625" in spec.step(2).explanation
    assert {op.result: op.decimals for op in spec.step(2).operations if isinstance(op, CrossTab)}["ortak"] == 6
    pairs = [(1, 1)] * 803 + [(1, 2)] * 2 + [(2, 1)] * 400 + [(2, 2)] * 395
    spec, _ = _konu08(pd.DataFrame(pairs, columns=["x", "y"]), {"kesikli": "x", "ikinci": "y"})
    assert "olasılığı 0,501875" in spec.step(9).takeaway
    counts = {103: 4, 105: 10, 106: 7, 108: 4}
    spec, _ = _konu08(pd.DataFrame({"x": [v for v, c in counts.items() for _ in range(c)]}), {"kesikli": "x"})
    assert "(x = 108): 1,048576" in spec.step(7).takeaway and "1,048576" in _shown_cells(spec, 7)
    counts = {1001: 3, 1014: 2, 1016: 3, 1018: 2, 1019: 3, 1020: 3, 1022: 3, 1024: 3}
    spec, _ = _konu08(pd.DataFrame({"x": [v for v, c in counts.items() for _ in range(c)]}), {"kesikli": "x"})
    assert "yaklaşık 34,1202" in spec.step(7).takeaway and "34,1202" in _shown_cells(spec, 7)
    counts = {-15: 2, -11: 5, -6: 2, -4: 9, 3: 8, 5: 6, 7: 10, 17: 6}
    spec, _ = _konu08(pd.DataFrame({"x": [v for v, c in counts.items() for _ in range(c)]}), {"kesikli": "x"})
    assert "\\approx 0{,}5293$" in spec.step(8).explanation and "0,5293" in _shown_cells(spec, 8)
    spec, _ = _konu08(pd.DataFrame({"x": [-3.3, -3.3, 12.3, 12.3, 27.9, 27.9]}), {"kesikli": "x"})
    assert "katkısı 81,12" in spec.step(7).takeaway and "81,12" in _shown_cells(spec, 7)
    assert "0,0000000000" in _shown_cells(O9.alternative(), 3)  # x = μ: artık (1e-30) sıfır görünür
    counts = {5: 1, 7: 1, 12: 3, 15: 6, 19: 3, 20: 1, 25: 2, 26: 3, 28: 2, 32: 1, 33: 2, 35: 1, 36: 3, 37: 5, 39: 5,
              41: 9}  # uzun kesin değerler (27,281982421875) dört basamakla
    spec, _ = _konu08(pd.DataFrame({"x": [v for v, c in counts.items() for _ in range(c)]}), {"kesikli": "x"})
    assert "(yaklaşık 27,282)" in spec.step(7).takeaway and "11,9376" in _shown_cells(spec, 7)
    spec = _konu07(_rows((("A", "Evet"), 1), (("A", "Hayır"), 3), (("B", "Evet"), 40), (("B", "Hayır"), 52)),
                   {"kosul": "Grup", "sonuc": "Durum"}, picks={"kosul": "A", "sonuc": "Evet"})
    assert "P(M \\cap S) \\approx 0{,}01042$" in spec.step(8).explanation and "0,01042" in _shown_cells(spec, 8)
    spec, _ = _konu08(pd.DataFrame({"x": [-15, -15, -11, 3, 3, 7, 7, 17]}), {"kesikli": "x"},
                      settings={"katki": 10, "sabit": 0})
    cells = _shown_cells(spec, 12)
    assert "−15" in cells and "-15" not in cells  # tamsayı sütununda da tipografik eksi


# --- Metin kuralları -----------------------------------------------------------------------------

def _own_specs():
    frame = pd.DataFrame({"Kanal": ["A", "B", "A", "C", "B", "A", "C", "B", "A", "B"],
                          "Sonuç": ["Evet", "Hayır", "Evet", "Evet", "Hayır", "Hayır", "Evet", "Evet", "Evet",
                                    "Hayır"]})
    yield _konu07(frame, {"kosul": "Kanal", "sonuc": "Sonuç"}, picks={"kosul": "B", "sonuc": "Evet"},
                  settings={"temel": 7, "yakalama": 81, "yanlis": 13})
    data = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4, 4, 7, 2, 1], "y": [0, 1, 1, 2, 1, 3, 2, 4, 5, 2, 0]})
    yield _konu08(data, {"kesikli": "x", "ikinci": "y"}, settings={"katki": 37, "sabit": 91})[0]
    yield _konu08(LONG_VALUES, {"kesikli": "x", "ikinci": "y"}, settings={"katki": 1, "sabit": 0})[0]
    yield _konu08(BASIS_POINTS, {"kesikli": "x", "ikinci": "y"})[0]
    yield _konu08(MANY_VALUES, {"kesikli": "x"})[0]
    yield _konu08(LARGE, {"kesikli": "x", "ikinci": "y"})[0]
    yield _konu07(NEAR_TIE, {"kosul": "Grup", "sonuc": "Durum"}, picks={"kosul": "A", "sonuc": "Evet"},
                  settings={"temel": 30, "yakalama": 90, "yanlis": 45})
    yield _konu09(n=7, p=0.43, x=5, saatlik=13.5, dakika=7, x_pois=3, N=31, r=9, n_h=6, x_h=2)
    yield _konu09(n=48, p=0.37, x=17, saatlik=119.5, dakika=25, x_pois=148, N=488, r=233, n_h=377, x_h=181)


def test_texts_add_no_suffix_to_runtime_numbers() -> None:
    for spec in (O7.alternative(), O8.alternative(), O9.alternative(), *_own_specs()):
        for text in _texts(spec):
            plain = re.sub(r"\$[^$]*\$", "", text)
            for word in re.findall(r"%?\d[\d,]*'[a-zçğıöşü]+", plain):
                assert word in ALLOWED_SUFFIXES, (spec.topic_key, word, text)
            for formula in re.findall(r"\$([^$]*)\$'[a-zçğıöşü]+", text):
                if formula.strip() not in CONSTANT_FORMULAS:
                    assert not re.search(r"\d\}?$", formula.strip()), (spec.topic_key, formula, text)


def test_metric_titles_fit_their_columns() -> None:
    from topics.lab_ui import _METRICS, _metrics

    limit = {4: 28, 3: 38, 2: 57, 1: 110}
    for spec in (O7.alternative(), O8.alternative(), O9.alternative(), *_own_specs()):
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
