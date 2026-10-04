"""Konu 10–12 alternatif örnekleri ve kendi değerlerini gir: değerler motordan bağımsız bir hesapla (kesirler, math,
scipy) doğrulanır; tablo kuralı (ders kuralıyla yuvarlama, ``E.yuvarla``), uç değerlerdeki metinler, geçersiz
değerlerin iletileri, metin kuralları ve iki dilde yeniden üretim denetlenir."""

from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import sys
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from scipy import stats

from core.codegen.base import render_script, render_step, script_filename
from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs import ornek_konu10 as O10
from core.labs import ornek_konu11 as O11
from core.labs import ornek_konu12 as O12
from core.labs.ornek import ders_yuvarla, parameter_values
from core.labs.runner import run_lab

ALLOWED_SUFFIXES = {"1'den", "1'dir", "1'in", "1'i", "0,50'den", "3'teki", "11'de", "11'deki", "11'in", "2'deki",
                    "0'dır", "12.6'daki", "5'ten"}
"""Rakamdan sonra ek yalnız sabit ifadelerde (ör. "1'den büyük", "Adım 3'teki", "Konu 11'deki tablo"); değişken sayılara
ek getirilmez."""
MODULES = (O10, O11, O12)


def _values(spec) -> dict[str, float]:
    return {check.label: check.expected for step in spec.steps for check in step.checks}


def _step_values(spec, number: int) -> dict[str, float]:
    return {check.label: check.expected for check in spec.step(number).checks}


def _texts(spec) -> list[str]:
    return [text for step in spec.steps for text in (step.explanation, step.takeaway, step.code_note)]


def _build(module, **changes):
    values = dict(module.ALT_VALUES)
    values.update(changes)
    return module.build(values)


def _half_up(value: float, digits: int) -> float:
    """Bağımsız ders kuralı: kısa ondalık yazımın yarımı sıfırdan uzağa."""

    return float(Decimal(repr(value)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))


def _table(z: float) -> float:
    return _half_up(round(float(stats.norm.cdf(z)), 12), 4)


# --- Konu 10 -------------------------------------------------------------------------------------

def test_konu10_alternative_matches_an_independent_calculation() -> None:
    spec = O10.alternative()
    values = _values(spec)
    assert values["f(x) = 1/(90 − 30)"] == pytest.approx(1 / 60)
    assert values["P(42 ≤ X ≤ 78): dikdörtgenin alanı"] == pytest.approx(0.6)
    assert values["P(42 ≤ X ≤ 78): uzunluk oranı"] == pytest.approx(0.6)
    assert values["μ = (a + b)/2"] == 60 and values["σ² = (b − a)²/12"] == pytest.approx(300)
    assert values["σ"] == pytest.approx(math.sqrt(300))
    assert values["f(x) = 1/0,4"] == pytest.approx(2.5) and values["Toplam alan w × f(x)"] == pytest.approx(1)
    assert [values[label] for label in ("μ − σ", "μ + σ", "μ − 2σ", "μ + 2σ")] == [246, 254, 242, 258]
    for k, label in ((1, "μ ± σ"), (2, "μ ± 2σ"), (3, "μ ± 3σ")):
        assert values[label] == pytest.approx(stats.norm.cdf(k) - stats.norm.cdf(-k), abs=1e-7)
    assert values["μ'nun solundaki alan"] == pytest.approx(0.5, abs=1e-9)
    assert values["z(257)"] == pytest.approx(1.75) and values["z(243)"] == pytest.approx(-1.75)
    assert values["x(z = −1,25)"] == pytest.approx(245)
    assert values["z_A = (62 − 55)/5"] == pytest.approx(1.4) and values["z_B = (81 − 72)/7,5"] == pytest.approx(1.2)
    exact = stats.norm.cdf(2) - stats.norm.cdf(-1)
    assert values["P(246 ≤ X ≤ 258)"] == pytest.approx(exact, abs=1e-7)
    assert values["P(z₁ ≤ Z ≤ z₂)"] == pytest.approx(values["P(246 ≤ X ≤ 258)"], abs=1e-12)
    assert values["z(416)"] == pytest.approx(2) and values["z(394)"] == pytest.approx(-0.75)
    assert values["P(384 ≤ X ≤ 416)"] == pytest.approx(stats.norm.cdf(2) - stats.norm.cdf(-2), abs=1e-7)
    assert sum(len(step.checks) for step in spec.steps) == 31


@pytest.mark.parametrize("changes, message", [
    ({"a": 90, "b": 30}, "b'den"),
    ({"c": 20}, "a ≤ c < d ≤ b"),
    ({"d": 42}, "a ≤ c < d ≤ b"),
    ({"x": 300}, "μ ± 10σ"),
    ({"x1": 258, "x2": 246}, "x₂'den"),
    ({"x2": 291}, "μ ± 10σ"),
    ({"v2": 416}, "iki farklı değer"),
    ({"v1": 481}, "μ ± 10σ"),
])
def test_konu10_invalid_values_are_explained(changes, message) -> None:
    values = dict(O10.ALT_VALUES)
    values.update(changes)
    with pytest.raises(K.UploadError, match=re.escape(message)):
        O10.validate(values)


def test_konu10_texts_follow_the_values() -> None:
    whole = _build(O10, c=30, d=90)
    assert "bütününü kapsar" in whole.step(1).takeaway and _step_values(whole, 1)["P(30 ≤ X ≤ 90): uzunluk oranı"] == 1
    wide = _build(O10, w=2)
    assert "Genişlik 1'den büyük" in wide.step(2).explanation and "1'i aşar" in wide.step(2).takeaway
    unit = _build(O10, w=1)
    assert "tam 1'dir" in unit.step(2).explanation
    center = _build(O10, x=250, z0=0)
    assert "ortalamanın kendisidir: z = 0" in center.step(4).takeaway
    assert "z = 0 olan değer ortalamanın kendisidir" in center.step(4).takeaway
    assert len(center.step(4).checks) == 2
    same = _build(O10, xA=60, muA=50, sdA=5, xB=70, muB=60, sdB=5)
    assert "iki ölçekte göreli konum aynıdır" in same.step(5).takeaway
    reverse = _build(O10, xA=81, muA=72, sdA=7.5, xB=62, muB=55, sdB=5)
    assert "Ham değer A ölçeğinde daha yüksektir (81 > 62)" in reverse.step(5).takeaway
    assert "sıralaması farklıdır" in reverse.step(5).takeaway
    sigma = _build(O10, x1=246, x2=254)
    assert "Adım 3'teki μ ± σ alanıyla aynıdır" in sigma.step(6).takeaway
    assert _step_values(sigma, 6)["P(246 ≤ X ≤ 254)"] == pytest.approx(_step_values(sigma, 3)["μ ± σ"], abs=1e-12)
    third = _build(O10, a=0, b=3, c=0.5, d=1.5)
    assert "≈ 0,3333" in third.step(1).explanation or "\\approx 0{,}3333" in third.step(1).explanation
    assert "yaklaşık %33,3 olasılıkla" in third.step(1).takeaway


def test_konu10_rectangles_cover_the_interval_finely() -> None:
    spec = _build(O10, mu=0, sigma=0.01, x=0.01, x1=-0.1, x2=0.1)
    rectangles = [op for op in spec.step(6).operations if type(op).__name__ == "Rectangles"][0]
    assert rectangles.count == 20000 and rectangles.width == pytest.approx(0.2 / 20000)
    assert _step_values(spec, 6)["P(−0,1 ≤ X ≤ 0,1)"] == pytest.approx(stats.norm.cdf(10) - stats.norm.cdf(-10),
                                                                        abs=1e-9)
    step3 = [op for op in spec.step(3).operations if type(op).__name__ == "Rectangles"][0]
    assert step3.count == 12000


# --- Konu 11 -------------------------------------------------------------------------------------

def test_konu11_alternative_matches_an_independent_calculation() -> None:
    spec = O11.alternative()
    values = _values(spec)
    assert values["Φ(1,37)"] == _table(1.37) == 0.9147
    assert [values[f"Tablo: satır {row}, sütun 0,07"] for row in ("1,2", "1,3", "1,4")] == \
        [_table(1.27), _table(1.37), _table(1.47)]
    assert values["P(Z ≤ 1,37)"] == 0.9147
    assert values["Φ(−1,37) = 1 − Φ(1,37)"] == pytest.approx(0.0853) and values["Φ(−1,37) doğrudan"] == _table(-1.37)
    assert values["P(Z > 1,37)"] == pytest.approx(0.0853)
    assert values["Φ(−0,83)"] == _table(-0.83) and values["Φ(1,42)"] == _table(1.42)
    assert values["P(−0,83 ≤ Z ≤ 1,42) = Φ(1,42) − Φ(−0,83)"] == pytest.approx(_table(1.42) - _table(-0.83))
    assert values["P(−0,83 ≤ Z ≤ 1,42), yuvarlamasız"] == pytest.approx(stats.norm.cdf(1.42) - stats.norm.cdf(-0.83))
    assert values["z(8,7)"] == pytest.approx(1.8) and values["P(X ≤ 8,7), tablo kuralı"] == _table(1.8)
    assert values["P(X > 8,7), tablo kuralı"] == pytest.approx(1 - _table(1.8))
    assert values["P(X ≤ 8,7), yuvarlamasız"] == pytest.approx(stats.norm.cdf(1.8))
    assert values["P(5,1 ≤ X ≤ 7,8), tablo kuralı"] == pytest.approx(_table(1.2) - _table(-0.6))
    for p in O11.PERCENTILES:
        label = f"Tablo 11.2: p = {format(Decimal(str(p)).normalize(), 'f').replace('.', ',')}"
        assert values[label] == pytest.approx(_half_up(round(float(stats.norm.ppf(p)), 12), 3))
    assert values["z = Φ⁻¹(0,95)"] == 1.645 and values["Eşik x = μ + zσ"] == pytest.approx(6 + 1.645 * 1.5)
    sd = math.sqrt(60 * 0.3 * 0.7)
    assert values["np"] == 18 and values["n(1 − p)"] == 42 and values["σ = √(np(1 − p))"] == pytest.approx(sd)
    assert values["P(X = 18): en olası değer"] == pytest.approx(stats.binom.pmf(18, 60, 0.3))
    assert values["Normal eğrinin yüksekliği f(18)"] == pytest.approx(stats.norm.pdf(18, 18, sd))
    assert values["z₁ = (19,5 − np)/σ, tablo için"] == _half_up(1.5 / sd, 2) == 0.42
    assert values["z₂ = (20,5 − np)/σ, tablo için"] == _half_up(2.5 / sd, 2) == 0.70
    assert values["P(X = 20) ≈ Φ(z₂) − Φ(z₁)"] == pytest.approx(_table(0.70) - _table(0.42))
    assert values["P(X = 20), yuvarlamasız z ile"] == pytest.approx(stats.norm.cdf(2.5 / sd) - stats.norm.cdf(1.5 / sd))
    assert values["Tam binom olasılığı P(X = 20)"] == pytest.approx(stats.binom.pmf(20, 60, 0.3))
    assert values["P(X ≤ 4)"] == pytest.approx(1 - math.exp(-0.5)) and values["P(X ≤ 12)"] == pytest.approx(
        1 - math.exp(-1.5))
    assert values["P(4 < X ≤ 12)"] == pytest.approx(math.exp(-0.5) - math.exp(-1.5))
    assert values["Ortalama bekleme (dakika)"] == 3 and values["P(X > 5)"] == pytest.approx(math.exp(-5 / 3))
    assert values["Ortalama bekleme (dakika), bütünleştirici"] == 4
    assert values["P(T > 6)"] == pytest.approx(math.exp(-1.5))
    assert values["z(1400), tablo için"] == 1.33
    assert values["P(X > 1400), tablo kuralı"] == pytest.approx(1 - _table(1.33))
    assert values["P(X > 1400), yuvarlamasız"] == pytest.approx(stats.norm.sf(4 / 3))


def test_table_rule_rounds_half_away_from_zero_like_the_course() -> None:
    for numerator in range(-2400, 2401):
        for denominator in (8, 40, 200, 3, 7, 16, 400):
            exact = Fraction(numerator, denominator)
            value = float(E.evaluate(E.yuvarla(numerator / denominator, 2)))
            assert value == float(ders_yuvarla(exact, 2)), exact
    assert float(E.evaluate(E.yuvarla(E.div(E.sub(108.35, 100), 10), 2))) == 0.84
    assert float(E.evaluate(E.roundto(E.div(E.sub(108.35, 100), 10), 2))) == 0.83  # np.round tam yarımda
    assert float(E.evaluate(E.yuvarla(-0.835, 2))) == -0.84 and float(E.evaluate(E.yuvarla(2.675, 2))) == 2.68


def test_konu11_half_points_follow_the_course_rule_in_text_and_both_languages(tmp_path: Path) -> None:
    spec = _build(O11, mu=100, sigma=10, x=108.35, x1=91.65, x2=108.25)
    values = _step_values(spec, 4)
    assert values["z(108,35), tablo için"] == 0.84 and values["z(91,65), tablo için"] == -0.84
    assert values["z(108,25), tablo için"] == 0.83
    assert "z = 0,835 → tablo için 0,84" in spec.step(4).takeaway
    _reproduce(spec, tmp_path)


def test_konu11_float_noise_at_a_half_point_is_reported() -> None:
    values = dict(O11.ALT_VALUES)
    values.update(mu=99999.99, sigma=0.08, x=100000.0, x1=99999.98, x2=100000.06)
    spec = O11.build(values)  # 10⁻⁷ payı: 10⁵ ölçeğinde de ders kuralı
    assert _step_values(spec, 4)["z(100000), tablo için"] == 0.13
    with pytest.raises(K.UploadError, match="tablo kuralını"):
        O11._check_table_rule(Fraction(1, 8), Fraction(1), 0.12, "Normal model")


@pytest.mark.parametrize("changes, message", [
    ({"a": 1.5, "b": 1.5}, "b'den"),
    ({"x1": 7.8, "x2": 5.1}, "x₂'den"),
    ({"x": 21.1}, "μ ± 10σ"),
    ({"k": 61}, "n'den"),
    ({"t1": 12, "t2": 4}, "t₂'den"),
    ({"s": 2800}, "μ ± 10σ"),
])
def test_konu11_invalid_values_are_explained(changes, message) -> None:
    values = dict(O11.ALT_VALUES)
    values.update(changes)
    with pytest.raises(K.UploadError, match=re.escape(message)):
        O11.validate(values)


def test_konu11_texts_follow_the_values() -> None:
    negative = _build(O11, z=-1.37)
    assert "Tablo pozitif" in negative.step(1).explanation
    assert "simetriyle bulunur" in negative.step(2).takeaway
    assert _step_values(negative, 2)["P(Z ≤ −1,37)"] == pytest.approx(1 - 0.9147)
    zero = _build(O11, z=0)
    assert "Φ(0) = 0,5000" in zero.step(2).takeaway and "Φ(−0,00" not in " ".join(_values(zero))
    weak = _build(O11, n=20, p=0.1, k=2)
    assert "sağlanmıyor" in weak.step(6).takeaway and "yaklaşım zayıf olabilir" in weak.step(7).takeaway
    start = _build(O11, t1=0)
    assert "P(X ≤ 0) = 0" in start.step(8).takeaway and _step_values(start, 8)["P(X ≤ 0)"] == 0
    median = _build(O11, p_sol=0.5)
    assert "z = 0: eşik ortalamanın kendisidir" in median.step(5).takeaway
    exact_sigma = _build(O11, n=100, p=0.1, k=12)
    takeaway = exact_sigma.step(7).takeaway
    assert "z₁ = 0,5" in takeaway and "z₂ ≈ 0,8333 → tablo için 0,83" in takeaway
    assert _step_values(exact_sigma, 7)["P(X = 12) ≈ Φ(z₂) − Φ(z₁)"] == pytest.approx(0.1052)  # §11.8.1
    same = _build(O11, a=-0.5, b=1.25)
    assert "0,8944 − 0,3085 = 0,5859" in same.step(3).takeaway and "≈ 0,5858" in same.step(3).takeaway  # §11.3


def test_konu11_large_n_uses_a_window_and_tiny_tails_are_written() -> None:
    spec = _build(O11, n=1000, p=0.5, k=500, mu=0, sigma=1, x=9.5, x1=-9.5, x2=9.5)
    frame = run_lab(spec).state.frames["binom"]
    assert len(frame) < 200 and frame["x"].min() > 0
    assert "10⁻¹²'den küçük" in spec.step(4).takeaway or "0,0000000" in spec.step(4).takeaway


# --- Konu 12 -------------------------------------------------------------------------------------

def test_konu12_alternative_matches_an_independent_calculation() -> None:
    spec = O12.alternative()
    values = _values(spec)
    assert values["Standart hata, n = 16"] == 9 and values["Standart hata, n = 64"] == 4.5
    assert [values[f"Standart hata, n = {n}"] for n in (9, 36, 144, 576)] == [10, 5, 2.5, 1.25]
    assert values["σ_X̄ = σ/√n"] == 2.5
    assert values["z(72), tablo için"] == -1.2 and values["z(79), tablo için"] == 1.6
    assert values["P(72 ≤ X̄ ≤ 79), tablo kuralı"] == pytest.approx(_table(1.6) - _table(-1.2))
    assert values["P(72 ≤ X̄ ≤ 79), yuvarlamasız"] == pytest.approx(stats.norm.cdf(1.6) - stats.norm.cdf(-1.2))
    assert values["σ_p̂, n = 48"] == pytest.approx(0.0625) and values["σ_p̂, n = 192"] == pytest.approx(0.03125)
    assert values["Düzeltmesiz standart hata"] == pytest.approx(50 / math.sqrt(200))
    assert values["Düzeltme faktörü"] == pytest.approx(math.sqrt(800 / 999))
    assert values["Düzeltilmiş standart hata"] == pytest.approx(math.sqrt(800 / 999) * 50 / math.sqrt(200))
    assert values["σ_X̄ (bütünleştirici)"] == 10
    assert values["σ_p̂ (bütünleştirici)"] == pytest.approx(math.sqrt(0.72 * 0.28 / 81))
    assert values["np (bütünleştirici)"] == pytest.approx(58.32) and values["n(1 − p) (bütünleştirici)"] == \
        pytest.approx(22.68)


@pytest.mark.parametrize("changes, message", [
    ({"n1a": 64, "n1b": 16}, "küçük olmalıdır"),
    ({"xb1": 79, "xb2": 72}, "x̄₂'den"),
    ({"xb2": 101}, "μ ± 10σ/√n"),
    ({"n4a": 192, "n4b": 48}, "Adım 4"),
    ({"n5": 1001}, "N'den"),
])
def test_konu12_invalid_values_are_explained(changes, message) -> None:
    values = dict(O12.ALT_VALUES)
    values.update(changes)
    with pytest.raises(K.UploadError, match=re.escape(message)):
        O12.validate(values)


def test_konu12_texts_follow_the_values() -> None:
    census = _build(O12, n5=1000)
    assert "Bütün anakütle gözlenir" in census.step(5).takeaway and _step_values(census, 5)["Düzeltme faktörü"] == 0
    single = _build(O12, n5=1)
    assert "Tek birim seçildiğinde" in single.step(5).takeaway
    small = _build(O12, N5=100000, n5=200)
    assert "n/N ≤ 0,05" in small.step(5).takeaway
    few = _build(O12, n3=16, xb1=70, xb2=80)
    assert "n = 16 < 30" in few.step(3).explanation
    rare = _build(O12, p4=0.02, n4a=50, n4b=300)
    assert "yalnız n = 300 için sağlanır" in rare.step(4).takeaway
    odd = _build(O12, n4a=50, n4b=300)
    assert "√(300/50) ≈ 2,4495 kat küçülür" in odd.step(4).takeaway and "1/√n ile orantılıdır" in odd.step(4).takeaway
    nine = _build(O12, n4a=25, n4b=225)
    assert "n = 25 yerine n = 225 olunca standart hata √(225/25) = 3 kat küçülür" in nine.step(4).takeaway
    ninths = _build(O12, n4a=9, n4b=16)  # 16/9 sonsuz ondalıklı: kesir olarak yazılır
    assert "√(16/9) = 4/3 kat küçülür" in ninths.step(4).takeaway
    root = _build(O12, n1a=10, n1b=20)
    assert "yaklaşık 11,3842" in root.step(1).takeaway


def test_konu12_float_noise_at_a_half_point_is_reported() -> None:
    """10⁵ ölçeğinde σ/√n çok küçükken tam yarımdaki z (3,125) kayan nokta farkıyla aşağı yuvarlanabilir; uygulama
    sessiz kalmaz, değer değiştirilmesini ister."""

    values = dict(O12.ALT_VALUES)
    values.update(mu3=99999.99, sd3=0.32, n3=10000, xb1=99999.98, xb2=100000.0)
    with pytest.raises(K.UploadError, match="tablo kuralını"):
        O12.build(values)
    values.update(mu3=999.99, xb1=999.98, xb2=1000.0)
    assert _step_values(O12.build(values), 3)["z(999,98), tablo için"] == -3.13


# --- İki dilde yeniden üretim ve metin kuralları ------------------------------------------------------

AGG_SHOW = "ignore:FigureCanvasAgg is non-interactive:UserWarning"
"""Agg arka ucunda ``plt.show()`` Windows'ta (ve DISPLAY tanımlı Linux'ta) bu uyarıyı basar; betikten değil test
ortamından gelir (``tests/test_lab_variants.py`` ile aynı süzgeç). Diğer bütün uyarılar yakalanır."""


def _run(spec, language: str, folder: Path):
    path = folder / script_filename(spec, language)
    path.write_text(render_script(spec, language), encoding="utf-8")
    command = [sys.executable] if language == "Python" else ["Rscript"]
    warnings = ",".join(item for item in (os.environ.get("PYTHONWARNINGS", ""), AGG_SHOW) if item)
    environment = {**os.environ, "MPLBACKEND": "Agg", "PYTHONWARNINGS": warnings}
    return subprocess.run(command + [path.name], cwd=folder, capture_output=True, encoding="utf-8", errors="replace",
                          timeout=300, env=environment)


def _reproduce(spec, tmp_path: Path) -> None:
    assert run_lab(spec).all_passed
    checks = sum(len(step.checks) for step in spec.steps)
    for language in ["Python"] + (["R"] if shutil.which("Rscript") else []):
        place = tmp_path / language
        place.mkdir()
        result = _run(spec, language, place)
        assert result.returncode == 0, (language, result.stdout[-1500:] + result.stderr[-1500:])
        assert result.stdout.count("  OK   ") == checks, language
        assert "warning" not in (result.stdout + result.stderr).lower(), language
        assert not re.search(r"(?<![\d.])-0(?:\.0+)?(?![\d.,])", result.stdout), (language, "işaretli sıfır")


OWN_VALUES = [
    (O10, {"a": -5, "b": 0.5, "c": -4.25, "d": 0.5, "w": 99.99, "mu": -12.5, "sigma": 0.37, "x": -14.03, "z0": 0,
           "x1": -16.2, "x2": -8.8, "xA": 3, "muA": 7.5, "sdA": 0.01, "xB": 3, "muB": -3, "sdB": 12, "mu7": 99999.99,
           "sd7": 0.08, "v1": 100000.0, "v2": 99999.21}),
    (O11, {"z": -3.99, "a": -3.99, "b": 3.99, "mu": 99999.99, "sigma": 0.08, "x": 100000.0, "x1": 99999.21,
           "x2": 100000.79, "p_sol": 0.001, "n": 1, "p": 0.99, "k": 1, "mu_e": 0.01, "t1": 0, "t2": 99999.99,
           "hiz": 7, "t": 0.01, "hiz10": 9, "t10": 25, "mu_s": -500, "sd_s": 10000, "s": -100000}),
    (O11, {"z": 0.05, "a": 0, "b": 0.01, "mu": 0, "sigma": 1, "x": 0, "x1": -0.01, "x2": 0.01, "p_sol": 0.999,
           "n": 1000, "p": 0.5, "k": 500, "mu_e": 3, "t1": 1, "t2": 2, "hiz": 0.01, "t": 1000, "hiz10": 0.37,
           "t10": 0.01, "mu_s": 0, "sd_s": 0.01, "s": 0.05}),
    (O12, {"mu1": -40, "sd1": 0.01, "n1a": 1, "n1b": 10000, "sd2": 9999.99, "n2": 156, "mu3": 99999.99, "sd3": 0.8,
           "n3": 10000, "xb1": 99999.98, "xb2": 100000.0, "p4": 0.01, "n4a": 1, "n4b": 2, "N5": 1000000, "n5": 999999,
           "sd5": 0.01, "mu6": 0, "sd6": 3, "p6": 0.99, "n6": 7}),
]


TINY_VALUES = [
    (O10, {"a": 0, "b": 1000, "c": 0, "d": 0.01, "mu": 0, "sigma": 1, "x": 1, "x1": 9, "x2": 9.5}),
    (O11, {"x": 14.25, "n": 60, "p": 0.3, "k": 0, "hiz": 60, "t": 100000, "hiz10": 15, "t10": 100}),
    (O12, {"mu3": 0.01, "sd3": 10000, "n3": 2, "xb1": 0, "xb2": 1, "N5": 1000000, "n5": 400000, "sd5": 0.01}),
]
"""Çok küçük değerler (üç anlamlı basamak, en çok 12 ondalık): iki dil aynı sayıyı vermeli."""


@pytest.mark.parametrize("module, values", OWN_VALUES + TINY_VALUES,
                         ids=["konu10-uc", "konu11-uc", "konu11-kucuk", "konu12-uc", "konu10-minik", "konu11-minik",
                              "konu12-minik"])
def test_own_values_are_reproduced_in_both_languages(module, values, tmp_path: Path) -> None:
    params = module.PARAMS
    spec = params.build(parameter_values(params, values))
    _reproduce(spec, tmp_path)


def _own_specs():
    for module, values in OWN_VALUES:
        yield module.PARAMS.build(parameter_values(module.PARAMS, values))
    yield _build(O10, a=0, b=3, c=0.5, d=1.5, w=1, x=250, z0=0)
    yield _build(O11, z=-1.37, n=20, p=0.1, k=2, t1=0, p_sol=0.5)
    yield _build(O12, n5=1, n3=16, xb1=70, xb2=80, p4=0.02, n4a=50, n4b=300)


def test_texts_add_no_suffix_to_runtime_numbers() -> None:
    for spec in (*(module.alternative() for module in MODULES), *_own_specs()):
        for text in _texts(spec):
            plain = re.sub(r"\$[^$]*\$", "", text)
            for word in re.findall(r"%?\d[\d,.]*'[a-zçğıöşü]+", plain):
                assert word in ALLOWED_SUFFIXES, (spec.topic_key, word, text)
            for formula in re.findall(r"\$([^$]*)\$'[a-zçğıöşü]+", text):
                assert not re.search(r"\d\}?$", formula.strip()), (spec.topic_key, formula, text)


def test_math_uses_ascii_minus_and_braced_commas() -> None:
    for spec in (*(module.alternative() for module in MODULES), *_own_specs()):
        for text in _texts(spec):
            for formula in re.findall(r"\$([^$]*)\$", text):
                assert "−" not in formula, (spec.topic_key, formula)
                assert not re.search(r"\d,\d", formula), (spec.topic_key, formula)


def test_metric_titles_and_values_fit_their_columns() -> None:
    """1280 px'de sütun başına başlık (4 → 28, 3 → 38, 2 → 57, 1 → 110 karakter) ve değer (4 → 12, 3 → 16, 2 → 24)
    sınırı; satırdaki metrik sayısı ``lab_ui._metric_row_size`` ile seçilir (uzun değerde satır daralır)."""

    from topics.lab_ui import _METRICS, _metric_row_size, _metrics

    title_limit = {4: 28, 3: 38, 2: 57, 1: 110}
    value_limit = {4: 12, 3: 16, 2: 24, 1: 50}
    tiny = [_build(O11, mu=6, sigma=1.5, x=14.25, hiz10=15, t10=100), _build(O11, n=60, p=0.3, k=0),
            _build(O12, xb1=85, xb2=90), _build(O10, mu=0, sigma=1, x=1, x1=9, x2=9.5)]
    for spec in (*(module.alternative() for module in MODULES), *_own_specs(), *tiny):
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
                size = _metric_row_size(row)
                for start in range(0, len(row), size):
                    chunk = row[start:start + size]
                    for title, value in chunk:
                        assert len(title) <= title_limit[len(chunk)], (spec.topic_key, step.number, title)
                        assert len(value) <= value_limit[len(chunk)], (spec.topic_key, step.number, title, value)


def test_step_code_defines_the_rounding_helper_only_when_used() -> None:
    spec = O11.alternative()
    for language in ("Python", "R"):
        definition = "yuvarla <- function" if language == "R" else "def yuvarla("
        used, unused = render_step(spec, 4, language), render_step(spec, 8, language)
        assert definition in used and re.search(r"= yuvarla\(|<- yuvarla\(", used)
        assert not re.search(r"\byuvarla\(", unused) and definition not in unused
        assert render_script(spec, language).count(definition) == 1
        assert not re.search(r"\byuvarla\(", render_script(O10.alternative(), language))


# --- Bağımsız inceleme bulguları (Blok E) için gerileme testleri ---------------------------------------

def _strings(value) -> list[str]:
    """Bir işlemin içindeki bütün metinler (başlık, eksen, açıklama, başvuru etiketleri)."""

    if isinstance(value, str):
        return [value]
    if isinstance(value, (tuple, list)):
        return [text for item in value for text in _strings(item)]
    if hasattr(value, "__dataclass_fields__"):
        return [text for name in value.__dataclass_fields__ for text in _strings(getattr(value, name))]
    return []


def test_labels_have_one_relation_sign_and_no_runaway_digits() -> None:
    specs = [*(module.alternative() for module in MODULES), *_own_specs(),
             _build(O10, mu=0, sigma=3, x=1, x1=-1, x2=2, mu7=0, sd7=3, v1=1, v2=-2),
             _build(O12, n4a=9, n4b=16), _build(O12, n4a=36, n4b=49)]
    for spec in specs:
        for step in spec.steps:
            texts = [step.explanation, step.takeaway, step.code_note, *_strings(step.operations)]
            for text in texts:
                assert "= ≈" not in text and "=≈" not in text, (spec.topic_key, step.number, text)
                assert not re.search(r"\d{15,}", text.replace(" ", "")), (spec.topic_key, step.number, text)


def test_small_quantities_keep_significant_digits() -> None:
    wide = _build(O10, a=0, b=1000, c=0, d=0.01)
    assert "= 0,00001: X, %0,001 olasılıkla" in wide.step(1).takeaway
    assert _step_values(wide, 1)["P(0 ≤ X ≤ 0,01): uzunluk oranı"] == pytest.approx(1e-5)
    far = _build(O10, a=20000, b=60000, c=20000, d=20000.01)
    assert "1/(60000 - 20000) = 0{,}000025" in far.step(1).explanation
    check = next(check for check in far.step(1).checks if check.label.startswith("f(x)"))
    assert check.decimals >= 6  # tolerans değerin kendisinden küçük
    tiny = _build(O10, mu=0, sigma=10000, x=0.01, x1=0.01, x2=0.02)
    assert "0,000001 standart sapma üzerindedir" in tiny.step(4).takeaway
    tail = _build(O10, mu=0, sigma=1, x=1, x1=9, x2=9.5)
    assert "10⁻¹²'den küçük" in tail.step(6).takeaway
    share = _build(O12, N5=1000000, n5=1)
    assert "1/1000000 = 0{,}000001" in share.step(5).explanation
    small_se = _build(O12, sd5=0.01, N5=1000000, n5=400000)
    assert "yaklaşık 0 " not in small_se.step(5).takeaway and "yaklaşık 0,0000" in small_se.step(5).takeaway


def test_exact_zero_and_exact_half_are_written_with_equals() -> None:
    zero = _build(O11, z=0)
    assert "%50 olasılıkla" in zero.step(1).takeaway and "yaklaşık %50" not in zero.step(1).takeaway
    centre = _build(O11, x=6)
    assert "yuvarlamasız değerler de tam 0,5" in centre.step(4).takeaway
    edge = _build(O11, n=61, p=0.5, k=30)  # üst sınır 30,5 = np: z₂ tam 0, σ irrasyonel
    assert "z₂ = 0" in edge.step(7).takeaway and "z₂ ≈ 0" not in edge.step(7).takeaway
    mean_bound = _build(O12, n3=50, xb1=75, xb2=79)  # x̄₁ = μ, n tam kare değil
    assert "z₁ = 0" in mean_bound.step(3).takeaway and "z₁ ≈ 0" not in mean_bound.step(3).takeaway


def test_rounding_returns_unsigned_zero() -> None:
    value = float(E.evaluate(E.yuvarla(-0.004, 2)))
    assert value == 0 and math.copysign(1, value) == 1
    spec = _build(O11, mu=100, sigma=10, x=99.96, x1=99.96, x2=100.04)
    assert _step_values(spec, 4)["z(99,96), tablo için"] == 0
    assert "z = −0,004 → tablo için 0,00" in spec.step(4).takeaway


def test_case_specific_sentences_stay_true() -> None:
    symmetric = _build(O11, n=9, p=0.5, k=4)
    assert "simetriktir" in symmetric.step(6).takeaway and "çarpıktır" not in symmetric.step(6).takeaway
    skewed = _build(O11, n=20, p=0.1, k=2)
    assert "sağa çarpıktır" in skewed.step(6).takeaway and "Ayrıca binom" in skewed.step(6).takeaway
    single = _build(O11, n=1, p=0.3, k=1)
    assert "Tek bir denemede" in single.step(6).explanation and "x = 0 ve 1" in " ".join(
        _strings(single.step(6).operations))
    low = _build(O11, p_sol=0.1)
    assert "en düşük %10 kadarı bu eşiğin altındadır" in low.step(5).takeaway
    edge = _build(O11, k=0, n=60, p=0.3)
    assert "−0,5 ile 0,5 arasının alanı" in " ".join(_strings(edge.step(7).operations))
    negative = _build(O11, mu_s=-1200, sd_s=150, s=-1000)
    assert "z = (−1000 − (−1200))/150" in negative.step(10).takeaway
    one = _build(O12, n3=1, xb1=70, xb2=80)
    assert "n = 1 iken X̄ = X" in one.step(3).takeaway and "başka bir olaydır" not in one.step(3).takeaway
    unit = _build(O12, n5=1)
    assert "aynıdır, " in unit.step(5).takeaway and ") (§12.11)" not in unit.step(5).takeaway
    scales = _build(O10, xA=50, xB=60)  # iki z de eksi: nötr başlık (eksi çubuk + "aşağıda" çift olumsuz okunurdu)
    assert any("ortalamadan kaç standart sapma uzakta (z)" in text for text in _strings(scales.step(5).operations))
    equal = _build(O10, xA=60, muA=55, sdA=5, xB=82, muB=72, sdB=10)
    assert equal.step(5).takeaway.count("göreli konum aynıdır") == 1


def test_irrational_z_near_a_half_is_not_rounded_silently() -> None:
    """z = (x̄ − μ)√n/σ irrasyonel ve yarıma 10⁻⁹ kadar yakınken kayan noktalı yuvarlama ders kuralından ayrılır
    (2,6949999996 → 2,70); uygulama sessiz kalmaz."""

    values = dict(O12.ALT_VALUES)
    values.update(mu3=0, sd3=1.09, n3=2397, xb1=0.06, xb2=0.07)
    with pytest.raises(K.UploadError, match="ortasına çok yakın"):
        O12.build(values)
    assert float(O12.ders_yuvarla_kok(Fraction(7, 109), Fraction(2397), 2)) == 3.14
    assert float(O12.ders_yuvarla_kok(Fraction(6, 109), Fraction(2397), 2)) == 2.69


def test_table_values_are_far_from_rounding_halves() -> None:
    """Φ'nin iki ondalıklı z'lerde (|z| ≤ 10) ve Φ⁻¹'in üç ondalıklı p'lerde değeri, ölçeklenmiş olarak hiçbir yarıma
    10⁻⁵'ten yakın değildir: ``E.yuvarla``'nın 10⁻⁷ payı bu yuvarlamaları değiştirmez."""

    for hundredths in range(-1000, 1001):
        scaled = float(stats.norm.cdf(hundredths / 100)) * 1e4
        assert abs(scaled - math.floor(scaled) - 0.5) > 1e-5, hundredths
    for thousandths in range(1, 1000):
        scaled = abs(float(stats.norm.ppf(thousandths / 1000))) * 1e3
        assert abs(scaled - math.floor(scaled) - 0.5) > 1e-5, thousandths


def test_tail_intervals_keep_their_precision() -> None:
    spec = _build(O12, mu3=0, sd3=1, n3=1, xb1=9, xb2=9.5)
    value = _step_values(spec, 3)["P(9 ≤ X̄ ≤ 9,5), yuvarlamasız"]
    assert value == pytest.approx(stats.norm.sf(9) - stats.norm.sf(9.5), rel=1e-9) and value > 0
    binom = _build(O11, n=1000, p=0.5, k=600)
    exact = stats.norm.sf(99.5 / math.sqrt(250)) - stats.norm.sf(100.5 / math.sqrt(250))
    assert _step_values(binom, 7)["P(X = 600), yuvarlamasız z ile"] == pytest.approx(exact, rel=1e-9)


def test_generated_loops_do_not_overwrite_lab_frames_or_scalars() -> None:
    """Kod üreticilerinin döngü değişkenleri (R'de boyalı alan için ``aralik`` gibi) tanımın çerçeve ve skaler adlarını
    ezmemeli: notlar, alternatif örnekler ve kendi değerlerin başlangıç tanımları."""

    from core.labs import spec as S
    from core.labs.ornekler import VARIANTS
    from core.labs.registry import LABS

    scalar_ops = (S.Scalar, S.Statistic, S.Count, S.PairStatistic, S.Percentile)
    specs = list(LABS.values())
    for variants in VARIANTS.values():
        specs.append(variants.alternative() if callable(variants.alternative) else variants.alternative)
        if variants.params is not None:
            specs.append(variants.params.build(parameter_values(variants.params)))
    for spec in specs:
        names = set()
        for step in spec.steps:
            for op in step.operations:
                names |= {getattr(op, field) for field in ("frame", "result")
                          if isinstance(getattr(op, field, None), str)}
                if isinstance(op, scalar_ops):
                    names.add(op.name)
        r_loops = set(re.findall(r"for \((\w+) in", render_script(spec, "R")))
        python_loops = set()
        for match in re.finditer(r"^\s*for ([\w, ()]+?) in ", render_script(spec, "Python"), re.M):
            python_loops |= set(re.findall(r"\w+", match.group(1)))
        assert not names & (r_loops | python_loops), (spec.topic_key, spec.source, names & (r_loops | python_loops))


def test_parameter_groups_are_laid_out_in_rows_of_at_most_three(monkeypatch) -> None:
    from topics import kendi_veri_ui

    rows = []

    def columns(count):
        rows.append(count)
        return [f"{len(rows)}.{index}" for index in range(count)]

    monkeypatch.setattr(kendi_veri_ui.st, "columns", columns)
    layouts = {}
    for count in range(1, 8):
        rows.clear()
        chosen = kendi_veri_ui._group_columns(count)
        assert len(chosen) == count and len(set(chosen)) == count
        layouts[count] = [sum(1 for item in chosen if item.startswith(f"{row + 1}.")) for row in range(len(rows))]
        assert set(rows) == {rows[0]}  # her satır aynı sayıda sütunla açılır: genişlikler eşit
    assert layouts == {1: [1], 2: [2], 3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3], 7: [3, 2, 2]}
    assert kendi_veri_ui._group_columns(0) == []


def test_inline_table_uses_the_digits_of_the_result_table() -> None:
    from topics import lab_ui

    operations = O11.alternative().step(1).operations
    hints = lab_ui._later_hints(operations, 0)
    assert hints["z_satir"] == 1 and hints["s00"] == 4
    state = run_lab(O11.alternative()).state
    text = lab_ui._frame(state.frames["ztablo"][["z_satir"]], str, True, hints).to_string()
    assert "1,2" in text and "1,20" not in text


def test_round_two_findings_stay_fixed() -> None:
    tiny_z = _build(O12, mu3=0.01, sd3=10000, n3=2, xb1=0, xb2=1)  # irrasyonel ve çok küçük z
    assert "z₁ ≈ −0,00000141" in tiny_z.step(3).takeaway
    exact_binom = _build(O11, n=2, p=0.5, k=1)
    assert "tam binom olasılığı = 0,5" in exact_binom.step(7).takeaway
    tie = _build(O11, n=9, p=0.5, k=4)
    assert any(check.label.endswith("en olası değerlerden biri") for check in tie.step(6).checks)
    underflow = _build(O11, hiz=60, t=100000)
    assert "e^(−t/μ) ≈ 0 (10⁻¹²'den küçük)" in underflow.step(9).takeaway
    far = _build(O11, x=14.25)
    assert "≈ 0,000000019" in far.step(4).takeaway
    assert next(c for c in far.step(4).checks if c.label == "P(X > 14,25), yuvarlamasız").decimals > 4
    census = _build(O12, N5=1000, n5=1000, sd5=0.01)
    assert {c.label: c.decimals for c in census.step(5).checks}["Düzeltme faktörü"] >= 4
    start = _build(O11, t1=0)
    assert {c.label: c.decimals for c in start.step(8).checks}["P(X ≤ 0)"] == 4
    one = _build(O12, n3=1, xb1=70, xb2=80)
    assert "σ_X̄ = σ = 20 (§12.9)" in one.step(3).takeaway
    many = O12.alternative()
    assert "Örneklem büyüklüğü n = 64 iken örneklem ortalamasının 72 ile 79" in many.step(3).takeaway
    assert "bireysel X için standart sapma 20; X̄ için 2,5" in many.step(3).takeaway
    decimals = _build(O12, mu1=262.4, mu3=262.4, xb1=262, xb2=263, mu6=262.4)
    for number in (1, 3, 6):
        assert "μ = 262,4; standart sapması" in decimals.step(number).explanation, number
    assert "P(X ≤ 8,7) = 0,9641; P(X > 8,7)" in O11.alternative().step(4).takeaway
