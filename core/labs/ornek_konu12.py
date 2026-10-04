"""Konu 12 genel uygulaması: örneklem ortalamasının ve oranının örnekleme dağılımı, standart hata, örneklem
ortalamasıyla olasılık ve sonlu anakütle düzeltmesi.

Ders notlarındaki adımlar (§12.6, §12.7, §12.9, §12.10, §12.11 ve §12.15) aynı numaralarla, parametreleri
değiştirilebilir biçimde yazılır. Bu konuda dosya yoktur: "Kendi değerlerini gir" seçeneğinde öğrenci notlardaki her
örnek için ayrı değerler girer: anakütlenin μ ve σ değerleri ile iki örneklem büyüklüğü (Adım 1), σ ve başlangıç
örneklem büyüklüğü (Adım 2; n, 4n, 16n, 64n), μ, σ, n ve örneklem ortalaması için bir aralık (Adım 3), anakütle oranı ve
iki örneklem büyüklüğü (Adım 4), anakütle büyüklüğü N, örneklem büyüklüğü n ve σ (Adım 5), bütünleştirici uygulamanın
μ, σ, p ve n değerleri (Adım 6). Alternatif örnek kurgusaldır. Notlardaki uygulama (``core.labs.konu12``) değişmez.

Standart hata σ/√n yalnız n tam kare iken kesin bir ondalık sayıdır; metindeki "=" / "≈" ayrımı kesin karekökten
kurulur. Adım 3'te Φ değerleri Konu 11'deki tablo kuralıyla (z iki, Φ dört ondalık; ``E.yuvarla``) bulunur ve
yuvarlamasız sonuç birlikte gösterilir. z = (x̄ − μ)√n/σ n tam kare değilse irrasyoneldir; kayan noktalı yuvarlamanın
ders kuralının kesin sonucunu verdiği ayrıca denetlenir (``ders_yuvarla_kok``), ayrılırsa değer değiştirilmesi istenir.
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
    ders_yuvarla,
    ders_yuvarla_kok,
    deger_metni,
    deger_tex,
    kesir_degeri,
    kesir_kok,
    kisa_kesir as _txt,
    olasilik_basamak,
    olasilik_metni,
    onemli_basamak,
    parameter_values,
    sabit as _c,
    with_app_values,
)
from core.labs.runner import run_operations
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    DensityCompare,
    DensityPlot,
    Derive,
    InlineData,
    LabSpec,
    LabStep,
    LineChart,
    NoteRef,
    Scalar,
    ScalarTable,
    ScalarTarget,
    ShowFrame,
    Support,
)

TITLE = "Örnekleme dağılımlarını, standart hatayı ve sonlu anakütle düzeltmesini uygulamak"
LIMIT = 100000
SCALE_LIMIT = 10000
"""Standart sapmaların üst sınırı (konum değerleri ±10⁵). σ/√n çok küçük olabildiği için tablo kuralı ayrıca kesin
hesapla denetlenir (``_check_table_rule``)."""
N_LIMIT = 10000
REACH = 10
"""Adım 3: örneklem ortalamasının sınırları μ ± 10σ_X̄ içinde (daha uzak değerlerin olasılığı 10⁻²³'ten küçüktür)."""
FPC_SHARE = Fraction(5, 100)
"""Sonlu anakütle düzeltmesinin gerekli sayıldığı örnekleme oranı: n/N > 0,05."""

ALT_VALUES = {"mu1": 120, "sd1": 36, "n1a": 16, "n1b": 64, "sd2": 30, "n2": 9, "mu3": 75, "sd3": 20, "n3": 64,
              "xb1": 72, "xb2": 79, "p4": 0.25, "n4a": 48, "n4b": 192, "N5": 1000, "n5": 200, "sd5": 50,
              "mu6": 450, "sd6": 90, "p6": 0.72, "n6": 81}
ALT_TEXTS = {
    "adim1": "Bir kafede sipariş tutarının (TL) anakütle ortalaması 120, standart sapması 36 olsun.",
    "adim1_eksen": "Sipariş tutarı (TL)",
    "adim2": "Bir anket sorusunda puanların standart sapması 30 olsun.",
    "adim3": "Bir kargo şirketinde teslimat süresinin (dakika) anakütle ortalaması 75, standart sapması 20 olsun.",
    "adim3_eksen": "Ortalama teslimat süresi x̄ (dakika)",
    "adim4": "Bir dijital platformda premium üyelerin oranı p = 0,25 olsun.",
    "adim5": ("Bin çalışanlı bir şirketten 200 çalışan yerine koymadan seçilir; çalışanların günlük öğle yemeği "
              "harcamasının (TL) standart sapması 50 olsun."),
    "adim6": ("Bir e-ticaret sitesinde sepet tutarının anakütle ortalaması μ = 450 TL, standart sapması σ = 90 TL, "
              "tekrar alışveriş yapan müşteri oranı p = 0,72; site her ay n = 81 müşterilik basit rassal örneklem "
              "seçer."),
    "adim6_eksen": "Örneklem ortalaması x̄ (TL)",
}
STORY = (
    "Kurgusal veri: kafede sipariş tutarı (μ = 120, σ = 36 TL), anket puanları (σ = 30), teslimat süresi (μ = 75, "
    "σ = 20 dakika, n = 64), premium üye oranı (p = 0,25), 1000 çalışandan 200 kişilik örneklem ve e-ticaret sitesinde "
    "sepet tutarı ile tekrar alışveriş oranı."
)


# --- Yardımcılar -------------------------------------------------------------------------------

def _digits(value: Fraction, minimum: int = 0) -> int:
    """Kesin bir büyüklüğün gösterim basamağı (``onemli_basamak``): en çok dört; çok küçük değerlerde üç anlamlı
    basamak (n/N = 0,000001 "≈ 0" görünmez)."""

    return onemli_basamak(float(value), value, minimum)


def _scalar(name: str, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _root_digits(exact: Fraction | None, value: float) -> int:
    """Karekök içeren bir büyüklüğün basamağı: kesin ise kesir basamağı, değilse dört; çok küçük değerlerde üç
    anlamlı basamak (``onemli_basamak``)."""

    return onemli_basamak(value, exact)


def _ratio_text(value: Fraction) -> str:
    """İki büyüklüğün oranı: dört basamakla tam yazılabiliyorsa ondalık (2,5), değilse kesir (16/9)."""

    if (value * 10 ** 4).denominator == 1:
        return _txt(value)
    return f"{value.numerator}/{value.denominator}"


def _shown(value: float, exact: Fraction | None, digits: int) -> str:
    """Düzyazıda bir büyüklük: tam ise olduğu gibi, değilse başında "yaklaşık"."""

    sign, text = deger_metni(value, exact, digits)
    return text if sign == "=" else f"yaklaşık {text}"


def _fixed(value: float, digits: int) -> str:
    text = f"{float(value):.{digits}f}"
    if float(text) == 0:
        text = text.lstrip("-")
    return text.replace(".", ",").replace("-", "−")


def _nice_range(center: Fraction, half: float) -> tuple[float, float]:
    """Grafik ekseni: merkez ± yarı genişlik, dışa doğru kısa sayılara yuvarlanır (yarı genişliğin onda biri adımla)."""

    step = Fraction(10) ** (math.floor(math.log10(half)) - 1)
    low = math.floor((center - Fraction(half)) / step) * step
    high = math.ceil((center + Fraction(half)) / step) * step
    return float(low), float(high)


def _se(sd: Fraction, n: int) -> Fraction | None:
    """σ/√n kesin değeri (n tam kare ise), değilse ``None``."""

    root = kesir_kok(Fraction(n))
    return sd / root if root is not None else None


def _se_p(p: Fraction, n: int) -> Fraction | None:
    return kesir_kok(p * (1 - p) / n)


def _condition(p: Fraction, n: int) -> tuple[bool, str]:
    successes, failures = n * p, n * (1 - p)
    return (successes >= 5 and failures >= 5,
            f"np = {_txt(successes)} ve n(1 − p) = {_txt(failures)}")


def _context(values: Mapping[str, float], texts: Mapping[str, str] | None) -> dict:
    ctx = {key: kesir_degeri(value) for key, value in values.items()}
    for key in ("n1a", "n1b", "n2", "n3", "n4a", "n4b", "N5", "n5", "n6"):
        ctx[key] = int(values[key])
    ctx["texts"] = dict(texts or {})
    return ctx


def _story(ctx: dict, key: str, default: str) -> str:
    return ctx["texts"].get(key) or default


def _axis(ctx: dict, key: str, default: str) -> str:
    return ctx["texts"].get(f"{key}_eksen") or default


# --- Adımlar -------------------------------------------------------------------------------

def _step1(ctx: dict) -> LabStep:
    mean, sd, n_a, n_b = ctx["mu1"], ctx["sd1"], ctx["n1a"], ctx["n1b"]
    exact = {n: _se(sd, n) for n in (n_a, n_b)}
    digits = {n: _root_digits(exact[n], float(sd) / math.sqrt(n)) for n in (n_a, n_b)}
    operations = (
        Scalar("se_1a", E.div(_c(sd), E.sqrt(n_a)), f"σ_X̄, n = {n_a}", decimals=digits[n_a]),
        Scalar("se_1b", E.div(_c(sd), E.sqrt(n_b)), f"σ_X̄, n = {n_b}", decimals=digits[n_b]),
    )
    s = run_operations(operations).scalars
    shown = {n: deger_metni(s[name], exact[n], digits[n]) for n, name in ((n_a, "se_1a"), (n_b, "se_1b"))}
    labels = {n: f"X̄, n = {n}: SH {sign} {text}" for n, (sign, text) in shown.items()}
    S = _txt(sd)
    operations += (
        DensityCompare(
            (
                ("normal", float(mean), float(sd), f"Bireysel X: σ = {S}"),
                ("normal", float(mean), "se_1a", labels[n_a]),
                ("normal", float(mean), "se_1b", labels[n_b]),
            ),
            (float(mean - 2 * sd), float(mean + 2 * sd)), "Örneklem ortalamasının aynı merkezde daha dar dağılımı",
            _axis(ctx, "adim1", "Değer"), y_label="Yoğunluk",
        ),
    )
    story = _story(ctx, "adim1", f"Anakütle ortalaması μ = {_txt(mean)}; standart sapması σ = {S} olsun.")
    return LabStep(
        number=1,
        title="Örneklem ortalaması: aynı merkez, daha dar dağılım",
        note=NoteRef("12.6", objects=("Şekil 12.6", "(12.2)", "(12.3)")),
        explanation=(
            f"{story} Basit rassal örneklemlerde $E(\\bar X) = \\mu$ (Denklem 12.2) ve $\\sigma_{{\\bar X}} = "
            "\\sigma/\\sqrt n$ olur (Denklem 12.3); $\\sigma_{\\bar X}$ ortalamanın standart hatasıdır. Şekil "
            f"12.6'daki gibi $X$ ile $n = {n_a}$ ve $n = {n_b}$ için $\\bar X$'in normal dağılımları aynı eksende "
            "çizilir."
        ),
        operations=operations,
        checks=(
            _scalar("se_1a", f"Standart hata, n = {n_a}", digits[n_a]),
            _scalar("se_1b", f"Standart hata, n = {n_b}", digits[n_b]),
        ),
        takeaway=(
            f"Bütün eğrilerin merkezi μ = {_txt(mean)}; değişen unsur yayılımdır. n = {n_a} iken standart hata "
            f"{_shown(s['se_1a'], exact[n_a], digits[n_a])}; n = {n_b} iken "
            f"{_shown(s['se_1b'], exact[n_b], digits[n_b])}: n büyüdükçe olası örneklem ortalamaları μ çevresinde "
            "daha sık toplanır. Standart hata bireysel gözlemlerin standart sapması değil, örneklem ortalamalarının "
            "standart sapmasıdır (§12.6)."
        ),
    )


def _step2(ctx: dict) -> LabStep:
    sd, start = ctx["sd2"], ctx["n2"]
    sizes = [start * 4 ** k for k in range(4)]
    exact = [_se(sd, n) for n in sizes]
    roots = [kesir_kok(Fraction(n)) for n in sizes]
    d_root = max(_root_digits(root, math.sqrt(n)) for root, n in zip(roots, sizes))
    d_se = max(_root_digits(value, float(sd) / math.sqrt(n)) for value, n in zip(exact, sizes))
    S = _txt(sd)
    operations = (
        InlineData("se_tablo", ("n",), tuple((n,) for n in sizes),
                   "Örneklem büyüklükleri: her satırda dört katı"),
        Derive("se_tablo", "kok_n", E.sqrt(E.var("n")), "√n"),
        Derive("se_tablo", "se", E.div(_c(sd), E.var("kok_n")), f"σ_X̄ = {S}/√n"),
        ShowFrame("se_tablo", ("n", "kok_n", "se"), f"σ = {S} için örneklem büyüklüğü ve standart hata",
                  decimals=(("kok_n", d_root), ("se", d_se))),
        Support("se_egri", "n", 1, sizes[-1], f"n = 1, 2, …, {sizes[-1]}"),
        Derive("se_egri", "se", E.div(_c(sd), E.sqrt(E.var("n"))), f"σ_X̄ = {S}/√n"),
        LineChart("se_egri", "n", "se", "Örneklem büyüklüğü n", "Standart hata σ/√n",
                  f"σ = {S} iken örneklem büyüklüğü arttıkça standart hatanın azalması", markers=False),
    )
    frame = run_operations(operations[:3]).frames["se_tablo"]
    first, last = (_shown(float(frame["se"].iloc[index]), exact[index], d_se) for index in (0, 3))
    story = _story(ctx, "adim2", f"Anakütle standart sapması σ = {S} olsun.")
    return LabStep(
        number=2,
        title="Örneklem büyüklüğü ve kesinlik",
        note=NoteRef("12.7", objects=("Tablo 12.2", "Şekil 12.7")),
        explanation=(
            f"{story} Standart hata $\\sigma/\\sqrt n$ olur. $n$ paydada karekök içinde olduğu için örneklem "
            "büyüklüğünü iki katına çıkarmak standart hatayı yarıya indirmez; yarıya indirmek için $n$ yaklaşık dört "
            f"katına çıkarılmalıdır. Tablo $n = {sizes[0]}$ ile başlar ve her satırda $n$ dört katına çıkar."
        ),
        operations=operations,
        checks=tuple(Check(f"Standart hata, n = {n}", CellTarget("se_tablo", "se", index), 0.0, d_se)
                     for index, n in enumerate(sizes, start=1)),
        takeaway=(
            f"n = {sizes[0]} iken standart hata {first}; n = {sizes[-1]} iken {last}: her dört katlık artış standart "
            "hatayı yarıya indirir. Eğri başta hızlı, sonra yavaş düşer: azalan marjinal kazanç. Büyük n örnekleme "
            "belirsizliğini azaltır, ama sistematik ölçüm veya kapsama hatasını düzeltmez (§12.7)."
        ),
    )


def _check_table_rule(factor: Fraction, n: int, exact: Fraction | None, value: float) -> None:
    """z = (x̄ − μ)√n/σ = factor · √n için kayan noktalı tablo yuvarlaması ders kuralının kesin sonucunu vermeli
    (``ders_yuvarla_kok``; n tam kare değilse z irrasyoneldir ve yarıma çok yakın olabilir). Vermiyorsa sessiz
    kalınmaz, değerin değiştirilmesi istenir."""

    if float(ders_yuvarla_kok(factor, Fraction(n), 2)) == value:
        return
    if exact is not None:
        where_z = f"z = {_txt(exact)} tam iki tablo değerinin ortasında ve sayıların büyüklüğü yüzünden"
    else:
        approx = f"{float(factor) * math.sqrt(n):.10f}".replace(".", ",").replace("-", "−")
        where_z = f"z ≈ {approx} iki tablo değerinin ortasına çok yakın ve"
    raise K.UploadError(
        f"Örneklem ortalamasıyla olasılık: {where_z} bilgisayar hesabı tablo kuralını (yarım sıfırdan uzağa) "
        "güvenle uygulayamıyor. Değerlerden birini biraz değiştirin.")


def _table(z) -> E.Expr:
    return E.yuvarla(E.normcdf(z), 4)


def _between(z_low: E.Expr, z_high: E.Expr, upper: bool) -> E.Expr:
    """Yuvarlamasız Φ(z₂) − Φ(z₁); aralık ortalamanın üstündeyse (z₁ ≥ 0) Φ(−z₁) − Φ(−z₂): büyük z'de 1'e çok yakın
    iki sayının farkı kesinliğini yitirir."""

    if upper:
        return E.sub(E.normcdf(E.neg(z_low)), E.normcdf(E.neg(z_high)))
    return E.sub(E.normcdf(z_high), E.normcdf(z_low))


def _step3(ctx: dict) -> LabStep:
    mean, sd, n, low, high = ctx["mu3"], ctx["sd3"], ctx["n3"], ctx["xb1"], ctx["xb2"]
    se_exact = _se(sd, n)
    d_se = _root_digits(se_exact, float(sd) / math.sqrt(n))
    z_exact = {key: ((value - mean) / se_exact if se_exact is not None else (Fraction(0) if value == mean else None))
               for key, value in (("a", low), ("b", high))}
    L, H = _txt(low), _txt(high)
    probe = run_operations((Scalar("se_3", E.div(_c(sd), E.sqrt(n)), "", 4),
                            Scalar("z_3a", E.div(E.sub(_c(low), _c(mean)), E.ref("se_3")), "", 4),
                            Scalar("z_3b", E.div(E.sub(_c(high), _c(mean)), E.ref("se_3")), "", 4),
                            Scalar("P_3_yuv", _between(E.ref("z_3a"), E.ref("z_3b"), low >= mean), "", 4))).scalars
    d_z = {key: onemli_basamak(probe[f"z_3{key}"], z_exact[key]) for key in ("a", "b")}
    d_raw = olasilik_basamak(probe["P_3_yuv"])
    se_value = probe["se_3"]
    reach = max(Fraction(7, 2), *(Fraction(math.ceil(abs(probe[name]) + 0.5)) for name in ("z_3a", "z_3b")))
    axis = _nice_range(mean, float(reach) * se_value)
    operations = (
        Scalar("se_3", E.div(_c(sd), E.sqrt(n)), "σ_X̄ = σ/√n", decimals=d_se),
        Scalar("z_3a", E.div(E.sub(_c(low), _c(mean)), E.ref("se_3")), "z₁ = (x̄₁ − μ)/σ_X̄", decimals=d_z["a"]),
        Scalar("z_3b", E.div(E.sub(_c(high), _c(mean)), E.ref("se_3")), "z₂ = (x̄₂ − μ)/σ_X̄", decimals=d_z["b"]),
        Scalar("z_3a_tablo", E.yuvarla(E.ref("z_3a"), 2), "z₁, tablo için", decimals=2),
        Scalar("z_3b_tablo", E.yuvarla(E.ref("z_3b"), 2), "z₂, tablo için", decimals=2),
        Scalar("P_3", E.sub(_table(E.ref("z_3b_tablo")), _table(E.ref("z_3a_tablo"))), "P(x̄₁ ≤ X̄ ≤ x̄₂), tablo",
               decimals=4),
        Scalar("P_3_yuv", _between(E.ref("z_3a"), E.ref("z_3b"), low >= mean), "P(x̄₁ ≤ X̄ ≤ x̄₂), yuvarlamasız",
               decimals=d_raw),
        DensityPlot("normal", float(mean), se_value, axis,
                    f"n = {n}: örneklem ortalamasının {L} ile {H} arasında olması",
                    _axis(ctx, "adim3", "Örneklem ortalaması x̄"), y_label="Yoğunluk",
                    shade=((float(low), float(high)),)),
    )
    s = run_operations(operations[:7] + (Scalar("Phi_a", _table(E.ref("z_3a_tablo")), "", 4),
                                         Scalar("Phi_b", _table(E.ref("z_3b_tablo")), "", 4))).scalars
    for key, value, name in (("a", low, "z_3a_tablo"), ("b", high, "z_3b_tablo")):
        _check_table_rule((value - mean) / sd, n, z_exact[key], s[name])

    def z_phrase(key: str, label: str) -> str:
        name = f"z_3{key}"
        text = " ".join(deger_metni(s[name], z_exact[key], d_z[key]))
        if z_exact[key] is not None and ders_yuvarla(z_exact[key], 2) == z_exact[key]:
            return f"{label} {text}"
        return f"{label} {text} → tablo için {_fixed(s[name + '_tablo'], 2)}"

    raw = olasilik_metni(s["P_3_yuv"], None, d_raw)
    small = (f" Burada n = {n} < 30: hesap anakütlenin normal olduğunu varsayar; anakütle normal değilse sonuç "
             "güvenilir olmayabilir." if n < 30 else "")
    story = _story(ctx, "adim3", f"Anakütle ortalaması μ = {_txt(mean)}; standart sapması σ = {_txt(sd)} olsun.")
    se_text = _shown(se_value, se_exact, d_se)
    se_sign = " ".join(deger_metni(se_value, se_exact, d_se))
    if n == 1:
        single = ("n = 1 iken X̄ = X: tek gözlemin ortalaması gözlemin kendisidir; örneklem ortalamasının ve tek bir "
                  "gözlemin bu aralıkta olma olasılığı aynıdır, standart hata da anakütle standart sapmasına eşittir: "
                  f"σ_X̄ = σ = {_txt(sd)}")
    else:
        single = (f"Tek bir gözlemin aynı aralıkta olması başka bir olaydır: bireysel X için standart sapma "
                  f"{_txt(sd)}; X̄ için {se_text}")
    sample = ("Tek gözlemin" if n == 1 else
              f"Örneklem büyüklüğü n = {n} iken örneklem ortalamasının")
    return LabStep(
        number=3,
        title="Örneklem ortalamasıyla olasılık",
        note=NoteRef("12.9", objects=("Şekil 12.9", "(12.5)")),
        explanation=(
            f"{story} Örneklem büyüklüğü $n = {n}$. Örnekleme dağılımı normal ya da yaklaşık normal olduğunda "
            "(anakütle normalse her $n$ için; değilse Merkezi Limit Teoremiyle büyük $n$'de, pratikte $n \\geq 30$) "
            "$Z = (\\bar X - \\mu)/(\\sigma/\\sqrt n)$ olur (Denklem 12.5): paydada $\\sigma$ değil standart hata "
            f"vardır. Φ değerleri Konu 11'deki tablo kuralıyla okunur.{small}"
        ),
        operations=operations,
        checks=(
            _scalar("se_3", "σ_X̄ = σ/√n", d_se),
            _scalar("z_3a_tablo", f"z({L}), tablo için", 2),
            _scalar("z_3b_tablo", f"z({H}), tablo için", 2),
            _scalar("P_3", f"P({L} ≤ X̄ ≤ {H}), tablo kuralı", 4),
            _scalar("P_3_yuv", f"P({L} ≤ X̄ ≤ {H}), yuvarlamasız", d_raw),
        ),
        takeaway=(
            f"σ_X̄ = {_txt(sd)}/√{n} {se_sign}; {z_phrase('a', 'z₁')}; {z_phrase('b', 'z₂')}. {sample} {L} ile "
            f"{H} arasında olma olasılığı tablo kuralıyla {_fixed(s['Phi_b'], 4)} − {_fixed(s['Phi_a'], 4)} = "
            f"{_fixed(s['P_3'], 4)} (yuvarlamasız {raw}). {single} (§12.9)."
        ),
    )


def _step4(ctx: dict) -> LabStep:
    p, n_a, n_b = ctx["p4"], ctx["n4a"], ctx["n4b"]
    exact = {n: _se_p(p, n) for n in (n_a, n_b)}
    digits = {n: _root_digits(exact[n], math.sqrt(float(p * (1 - p)) / n)) for n in (n_a, n_b)}
    P = _txt(p)

    def se(n: int) -> E.Expr:
        return E.sqrt(E.div(E.mul(_c(p), _c(1 - p)), n))

    operations = (
        Scalar("se_pa", se(n_a), f"σ_p̂, n = {n_a}", decimals=digits[n_a]),
        Scalar("se_pb", se(n_b), f"σ_p̂, n = {n_b}", decimals=digits[n_b]),
    )
    s = run_operations(operations).scalars
    shown = {n: deger_metni(s[name], exact[n], digits[n]) for n, name in ((n_a, "se_pa"), (n_b, "se_pb"))}
    half = 4 * s["se_pa"]
    low, high = _nice_range(p, half)
    operations += (
        DensityCompare(
            (
                ("normal", float(p), "se_pa", f"n = {n_a}: SH {shown[n_a][0]} {shown[n_a][1]}"),
                ("normal", float(p), "se_pb", f"n = {n_b}: SH {shown[n_b][0]} {shown[n_b][1]}"),
            ),
            (max(low, 0.0), min(high, 1.0)), f"p = {P}: örneklem büyüdükçe p̂ dağılımının daralması",
            "Örneklem oranı p̂", y_label="Yoğunluk",
        ),
    )
    held = {n: _condition(p, n) for n in (n_a, n_b)}
    conditions = f"n = {n_a} için {held[n_a][1]}; n = {n_b} için {held[n_b][1]}"
    if held[n_a][0] and held[n_b][0]:
        verdict = "normal yaklaşım koşulları iki durumda da sağlanır"
    elif held[n_b][0]:
        verdict = f"normal yaklaşım koşulları yalnız n = {n_b} için sağlanır"
    elif held[n_a][0]:
        verdict = f"normal yaklaşım koşulları yalnız n = {n_a} için sağlanır"
    else:
        verdict = "normal yaklaşım koşulları iki durumda da sağlanmaz; p̂'nin dağılımı çarpık kalabilir"
    ratio = Fraction(n_b, n_a)
    if ratio == 4:
        change = "n dört katına çıkınca standart hata yarıya iner"
    else:
        factor = kesir_kok(ratio)
        shrink = (f"≈ {_fixed(math.sqrt(float(ratio)), 4)}" if factor is None else f"= {_ratio_text(factor)}")
        change = (f"n = {n_a} yerine n = {n_b} olunca standart hata √({n_b}/{n_a}) {shrink} kat küçülür (standart "
                  "hata 1/√n ile orantılıdır)")
    story = _story(ctx, "adim4", f"Anakütle oranı p = {P} olsun.")
    return LabStep(
        number=4,
        title="Örneklem oranının örnekleme dağılımı",
        note=NoteRef("12.10", objects=("Şekil 12.10", "(12.7)", "(12.8)")),
        explanation=(
            f"{story} Örneklem oranı $\\hat p = x/n$ için $E(\\hat p) = p$ (Denklem 12.7) ve "
            "$\\sigma_{\\hat p} = \\sqrt{p(1 - p)/n}$ olur (Denklem 12.8). $np \\geq 5$ ve $n(1 - p) \\geq 5$ "
            f"sağlandığında dağılım yaklaşık normaldir. $n = {n_a}$ ve $n = {n_b}$ karşılaştırılır."
        ),
        operations=operations,
        checks=(
            _scalar("se_pa", f"σ_p̂, n = {n_a}", digits[n_a]),
            _scalar("se_pb", f"σ_p̂, n = {n_b}", digits[n_b]),
        ),
        takeaway=(
            f"İki dağılımın merkezi p = {P}; standart hata n = {n_a} iken "
            f"{_shown(s['se_pa'], exact[n_a], digits[n_a])}; n = {n_b} iken "
            f"{_shown(s['se_pb'], exact[n_b], digits[n_b])}: {change}. {conditions}: {verdict} (§12.10)."
        ),
    )


def _step5(ctx: dict) -> LabStep:
    population, n, sd = ctx["N5"], ctx["n5"], ctx["sd5"]
    plain = _se(sd, n)
    factor = kesir_kok(Fraction(population - n, population - 1))
    corrected = kesir_kok(sd ** 2 * Fraction(population - n, (population - 1) * n))
    plain_value = float(sd) / math.sqrt(n)
    factor_value = math.sqrt((population - n) / (population - 1))
    d_plain = _root_digits(plain, plain_value)
    d_factor = _root_digits(factor, factor_value)
    d_corrected = _root_digits(corrected, factor_value * plain_value)
    S = _txt(sd)
    operations = (
        Scalar("se_sonsuz", E.div(_c(sd), E.sqrt(n)), "Düzeltmesiz σ/√n", decimals=d_plain),
        Scalar("fpc", E.sqrt(E.div(E.sub(population, n), E.sub(population, 1))), "√((N − n)/(N − 1))",
               decimals=d_factor),
        Scalar("se_sonlu", E.mul(E.ref("fpc"), E.ref("se_sonsuz")), "Düzeltilmiş standart hata", decimals=d_corrected),
        ScalarTable((("Düzeltmesiz", E.ref("se_sonsuz")), ("Sonlu anakütle", E.ref("se_sonlu"))), "fpc_tablo",
                    decimals=max(d_plain, d_corrected)),
        BarChart("fpc_tablo", "deger", "Standart hata hesabı", "Standart hata",
                 f"N = {population}, n = {n}, σ = {S}: sonlu anakütle düzeltmesinin etkisi",
                 decimals=max(d_plain, d_corrected)),
    )
    s = run_operations(operations[:3]).scalars
    share = Fraction(n, population)
    share_tex = deger_tex(float(share), share, _digits(share, 2))
    plain_text = _shown(s["se_sonsuz"], plain, d_plain)
    corrected_text = _shown(s["se_sonlu"], corrected, d_corrected)
    if n == population:
        verdict = ("Bütün anakütle gözlenir (n = N): düzeltme faktörü 0, standart hata da 0'dır; örnekleme hatası "
                   "yoktur.")
    elif n == 1:
        verdict = f"Tek birim seçildiğinde düzeltme faktörü 1'dir: iki standart hata aynıdır, {plain_text}."
    elif share > FPC_SHARE:
        verdict = (f"Anakütlenin önemli bir bölümünü gözlediğimiz için geride kalan belirsizlik azalır: standart hata "
                   f"{plain_text} yerine {corrected_text}. Düzeltme faktörü 1'den büyük olamaz.")
    else:
        verdict = (f"n/N ≤ 0,05: düzeltme genellikle ihmal edilir; iki standart hata neredeyse aynıdır ({plain_text} "
                   f"ve {corrected_text}). Düzeltme faktörü 1'den büyük olamaz; n/N çok küçükse 1'e yaklaşır.")
    story = _story(ctx, "adim5", f"N = {population} birimlik bir anakütleden n = {n} birim yerine koymadan seçilir; "
                                 f"σ = {S}.")
    return LabStep(
        number=5,
        title="Sonlu anakütle düzeltmesi",
        note=NoteRef("12.11", objects=("Şekil 12.11", "(12.4)")),
        explanation=(
            f"{story} Sonlu bir anakütleden yerine koymadan örnekleme yapılırken $n/N > 0{{,}}05$ ise standart hata "
            "$\\sqrt{(N - n)/(N - 1)}$ çarpanıyla düzeltilir (Denklem 12.4). Örnekleme oranı "
            f"$n/N = {n}/{population} {share_tex}$."
        ),
        operations=operations,
        checks=(
            _scalar("se_sonsuz", "Düzeltmesiz standart hata", d_plain),
            # tam 0 ya da 1 olan değerin denetimi de en az dört (düzeltilmiş hatada düzeltmesizin) basamakla: tolerans
            # 0,5 olup düzeltmeyi unutan bir hesabı geçirmez
            _scalar("fpc", "Düzeltme faktörü", max(d_factor, 4)),
            _scalar("se_sonlu", "Düzeltilmiş standart hata", max(d_corrected, d_plain)),
        ),
        takeaway=f"{verdict.removesuffix('.')} (§12.11).",
    )


def _step6(ctx: dict) -> LabStep:
    mean, sd, p, n = ctx["mu6"], ctx["sd6"], ctx["p6"], ctx["n6"]
    se_exact, se_p_exact = _se(sd, n), _se_p(p, n)
    successes, failures = n * p, n * (1 - p)
    d_se = _root_digits(se_exact, float(sd) / math.sqrt(n))
    d_p = _root_digits(se_p_exact, math.sqrt(float(p * (1 - p)) / n))
    operations = (
        Scalar("se_harcama", E.div(_c(sd), E.sqrt(n)), "σ_X̄ = σ/√n", decimals=d_se),
        Scalar("se_memnun", E.sqrt(E.div(E.mul(_c(p), _c(1 - p)), n)), "σ_p̂ = √(p(1 − p)/n)", decimals=d_p),
        Scalar("np_m", E.mul(n, _c(p)), "np", decimals=_digits(successes)),
        Scalar("nq_m", E.mul(n, _c(1 - p)), "n(1 − p)", decimals=_digits(failures)),
    )
    s = run_operations(operations).scalars
    axis = _nice_range(mean, 4 * s["se_harcama"])
    operations += (
        DensityPlot("normal", float(mean), s["se_harcama"], axis, f"n = {n}: örneklem ortalamasının örnekleme dağılımı",
                    _axis(ctx, "adim6", "Örneklem ortalaması x̄"), y_label="Yoğunluk",
                    references=((float(mean), f"μ = {_txt(mean)}"),)),
    )
    held, condition = _condition(p, n)
    verdict = ("ikisi de en az 5 olduğu için p̂ yaklaşık normaldir" if held else
               "en az biri 5'ten küçük olduğu için normal yaklaşım koşulu sağlanmaz; p̂'nin dağılımı çarpık kalabilir")
    story = _story(ctx, "adim6", (f"Anakütle ortalaması μ = {_txt(mean)}; standart sapması σ = {_txt(sd)} ve oran "
                                  f"p = {_txt(p)} olsun; her dönem n = {n} birimlik basit rassal örneklem seçilir."))
    return LabStep(
        number=6,
        title="Bütünleştirici uygulama: ortalama ve oran",
        note=NoteRef("12.15", objects=("Şekil 12.16",)),
        explanation=(
            f"{story} Örneklem ortalaması ve örneklem oranının örnekleme dağılımlarının merkezi ve standart hatası "
            f"hesaplanır: $E(\\bar X) = \\mu$, $\\sigma_{{\\bar X}} = \\sigma/\\sqrt n$, $E(\\hat p) = p$, "
            "$\\sigma_{\\hat p} = \\sqrt{p(1 - p)/n}$."
        ),
        operations=operations,
        checks=(
            _scalar("se_harcama", "σ_X̄ (bütünleştirici)", d_se),
            _scalar("se_memnun", "σ_p̂ (bütünleştirici)", d_p),
            _scalar("np_m", "np (bütünleştirici)", _digits(successes)),
            _scalar("nq_m", "n(1 − p) (bütünleştirici)", _digits(failures)),
        ),
        takeaway=(
            f"Örneklem ortalaması μ = {_txt(mean)} çevresinde dağılır, standart hatası "
            f"{_shown(s['se_harcama'], se_exact, d_se)}; örneklem oranı p = {_txt(p)} çevresinde dağılır, standart "
            f"hatası {_shown(s['se_memnun'], se_p_exact, d_p)}. {condition}: {verdict}. Standart hata ikinci dönemde "
            "güven aralığı ve hipotez testinin temel ölçüsüdür (§12.15)."
        ),
    )


def build(values: Mapping[str, float], texts: Mapping[str, str] | None = None, source: str = "kendi") -> LabSpec:
    """Konu 12 uygulamasını verilen parametrelerle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    validate(values)
    ctx = _context(values, texts)
    steps = (_step1(ctx), _step2(ctx), _step3(ctx), _step4(ctx), _step5(ctx), _step6(ctx))
    spec = LabSpec(
        topic_key="konu12",
        title=TITLE,
        note_section="12",
        steps=steps,
        labels=(
            ("n", "n"),
            ("kok_n", "√n"),
            ("se", "Standart hata σ/√n"),
            ("deger", "Standart hata"),
        ),
        source=source,
    )
    return with_app_values(spec)


def validate(values: Mapping[str, float]) -> None:
    """Parametreler arasındaki koşullar: n₁ < n₂ (Adım 1 ve 4); x̄₁ < x̄₂ ve μ ± 10σ_X̄ içinde; n ≤ N."""

    q = {key: kesir_degeri(value) for key, value in values.items()}
    n = {key: int(values[key]) for key in ("n1a", "n1b", "n3", "n4a", "n4b", "N5", "n5")}
    if n["n1a"] >= n["n1b"]:
        raise K.UploadError(f"Adım 1: birinci örneklem büyüklüğü ({n['n1a']}) ikinciden ({n['n1b']}) küçük "
                            "olmalıdır.")
    if q["xb1"] >= q["xb2"]:
        raise K.UploadError(f"Adım 3: aralığın alt ucu x̄₁ ({_txt(q['xb1'])}) üst ucu x̄₂'den ({_txt(q['xb2'])}) "
                            "küçük olmalıdır.")
    mean, sd, size = q["mu3"], q["sd3"], n["n3"]
    if any((q[key] - mean) ** 2 * size > (REACH * sd) ** 2 for key in ("xb1", "xb2")):
        raise K.UploadError("Adım 3: x̄₁ ve x̄₂, μ ± 10σ/√n aralığında olmalıdır; daha uzak değerlerin olasılığı "
                            "10⁻²³'ten küçüktür.")
    if n["n4a"] >= n["n4b"]:
        raise K.UploadError(f"Adım 4: birinci örneklem büyüklüğü ({n['n4a']}) ikinciden ({n['n4b']}) küçük "
                            "olmalıdır.")
    if n["n5"] > n["N5"]:
        raise K.UploadError(f"Adım 5: örneklem büyüklüğü n ({n['n5']}) anakütle büyüklüğü N'den ({n['N5']}) büyük "
                            "olamaz.")


# --- Alternatif örnek ve kendi değerlerin ----------------------------------------------------

@cache
def alternative() -> LabSpec:
    return build(ALT_VALUES, ALT_TEXTS, source="alternatif")


G1, G2, G3, G4, G5, G6 = ("Ortalamanın dağılımı · Adım 1", "Kesinlik · Adım 2", "Ortalamayla olasılık · Adım 3",
                          "Örneklem oranı · Adım 4", "Sonlu anakütle · Adım 5", "Bütünleştirici · Adım 6")


def _real(key: str, label: str, low: float, high: float, group: str, step: int, help: str, size: float = 1,
          decimals: int = 2) -> Parameter:
    return Parameter(key, label, low, high, ALT_VALUES[key], step=size, decimals=decimals, group=group, steps=(step,),
                     help=help)


def _count(key: str, label: str, low: int, high: int, group: str, step: int, help: str) -> Parameter:
    return Parameter(key, label, low, high, ALT_VALUES[key], group=group, steps=(step,), help=help)


PARAMETERS = (
    _real("mu1", "Anakütle ortalaması μ", -LIMIT, LIMIT, G1, 1, "Bütün eğrilerin merkezi."),
    _real("sd1", "Anakütle standart sapması σ", 0.01, SCALE_LIMIT, G1, 1,
          "Bireysel gözlemlerin standart sapması.", 0.5),
    _count("n1a", "Örneklem büyüklüğü n₁", 1, N_LIMIT, G1, 1, "Birinci örneklem büyüklüğü."),
    _count("n1b", "Örneklem büyüklüğü n₂", 2, N_LIMIT, G1, 1, "n₁'den büyük olmalıdır."),
    _real("sd2", "Anakütle standart sapması σ", 0.01, SCALE_LIMIT, G2, 2, "Standart hata σ/√n.", 0.5),
    _count("n2", "Başlangıç örneklem büyüklüğü n", 1, 156, G2, 2, "Tablo n, 4n, 16n ve 64n satırlarıyla kurulur."),
    _real("mu3", "Anakütle ortalaması μ", -LIMIT, LIMIT, G3, 3, "Örneklem ortalamasının beklenen değeri."),
    _real("sd3", "Anakütle standart sapması σ", 0.01, SCALE_LIMIT, G3, 3,
          "Bireysel gözlemlerin standart sapması.", 0.5),
    _count("n3", "Örneklem büyüklüğü n", 1, N_LIMIT, G3, 3, "n < 30 iken anakütle normal varsayılır."),
    _real("xb1", "Aralığın alt ucu x̄₁", -LIMIT, LIMIT, G3, 3, "P(x̄₁ ≤ X̄ ≤ x̄₂); μ ± 10σ/√n içinde."),
    _real("xb2", "Aralığın üst ucu x̄₂", -LIMIT, LIMIT, G3, 3, "x̄₁'den büyük olmalıdır."),
    _real("p4", "Anakütle oranı p", 0.01, 0.99, G4, 4, "Örneklem oranının beklenen değeri (iki ondalık).", 0.01),
    _count("n4a", "Örneklem büyüklüğü n₁", 1, N_LIMIT, G4, 4, "Birinci örneklem büyüklüğü."),
    _count("n4b", "Örneklem büyüklüğü n₂", 2, N_LIMIT, G4, 4, "n₁'den büyük olmalıdır."),
    _count("N5", "Anakütle büyüklüğü N", 2, 1000000, G5, 5, "Sonlu anakütledeki birim sayısı."),
    _count("n5", "Örneklem büyüklüğü n", 1, 1000000, G5, 5, "Yerine koymadan seçilir; N'den büyük olamaz."),
    _real("sd5", "Anakütle standart sapması σ", 0.01, SCALE_LIMIT, G5, 5, "Düzeltmesiz standart hata σ/√n.", 0.5),
    _real("mu6", "Anakütle ortalaması μ", -LIMIT, LIMIT, G6, 6, "Ortalamanın örnekleme dağılımının merkezi."),
    _real("sd6", "Anakütle standart sapması σ", 0.01, SCALE_LIMIT, G6, 6, "Standart hata σ/√n.", 0.5),
    _real("p6", "Anakütle oranı p", 0.01, 0.99, G6, 6, "Oranın örnekleme dağılımının merkezi.", 0.01),
    _count("n6", "Örneklem büyüklüğü n", 1, N_LIMIT, G6, 6, "Her dönem seçilen örneklem."),
)

PARAMS = ParamLab(
    parameters=PARAMETERS,
    build=lambda values: build(values),
    intro=(
        "Bu konuda dosya yüklenmez: notlardaki her örnek için değerleri aşağıya girin; her grup başlığındaki adımı "
        "kurar. Başlangıç değerleri alternatif örneğinkilerdir."
    ),
    groups=(G1, G2, G3, G4, G5, G6),
    validate=validate,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, params=PARAMS)


def default_values() -> dict[str, int | float]:
    return parameter_values(PARAMS)
