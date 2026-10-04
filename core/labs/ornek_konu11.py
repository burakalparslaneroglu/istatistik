"""Konu 11 genel uygulaması: standart normal tablo, normal olasılıklar, ters normal, binomun normal yaklaştırması ve
üstel dağılım.

Ders notlarındaki adımlar (§11.1–§11.5, §11.7, §11.8.1, §11.10, §11.11 ve §11.13) aynı numaralarla, parametreleri
değiştirilebilir biçimde yazılır. Bu konuda dosya yoktur: "Kendi değerlerini gir" seçeneğinde öğrenci notlardaki her
örnek için ayrı değerler girer: standart normal z ve [a, b] aralığı (Adım 1–3); normal dağılım N(μ, σ²), bir x değeri,
bir [x₁, x₂] aralığı ve ters normal için sol alan p (Adım 4–5); binom n, p ve x (Adım 6–7); üstel dağılımın ortalama
süresi ve iki süre, saatlik geliş hızı ve bir bekleme süresi (Adım 8–9); bütünleştirici uygulamanın geliş hızı,
bekleme süresi ve günlük satış dağılımı (Adım 10). Alternatif örnek kurgusaldır. Notlardaki uygulama
(``core.labs.konu11``) değişmez.

Tablo kuralı notlardaki gibidir: z iki, Φ(z) dört ondalık basamağa yuvarlanır; Φ⁻¹(p) üç basamakla yazılır.
Yuvarlama ders kuralıyla yapılır (``E.yuvarla``: tam yarım sıfırdan uzağa); np.round ve R'nin round fonksiyonu tam
yarımı iki dilde farklı yuvarlayabilir. Tablo kuralıyla bulunan ve yuvarlamasız sonuç birlikte gösterilir. Her z için
(z = (x − μ)/σ ve binom yaklaşımının irrasyonel z'si) kayan noktalı hesabın ders kuralının kesin sonucunu verdiği ayrıca
denetlenir (``ders_yuvarla_kok``); z tam yarımda ya da yarıma çok yakınsa ve hesap ayrılırsa açık bir iletiyle değer
değiştirilmesi istenir.
"""

from __future__ import annotations

import math
from dataclasses import replace
from fractions import Fraction
from functools import cache
from typing import Mapping

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs.ornek import (
    Parameter,
    ParamLab,
    TopicVariants,
    ders_yuvarla,
    ders_yuvarla_kok,
    deger_metni,
    isaretsiz_skalerler,
    kesir_basamak,
    kesir_degeri,
    kesir_kok,
    kisa_kesir as _txt,
    kisa_kesir_tex as _tx,
    liste,
    olasilik_basamak,
    olasilik_metni,
    onemli_basamak,
    parameter_values,
    parantezli as _par,
    sabit as _c,
    with_app_values,
)
from core.labs.runner import run_operations
from core.labs.spec import (
    CellTarget,
    Check,
    DensityPlot,
    Derive,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    PmfWithDensity,
    Scalar,
    ScalarTarget,
    ShowFrame,
    Support,
)

TITLE = "Normal olasılıkları, binomun normal yaklaştırmasını ve üstel dağılımı uygulamak"
PERCENTILES = (0.025, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)
"""Tablo 11.2'nin sol kümülatif olasılıkları (notlardaki tablo)."""
Z_LIMIT = Fraction(399, 100)
REACH = 10
"""Normal dağılımda girilen değerler μ ± 10σ içinde: daha uzak değerlerin kuyruk olasılığı 10⁻²³'ten küçüktür."""
LIMIT = 100000
SCALE_LIMIT = 10000
"""Normal dağılımların standart sapması en çok 10⁴ (konum değerleri ±10⁵): z = (x − μ)/σ için ``E.yuvarla``'nın payı
bu aralıkta güvenlidir."""
LIST_LIMIT = 30
"""Binom olasılık tablosu n ≤ 30 iken bütün değerlerle; daha büyük n'de np ± (5σ + 3) penceresiyle."""

ALT_VALUES = {"z": 1.37, "a": -0.83, "b": 1.42, "mu": 6, "sigma": 1.5, "x": 8.7, "x1": 5.1, "x2": 7.8, "p_sol": 0.95,
              "n": 60, "p": 0.3, "k": 20, "mu_e": 8, "t1": 4, "t2": 12, "hiz": 20, "t": 5, "hiz10": 15, "t10": 6,
              "mu_s": 1200, "sd_s": 150, "s": 1400}
ALT_TEXTS = {
    "normal": "Bir çağrı merkezinde görüşme süresi (dakika) yaklaşık normal dağılsın.",
    "normal_eksen": "Görüşme süresi (dakika)",
    "binom": ("Bir mağazada her müşterinin indirim kartı kullanma olasılığı 0,30 olsun; 60 müşteri birbirinden "
              "bağımsız olarak incelenir."),
    "binom_eksen": "İndirim kartı kullanan müşteri sayısı, x",
    "ustel": "Bir servis masasında işlemin tamamlanma süresi, ortalaması 8 dakika olan üstel dağılıma sahip olsun.",
    "poisson": "Bir otoparka saatte ortalama 20 araç giriyor.",
    "butun": "Bir dükkâna saatte ortalama 15 müşteri geliyor; günlük satış tutarı (TL) yaklaşık normal dağılıyor.",
    "butun_eksen": "Günlük satış tutarı (TL)",
}
STORY = (
    "Kurgusal veri: standart normal tabloda z = 1,37 ve −0,83 ile 1,42 arası; görüşme süresi N(6, 1,5²) dakika; 60 "
    "müşteriden indirim kartı kullananlar (p = 0,30); ortalaması 8 dakika olan üstel işlem süresi ve saatte 20 araç; "
    "bütünleştirici uygulamada saatte 15 müşteri ve günlük satış tutarı N(1200, 150²) TL."
)


# --- Yardımcılar -------------------------------------------------------------------------------

def _digits(value: Fraction, minimum: int = 0) -> int:
    """Kesin bir büyüklüğün gösterim basamağı (``onemli_basamak``): en çok dört; çok küçük değerlerde üç anlamlı
    basamak."""

    return onemli_basamak(float(value), value, minimum)


def _span(start: int, end: int) -> str:
    """Ardışık tam sayılar: "0 ve 1", "0, 1, 2 ve 3", "0, 1, …, 60"."""

    if end - start <= 3:
        return liste([str(value) for value in range(start, end + 1)])
    return f"{start}, {start + 1}, …, {end}"


def _trials(n: int, p_text: str) -> str:
    """Binomun varsayılan öyküsü: "60 bağımsız denemenin her birinde …"; n = 1 iken tek deneme."""

    if n == 1:
        return f"Tek bir denemede başarı olasılığı p = {p_text} olsun."
    return f"{n} bağımsız denemenin her birinde başarı olasılığı p = {p_text} olsun."


def _scalar(name: str, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _with_decimals(operations: tuple, decimals: Mapping[str, int]) -> tuple:
    """Hesaplanan değere göre seçilen gösterim basamakları (yuvarlamasız olasılıklar: ``olasilik_basamak``)."""

    return tuple(replace(op, decimals=decimals[op.name]) if isinstance(op, Scalar) and op.name in decimals else op
                 for op in operations)


def _table(z) -> E.Expr:
    """Tablo değeri: Φ(z) dört ondalık basamağa, ders kuralıyla yuvarlanır."""

    return E.yuvarla(E.normcdf(z), 4)


def _z(x: Fraction, mean: Fraction, sd: Fraction) -> E.Expr:
    return E.div(E.sub(_c(x), _c(mean)), _c(sd))


def _between(z_low: E.Expr, z_high: E.Expr, upper: bool) -> E.Expr:
    """Yuvarlamasız P(z₁ ≤ Z ≤ z₂) = Φ(z₂) − Φ(z₁). Aralık ortalamanın üstündeyse (z₁ ≥ 0) Φ(−z₁) − Φ(−z₂) yazılır:
    büyük z'de 1'e çok yakın iki sayının farkı kesinliğini yitirir (sıfır çıkardı)."""

    if upper:
        return E.sub(E.normcdf(E.neg(z_low)), E.normcdf(E.neg(z_high)))
    return E.sub(E.normcdf(z_high), E.normcdf(z_low))


def _fixed(value: float, digits: int) -> str:
    """Tablo değeri düzyazıda sabit basamakla (0,8944; 0,50; −1,645); işaretsiz sıfır."""

    text = f"{float(value):.{digits}f}"
    if float(text) == 0:
        text = text.lstrip("-")
    return text.replace(".", ",").replace("-", "−")


def _percent(value: float) -> str:
    """Dört basamaklı tablo değerinin yüzdesi: 0,9147 → %91,47."""

    text = f"{float(value) * 100:.2f}".rstrip("0").rstrip(".")
    return "%" + text.replace(".", ",")


def _normal(mean: Fraction, sd: Fraction) -> str:
    return f"N({_txt(mean)}, {_txt(sd)}²)"


def _normal_tex(mean: Fraction, sd: Fraction) -> str:
    return f"N({_tx(mean)}, {_tx(sd)}^2)"


def _reach(*values: Fraction) -> int:
    """Grafik ekseninin yarı genişliği (σ cinsinden): en az 4; gösterilen z değerlerini kapsayacak kadar."""

    return max(4, *(math.ceil(abs(value) + Fraction(1, 2)) for value in values))


def _nice_up(value: Fraction) -> Fraction:
    """Grafik ekseninin üst sınırı: değerden küçük olmayan, iki anlamlı basamaklı sayı (51,43 → 52; 0,0857 → 0,086)."""

    exponent = math.floor(math.log10(float(value))) - 1
    step = Fraction(10) ** exponent
    return math.ceil(value / step) * step


def _z_text(value: Fraction | None, number: float, digits: int) -> str:
    """z değeri düzyazıda: "= 1,8" ya da "≈ 0,4226"."""

    return " ".join(deger_metni(number, value, digits))


def _check_table_rule(factor: Fraction, radicand: Fraction, value: float, where: str) -> None:
    """z = factor · √radicand için kayan noktalı tablo yuvarlaması (``E.yuvarla``) ders kuralının kesin sonucunu
    vermeli (``ders_yuvarla_kok``). Vermiyorsa z tam yarımda ya da yarıma çok yakındır (çok büyük ölçekte ya da
    irrasyonel z); sessiz kalınmaz, değerin değiştirilmesi istenir."""

    if float(ders_yuvarla_kok(factor, radicand, 2)) == value:
        return
    if radicand == 1:
        where_z = f"z = {_txt(factor)} tam iki tablo değerinin ortasında ve sayıların büyüklüğü yüzünden"
    else:
        approx = f"{float(factor) * math.sqrt(float(radicand)):.10f}".replace(".", ",").replace("-", "−")
        where_z = f"z ≈ {approx} iki tablo değerinin ortasına çok yakın ve"
    raise K.UploadError(
        f"{where}: {where_z} bilgisayar hesabı tablo kuralını (yarım sıfırdan uzağa) güvenle uygulayamıyor. "
        "Değerlerden birini biraz değiştirin.")


def _context(values: Mapping[str, float], texts: Mapping[str, str] | None) -> dict:
    ctx = {key: kesir_degeri(value) for key, value in values.items()}
    ctx["n"], ctx["k"] = int(values["n"]), int(values["k"])
    ctx["texts"] = dict(texts or {})
    return ctx


def _axis(ctx: dict, key: str, default: str = "x") -> str:
    return ctx["texts"].get(f"{key}_eksen") or default


# --- Adım 1–3: standart normal tablo -----------------------------------------------------------

def _rows(magnitude: Fraction) -> tuple[list[Fraction], Fraction, int]:
    """Tablo kesitinin satırları (|z|'nin satırı ve komşuları, 0,0–3,9), satır ve sütun (ikinci ondalık)."""

    row = Fraction(math.floor(magnitude * 10), 10)
    column = int(magnitude * 100 - row * 100)
    first = min(max(row - Fraction(1, 10), Fraction(0)), Fraction(37, 10))
    return [first + Fraction(index, 10) for index in range(3)], row, column


def _column(offset: int) -> Derive:
    z = E.var("z_satir") if offset == 0 else E.add(E.var("z_satir"), offset / 100)
    return Derive("ztablo", f"s0{offset}", _table(z), f"Sütun 0,0{offset}: Φ(z), dört basamak")


def _step1(ctx: dict) -> LabStep:
    z = ctx["z"]
    magnitude = abs(z)
    rows, row, column = _rows(magnitude)
    M, R, C = _fixed(float(magnitude), 2), _fixed(float(row), 1), f"0,0{column}"
    operations = (
        InlineData("ztablo", ("z_satir",), tuple((float(value),) for value in rows),
                   "Tablo satırları: z'nin birler basamağı ve ilk ondalığı"),
        *(_column(offset) for offset in range(10)),
        ShowFrame("ztablo", ("z_satir", *(f"s0{offset}" for offset in range(10))),
                  f"Standart normal kümülatif tablo kesiti: satır {R}, sütun {C}",
                  decimals=(("z_satir", 1), *((f"s0{offset}", 4) for offset in range(10)))),
        Scalar("Phi_z", _table(float(magnitude)), f"Φ({M}): satır {R}, sütun {C}", decimals=4),
        DensityPlot("normal", 0, 1, (-4, 4), f"Φ({M}) = P(Z ≤ {M}): solundaki alan", "z", y_label="φ(z)",
                    shade=((-4, float(magnitude)),)),
    )
    phi = run_operations(operations).scalars["Phi_z"]
    negative = (f" Tablo pozitif $z$ değerleri içindir; $z = {_tx(z)}$ için önce $|z| = {_tx(magnitude)}$ okunur, "
                "negatif değerin alanı Adım 2'deki simetriyle bulunur." if z < 0 else "")
    checks = [_scalar("Phi_z", f"Φ({M})", 4)]
    for index, value in enumerate(rows, start=1):
        checks.append(Check(f"Tablo: satır {_fixed(float(value), 1)}, sütun {C}",
                            CellTarget("ztablo", f"s0{column}", index), 0.0, 4))
    return LabStep(
        number=1,
        title="Standart normal tablo: Φ(z) = P(Z ≤ z)",
        note=NoteRef("11.1", objects=("Tablo 11.1", "Şekil 11.1", "(11.1)")),
        explanation=(
            "$Z \\sim N(0, 1)$ için $\\Phi(z) = P(Z \\leq z)$, $z$'nin solunda kalan kümülatif alandır (Denklem 11.1). "
            "Tablonun satırı $z$'nin birler basamağı ve ilk ondalığı, sütunu ikinci ondalığıdır: "
            f"$z = {_tx(magnitude)}$ için satır {R}, sütun {C}.{negative} Tablo aşağıda Φ fonksiyonuyla kurulur; "
            "değerler tablodaki gibi dört ondalık basamağa yuvarlanır (ders kuralı: tam yarım sıfırdan uzağa)."
        ),
        operations=operations,
        checks=tuple(checks),
        takeaway=(
            f"Φ({M}) = {_fixed(phi, 4)}: standart normal bir değişken {'' if magnitude == 0 else 'yaklaşık '}"
            f"{_percent(phi)} olasılıkla z = {M} değerinin altında kalır. Φ(z) bir olasılıktır (alan); z ise "
            "konumdur. Bazı tablolar 0 ile z arasındaki alanı ya da kuyruk alanını verir; bu derste temel tablo sol "
            "kümülatif alandır (§11.1)."
        ),
    )


def _step2(ctx: dict) -> LabStep:
    z = ctx["z"]
    magnitude = abs(z)
    M, Z = _fixed(float(magnitude), 2), _fixed(float(z), 2)
    mirror = f"Φ(−{M})" if magnitude else f"Φ({M})"
    operations = (
        Scalar("P_sol", E.ref("Phi_z") if z >= 0 else E.sub(1, E.ref("Phi_z")), f"P(Z ≤ {Z})", decimals=4),
        Scalar("Phi_negatif", E.sub(1, E.ref("Phi_z")), f"{mirror} = 1 − Φ({M})", decimals=4),
        Scalar("Phi_negatif_dogrudan", _table(_c(-magnitude)), f"{mirror}: Φ fonksiyonundan", decimals=4),
        DensityPlot("normal", 0, 1, (-4, 4), f"Sol kuyruk: P(Z ≤ {Z})", "z", y_label="φ(z)", shade=((-4, float(z)),)),
    )
    s = run_operations((Scalar("Phi_z", _table(float(magnitude)), "", 4),) + operations).scalars
    phi, rest = _fixed(s["Phi_z"], 4), _fixed(s["Phi_negatif"], 4)
    if magnitude == 0:
        takeaway = ("Φ(0) = 0,5000: eğri 0 çevresinde simetrik olduğu için sol ve sağ alan eşittir; 1 − Φ(0) de aynı "
                    "sayıyı verir (§11.2).")
    elif z > 0:
        takeaway = (f"P(Z ≤ {Z}) = {phi}. Eğri 0 çevresinde simetrik olduğu için z = −{M} değerinin solundaki alan "
                    f"z = {M} değerinin sağındaki alana eşittir: Φ(−{M}) = 1 − {phi} = {rest}. Negatif z için sol alan "
                    "0,50'den küçüktür (§11.2).")
    else:
        takeaway = (f"P(Z ≤ {Z}) = Φ({Z}) = 1 − Φ({M}) = 1 − {phi} = {rest}: tablo pozitif z verdiği için "
                    "negatif z'nin alanı simetriyle bulunur; Φ fonksiyonu da aynı sayıyı verir. Negatif z için sol "
                    "alan 0,50'den küçüktür (§11.2).")
    return LabStep(
        number=2,
        title="Sol kuyruk ve simetri",
        note=NoteRef("11.2", objects=("Şekil 11.2", "(11.2)", "(11.3)")),
        explanation=(
            "Sol kuyruk olasılığı doğrudan tablodan okunur: $P(Z \\leq z_0) = \\Phi(z_0)$ (Denklem 11.2). Negatif "
            f"$z$ için simetri kullanılır: $\\Phi(-z) = 1 - \\Phi(z)$ (Denklem 11.3). Burada $z = {_tx(z)}$."
        ),
        operations=operations,
        checks=(
            _scalar("P_sol", f"P(Z ≤ {Z})", 4),
            _scalar("Phi_negatif", f"{mirror} = 1 − Φ({M})", 4),
            _scalar("Phi_negatif_dogrudan", f"{mirror} doğrudan", 4),
        ),
        takeaway=takeaway,
    )


def _step3(ctx: dict) -> LabStep:
    z, a, b = ctx["z"], ctx["a"], ctx["b"]
    Z, A, B = _fixed(float(z), 2), _fixed(float(a), 2), _fixed(float(b), 2)
    operations = (
        Scalar("P_sag", E.sub(1, E.ref("P_sol")), f"P(Z > {Z}) = 1 − Φ({Z})", decimals=4),
        Scalar("Phi_a", _table(_c(a)), f"Φ({A})", decimals=4),
        Scalar("Phi_b", _table(_c(b)), f"Φ({B})", decimals=4),
        Scalar("P_arasi", E.sub(E.ref("Phi_b"), E.ref("Phi_a")), "P(a ≤ Z ≤ b): tablo kuralı", decimals=4),
        Scalar("P_arasi_yuvarlamasiz", E.sub(E.normcdf(_c(b)), E.normcdf(_c(a))), "Yuvarlamasız Φ(b) − Φ(a)",
               decimals=4),
        DensityPlot("normal", 0, 1, (-4, 4), f"İki değer arası: P({A} ≤ Z ≤ {B})", "z", y_label="φ(z)",
                    shade=((float(a), float(b)),)),
    )
    s = run_operations((Scalar("Phi_z", _table(float(abs(z))), "", 4),
                        Scalar("P_sol", E.ref("Phi_z") if z >= 0 else E.sub(1, E.ref("Phi_z")), "", 4))
                       + operations[:5]).scalars
    raw = s["P_arasi_yuvarlamasiz"]
    digits = olasilik_basamak(raw)
    operations = _with_decimals(operations, {"P_arasi_yuvarlamasiz": digits})
    table = _fixed(s["P_arasi"], 4)
    if _fixed(raw, 4) == table:
        same = "Yuvarlanmamış Φ değerleri de dört basamakta aynı sonucu verir."
    else:
        same = (f"Yuvarlanmamış Φ değerleriyle sonuç {olasilik_metni(raw, None, digits)}; fark tablonun dört "
                "basamağa yuvarlanmasından gelir.")
    return LabStep(
        number=3,
        title="Sağ kuyruk ve iki değer arası",
        note=NoteRef("11.3", objects=("Şekil 11.3", "(11.4)", "(11.5)")),
        explanation=(
            "Tablo sol alanı verdiği için sağ kuyrukta tümleyen kullanılır: $P(Z > z_0) = 1 - \\Phi(z_0)$ "
            "(Denklem 11.4). İki değer arasındaki alan iki sol alanın farkıdır: "
            f"$P(a \\leq Z \\leq b) = \\Phi(b) - \\Phi(a)$ (Denklem 11.5). Burada $z = {_tx(z)}$; $a = {_tx(a)}$; "
            f"$b = {_tx(b)}$."
        ),
        operations=operations,
        checks=(
            _scalar("P_sag", f"P(Z > {Z})", 4),
            _scalar("Phi_a", f"Φ({A})", 4),
            _scalar("Phi_b", f"Φ({B})", 4),
            _scalar("P_arasi", f"P({A} ≤ Z ≤ {B}) = Φ({B}) − Φ({A})", 4),
            _scalar("P_arasi_yuvarlamasiz", f"P({A} ≤ Z ≤ {B}), yuvarlamasız", digits),
        ),
        takeaway=(
            f"Sağ kuyruk: P(Z > {Z}) = 1 − {_fixed(s['P_sol'], 4)} = {_fixed(s['P_sag'], 4)}. Büyük sol alandan küçük "
            f"sol alan çıkarılınca aradaki şerit kalır: {_fixed(s['Phi_b'], 4)} − "
            f"{_fixed(s['Phi_a'], 4)} = {table}. {same} Sürekli dağılımda < ile ≤ aynı olasılığı verir, çünkü tek bir "
            "noktanın olasılığı sıfırdır (§11.3)."
        ),
    )


# --- Adım 4–5: özgün ölçek ve ters normal ---------------------------------------------------------

def _step4(ctx: dict) -> LabStep:
    mean, sd, x, x1, x2 = ctx["mu"], ctx["sigma"], ctx["x"], ctx["x1"], ctx["x2"]
    zs = {"x": (x - mean) / sd, "1": (x1 - mean) / sd, "2": (x2 - mean) / sd}
    d = {key: _digits(value) for key, value in zs.items()}
    X, X1, X2 = _txt(x), _txt(x1), _txt(x2)
    operations = (
        Scalar("z_x", _z(x, mean, sd), f"x = {X}: z", decimals=d["x"]),
        Scalar("z_x_tablo", E.yuvarla(E.ref("z_x"), 2), "z, tablo için", decimals=2),
        Scalar("P_x_alti", _table(E.ref("z_x_tablo")), "P(X ≤ x), tablo", decimals=4),
        Scalar("P_x_ustu", E.sub(1, E.ref("P_x_alti")), "P(X > x) = 1 − Φ(z), tablo", decimals=4),
        Scalar("P_x_alti_yuv", E.normcdf(E.ref("z_x")), "P(X ≤ x), yuvarlamasız", decimals=4),
        Scalar("P_x_ustu_yuv", E.normcdf(E.neg(E.ref("z_x"))), "P(X > x), yuvarlamasız", decimals=4),
        Scalar("z_1", _z(x1, mean, sd), "z₁ = (x₁ − μ)/σ", decimals=d["1"]),
        Scalar("z_2", _z(x2, mean, sd), "z₂ = (x₂ − μ)/σ", decimals=d["2"]),
        Scalar("z_1_tablo", E.yuvarla(E.ref("z_1"), 2), "z₁, tablo için", decimals=2),
        Scalar("z_2_tablo", E.yuvarla(E.ref("z_2"), 2), "z₂, tablo için", decimals=2),
        Scalar("P_aralik", E.sub(_table(E.ref("z_2_tablo")), _table(E.ref("z_1_tablo"))), "P(x₁ ≤ X ≤ x₂), tablo",
               decimals=4),
        Scalar("P_aralik_yuv", _between(E.ref("z_1"), E.ref("z_2"), x1 >= mean),
               "P(x₁ ≤ X ≤ x₂), yuvarlamasız", decimals=4),
        DensityPlot("normal", float(mean), float(sd),
                    tuple(float(mean + sign * _reach(*zs.values()) * sd) for sign in (-1, 1)),
                    f"{_normal(mean, sd)}: {X1} ile {X2} arasının alanı ve x = {X}", _axis(ctx, "normal"),
                    shade=((float(x1), float(x2)),), references=((float(x), f"x = {X}"),)),
    )
    s = run_operations(operations + (Scalar("Phi_1", _table(E.ref("z_1_tablo")), "", 4),
                                     Scalar("Phi_2", _table(E.ref("z_2_tablo")), "", 4))).scalars
    for key, name in (("x", "z_x_tablo"), ("1", "z_1_tablo"), ("2", "z_2_tablo")):
        _check_table_rule(zs[key], Fraction(1), s[name], "Normal model")
    table_phi = {key: _fixed(s[f"Phi_{key}"], 4) for key in ("1", "2")}

    def z_phrase(key: str, label: str, value: Fraction) -> str:
        text = _z_text(value, float(value), d[key])
        rounded = _fixed(s[{"x": "z_x_tablo", "1": "z_1_tablo", "2": "z_2_tablo"}[key]], 2)
        if ders_yuvarla(value, 2) == value:
            return f"{label} {text}"
        return f"{label} {text} → tablo için {rounded}"

    below, above = _fixed(s["P_x_alti"], 4), _fixed(s["P_x_ustu"], 4)
    phi_zero = Fraction(1, 2) if zs["x"] == 0 else None  # x = μ: Φ(0) = 0,5 tam
    dd = {"P_x_alti_yuv": olasilik_basamak(s["P_x_alti_yuv"], phi_zero),
          "P_x_ustu_yuv": olasilik_basamak(s["P_x_ustu_yuv"], phi_zero),
          "P_aralik_yuv": olasilik_basamak(s["P_aralik_yuv"])}
    operations = _with_decimals(operations, dd)
    if phi_zero is None:
        raw_pair = (f"yuvarlamasız değerler {olasilik_metni(s['P_x_alti_yuv'], None, dd['P_x_alti_yuv'])} ve "
                    f"{olasilik_metni(s['P_x_ustu_yuv'], None, dd['P_x_ustu_yuv'])}")
    else:
        raw_pair = "yuvarlamasız değerler de tam 0,5"
    raw_range = olasilik_metni(s["P_aralik_yuv"], None, dd["P_aralik_yuv"])
    story = ctx["texts"].get("normal")
    lead = f"{story} " if story else ""
    return LabStep(
        number=4,
        title="Özgün ölçekte normal olasılık",
        note=NoteRef("11.4", objects=("Şekil 11.4",)),
        explanation=(
            "Dört adım: istenen alanı belirle, sınırları $z = (x - \\mu)/\\sigma$ ile standartlaştır, $\\Phi(z)$ "
            f"değerlerini bul, sol / sağ / aralık işlemini tamamla. {lead}$X \\sim {_normal_tex(mean, sd)}$; "
            f"$x = {_tx(x)}$ ve $x_1 = {_tx(x1)}$ ile $x_2 = {_tx(x2)}$ arası incelenir. Tablo kuralı: $z$ iki, "
            "$\\Phi(z)$ dört ondalık basamağa yuvarlanır (tam yarım sıfırdan uzağa); yuvarlamasız sonuç da gösterilir. "
            "Yuvarlamasız sağ kuyruk $1 - \\Phi(z) = \\Phi(-z)$ ile hesaplanır: çok küçük kuyruklarda da doğru kalır."
        ),
        operations=operations,
        checks=(
            _scalar("z_x", f"z({X})", d["x"]),
            _scalar("z_x_tablo", f"z({X}), tablo için", 2),
            _scalar("P_x_alti", f"P(X ≤ {X}), tablo kuralı", 4),
            _scalar("P_x_ustu", f"P(X > {X}), tablo kuralı", 4),
            _scalar("P_x_alti_yuv", f"P(X ≤ {X}), yuvarlamasız", dd["P_x_alti_yuv"]),
            _scalar("P_x_ustu_yuv", f"P(X > {X}), yuvarlamasız", dd["P_x_ustu_yuv"]),
            _scalar("z_1_tablo", f"z({X1}), tablo için", 2),
            _scalar("z_2_tablo", f"z({X2}), tablo için", 2),
            _scalar("P_aralik", f"P({X1} ≤ X ≤ {X2}), tablo kuralı", 4),
            _scalar("P_aralik_yuv", f"P({X1} ≤ X ≤ {X2}), yuvarlamasız", dd["P_aralik_yuv"]),
        ),
        takeaway=(
            f"{z_phrase('x', 'x = ' + X + ' için z', zs['x'])}. Tablo kuralıyla P(X ≤ {X}) = {below}; P(X > {X}) = "
            f"1 − {below} = {above}; {raw_pair}. Aynı z değeri sorunun yönüne "
            "göre farklı alan işlemi gerektirir. İki ham sınır için iki ayrı z hesaplanır: "
            f"{z_phrase('1', 'z₁', zs['1'])}; {z_phrase('2', 'z₂', zs['2'])}; P({X1} ≤ X ≤ {X2}) = "
            f"{table_phi['2']} − {table_phi['1']} = {_fixed(s['P_aralik'], 4)} (yuvarlamasız {raw_range}). z bulmak "
            "işlemin sonu değildir; olasılık, uygun alanın hesaplanmasıdır (§11.4)."
        ),
    )


def _step5(ctx: dict) -> LabStep:
    mean, sd, p = ctx["mu"], ctx["sigma"], ctx["p_sol"]
    P = _txt(p)
    probe = run_operations((Scalar("z_p", E.yuvarla(E.norminv(_c(p)), 3), "", 3),)).scalars["z_p"]
    z_exact = kesir_degeri(probe)
    threshold = mean + z_exact * sd
    d_t = kesir_basamak(threshold, 6, 0)
    operations = (
        InlineData("yuzdelik", ("p",), tuple((value,) for value in PERCENTILES),
                   "Tablo 11.2'nin sol kümülatif olasılıkları"),
        Derive("yuzdelik", "z", E.yuvarla(E.norminv(E.var("p")), 3), "z = Φ⁻¹(p), üç ondalık basamak"),
        ShowFrame("yuzdelik", ("p", "z"), "Tablo 11.2: yaygın sol kümülatif olasılıklar ve z değerleri"),
        Scalar("z_p", E.yuvarla(E.norminv(_c(p)), 3), f"Sol alan {P}: z = Φ⁻¹(p)", decimals=3),
        Scalar("esik", E.add(_c(mean), E.mul(E.ref("z_p"), _c(sd))), "Eşik x = μ + zσ", decimals=d_t),
        DensityPlot("normal", 0, 1, (-4, 4), f"Solunda {P} alan bulunan eşik: z = {_fixed(probe, 3)}", "z",
                    y_label="φ(z)", shade=((probe, 4),), references=((probe, f"z = {_fixed(probe, 3)}"),)),
    )
    upper = 1 - p
    share = "%" + _txt(upper * 100)
    Zp = _fixed(probe, 3)
    if probe == 0:
        result = (f"Sol alan 0,5 için z = 0: eşik ortalamanın kendisidir, x = μ = {_txt(mean)}. z = 0 medyana (50. "
                  "yüzdeliğe) karşılık gelir (§11.5).")
    else:
        shown = " ".join(deger_metni(float(threshold), threshold, d_t))
        side = (f"değerlerin en yüksek {share} kadarı bu eşiğin üzerindedir" if p > Fraction(1, 2) else
                f"değerlerin en düşük %{_txt(p * 100)} kadarı bu eşiğin altındadır")
        result = (f"Solunda {P} alan bulunan z yaklaşık {Zp}; {_normal(mean, sd)} için eşik x = {_txt(mean)} + "
                  f"({Zp})({_txt(sd)}) {shown}: {side}. z = 0 medyana (50. yüzdeliğe) karşılık gelir (§11.5).")
    checks = [Check(f"Tablo 11.2: p = {_txt(Fraction(str(value)))}", CellTarget("yuzdelik", "z", index), 0.0, 3)
              for index, value in enumerate(PERCENTILES, start=1)]
    checks += [_scalar("z_p", f"z = Φ⁻¹({P})", 3), _scalar("esik", "Eşik x = μ + zσ", d_t)]
    return LabStep(
        number=5,
        title="Ters normal: olasılıktan eşik değere",
        note=NoteRef("11.5", objects=("Tablo 11.2", "Şekil 11.5")),
        explanation=(
            "Bu kez yön tersinedir: olasılık → $z$ → $x$. Solunda $p$ alan bulunan $z$ değeri $\\Phi^{-1}(p)$ "
            "olur (Tablo 11.2); değer üç ondalık basamakla yazılır. Özgün ölçeğe dönüş $x = \\mu + z\\sigma$ ile "
            f"yapılır. Burada $X \\sim {_normal_tex(mean, sd)}$ ve sol alan $p = {_tx(p)}$: eşiğin üstünde "
            f"{share} alan kalır."
        ),
        operations=operations,
        checks=tuple(checks),
        takeaway=result,
    )


# --- Adım 6–7: binomun normal yaklaştırması ------------------------------------------------------

def _window(n: int, mean: float, sd: float, k: int | None = None) -> tuple[int, int]:
    """Binom olasılık tablosunun değerleri: n ≤ 30 iken 0, …, n; değilse np ± (5σ + 3) (0 ile n arasında) ve x."""

    if n <= LIST_LIMIT:
        low, high = 0, n
    else:
        low, high = max(0, math.floor(mean - 5 * sd) - 3), min(n, math.ceil(mean + 5 * sd) + 3)
    if k is not None:
        low, high = min(low, k), max(high, k)
    return low, high


def _binom_exact(n: int, p: Fraction, k: int) -> Fraction:
    """P(X = k), X ~ Bin(n, p), kesin kesir (p iki ondalıklı): metinde "=" / "≈" bu kesirden."""

    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def _condition(ctx: dict) -> tuple[bool, str]:
    n, p = ctx["n"], ctx["p"]
    successes, failures = n * p, n * (1 - p)
    held = successes >= 5 and failures >= 5
    text = (f"np = {_txt(successes)} {'≥' if successes >= 5 else '<'} 5 ve n(1 − p) = {_txt(failures)} "
            f"{'≥' if failures >= 5 else '<'} 5")
    return held, text


def _step6(ctx: dict) -> LabStep:
    n, p = ctx["n"], ctx["p"]
    successes, failures = n * p, n * (1 - p)
    variance = successes * (1 - p)
    root = kesir_kok(variance)
    d_s = _digits(root) if root is not None else 4
    sd = math.sqrt(float(variance))
    low, high = _window(n, float(successes), sd)
    mode = math.floor((n + 1) * p)
    mode = min(max(mode, low), high)
    P = _txt(p)
    operations = (
        Scalar("np_b", E.mul(n, _c(p)), "np", decimals=_digits(successes)),
        Scalar("nq_b", E.mul(n, E.sub(1, _c(p))), "n(1 − p)", decimals=_digits(failures)),
        Scalar("sigma_b", E.sqrt(E.mul(E.ref("np_b"), E.sub(1, _c(p)))), "σ = √(np(1 − p))", decimals=d_s),
        Support("binom", "x", low, high,
                f"Başarı sayısı x = {_span(low, high)}" if n <= LIST_LIMIT or (low, high) == (0, n) else
                f"Başarı sayısı x = {low}, …, {high} (np ± (5σ + 3); dışarıdaki olasılık ihmal edilebilir)"),
        Derive("binom", "f", E.dbinom(E.var("x"), n, _c(p)), f"P(X = x), X ~ Bin({n}, {P})"),
        Derive("binom", "g", E.dnorm(E.var("x"), E.ref("np_b"), E.ref("sigma_b")),
               "Aynı ortalama ve standart sapmalı normal yoğunluk"),
        ShowFrame("binom", ("x", "f", "g"), "Binom olasılıkları ve normal yoğunluk", decimals=(("f", 6), ("g", 6))),
        PmfWithDensity("binom", "x", "f", "normal", "np_b", "sigma_b", _axis(ctx, "binom", "Başarı sayısı, x"),
                       "Olasılık / yoğunluk", f"Bin({n}, {P}) ve aynı ortalama ile standart sapmalı normal eğri",
                       bar_label="Binom: P(X = x)", curve_label="Normal yaklaşım"),
    )
    state = run_operations(operations)
    frame = state.frames["binom"]
    row = mode - low + 1
    f_mode, g_mode = float(frame["f"].iloc[row - 1]), float(frame["g"].iloc[row - 1])
    peak = (n + 1) * p  # tam sayıysa peak − 1 ve peak eşit olasılıklıdır
    tie = peak.denominator == 1 and 1 <= peak <= n
    mode_label = f"P(X = {mode}): en olası değerlerden biri" if tie else f"P(X = {mode}): en olası değer"
    held, condition = _condition(ctx)
    story = ctx["texts"].get("binom") or _trials(n, P)
    if held:
        shape = f"{condition}: yaklaşım koşulları sağlanır ve iki şekil birbirine yakındır. Yine de"
    else:
        if p == Fraction(1, 2):
            form = ("dağılım simetriktir, ama çubuk sayısı az olduğu için normal eğri çubukları ancak kabaca "
                    "izler")
        else:
            form = (f"dağılım {'sağa' if p < Fraction(1, 2) else 'sola'} çarpıktır; normal eğri çubukları iyi "
                    "izlemeyebilir")
        shape = (f"{condition}: koşul (11.6) sağlanmıyor; beklenen başarı ya da başarısızlık sayısı küçüktür, {form}. "
                 "Ayrıca")
    return LabStep(
        number=6,
        title="Binom dağılımının normal yaklaştırması",
        note=NoteRef("11.7", objects=("Şekil 11.7", "(11.6)")),
        explanation=(
            "$X \\sim \\mathrm{Bin}(n, p)$ için $\\mu = np$ ve $\\sigma = \\sqrt{np(1 - p)}$ olur. Binom dağılımı "
            "yeterince çan biçimine yaklaştığında aynı ortalama ve standart sapmalı normal dağılım yaklaşık model "
            "olur. Pratik koşul: $np \\geq 5$ ve $n(1 - p) \\geq 5$ (Denklem 11.6). "
            f"{story} $X \\sim \\mathrm{{Bin}}({n}, {_tx(p)})$."
        ),
        operations=operations,
        checks=(
            _scalar("np_b", "np", _digits(successes)),
            _scalar("nq_b", "n(1 − p)", _digits(failures)),
            _scalar("sigma_b", "σ = √(np(1 − p))", d_s),
            Check(mode_label, CellTarget("binom", "f", row), 0.0, olasilik_basamak(f_mode, _binom_exact(n, p, mode))),
            Check(f"Normal eğrinin yüksekliği f({mode})", CellTarget("binom", "g", row), 0.0,
                  olasilik_basamak(g_mode)),
        ),
        takeaway=(
            f"{shape} binom yalnız tam sayılarda olasılık taşır, normal eğri süreklidir; bu yüzden yaklaşık "
            "hesapta süreklilik düzeltmesi gerekir. Yalnız n'in büyük olması yetmez: p sıfıra ya da bire çok yakınsa "
            "dağılım çarpık kalabilir (§11.7)."
        ),
    )


def _step7(ctx: dict) -> LabStep:
    n, p, k = ctx["n"], ctx["p"], ctx["k"]
    successes = n * p
    variance = successes * (1 - p)
    root = kesir_kok(variance)
    sd = math.sqrt(float(variance))
    low, high = _window(n, float(successes), sd, k)
    lower, upper = Fraction(2 * k - 1, 2), Fraction(2 * k + 1, 2)
    L, U = _txt(lower), _txt(upper)

    def z_raw(bound: Fraction) -> E.Expr:
        return E.div(E.sub(_c(bound), E.ref("np_b")), E.ref("sigma_b"))

    operations = (
        Scalar("z1_b", E.yuvarla(z_raw(lower), 2), f"z₁ (tablo) = ({L} − np)/σ", decimals=2),
        Scalar("z2_b", E.yuvarla(z_raw(upper), 2), f"z₂ (tablo) = ({U} − np)/σ", decimals=2),
        Scalar("Phi_z1_b", _table(E.ref("z1_b")), "Φ(z₁), tablo", decimals=4),
        Scalar("Phi_z2_b", _table(E.ref("z2_b")), "Φ(z₂), tablo", decimals=4),
        Scalar("P_k_yaklasik", E.sub(E.ref("Phi_z2_b"), E.ref("Phi_z1_b")), f"P(X = {k}) ≈ Φ(z₂) − Φ(z₁)",
               decimals=4),
        Scalar("P_k_yuvarlamasiz", _between(z_raw(lower), z_raw(upper), lower >= successes),
               "Aynı yaklaşım, yuvarlamasız z", decimals=4),
        Scalar("P_k_binom", E.dbinom(k, n, _c(p)), f"Tam binom olasılığı P(X = {k})", decimals=4),
        Support("binom_k", "x", low, high, f"Başarı sayısı x = {_span(low, high)}"),
        Derive("binom_k", "f", E.dbinom(E.var("x"), n, _c(p)), f"P(X = x), X ~ Bin({n}, {_txt(p)})"),
        PmfWithDensity("binom_k", "x", "f", "normal", "np_b", "sigma_b", _axis(ctx, "binom", "Başarı sayısı, x"),
                       "Olasılık / yoğunluk", f"X = {k} için normal yaklaşımda {L} ile {U} arasının alanı",
                       bar_label="Binom: P(X = x)", curve_label="Normal yaklaşım", shade=((float(lower),
                                                                                        float(upper)),)),
    )
    base = (
        Scalar("np_b", E.mul(n, _c(p)), "", 4),
        Scalar("sigma_b", E.sqrt(E.mul(E.ref("np_b"), E.sub(1, _c(p)))), "", 4),
    )
    s = run_operations(base + operations[:7]).scalars
    raw = {}
    for key, bound in (("1", lower), ("2", upper)):
        value = run_operations(base + (Scalar("z", z_raw(bound), "", 4),)).scalars["z"]
        exact = (bound - successes) / root if root else (Fraction(0) if bound == successes else None)
        _check_table_rule(bound - successes, 1 / variance, s[f"z{key}_b"], "Binom yaklaşımı")
        raw[key] = (value, exact)
    digits = {key: onemli_basamak(value, exact) for key, (value, exact) in raw.items()}

    def z_phrase(key: str) -> str:
        value, exact = raw[key]
        text = _z_text(exact, value, digits[key])
        rounded = _fixed(s[f"z{key}_b"], 2)
        if exact is not None and ders_yuvarla(exact, 2) == exact:
            return f"z{'₁' if key == '1' else '₂'} {text}"
        return f"z{'₁' if key == '1' else '₂'} {text} → tablo için {rounded}"

    approximate, rawp, exact_p = s["P_k_yaklasik"], s["P_k_yuvarlamasiz"], s["P_k_binom"]
    binom_exact = _binom_exact(n, p, k)
    dd = {"P_k_yuvarlamasiz": olasilik_basamak(rawp), "P_k_binom": olasilik_basamak(exact_p, binom_exact)}
    operations = _with_decimals(operations, dd)
    held, condition = _condition(ctx)
    warning = "" if held else f" {condition}: koşul (11.6) sağlanmadığı için yaklaşım zayıf olabilir."
    story = ctx["texts"].get("binom") or _trials(n, _txt(p))
    return LabStep(
        number=7,
        title=f"Süreklilik düzeltmesi: tam {k} başarı",
        note=NoteRef("11.8.1", objects=("Şekil 11.8", "Tablo 11.3")),
        explanation=(
            f"{story} Binomda $X = {k}$ tek bir çubuktur; normal eğride tek noktanın alanı sıfırdır. Çubuk "
            f"$0{{,}}5$ birim genişletilir: $P(X = {k}) \\approx P({_tx(lower)} < Y < {_tx(upper)})$, "
            f"$Y \\sim N(np, np(1 - p))$. Sınırlar standartlaştırılıp tablodan okunur (z iki basamak, Φ dört basamak)."
        ),
        operations=operations,
        checks=(
            _scalar("z1_b", f"z₁ = ({L} − np)/σ, tablo için", 2),
            _scalar("z2_b", f"z₂ = ({U} − np)/σ, tablo için", 2),
            _scalar("Phi_z1_b", "Φ(z₁)", 4),
            _scalar("Phi_z2_b", "Φ(z₂)", 4),
            _scalar("P_k_yaklasik", f"P(X = {k}) ≈ Φ(z₂) − Φ(z₁)", 4),
            _scalar("P_k_yuvarlamasiz", f"P(X = {k}), yuvarlamasız z ile", dd["P_k_yuvarlamasiz"]),
            _scalar("P_k_binom", f"Tam binom olasılığı P(X = {k})", dd["P_k_binom"]),
        ),
        takeaway=(
            f"{z_phrase('1')}; {z_phrase('2')}. Tablo değerleriyle yaklaşık olasılık {_fixed(s['Phi_z2_b'], 4)} − "
            f"{_fixed(s['Phi_z1_b'], 4)} = {_fixed(approximate, 4)}. Yuvarlanmamış z ile sonuç "
            f"{olasilik_metni(rawp, None, dd['P_k_yuvarlamasiz'])}; tam binom olasılığı "
            f"{olasilik_metni(exact_p, binom_exact, dd['P_k_binom'])}: sonuç yaklaşıktır.{warning} Süreklilik "
            "düzeltmesinin yönünü ezberlemek yerine olayın kapsadığı tam sayı çubuklarının dış kenarlarını 0,5 "
            "genişletin (§11.8, Tablo 11.3)."
        ),
        code_note=(
            "Tablo kuralı kodda yuvarla() ile yazılır: z iki, Φ(z) dört ondalık basamağa; tam yarım sıfırdan uzağa "
            "gider (np.round ve R'nin round fonksiyonu tam yarımı farklı yuvarlayabilir)."
        ),
    )


# --- Adım 8–10: üstel dağılım --------------------------------------------------------------------

def _exp_prob(t: Fraction, mean) -> E.Expr:
    """P(X ≤ t) = 1 − e^(−t/μ); ``mean`` sabit ya da skaler."""

    return E.sub(1, E.exp(E.neg(E.div(_c(t), mean))))


def _exp_between(t1: Fraction, t2: Fraction, mean) -> E.Expr:
    """P(t₁ < X ≤ t₂) = e^(−t₁/μ) − e^(−t₂/μ): sağ kuyruk olasılıklarının farkı. F(t₂) − F(t₁) farkı uzak kuyrukta iki
    sayı 1'e çok yakın olduğundan sıfıra çökerdi; bu yazılışta çökme olmaz."""

    return E.sub(E.exp(E.neg(E.div(_c(t1), mean))), E.exp(E.neg(E.div(_c(t2), mean))))


def _step8(ctx: dict) -> LabStep:
    mean, t1, t2 = ctx["mu_e"], ctx["t1"], ctx["t2"]
    M, T1, T2 = _txt(mean), _txt(t1), _txt(t2)
    end = _nice_up(max(4 * mean, t2 + mean))
    probe = run_operations((Scalar("a", _exp_prob(t1, _c(mean)), "", 4), Scalar("b", _exp_prob(t2, _c(mean)), "", 4),
                            Scalar("c", _exp_between(t1, t2, _c(mean)), "", 4))).scalars
    d1, d2, d12 = (olasilik_basamak(probe[key]) for key in ("a", "b", "c"))
    if t1 == 0:
        d1 = 0
    operations = (
        Scalar("P_t1", _exp_prob(t1, _c(mean)), "P(X ≤ t₁) = 1 − e^(−t₁/μ)", decimals=d1),
        Scalar("P_t2", _exp_prob(t2, _c(mean)), "P(X ≤ t₂) = 1 − e^(−t₂/μ)", decimals=d2),
        Scalar("P_t12", _exp_between(t1, t2, _c(mean)), "P(t₁ < X ≤ t₂) = e^(−t₁/μ) − e^(−t₂/μ)", decimals=d12),
        DensityPlot("exponential", float(mean), float(mean), (0, float(end)),
                    f"Üstel dağılım, μ = {M}: P(X ≤ {T2})", _axis(ctx, "ustel", "Süre (dakika)"),
                    shade=((0, float(t2)),), references=((float(t1), f"x = {T1}"),)),
    )
    story = ctx["texts"].get("ustel") or f"Bir işlemin tamamlanma süresi ortalaması μ = {M} dakika olan üstel dağılsın."
    first = ("P(X ≤ 0) = 0: süre negatif olamaz" if t1 == 0 else
             f"Tamamlanma süresinin {T1} dakikayı aşmama olasılığı {olasilik_metni(probe['a'], None, d1)}")
    return LabStep(
        number=8,
        title="Üstel dağılım: bekleme ve tamamlanma süreleri",
        note=NoteRef("11.10", objects=("Şekil 11.10", "(11.8)", "(11.9)", "(11.10)")),
        explanation=(
            f"{story} $X \\sim \\mathrm{{Exp}}(\\mu)$, $f(x) = (1/\\mu)e^{{-x/\\mu}}$, $\\mu = {_tx(mean)}$. "
            "Kümülatif olasılık $P(X \\leq x_0) = 1 - e^{-x_0/\\mu}$ (Denklem 11.8), sağ kuyruk "
            "$P(X > x_0) = e^{-x_0/\\mu}$ olur (Denklem 11.9). Aralık olasılığı iki kümülatif olasılığın farkıdır, "
            "$F(t_2) - F(t_1)$; kodda aynı fark sağ kuyruklarla $e^{-t_1/\\mu} - e^{-t_2/\\mu}$ diye yazılır "
            "(uzak kuyrukta iki kümülatif olasılık da 1 değerine çok yakındır ve farkları sıfıra çökerdi). "
            f"$t_1 = {_tx(t1)}$ ve $t_2 = {_tx(t2)}$ dakika."
        ),
        operations=operations,
        checks=(
            _scalar("P_t1", f"P(X ≤ {T1})", 4 if t1 == 0 else d1),  # tam 0: tolerans 0,5 olmasın
            _scalar("P_t2", f"P(X ≤ {T2})", d2),
            _scalar("P_t12", f"P({T1} < X ≤ {T2})", d12),
        ),
        takeaway=(
            f"{first}; {T2} dakikayı aşmama olasılığı {olasilik_metni(probe['b'], None, d2)}; {T1} ile {T2} dakika "
            f"arası {olasilik_metni(probe['c'], None, d12)}. Üstel dağılımda ortalama ile standart sapma eşittir: "
            f"E(X) = σ = {M} dakika (Denklem 11.10). Üstel rassal değişken bir olay sayısı değil, negatif olmayan bir "
            "süredir (§11.10)."
        ),
    )


def _wait(rate: Fraction, t: Fraction, mean_name: str, label: str) -> tuple:
    return (
        Scalar(mean_name, E.div(60, _c(rate)), label, decimals=_digits(60 / rate)),
        E.exp(E.neg(E.div(_c(t), E.ref(mean_name)))),
    )


def _step9(ctx: dict) -> LabStep:
    rate, t = ctx["hiz"], ctx["t"]
    mean = 60 / rate
    R, T = _txt(rate), _txt(t)
    mean_scalar, survival = _wait(rate, t, "mu_bekleme", "Ortalama bekleme μ = 60/λ")
    probe = run_operations((mean_scalar, Scalar("p", survival, "", 4))).scalars
    d = olasilik_basamak(probe["p"])
    end = _nice_up(max(6 * mean, t + mean))
    M = " ".join(deger_metni(float(mean), mean, _digits(mean)))
    operations = (
        mean_scalar,
        Scalar("P_bekleme", survival, "P(X > t) = e^(−t/μ)", decimals=d),
        DensityPlot("exponential", float(mean), float(mean), (0, float(end)),
                    f"Ardışık iki olay arasındaki süre, μ {M} dakika: P(X > {T})", "Bekleme süresi (dakika)",
                    shade=((float(t), float(end)),)),
    )
    story = ctx["texts"].get("poisson") or f"Bir süreçte saatte ortalama {R} olay gerçekleşiyor."
    sign, value = deger_metni(float(mean), mean, _digits(mean))
    return LabStep(
        number=9,
        title="Poisson–üstel ilişkisi: sayı mı, süre mi?",
        note=NoteRef("11.11", objects=("Şekil 11.11", "(11.11)")),
        explanation=(
            f"{story} Bir saatteki olay sayısı Poisson, ardışık iki olay arasındaki süre üsteldir: "
            f"$\\lambda = {_tx(rate)}$. Ortalama bekleme $\\mu = 1/\\lambda$ saattir (Denklem 11.11); birimler "
            "dakikaya çevrilir: "
            f"$\\mu = 60/{_tx(rate)}$ dakika."
        ),
        operations=operations,
        checks=(
            _scalar("mu_bekleme", "Ortalama bekleme (dakika)", _digits(mean)),
            _scalar("P_bekleme", f"P(X > {T})", d),
        ),
        takeaway=(
            f"Saatte {R} olay, olaylar arasında ortalama {value if sign == '=' else 'yaklaşık ' + value} dakika "
            f"demektir. Bir sonraki olaya kadar {T} dakikadan uzun bekleme olasılığı e^(−t/μ) "
            f"{olasilik_metni(probe['p'], None, d)}. “Bir saatte kaç olay?” Poisson'a, “bir sonraki olaya kadar ne "
            "kadar süre?” üstele yönlendirir (§11.11)."
        ),
    )


def _step10(ctx: dict) -> LabStep:
    rate, t, mean_s, sd_s, s = ctx["hiz10"], ctx["t10"], ctx["mu_s"], ctx["sd_s"], ctx["s"]
    mean = 60 / rate
    z = (s - mean_s) / sd_s
    d_z = _digits(z)
    R, T, S = _txt(rate), _txt(t), _txt(s)
    mean_scalar, survival = _wait(rate, t, "mu_T", "Ortalama bekleme μ = 60/λ")
    end = _nice_up(max(6 * mean, t + mean))
    half = _reach(z) * sd_s
    tail = E.normcdf(E.neg(E.ref("z_s")))  # 1 − Φ(z) = Φ(−z); küçük kuyrukta da kesin
    probe = run_operations((mean_scalar, Scalar("P_T", survival, "", 4), Scalar("z_s", _z(s, mean_s, sd_s), "", 4),
                            Scalar("z_s_tablo", E.yuvarla(E.ref("z_s"), 2), "", 2),
                            Scalar("P_s", E.sub(1, _table(E.ref("z_s_tablo"))), "", 4),
                            Scalar("P_s_yuv", tail, "", 4))).scalars
    _check_table_rule(z, Fraction(1), probe["z_s_tablo"], "Bütünleştirici uygulama")
    phi_zero = Fraction(1, 2) if z == 0 else None  # s = μ: Φ(0) = 0,5 tam
    d_T, d_s = olasilik_basamak(probe["P_T"]), olasilik_basamak(probe["P_s_yuv"], phi_zero)
    operations = (
        mean_scalar,
        Scalar("P_T", survival, "P(T > t) = e^(−t/μ)", decimals=d_T),
        Scalar("z_s", _z(s, mean_s, sd_s), "z = (s − μ)/σ", decimals=d_z),
        Scalar("z_s_tablo", E.yuvarla(E.ref("z_s"), 2), "z, tablo için", decimals=2),
        Scalar("P_s", E.sub(1, _table(E.ref("z_s_tablo"))), "P(X > s) = 1 − Φ(z), tablo", decimals=4),
        Scalar("P_s_yuv", tail, "P(X > s) = Φ(−z), yuvarlamasız", decimals=d_s),
        DensityPlot("exponential", float(mean), float(mean), (0, float(end)),
                    "Bir sonraki gelişe kadar süre T", "Bekleme süresi (dakika)", shade=((float(t), float(end)),),
                    references=((float(t), f"t = {T} dakika"),)),
        DensityPlot("normal", float(mean_s), float(sd_s), (float(mean_s - half), float(mean_s + half)),
                    f"{_normal(mean_s, sd_s)}: P(X > {S})", _axis(ctx, "butun", "x"),
                    shade=((float(s), float(mean_s + half)),), references=((float(s), f"s = {S}"),)),
    )
    sign, value = deger_metni(float(mean), mean, _digits(mean))
    zt = _fixed(probe["z_s_tablo"], 2)
    z_part = (f"z = ({S} − {_par(_txt(mean_s))})/{_txt(sd_s)} {_z_text(z, float(z), d_z)}"
              + ("" if ders_yuvarla(z, 2) == z else f" → tablo için {zt}"))
    story = ctx["texts"].get("butun") or (f"Bir işletmeye saatte ortalama {R} müşteri geliyor; günlük satış "
                                          "yaklaşık normal dağılıyor.")
    return LabStep(
        number=10,
        title="Bütünleştirici uygulama: gelişler ve satışlar",
        note=NoteRef("11.13"),
        explanation=(
            f"{story} Bir saatteki müşteri sayısı $N$ Poisson, bir sonraki gelişe kadar geçen süre $T$ üsteldir; "
            f"günlük satış $X \\sim {_normal_tex(mean_s, sd_s)}$. Aynı işletmede farklı sorular farklı dağılımlar "
            f"gerektirir: $P(T > {_tx(t)})$ ve $P(X > {_tx(s)})$. Yuvarlamasız sağ kuyruk "
            "$1 - \\Phi(z) = \\Phi(-z)$ ile hesaplanır."
        ),
        operations=operations,
        checks=(
            _scalar("mu_T", "Ortalama bekleme (dakika), bütünleştirici", _digits(mean)),
            _scalar("P_T", f"P(T > {T})", d_T),
            _scalar("z_s", f"z({S})", d_z),
            _scalar("z_s_tablo", f"z({S}), tablo için", 2),
            _scalar("P_s", f"P(X > {S}), tablo kuralı", 4),
            _scalar("P_s_yuv", f"P(X > {S}), yuvarlamasız", d_s),
        ),
        takeaway=(
            f"Gelişler arasında ortalama {value if sign == '=' else 'yaklaşık ' + value} dakika vardır; bir sonraki "
            f"müşteriye kadar {T} dakikadan fazla bekleme olasılığı {olasilik_metni(probe['P_T'], None, d_T)}. "
            f"{z_part}; günlük satışın {S} değerini aşma olasılığı tablo kuralıyla 1 − "
            f"{_fixed(1 - probe['P_s'], 4)} = {_fixed(probe['P_s'], 4)} (yuvarlamasız "
            f"{olasilik_metni(probe['P_s_yuv'], phi_zero, d_s)}). N sayıdır ve kesiklidir; T ve X süreklidir. Dağılım "
            "seçimi değişkenin adından değil veri üretim mekanizmasından gelir (§11.12, §11.13)."
        ),
    )


def build(values: Mapping[str, float], texts: Mapping[str, str] | None = None, source: str = "kendi") -> LabSpec:
    """Konu 11 uygulamasını verilen parametrelerle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    validate(values)
    ctx = _context(values, texts)
    steps = (_step1(ctx), _step2(ctx), _step3(ctx), _step4(ctx), _step5(ctx), _step6(ctx), _step7(ctx), _step8(ctx),
             _step9(ctx), _step10(ctx))
    spec = LabSpec(
        topic_key="konu11",
        title=TITLE,
        note_section="11",
        steps=steps,
        labels=(
            ("z_satir", "z satırı"),
            *((f"s0{offset}", f"0,0{offset}") for offset in range(10)),
            ("p", "P(Z ≤ z)"),
            ("z", "z"),
            ("x", "x"),
            ("f", "P(X = x)"),
            ("g", "Normal yoğunluk f(x)"),
        ),
        source=source,
    )
    return with_app_values(isaretsiz_skalerler(spec))


def _inside(value: Fraction, mean: Fraction, sd: Fraction) -> bool:
    return abs(value - mean) <= REACH * sd


def validate(values: Mapping[str, float]) -> None:
    """Parametreler arasındaki koşullar: a < b; x₁ < x₂; değerler μ ± 10σ içinde; x ≤ n; t₁ < t₂."""

    q = {key: kesir_degeri(value) for key, value in values.items()}
    if q["a"] >= q["b"]:
        raise K.UploadError(f"Standart normal: a ({_txt(q['a'])}) b'den ({_txt(q['b'])}) küçük olmalıdır.")
    mean, sd = q["mu"], q["sigma"]
    reach = f"μ ± 10σ aralığında ({_txt(mean - REACH * sd)} ile {_txt(mean + REACH * sd)} arası)"
    if q["x1"] >= q["x2"]:
        raise K.UploadError(f"Normal model: aralığın alt ucu x₁ ({_txt(q['x1'])}) üst ucu x₂'den ({_txt(q['x2'])}) "
                            "küçük olmalıdır.")
    if not all(_inside(q[key], mean, sd) for key in ("x", "x1", "x2")):
        raise K.UploadError(f"Normal model: x, x₁ ve x₂ {reach} olmalıdır; daha uzak değerlerin kuyruk olasılığı "
                            "10⁻²³'ten küçüktür.")
    if int(values["k"]) > int(values["n"]):
        raise K.UploadError(f"Binom: başarı sayısı x ({int(values['k'])}) deneme sayısı n'den ({int(values['n'])}) "
                            "büyük olamaz.")
    if q["t1"] >= q["t2"]:
        raise K.UploadError(f"Üstel: t₁ ({_txt(q['t1'])}) t₂'den ({_txt(q['t2'])}) küçük olmalıdır.")
    if not _inside(q["s"], q["mu_s"], q["sd_s"]):
        raise K.UploadError(f"Bütünleştirici uygulama: satış eşiği μ ± 10σ aralığında "
                            f"({_txt(q['mu_s'] - REACH * q['sd_s'])} ile {_txt(q['mu_s'] + REACH * q['sd_s'])} arası) "
                            "olmalıdır.")


# --- Alternatif örnek ve kendi değerlerin ----------------------------------------------------

@cache
def alternative() -> LabSpec:
    return build(ALT_VALUES, ALT_TEXTS, source="alternatif")


G_STANDARD, G_NORMAL, G_BINOM, G_EXP, G_LAST = ("Standart normal · Adım 1–3", "Normal model · Adım 4–5",
                                                "Binom · Adım 6–7", "Üstel · Adım 8–9", "Bütünleştirici · Adım 10")


def _number(key: str, label: str, low: float, high: float, group: str, steps: tuple[int, ...], help: str,
            step: float = 1, decimals: int = 2) -> Parameter:
    return Parameter(key, label, low, high, ALT_VALUES[key], step=step, decimals=decimals, group=group, steps=steps,
                     help=help)


PARAMETERS = (
    _number("z", "z değeri", -float(Z_LIMIT), float(Z_LIMIT), G_STANDARD, (1, 2, 3),
            "Tablodan okunan z; Φ(z), Φ(−z) ve P(Z > z).", step=0.01),
    _number("a", "Alt sınır a", -float(Z_LIMIT), float(Z_LIMIT), G_STANDARD, (3,), "P(a ≤ Z ≤ b) için alt sınır.",
            step=0.01),
    _number("b", "Üst sınır b", -float(Z_LIMIT), float(Z_LIMIT), G_STANDARD, (3,),
            "P(a ≤ Z ≤ b) için üst sınır; a'dan büyük.", step=0.01),
    _number("mu", "Ortalama μ", -LIMIT, LIMIT, G_NORMAL, (4, 5), "N(μ, σ²) dağılımının ortalaması."),
    _number("sigma", "Standart sapma σ", 0.01, SCALE_LIMIT, G_NORMAL, (4, 5), "N(μ, σ²) dağılımının standart sapması.",
            step=0.5),
    _number("x", "Değer x", -LIMIT, LIMIT, G_NORMAL, (4,), "P(X ≤ x) ve P(X > x); μ ± 10σ içinde."),
    _number("x1", "Aralığın alt ucu x₁", -LIMIT, LIMIT, G_NORMAL, (4,), "P(x₁ ≤ X ≤ x₂); μ ± 10σ içinde."),
    _number("x2", "Aralığın üst ucu x₂", -LIMIT, LIMIT, G_NORMAL, (4,), "x₁'den büyük olmalıdır."),
    _number("p_sol", "Ters normal: sol alan p", 0.001, 0.999, G_NORMAL, (5,),
            "Eşiğin solundaki alan; üst %10'luk grubun eşiği için p = 0,90.", step=0.005, decimals=3),
    Parameter("n", "Deneme sayısı n", 1, 1000, ALT_VALUES["n"], group=G_BINOM, steps=(6, 7),
              help="Bağımsız deneme sayısı."),
    _number("p", "Başarı olasılığı p", 0.01, 0.99, G_BINOM, (6, 7), "Her denemede başarı olasılığı (iki ondalık).",
            step=0.01),
    Parameter("k", "Başarı sayısı x", 0, 1000, ALT_VALUES["k"], group=G_BINOM, steps=(7,),
              help="P(X = x) için başarı sayısı; n'den büyük olamaz."),
    _number("mu_e", "Ortalama süre μ (dakika)", 0.01, LIMIT, G_EXP, (8,), "Üstel dağılımın ortalaması (σ = μ)."),
    _number("t1", "Süre t₁ (dakika)", 0, LIMIT, G_EXP, (8,), "P(X ≤ t₁) ve P(t₁ < X ≤ t₂)."),
    _number("t2", "Süre t₂ (dakika)", 0.01, LIMIT, G_EXP, (8,), "t₁'den büyük olmalıdır."),
    _number("hiz", "Saatlik ortalama λ", 0.01, LIMIT, G_EXP, (9,),
            "Bir saatteki ortalama olay sayısı; μ = 60/λ dakika."),
    _number("t", "Bekleme t (dakika)", 0.01, LIMIT, G_EXP, (9,), "P(X > t): t dakikadan uzun bekleme."),
    _number("hiz10", "Saatlik ortalama λ", 0.01, LIMIT, G_LAST, (10,), "Saatteki ortalama müşteri sayısı."),
    _number("t10", "Bekleme t (dakika)", 0.01, LIMIT, G_LAST, (10,), "P(T > t)."),
    _number("mu_s", "Satış ortalaması μ", -LIMIT, LIMIT, G_LAST, (10,), "Günlük satışın ortalaması."),
    _number("sd_s", "Satış standart sapması σ", 0.01, SCALE_LIMIT, G_LAST, (10,), "Günlük satışın standart sapması.",
            step=0.5),
    _number("s", "Satış eşiği s", -LIMIT, LIMIT, G_LAST, (10,), "P(X > s); μ ± 10σ içinde."),
)

PARAMS = ParamLab(
    parameters=PARAMETERS,
    build=lambda values: build(values),
    intro=(
        "Bu konuda dosya yüklenmez: notlardaki her örnek için değerleri aşağıya girin. Standart normal değerler Adım "
        "1–3'ü, normal model Adım 4–5'i, binom değerleri Adım 6–7'yi, üstel değerler Adım 8–9'u, son grup "
        "bütünleştirici uygulamayı (Adım 10) kurar. Başlangıç değerleri alternatif örneğinkilerdir."
    ),
    groups=(G_STANDARD, G_NORMAL, G_BINOM, G_EXP, G_LAST),
    validate=validate,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, params=PARAMS)


def default_values() -> dict[str, int | float]:
    return parameter_values(PARAMS)
