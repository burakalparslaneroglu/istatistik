"""Konu 10 genel uygulaması: tek-düze dağılım, yoğunluk yüksekliği, normal eğri altındaki alanlar ve z-dönüşümü.

Ders notlarındaki adımlar (§10.3, §10.4, §10.8, §10.10–§10.12 ve §10.14) aynı numaralarla, parametreleri
değiştirilebilir biçimde yazılır. Bu konuda dosya yoktur: "Kendi değerlerini gir" seçeneğinde öğrenci notlardaki her
örnek için ayrı değerler girer: tek-düze dağılım U(a, b), incelenen [c, d] aralığı ve dar dağılım U(0, w) (Adım 1–2);
normal dağılım N(μ, σ²), bir x değeri, bir z₀ ve bir [x₁, x₂] aralığı (Adım 3, 4, 6); iki ölçekteki değerler (Adım 5);
bütünleştirici uygulamanın normal dağılımı ve iki değeri (Adım 7). Alternatif örnek kurgusaldır (kargo deposu, tartı,
kahve paketi, iki ürün, fırın). Notlardaki uygulama (``core.labs.konu10``) değişmez.

Normal eğri altındaki alanlar notlardaki gibi Φ tablosu kullanılmadan, eğrinin altı dar dikdörtgenlere bölünerek
bulunur (orta nokta kuralı): Adım 3'te μ ± 6σ aralığı σ/1000 genişliğinde 12 000 dikdörtgen, Adım 6'da [x₁, x₂]
aralığı standart ölçekte en çok 0,001 genişliğinde dikdörtgenler, Adım 7'de μ ± 2σ aralığı 4000 dikdörtgen. Girilen
değerler kesin kesirlere çevrilir; z, μ ± kσ ve olasılık oranları kesin hesaplanır ve metindeki "=" / "≈" ayrımı bu
kesirden kurulur.
"""

from __future__ import annotations

import math
from fractions import Fraction
from functools import cache
from typing import Mapping

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs.ornek import (
    Parameter,
    ParamLab,
    TopicVariants,
    deger_metni,
    deger_tex,
    kesir_ayirt,
    kesir_degeri,
    kesir_yuzde,
    kisa_kesir as _txt,
    kisa_kesir_tex as _tx,
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
    BarChart,
    CellTarget,
    Check,
    DensityPlot,
    Derive,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    Rectangles,
    Scalar,
    ScalarTarget,
    ShowFrame,
    Statistic,
)

TITLE = "Sürekli dağılımlarda alanı, normal eğriyi ve z-dönüşümünü uygulamak"
GRID = 1000
"""Adım 3 ve 7: dikdörtgen genişliği σ/1000 (standart ölçekte 0,001); μ ± 6σ aralığı 12 000 dikdörtgen."""
COUNTS = (1000, 2000, 4000, 5000, 8000, 10000, 16000, 20000)
"""Adım 6: aralığın dikdörtgen sayısı; standart ölçekte genişlik en çok 0,001. Sayılar 2ᵃ5ᵇ biçimindedir: genişlik
(x₂ − x₁)/k kısa bir ondalık sayı olur."""
FRAME6 = "aralik_izgara"
"""Adım 6'nın dikdörtgen çerçevesi. Ad, kod üreticilerinin döngü değişkenlerinden farklıdır (R'de boyalı alan döngüsü
``aralik`` kullanır)."""
REACH = 10
"""x, x₁, x₂ ve bütünleştirici uygulamanın değerleri μ ± 10σ içinde: daha uzak değerlerin kuyruk olasılığı 10⁻²³'ten
küçüktür ve grafik ekseni anlamlı kalır."""
LIMIT = 100000
SCALE_LIMIT = 10000
"""Standart sapmaların üst sınırı (konum değerleri ±10⁵); Konu 11–12 ile aynı aralık."""

ALT_VALUES = {"a": 30, "b": 90, "c": 42, "d": 78, "w": 0.4, "mu": 250, "sigma": 4, "x": 257, "z0": -1.25, "x1": 246,
              "x2": 258, "xA": 62, "muA": 55, "sdA": 5, "xB": 81, "muB": 72, "sdB": 7.5, "mu7": 400, "sd7": 8,
              "v1": 416, "v2": 394}
ALT_TEXTS = {
    "tekduze": ("Bir kargo deposunda paketlerin rafta bekleme süresi 30 ile 90 dakika arasında tek-düze dağılsın; "
                "42–78 dakika aralığı incelenir."),
    "tekduze_eksen": "Bekleme süresi (dakika)",
    "dar": "Hassas bir tartının ölçüm hatası 0 ile 0,4 gram arasında tek-düze dağılsın.",
    "dar_eksen": "Ölçüm hatası (gram)",
    "normal": "Bir kavurma tesisinde kahve paketlerinin ağırlığı (gram) yaklaşık normal dağılsın.",
    "normal_eksen": "Paket ağırlığı (gram)",
    "olcek": ("Bir mağaza zincirinde iki ürünün bu ayki satışı (bin adet) kendi ürün grubunun dağılımıyla "
              "karşılaştırılır: A ürünü 62 (grup ortalaması 55, standart sapma 5), B ürünü 81 (grup ortalaması 72, "
              "standart sapma 7,5)."),
    "butun": "Bir fırında ekmeklerin ağırlığı (gram) yaklaşık normal dağılsın.",
    "butun_eksen": "Ekmek ağırlığı (gram)",
}
STORY = (
    "Kurgusal veri: kargo deposunda bekleme süresi U(30, 90) dakika ve 42–78 dakika aralığı, tartı hatası U(0, 0,4) "
    "gram, kahve paketi ağırlığı N(250, 4²) gram, iki ürünün kendi gruplarındaki satışı ve ekmek ağırlığı N(400, 8²) "
    "gram."
)


# --- Sayı yazımı ----------------------------------------------------------------------------

def _digits(value: Fraction, minimum: int = 0) -> int:
    """Kesin bir büyüklüğün gösterim basamağı (``onemli_basamak``): en çok dört; çok küçük değerlerde üç anlamlı
    basamak (1/(b − a) = 0,000025 "≈ 0" görünmez)."""

    return onemli_basamak(float(value), value, minimum)


def _sign_value(value: Fraction, digits: int) -> str:
    """Grafik etiketinde "z = 1,75" ya da "z ≈ 2,3333" için işaret ve sayı: "= 1,75", "≈ 2,3333"."""

    return " ".join(deger_metni(float(value), value, digits))


def _percent_text(share: Fraction) -> str:
    """Olasılığın yüzdesi düzyazıda: %60; yaklaşık %33,3; %1'in altında anlamlı basamaklarla (%0,001)."""

    if share == 0 or share * 100 >= 1:
        return kesir_yuzde(share)
    percent = share * 100
    sign, text = deger_metni(float(percent), percent, onemli_basamak(float(percent), percent))
    return f"%{text}" if sign == "=" else f"yaklaşık %{text}"


def _amount(value: Fraction, digits: int) -> str:
    """Düzyazıda bir büyüklük: tam yazılabiliyorsa olduğu gibi, değilse başında "yaklaşık" (1,75; yaklaşık 0,3333)."""

    sign, text = deger_metni(float(value), value, digits)
    return text if sign == "=" else f"yaklaşık {text}"


def _shown(value: float, digits: int) -> str:
    """Kesin değeri olmayan (alan, σ) bir sayı düzyazıda "≈ 0,6827"."""

    return " ".join(deger_metni(value, None, digits))


def _normal(mean: Fraction, sd: Fraction) -> str:
    return f"N({_txt(mean)}, {_txt(sd)}²)"


def _normal_tex(mean: Fraction, sd: Fraction) -> str:
    return f"N({_tx(mean)}, {_tx(sd)}^2)"


def _between(low: Fraction, high: Fraction) -> E.Expr:
    """Gösterge: low ≤ x ≤ high ise 1, değilse 0."""

    return E.mul(E.compare("ge", E.var("x"), _c(low)), E.compare("le", E.var("x"), _c(high)))


def _z(x: Fraction, mean: Fraction, sd: Fraction) -> E.Expr:
    return E.div(E.sub(_c(x), _c(mean)), _c(sd))


def _reach(*values: Fraction) -> int:
    """Grafik ekseninin yarı genişliği (σ cinsinden): en az 4; gösterilen z değerlerini kapsayacak kadar."""

    return max(4, *(math.ceil(abs(value) + Fraction(1, 2)) for value in values))


def _position(z: Fraction, digits: int) -> str:
    """Değerin ortalamaya göre konumu: "1,75 standart sapma üzerindedir", "ortalamanın kendisidir"."""

    if z == 0:
        return "ortalamanın kendisidir"
    side = "üzerindedir" if z > 0 else "altındadır"
    return f"ortalamanın {_amount(abs(z), digits)} standart sapma {side}"


def _scalar(name: str, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _context(values: Mapping[str, float], texts: Mapping[str, str] | None) -> dict:
    ctx = {key: kesir_degeri(value) for key, value in values.items()}
    ctx["texts"] = dict(texts or {})
    return ctx


def _axis(ctx: dict, key: str) -> str:
    return ctx["texts"].get(f"{key}_eksen") or "x"


# --- Adımlar -------------------------------------------------------------------------------

def _step1(ctx: dict) -> LabStep:
    a, b, c, d = ctx["a"], ctx["b"], ctx["c"], ctx["d"]
    length = b - a
    height, share = 1 / length, (d - c) / length
    mean, variance = (a + b) / 2, length ** 2 / 12
    d_f, d_p, d_m, d_v = _digits(height), _digits(share, 2), _digits(mean), _digits(variance)
    d_sd = onemli_basamak(math.sqrt(float(variance)))
    A, B, C, D = (_txt(value) for value in (a, b, c, d))
    Am, Bm, Cm, Dm = (_tx(value) for value in (a, b, c, d))
    operations = (
        Scalar("f_tekduze", E.div(1, E.sub(_c(b), _c(a))), "f(x) = 1/(b − a)", decimals=d_f),
        Scalar("P_dikdortgen", E.mul(E.sub(_c(d), _c(c)), E.ref("f_tekduze")), "Dikdörtgen: (d − c) f(x)",
               decimals=d_p),
        Scalar("P_oran", E.div(E.sub(_c(d), _c(c)), E.sub(_c(b), _c(a))), "(d − c)/(b − a): oran", decimals=d_p),
        Scalar("mu_tekduze", E.div(E.add(_c(a), _c(b)), 2), "μ = (a + b)/2", decimals=d_m),
        Scalar("var_tekduze", E.div(E.power(E.sub(_c(b), _c(a)), 2), 12), "σ² = (b − a)²/12", decimals=d_v),
        Scalar("sd_tekduze", E.sqrt(E.ref("var_tekduze")), "σ = √σ²", decimals=d_sd),
        DensityPlot("uniform", float(a), float(b), (float(a - length / 5), float(b + length / 5)),
                    f"U({A}, {B}): {C} ile {D} arasının alanı", _axis(ctx, "tekduze"), shade=((float(c), float(d)),)),
    )
    sd = run_operations(operations).scalars["sd_tekduze"]
    story = ctx["texts"].get("tekduze") or f"X, {A} ile {B} arasında tek-düze dağılsın."
    sign, P = deger_metni(float(share), share, d_p)
    if share == 1:
        lead = (f"Aralık dağılımın bütününü kapsar: P({C} ≤ X ≤ {D}) = 1; boyalı dikdörtgen bütün dikdörtgendir "
                f"(genişlik {_txt(d - c)}; yükseklik 1/{_txt(length)}).")
    else:
        lead = (f"Boyalı dikdörtgenin alanı (d − c) × f(x) = {_txt(d - c)} × (1/{_txt(length)}) {sign} {P}: X, "
                f"{_percent_text(share)} olasılıkla {C} ile {D} arasında bir değer alır.")
    return LabStep(
        number=1,
        title="Tek-düze dağılım: olasılık dikdörtgenin alanıdır",
        note=NoteRef("10.3", objects=("Şekil 10.4",)),
        explanation=(
            f"{story} $X \\sim U({Am}, {Bm})$. Yoğunluk bu aralıkta sabittir: $f(x) = 1/(b - a) = 1/({Bm} - "
            f"{_par(Am)}) {deger_tex(float(height), height, d_f)}$. $P({Cm} \\leq X \\leq {Dm})$, yüksekliği $f(x)$ "
            f"ve genişliği $d - c = {Dm} - {_par(Cm)}$ olan dikdörtgenin alanıdır; aynı sonuç uzunluk oranından da "
            "bulunur: $(d - c)/(b - a)$. Ortalama aralığın orta noktası $(a + b)/2$, varyans $(b - a)^2/12$ olur: "
            f"$\\mu {deger_tex(float(mean), mean, d_m)}$; $\\sigma^2 {deger_tex(float(variance), variance, d_v)}$; "
            f"$\\sigma {deger_tex(sd, None, d_sd)}$."
        ),
        operations=operations,
        checks=(
            _scalar("f_tekduze", f"f(x) = 1/({B} − {_par(A)})", d_f),
            _scalar("P_dikdortgen", f"P({C} ≤ X ≤ {D}): dikdörtgenin alanı", d_p),
            _scalar("P_oran", f"P({C} ≤ X ≤ {D}): uzunluk oranı", d_p),
            _scalar("mu_tekduze", "μ = (a + b)/2", d_m),
            _scalar("var_tekduze", "σ² = (b − a)²/12", d_v),
            _scalar("sd_tekduze", "σ", d_sd),
        ),
        takeaway=(
            f"{lead} Tek-düze dağılımda eşit uzunluktaki alt aralıkların olasılıkları eşittir; “bütün değerler eşit "
            "olasılıklı” demek yanlıştır, çünkü her tekil değerin olasılığı sıfırdır (§10.3)."
        ),
    )


def _step2(ctx: dict) -> LabStep:
    w = ctx["w"]
    height = 1 / w
    d_f = _digits(height)
    W, Wm = _txt(w), _tx(w)
    sign, F = deger_metni(float(height), height, d_f)
    shown = F if sign == "=" else f"≈ {F}"
    operations = (
        Scalar("f_dar", E.div(1, _c(w)), "f(x) = 1/w", decimals=d_f),
        Scalar("alan_dar", E.mul(_c(w), E.ref("f_dar")), "Toplam alan = w × f(x)", decimals=0),
        DensityPlot("uniform", 0, float(w), (float(-w / 5), float(w * 13 / 10)),
                    f"U(0, {W}): yükseklik {shown}; toplam alan 1", _axis(ctx, "dar"), shade=((0, float(w)),)),
    )
    story = ctx["texts"].get("dar")
    lead = f"{story} " if story else ""
    if height > 1:
        case = ("Yükseklik 1'den büyüktür, ama olasılık kuralları yükseklik için değil alan için geçerlidir: toplam "
                "alan $w \\times f(x) = w \\times (1/w) = 1$.")
        takeaway = (f"Yoğunluk yüksekliği {_amount(height, d_f)} olsa da dağılım geçerlidir; 0 ile 1 arasında olması "
                    "gereken büyüklük alandır. Yüksekliğin 1'i aşamayacağı düşüncesi kesikli olasılık fonksiyonunu "
                    "sürekli yoğunlukla karıştırmaktan gelir (§10.4).")
    elif height == 1:
        case = ("Genişlik 1 olduğu için yükseklik de tam 1'dir; olasılık kuralları yine yükseklik için değil alan için "
                "geçerlidir: toplam alan $w \\times f(x) = 1$.")
        takeaway = ("0 ile 1 arasında olması gereken büyüklük yükseklik değil alandır. Genişliği 1'den küçük bir "
                    "tek-düze dağılımda yükseklik 1'i aşar ve dağılım yine geçerlidir (§10.4).")
    else:
        case = ("Genişlik 1'den büyük olduğu için yükseklik 1'in altındadır; genişlik 1'den küçük seçilseydi yükseklik "
                "1'i aşardı. Olasılık kuralları yükseklik için değil alan için geçerlidir: toplam alan "
                "$w \\times f(x) = w \\times (1/w) = 1$.")
        takeaway = ("0 ile 1 arasında olması gereken büyüklük yükseklik değil alandır. Genişliği 1'den küçük bir "
                    "tek-düze dağılımda yükseklik 1'i aşar ve dağılım yine geçerlidir; yüksekliğin 1'i aşamayacağı "
                    "düşüncesi kesikli olasılık fonksiyonunu sürekli yoğunlukla karıştırmaktan gelir (§10.4).")
    return LabStep(
        number=2,
        title="Yoğunluk yüksekliği olasılık değildir",
        note=NoteRef("10.4", objects=("Şekil 10.5",)),
        explanation=(
            f"{lead}$X \\sim U(0, {Wm})$ ise yoğunluğun yüksekliği $f(x) = 1/{Wm} "
            f"{deger_tex(float(height), height, d_f)}$ olur. {case}"
        ),
        operations=operations,
        checks=(
            _scalar("f_dar", f"f(x) = 1/{W}", d_f),
            _scalar("alan_dar", "Toplam alan w × f(x)", 0),
        ),
        takeaway=takeaway,
    )


def _step3(ctx: dict) -> LabStep:
    mean, sd = ctx["mu"], ctx["sigma"]
    width = sd / GRID
    lower, upper = mean - 6 * sd, mean + 6 * sd
    bounds = {k: (mean - k * sd, mean + k * sd) for k in (1, 2, 3)}
    text = {k: (_txt(low), _txt(high)) for k, (low, high) in bounds.items()}
    operations = (
        Scalar("alt_1", E.sub(_c(mean), _c(sd)), "μ − σ", decimals=_digits(bounds[1][0])),
        Scalar("ust_1", E.add(_c(mean), _c(sd)), "μ + σ", decimals=_digits(bounds[1][1])),
        Scalar("alt_2", E.sub(_c(mean), E.mul(2, _c(sd))), "μ − 2σ", decimals=_digits(bounds[2][0])),
        Scalar("ust_2", E.add(_c(mean), E.mul(2, _c(sd))), "μ + 2σ", decimals=_digits(bounds[2][1])),
        Rectangles("izgara", "x", float(lower), float(upper), float(width),
                   f"μ ± 6σ aralığı ({_txt(lower)} ile {_txt(upper)} arası) σ/1000 = {_txt(width)} genişliğinde "
                   "dikdörtgenlere"),
        Derive("izgara", "f", E.dnorm(E.var("x"), _c(mean), _c(sd)), "Dikdörtgenin yüksekliği f(x)"),
        Derive("izgara", "alan", E.mul(E.var("f"), float(width)), "Dikdörtgenin alanı f(x) × genişlik"),
        Derive("izgara", "sol", E.compare("le", E.var("x"), _c(mean)), "x ≤ μ: ortalamanın solu"),
        *(Derive("izgara", name, _between(*bounds[k]), f"μ ± {k if k > 1 else ''}σ: {text[k][0]} ≤ x ≤ {text[k][1]}")
          for k, name in ((1, "bir"), (2, "iki"), (3, "uc"))),
        Statistic("izgara", "alan", "sum", "alan_toplam", "Toplam alan", decimals=3),
        Statistic("izgara", "alan", "sum", "alan_sol", "P(X ≤ μ): μ'nun solu", where=("sol", 1), decimals=3),
        Statistic("izgara", "alan", "sum", "alan_bir", "P(μ − σ ≤ X ≤ μ + σ)", where=("bir", 1), decimals=4),
        Statistic("izgara", "alan", "sum", "alan_iki", "P(μ − 2σ ≤ X ≤ μ + 2σ)", where=("iki", 1), decimals=4),
        Statistic("izgara", "alan", "sum", "alan_uc", "P(μ − 3σ ≤ X ≤ μ + 3σ)", where=("uc", 1), decimals=4),
        DensityPlot("normal", float(mean), float(sd), (float(mean - 4 * sd), float(mean + 4 * sd)),
                    f"{_normal(mean, sd)}: μ ± σ aralığının alanı", _axis(ctx, "normal"),
                    shade=((float(bounds[1][0]), float(bounds[1][1])),)),
    )
    s = run_operations(operations).scalars
    story = ctx["texts"].get("normal")
    lead = f"{story} " if story else ""
    areas = "; ".join(f"P({low} ≤ X ≤ {high}) {_shown(s[name], 4)}" for (low, high), name
                      in zip(text.values(), ("alan_bir", "alan_iki", "alan_uc")))
    return LabStep(
        number=3,
        title="Normal eğri altındaki alanlar: 68–95–99,7 kuralı",
        note=NoteRef("10.8", objects=("Şekil 10.9",)),
        explanation=(
            f"{lead}$X \\sim {_normal_tex(mean, sd)}$ olsun. Olasılık eğri altındaki alandır: μ ± 6σ aralığı "
            f"({_txt(lower)} ile {_txt(upper)} arası) σ/1000 = {_txt(width)} genişliğinde 12 000 dikdörtgene bölünür, "
            "her dikdörtgenin alanı yükseklik $f(x)$ × genişliktir. Bir aralığın olasılığı, o aralıktaki "
            "dikdörtgenlerin alanları toplanarak bulunur. Φ tablosuyla alan hesabı Konu 11'in konusudur."
        ),
        operations=operations,
        checks=(
            _scalar("alt_1", "μ − σ", _digits(bounds[1][0])),
            _scalar("ust_1", "μ + σ", _digits(bounds[1][1])),
            _scalar("alt_2", "μ − 2σ", _digits(bounds[2][0])),
            _scalar("ust_2", "μ + 2σ", _digits(bounds[2][1])),
            _scalar("alan_toplam", "Eğri altındaki toplam alan", 3),
            _scalar("alan_sol", "μ'nun solundaki alan", 3),
            _scalar("alan_bir", "μ ± σ", 4),
            _scalar("alan_iki", "μ ± 2σ", 4),
            _scalar("alan_uc", "μ ± 3σ", 4),
        ),
        takeaway=(
            f"{areas}: değerlerin yaklaşık %68,3; %95,4 ve %99,7 kadarı ortalamanın bir, iki ve üç standart sapma "
            "çevresindedir. Dikdörtgenlerin toplamı eğri altındaki alana çok yakındır: toplam alan 1, simetri "
            "nedeniyle ortalamanın solundaki alan 0,50. Kural μ ve σ ne olursa olsun aynıdır, ama yalnız yaklaşık "
            "normal (çan biçimli) dağılımlarda kullanılır (§10.5, §10.8)."
        ),
    )


def _step4(ctx: dict) -> LabStep:
    mean, sd, x, z0 = ctx["mu"], ctx["sigma"], ctx["x"], ctx["z0"]
    z = (x - mean) / sd
    mirror = 2 * mean - x
    x0 = mean + z0 * sd
    d_z, d_x0 = _digits(z), _digits(x0)
    X, Xm, Z0, X0 = _txt(x), _txt(mirror), _txt(z0), _txt(x0)
    sign, Zabs = deger_metni(float(abs(z)), abs(z), d_z)
    operations = [Scalar("z_x", _z(x, mean, sd), f"x = {X}: z", decimals=d_z)]
    checks = [_scalar("z_x", f"z({X})", d_z)]
    if z != 0:
        operations.append(Scalar("z_ayna", _z(mirror, mean, sd), f"x = {Xm}: z", decimals=d_z))
        checks.append(_scalar("z_ayna", f"z({Xm})", d_z))
    operations.append(Scalar("x_z0", E.add(_c(mean), E.mul(_c(z0), _c(sd))), f"z = {Z0}: x = μ + zσ", decimals=d_x0))
    checks.append(_scalar("x_z0", f"x(z = {Z0})", d_x0))
    half = _reach(z) * sd
    references = ((float(x), f"x = {X}: z {_sign_value(z, d_z)}"),)
    if z != 0:
        references += ((float(mirror), f"x = {Xm}: z {_sign_value(-z, d_z)}"),)
    title = f"Aynı uzaklık, zıt yön: z {sign} ±{Zabs}" if z != 0 else f"x = μ = {X}: z = 0"
    operations.append(DensityPlot("normal", float(mean), float(sd), (float(mean - half), float(mean + half)), title,
                                  _axis(ctx, "normal"), references=references))
    story = ctx["texts"].get("normal")
    lead = f"{story} " if story else ""
    if z == 0:
        first = f"x = {X} ortalamanın kendisidir: z = 0; ortalamaya göre aynadaki değer de aynı noktadır."
    else:
        other = "altındadır" if z > 0 else "üzerindedir"
        first = (f"x = {X} {_position(z, d_z)}; x = {Xm} aynı uzaklıkta, ortalamanın {other}: iki değer merkeze eşit "
                 "uzaklıktadır.")
    if z0 == 0:
        second = f"z = 0 olan değer ortalamanın kendisidir: x = μ = {_txt(mean)}."
    else:
        second = f"z = {Z0} olan değer x = μ + zσ = {_txt(mean)} + ({Z0})({_txt(sd)}) = {X0}."
    return LabStep(
        number=4,
        title="z-dönüşümü ve ters dönüşüm",
        note=NoteRef("10.10", objects=("(10.8)", "(10.9)")),
        explanation=(
            "$X \\sim N(\\mu, \\sigma^2)$ ise bir $x$ değeri $z = (x - \\mu)/\\sigma$ ile standart ölçeğe taşınır: "
            "$z$, değerin ortalamadan kaç standart sapma uzakta olduğunu söyler (Denklem 10.8). Ters yönde "
            f"$x = \\mu + z\\sigma$ olur (Denklem 10.9). {lead}$X \\sim {_normal_tex(mean, sd)}$; $x = {_tx(x)}$, "
            f"ortalamaya göre aynadaki değer $2\\mu - x = {_tx(mirror)}$ ve $z_0 = {_tx(z0)}$ incelenir."
        ),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=f"{first} {second} z birimsizdir ve bir yüzde değildir (§10.10).",
    )


def _step5(ctx: dict) -> LabStep:
    rows = []
    zs = []
    for name in ("A", "B"):
        x, mean, sd = ctx[f"x{name}"], ctx[f"mu{name}"], ctx[f"sd{name}"]
        rows.append((name, float(x), float(mean), float(sd)))
        zs.append((x - mean) / sd)
    z_a, z_b = zs
    digits = kesir_ayirt(z_a, z_b, start=max(_digits(z_a), _digits(z_b)))
    if z_a > 0 and z_b > 0:  # notlardaki başlık
        bar_title = "Göreli konum: kendi ölçeğinde kaç standart sapma yukarıda"
    else:  # eksi çubuk "aşağıda" başlığıyla çift olumsuz okunurdu
        bar_title = "Göreli konum: kendi ölçeğinde ortalamadan kaç standart sapma uzakta (z)"
    operations = (
        InlineData("olcekler", ("olcek", "deger", "ortalama", "std"), tuple(rows),
                   "İki ölçek: değer, ortalama ve standart sapma"),
        Derive("olcekler", "z", E.div(E.sub(E.var("deger"), E.var("ortalama")), E.var("std")), "z = (x − μ)/σ"),
        ShowFrame("olcekler", ("olcek", "deger", "ortalama", "std", "z"), "Ham değer ve göreli konum",
                  decimals=(("z", digits),)),
        BarChart("olcekler", "z", "Ölçek", "z-skoru", bar_title, x="olcek", decimals=digits),
    )
    texts = {name: (_txt(ctx[f"x{name}"]), _txt(ctx[f"mu{name}"]), _txt(ctx[f"sd{name}"])) for name in ("A", "B")}
    story = ctx["texts"].get("olcek") or (
        f"A ölçeğindeki değer {texts['A'][0]} (ortalama {texts['A'][1]}; standart sapma {texts['A'][2]}), B "
        f"ölçeğindeki değer {texts['B'][0]} (ortalama {texts['B'][1]}; standart sapma {texts['B'][2]}) olsun.")
    x_a, x_b = ctx["xA"], ctx["xB"]
    if x_a == x_b:
        raw = f"Ham değerler eşittir ({texts['A'][0]})"
    else:
        high, low = ("A", "B") if x_a > x_b else ("B", "A")
        raw = f"Ham değer {high} ölçeğinde daha yüksektir ({texts[high][0]} > {texts[low][0]})"

    def place(z: Fraction) -> str:
        return "tam ortalamada" if z == 0 else ("ortalamanın üzerinde" if z > 0 else "ortalamanın altında")

    shown = {name: " ".join(deger_metni(float(z), z, digits)) for name, z in (("A", z_a), ("B", z_b))}
    if z_a == z_b:
        relative = ("ham değerler farklı olsa da iki ölçekte göreli konum aynıdır" if x_a != x_b else
                    "iki ölçekte göreli konum aynıdır")
        order = ""
    else:
        best = "A" if z_a > z_b else "B"
        relative = f"kendi dağılımına göre {best} ölçeğindeki konum daha yüksektir"
        if x_a == x_b or (x_a > x_b) == (z_a > z_b):
            order = ""
        else:
            order = "Ham değerin sıralaması ile göreli konumun sıralaması farklıdır. "
    return LabStep(
        number=5,
        title="Farklı ölçeklerde göreli konum",
        note=NoteRef("10.11", objects=("Şekil 10.12",)),
        explanation=(
            f"{story} Ham değerler farklı ölçeklerdedir; her değer kendi dağılımında $z = (x - \\mu)/\\sigma$ ile "
            "standartlaştırılır."
        ),
        operations=operations,
        checks=(
            Check(f"z_A = ({texts['A'][0]} − {_par(texts['A'][1])})/{texts['A'][2]}", CellTarget("olcekler", "z", 1),
                  0.0, digits),
            Check(f"z_B = ({texts['B'][0]} − {_par(texts['B'][1])})/{texts['B'][2]}", CellTarget("olcekler", "z", 2),
                  0.0, digits),
        ),
        takeaway=(
            f"{raw}. A ölçeğinde z {shown['A']} ({place(z_a)}), B ölçeğinde z {shown['B']} ({place(z_b)}): "
            f"{relative}. {order}Farklı ölçekler ham farkla değil z-skoruyla karşılaştırılır (§10.11)."
        ),
    )


def _normal_area(z1: float, z2: float) -> float:
    """P(z₁ ≤ Z ≤ z₂), yalnız gösterim basamağını seçmek için; kuyruktaki aralıkta kesinlik kaybı olmadan (erfc)."""

    root = math.sqrt(2)
    if z1 >= 0:
        return 0.5 * (math.erfc(z1 / root) - math.erfc(z2 / root))
    if z2 <= 0:
        return 0.5 * (math.erfc(-z2 / root) - math.erfc(-z1 / root))
    return 1 - 0.5 * (math.erfc(-z1 / root) + math.erfc(z2 / root))


def _count(span: Fraction) -> int:
    """[x₁, x₂] aralığının dikdörtgen sayısı: standart ölçekte genişlik en çok 0,001."""

    return next(count for count in COUNTS if count >= 1000 * span)


def _count_text(count: int) -> str:
    """Dikdörtgen sayısı notlardaki gibi yazılır: beş ve daha çok basamakta binler boşlukla ayrılır (12 000)."""

    return f"{count:,}".replace(",", " ") if count >= 10000 else str(count)


def _step6(ctx: dict) -> LabStep:
    mean, sd, x1, x2 = ctx["mu"], ctx["sigma"], ctx["x1"], ctx["x2"]
    z1, z2 = (x1 - mean) / sd, (x2 - mean) / sd
    count = _count(z2 - z1)
    width = (x2 - x1) / count
    d1, d2 = _digits(z1), _digits(z2)
    d_area = olasilik_basamak(_normal_area(float(z1), float(z2)))
    X1, X2 = _txt(x1), _txt(x2)
    operations = (
        Scalar("z_alt", _z(x1, mean, sd), "z₁ = (x₁ − μ)/σ", decimals=d1),
        Scalar("z_ust", _z(x2, mean, sd), "z₂ = (x₂ − μ)/σ", decimals=d2),
        Rectangles(FRAME6, "x", float(x1), float(x2), float(width),
                   f"{X1} ile {X2} arası {_count_text(count)} dikdörtgene: genişlik {_txt(width)}"),
        Derive(FRAME6, "f", E.dnorm(E.var("x"), _c(mean), _c(sd)), "Özgün ölçekte yükseklik f(x)"),
        Derive(FRAME6, "alan", E.mul(E.var("f"), float(width)), "Özgün ölçekte alan f(x) × genişlik"),
        Derive(FRAME6, "z", E.div(E.sub(E.var("x"), _c(mean)), _c(sd)), "Orta noktanın z değeri (x − μ)/σ"),
        Derive(FRAME6, "f_z", E.dnorm(E.var("z"), 0, 1), "Standart ölçekte yükseklik f(z)"),
        Derive(FRAME6, "alan_z", E.div(E.mul(E.var("f_z"), float(width)), _c(sd)),
               "Standart ölçekte alan f(z) × genişlik/σ"),
        Statistic(FRAME6, "alan", "sum", "alan_x", "Özgün ölçekte alan", decimals=d_area),
        Statistic(FRAME6, "alan_z", "sum", "alan_z_toplam", "Standart ölçekte alan", decimals=d_area),
        Scalar("alan_farki", E.absolute(E.sub(E.ref("alan_z_toplam"), E.ref("alan_x"))), "İki alanın farkı",
               decimals=6),
        DensityPlot("normal", float(mean), float(sd),
                    (float(mean - _reach(z1, z2) * sd), float(mean + _reach(z1, z2) * sd)),
                    f"Özgün ölçek: {X1} ile {X2} arasının alanı", _axis(ctx, "normal"),
                    shade=((float(x1), float(x2)),)),
        DensityPlot("normal", 0, 1, (-_reach(z1, z2), _reach(z1, z2)),
                    f"Standart ölçek: z₁ {_sign_value(z1, d1)} ile z₂ {_sign_value(z2, d2)} arasının alanı", "z",
                    y_label="f(z)", shade=((float(z1), float(z2)),)),
    )
    s = run_operations(operations).scalars
    same = (x1, x2) == (mean - sd, mean + sd)
    return LabStep(
        number=6,
        title="Standartlaştırma alanı değiştirmez",
        note=NoteRef("10.12", objects=("Şekil 10.13", "(10.10)")),
        explanation=(
            f"$X \\sim {_normal_tex(mean, sd)}$ için $x_1 = {_tx(x1)}$ ile $x_2 = {_tx(x2)}$ arasındaki aralığın "
            f"uçları $z_1 = (x_1 - \\mu)/\\sigma {deger_tex(float(z1), z1, d1)}$ ve $z_2 = (x_2 - \\mu)/\\sigma "
            f"{deger_tex(float(z2), z2, d2)}$ olur. Aralık {_count_text(count)} dikdörtgene bölünür ({_txt(width)} "
            "genişliğinde); her dikdörtgenin orta noktası $z = (x - \\mu)/\\sigma$ ile standart ölçeğe taşınır, "
            "genişlik $\\sigma$ ile bölünür. Alan iki ölçekte ayrı ayrı toplanır: "
            "$P(x_1 \\leq X \\leq x_2) = P(z_1 \\leq Z \\leq z_2)$ (Denklem 10.10)."
        ),
        operations=operations,
        checks=(
            _scalar("z_alt", "z₁", d1),
            _scalar("z_ust", "z₂", d2),
            _scalar("alan_x", f"P({X1} ≤ X ≤ {X2})", d_area),
            _scalar("alan_z_toplam", "P(z₁ ≤ Z ≤ z₂)", d_area),
        ),
        takeaway=(
            f"İki ölçekteki alan aynıdır: P({X1} ≤ X ≤ {X2}) {olasilik_metni(s['alan_x'], None, d_area)}; fark "
            "bilgisayarın yuvarlama "
            "hatası düzeyindedir. Standartlaştırma yalnız yatay eksenin birimini değiştirir, olasılığı değiştirmez. "
            + ("Aralık μ ± σ olduğu için alan Adım 3'teki μ ± σ alanıyla aynıdır. " if same else "")
            + "Bütün normal dağılımlar ortak N(0, 1) ölçeğine taşınabildiği için Konu 11'de tek bir Φ tablosu yeterli "
            "olacaktır (§10.12)."
        ),
        code_note=(
            "Özgün ölçekteki her dikdörtgenin orta noktası z = (x − μ)/σ ile taşınır; genişlik σ'ya bölünür, "
            "yükseklik (yoğunluk) σ ile çarpılır. Bu yüzden iki toplam aynı sayıyı verir."
        ),
    )


def _step7(ctx: dict) -> LabStep:
    mean, sd, v1, v2 = ctx["mu7"], ctx["sd7"], ctx["v1"], ctx["v2"]
    z1, z2 = (v1 - mean) / sd, (v2 - mean) / sd
    d1, d2 = _digits(z1), _digits(z2)
    low, high = mean - 2 * sd, mean + 2 * sd
    width = sd / GRID
    V1, V2, L, H = _txt(v1), _txt(v2), _txt(low), _txt(high)
    half = _reach(z1, z2) * sd
    operations = (
        Scalar("z_v1", _z(v1, mean, sd), f"{V1}: z = (x − μ)/σ", decimals=d1),
        Scalar("z_v2", _z(v2, mean, sd), f"{V2}: z = (x − μ)/σ", decimals=d2),
        Scalar("butun_alt", E.sub(_c(mean), E.mul(2, _c(sd))), "μ − 2σ", decimals=_digits(low)),
        Scalar("butun_ust", E.add(_c(mean), E.mul(2, _c(sd))), "μ + 2σ", decimals=_digits(high)),
        Rectangles("butun", "x", float(low), float(high), float(width),
                   f"{L} ile {H} arası σ/1000 = {_txt(width)} genişliğinde dikdörtgenlere"),
        Derive("butun", "f", E.dnorm(E.var("x"), _c(mean), _c(sd)), "Dikdörtgenin yüksekliği f(x)"),
        Derive("butun", "alan", E.mul(E.var("f"), float(width)), "Dikdörtgenin alanı f(x) × genişlik"),
        Statistic("butun", "alan", "sum", "alan_butun", "P(μ − 2σ ≤ X ≤ μ + 2σ)", decimals=4),
        DensityPlot("normal", float(mean), float(sd), (float(mean - half), float(mean + half)),
                    f"{_normal(mean, sd)}: μ ± 2σ ve z konumları", _axis(ctx, "butun"),
                    shade=((float(low), float(high)),),
                    references=((float(v1), f"{V1}: z {_sign_value(z1, d1)}"),
                                (float(v2), f"{V2}: z {_sign_value(z2, d2)}"))),
    )
    s = run_operations(operations).scalars
    story = ctx["texts"].get("butun") or "Bir süreçte ölçülen değişken yaklaşık normal dağılsın."
    return LabStep(
        number=7,
        title="Bütünleştirici uygulama: z konumları ve μ ± 2σ aralığı",
        note=NoteRef("10.14", objects=("Şekil 10.15",)),
        explanation=(
            f"{story} $X \\sim {_normal_tex(mean, sd)}$. {V1} ve {V2} değerlerinin $z$ değerleri ile ampirik "
            "kurala göre değerlerin yaklaşık %95,4 kadarının bulunduğu $\\mu \\pm 2\\sigma$ aralığı hesaplanır; "
            "aralığın alanı dikdörtgenlerle doğrulanır."
        ),
        operations=operations,
        checks=(
            _scalar("z_v1", f"z({V1})", d1),
            _scalar("z_v2", f"z({V2})", d2),
            _scalar("butun_alt", "μ − 2σ (bütünleştirici)", _digits(low)),
            _scalar("butun_ust", "μ + 2σ (bütünleştirici)", _digits(high)),
            _scalar("alan_butun", f"P({L} ≤ X ≤ {H})", 4),
        ),
        takeaway=(
            f"{V1} {_position(z1, d1)}; {V2} {_position(z2, d2)}. Değerlerin yaklaşık %95,4 kadarı {L} ile {H} "
            f"arasındadır: P({L} ≤ X ≤ {H}) {_shown(s['alan_butun'], 4)}. Tek bir değerin olasılığı sıfırdır: "
            f"P(X = {_txt(mean)}) = 0; simetri nedeniyle P(X < {_txt(mean)}) = 0,50 (§10.14)."
        ),
    )


def build(values: Mapping[str, float], texts: Mapping[str, str] | None = None, source: str = "kendi") -> LabSpec:
    """Konu 10 uygulamasını verilen parametrelerle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    validate(values)
    ctx = _context(values, texts)
    steps = (_step1(ctx), _step2(ctx), _step3(ctx), _step4(ctx), _step5(ctx), _step6(ctx), _step7(ctx))
    spec = LabSpec(
        topic_key="konu10",
        title=TITLE,
        note_section="10",
        steps=steps,
        labels=(
            ("x", "x"),
            ("z", "z"),
            ("f", "f(x)"),
            ("alan", "Alan"),
            ("f_z", "f(z)"),
            ("alan_z", "Alan (standart ölçek)"),
            ("olcek", "Ölçek"),
            ("deger", "Değer x"),
            ("ortalama", "Ortalama μ"),
            ("std", "Standart sapma σ"),
        ),
        source=source,
    )
    return with_app_values(spec)


def _inside(value: Fraction, mean: Fraction, sd: Fraction) -> bool:
    return abs(value - mean) <= REACH * sd


def validate(values: Mapping[str, float]) -> None:
    """Parametreler arasındaki koşullar: a < b, a ≤ c < d ≤ b; x₁ < x₂; değerler μ ± 10σ içinde; iki farklı değer."""

    q = {key: kesir_degeri(value) for key, value in values.items()}
    a, b, c, d = q["a"], q["b"], q["c"], q["d"]
    if a >= b:
        raise K.UploadError(f"Tek-düze: alt sınır a ({_txt(a)}) üst sınır b'den ({_txt(b)}) küçük olmalıdır.")
    if not a <= c < d <= b:
        raise K.UploadError(f"Tek-düze: incelenen aralık a ≤ c < d ≤ b koşulunu sağlamalıdır (a = {_txt(a)}, "
                            f"c = {_txt(c)}, d = {_txt(d)}, b = {_txt(b)}).")
    mean, sd = q["mu"], q["sigma"]
    low, high = _txt(mean - REACH * sd), _txt(mean + REACH * sd)
    if not _inside(q["x"], mean, sd):
        raise K.UploadError(f"Normal: x değeri μ ± 10σ aralığında ({low} ile {high} arası) olmalıdır; daha uzak "
                            "değerlerin kuyruk olasılığı 10⁻²³'ten küçüktür.")
    if q["x1"] >= q["x2"]:
        raise K.UploadError(f"Normal: aralığın alt ucu x₁ ({_txt(q['x1'])}) üst ucu x₂'den ({_txt(q['x2'])}) küçük "
                            "olmalıdır.")
    if not (_inside(q["x1"], mean, sd) and _inside(q["x2"], mean, sd)):
        raise K.UploadError(f"Normal: x₁ ve x₂ μ ± 10σ aralığında ({low} ile {high} arası) olmalıdır; daha uzak "
                            "değerlerin kuyruk olasılığı 10⁻²³'ten küçüktür.")
    mean7, sd7 = q["mu7"], q["sd7"]
    if q["v1"] == q["v2"]:
        raise K.UploadError("Bütünleştirici uygulama: iki farklı değer girin.")
    if not (_inside(q["v1"], mean7, sd7) and _inside(q["v2"], mean7, sd7)):
        raise K.UploadError(f"Bütünleştirici uygulama: iki değer μ ± 10σ aralığında "
                            f"({_txt(mean7 - REACH * sd7)} ile {_txt(mean7 + REACH * sd7)} arası) olmalıdır.")


# --- Alternatif örnek ve kendi değerlerin ----------------------------------------------------

@cache
def alternative() -> LabSpec:
    return build(ALT_VALUES, ALT_TEXTS, source="alternatif")


G_UNIFORM, G_NORMAL, G_SCALES, G_LAST = ("Tek-düze · Adım 1–2", "Normal · Adım 3, 4, 6", "İki ölçek · Adım 5",
                                         "Bütünleştirici · Adım 7")


def _location(key: str, label: str, group: str, steps: tuple[int, ...], help: str) -> Parameter:
    return Parameter(key, label, -LIMIT, LIMIT, ALT_VALUES[key], step=1, decimals=2, group=group, steps=steps,
                     help=help)


def _scale(key: str, label: str, group: str, steps: tuple[int, ...], help: str) -> Parameter:
    return Parameter(key, label, 0.01, SCALE_LIMIT, ALT_VALUES[key], step=0.5, decimals=2, group=group, steps=steps,
                     help=help)


PARAMETERS = (
    _location("a", "Alt sınır a", G_UNIFORM, (1,), "U(a, b) dağılımının alt sınırı."),
    _location("b", "Üst sınır b", G_UNIFORM, (1,), "U(a, b) dağılımının üst sınırı; a'dan büyük olmalıdır."),
    _location("c", "Aralığın alt ucu c", G_UNIFORM, (1,), "İncelenen aralık: a ≤ c < d ≤ b."),
    _location("d", "Aralığın üst ucu d", G_UNIFORM, (1,), "İncelenen aralığın üst ucu."),
    Parameter("w", "Dar dağılımın genişliği w", 0.01, 100, ALT_VALUES["w"], step=0.05, decimals=2, group=G_UNIFORM,
              steps=(2,), help="U(0, w) dağılımı; w < 1 iken yoğunluk yüksekliği 1'i aşar."),
    _location("mu", "Ortalama μ", G_NORMAL, (3, 4, 6), "N(μ, σ²) dağılımının ortalaması."),
    _scale("sigma", "Standart sapma σ", G_NORMAL, (3, 4, 6), "N(μ, σ²) dağılımının standart sapması."),
    _location("x", "Değer x", G_NORMAL, (4,), "z = (x − μ)/σ ve aynadaki değer 2μ − x; μ ± 10σ içinde."),
    Parameter("z0", "Ters dönüşüm için z₀", -10, 10, ALT_VALUES["z0"], step=0.25, decimals=2, group=G_NORMAL,
              steps=(4,), help="Özgün ölçeğe dönüş: x = μ + z₀σ."),
    _location("x1", "Aralığın alt ucu x₁", G_NORMAL, (6,), "Alanı iki ölçekte hesaplanan aralık; μ ± 10σ içinde."),
    _location("x2", "Aralığın üst ucu x₂", G_NORMAL, (6,), "x₁'den büyük olmalıdır."),
    _location("xA", "A: değer", G_SCALES, (5,), "A ölçeğindeki değer."),
    _location("muA", "A: ortalama", G_SCALES, (5,), "A ölçeğinin ortalaması."),
    _scale("sdA", "A: standart sapma", G_SCALES, (5,), "A ölçeğinin standart sapması."),
    _location("xB", "B: değer", G_SCALES, (5,), "B ölçeğindeki değer."),
    _location("muB", "B: ortalama", G_SCALES, (5,), "B ölçeğinin ortalaması."),
    _scale("sdB", "B: standart sapma", G_SCALES, (5,), "B ölçeğinin standart sapması."),
    _location("mu7", "Ortalama μ", G_LAST, (7,), "Bütünleştirici uygulamanın normal dağılımı."),
    _scale("sd7", "Standart sapma σ", G_LAST, (7,), "Bütünleştirici uygulamanın standart sapması."),
    _location("v1", "Birinci değer", G_LAST, (7,), "z değeri hesaplanan değer; μ ± 10σ içinde."),
    _location("v2", "İkinci değer", G_LAST, (7,), "z değeri hesaplanan ikinci değer."),
)

PARAMS = ParamLab(
    parameters=PARAMETERS,
    build=lambda values: build(values),
    intro=(
        "Bu konuda dosya yüklenmez: notlardaki her örnek için değerleri aşağıya girin. Tek-düze değerler Adım 1–2'yi, "
        "normal dağılımın değerleri Adım 3, 4 ve 6'yı, iki ölçeğin değerleri Adım 5'i, son grup bütünleştirici "
        "uygulamayı (Adım 7) kurar. Başlangıç değerleri alternatif örneğinkilerdir."
    ),
    groups=(G_UNIFORM, G_NORMAL, G_SCALES, G_LAST),
    validate=validate,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, params=PARAMS)


def default_values() -> dict[str, int | float]:
    return parameter_values(PARAMS)
