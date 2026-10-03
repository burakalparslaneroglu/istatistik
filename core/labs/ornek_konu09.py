"""Konu 9 genel uygulaması: Bernoulli denemesi, binom, Poisson ve hipergeometrik dağılımlar.

Ders notlarındaki adımlar (§9.3–§9.5 ve §9.12) aynı numaralarla, parametreleri değiştirilebilir biçimde yazılır. Bu
konuda dosya yoktur: "Kendi değerlerini gir" seçeneğinde öğrenci binomun $n$, $p$ ve $x$ değerlerini, Poisson için
saatlik ortalamayı, aralığın uzunluğunu ve $x$'i, hipergeometrik için $N$, $r$, $n$ ve $x$'i girer. Bütünleştirici
uygulama (Adım 8) aynı üç modelin "en az bir" ve "hiç" olasılıklarıdır. Alternatif örnek kurgusal bir kafedir (kupon,
mobil sipariş, kahve paketi). Notlardaki uygulama (``core.labs.konu09``) değişmez.

Olasılıklar iki yoldan hesaplanır: notlardaki formülle (kombinasyon, üs, e) ve yazılımın dağılım fonksiyonlarıyla
(Python ``scipy.stats``, R ``dbinom``/``dpois``/``dhyper``). Binom ve hipergeometrik olasılıklar kesirdir; metindeki
"=" ile "≈" ayrımı bu kesirden kurulur. Poisson olasılıkları $e$ içerdiği için her zaman yuvarlanmış yazılır.
"""

from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction
from functools import cache
from typing import Mapping

from scipy import stats

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs.ornek import (
    Parameter,
    ParamLab,
    TopicVariants,
    kesin,
    kesir_basamak,
    kesir_isaret,
    kesir_sayi,
    kesir_tex,
    liste,
    ondalik,
    ondalik_tex,
    parameter_values,
    sayi,
    with_app_values,
)
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    Derive,
    Event,
    GroupSummary,
    LabSpec,
    LabStep,
    NoteRef,
    Outcomes,
    RowSum,
    Scalar,
    ScalarTarget,
    ShowFrame,
    Statistic,
    Support,
    TableTarget,
)

TITLE = "Binom, Poisson ve hipergeometrik olasılıkları hesaplamak"
LIST_LIMIT = 10
"""Bernoulli dizileri n ≤ 10 iken (en çok 2¹⁰ = 1024 dizi) tek tek listelenir."""
MAX_LAMBDA = 50
TAIL = 1e-20
"""Poisson momentleri için destek, kuyruk olasılığı bu sayının altına inene kadar uzatılır."""

ALT_VALUES = {"n": 10, "p": 0.3, "x": 3, "saatlik": 18.0, "dakika": 20, "x_pois": 4, "N": 25, "r": 4, "n_h": 5,
              "x_h": 1}
ALT_TEXTS = {
    "binom": ("Bir kafenin kampanya kuponunu gören 10 müşterinin her biri diğerlerinden bağımsız olarak 0,30 "
              "olasılıkla kuponu kullanır."),
    "poisson": "Kafeye saatte ortalama 18 mobil sipariş gelir; 20 dakikalık bir aralık incelenir.",
    "hiper": ("25 kahve paketinin 4'ü hatalı paketlenmiştir; kalite kontrolde 5 paket yerine koymadan seçilip "
              "incelenir."),
    "outro": ("Aynı kafe aynı gün üç soruyla karşılaşır: kuponu gören 10 müşteriden en az biri kuponu kullanır mı, "
              "20 dakikada hiç mobil sipariş gelmez mi, incelenen 5 pakette en az bir hatalı paket var mı?"),
}
STORY = (
    "Kurgusal veri: bir kafede kampanya kuponu (10 müşteri, p = 0,30), mobil siparişler (saatte ortalama 18, 20 "
    "dakikalık aralık) ve kalite kontrol (25 paketin 4'ü hatalı, 5 paket incelenir)."
)


# --- Yardımcılar -------------------------------------------------------------------------

def _scalar(name: str, label: str, decimals: int = 4) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _num(value: float) -> str:
    """Parametrenin düzyazıdaki yazımı (0,3; 18; 7,5)."""

    return ondalik(kesin(value))


def _tex(value: float) -> str:
    return ondalik_tex(kesin(value))


def _p(value: Fraction) -> str:
    """Başarı olasılığı iki ondalıkla, notlardaki gibi (0,30; Bin(10, 0,30))."""

    return sayi(float(value), 2)


def _pt(value: Fraction) -> str:
    return _p(value).replace(",", "{,}")


def _fraction(value: float) -> Fraction:
    return Fraction(kesin(value))


def _const(value: Fraction | float) -> float:
    """Koda yazılacak sabit: kesin değerin kısa yazımı (1 − 0,29 = 0,71; 0,7100000000000001 değil)."""

    if isinstance(value, Fraction):
        return float(Decimal(value.numerator) / Decimal(value.denominator))
    return float(value)


def _digits(value: float, exact: Fraction | None = None) -> int:
    """Olasılığın gösterim basamağı: kesir en çok dört basamakla tam yazılabiliyorsa o kadar; değilse dört; çok küçük
    olasılıklarda üç anlamlı basamak görünecek kadar (en çok 12)."""

    if exact is not None and kesir_isaret(exact, kesir_basamak(exact)) == "=" and kesir_basamak(exact) <= 4:
        return kesir_basamak(exact)
    magnitude = abs(float(value))
    if magnitude == 0 or magnitude >= 1e-3:
        return 4 if exact is None else max(4, kesir_basamak(exact))
    digits = min(12, math.floor(-math.log10(magnitude)) + 3)
    if exact is not None:  # tam yarımda bir basamak daha (kayan noktalı değer iki yöne de yuvarlanabilir)
        scaled = abs(exact) * 10 ** (digits + 1)
        if scaled.denominator == 1 and scaled.numerator % 10 == 5:
            digits += 1
    return digits


def _float_text(value: float, digits: int) -> Decimal:
    """Kayan noktalı değerin ekrandaki gibi yuvarlanmış hâli (tablo ve metrik bu biçimi kullanır)."""

    return Decimal(f"{float(value):.{digits}f}")


def _shown(value: float, exact: Fraction | None = None, digits: int | None = None) -> str:
    """Olasılık düzyazıda: "= 0,25", "≈ 0,2668", çok küçükse "10⁻¹²'den küçük"."""

    digits = _digits(value, exact) if digits is None else digits
    if 0 < abs(value) < 5e-13:
        return "≈ 0 (10⁻¹²'den küçük)"
    if exact is not None:
        sign = "=" if kesir_isaret(exact, digits) == "=" else "≈"
        return f"{sign} {kesir_sayi(exact, digits)}"
    return f"≈ {ondalik(_float_text(value, digits))}"


def _math(value: float, exact: Fraction | None = None, digits: int | None = None) -> str:
    """Olasılık matematik ifadesinde: "= 0{,}25" ya da "\\approx 0{,}2668"."""

    digits = _digits(value, exact) if digits is None else digits
    if exact is not None:
        return f"{kesir_isaret(exact, digits)} {kesir_tex(exact, digits)}"
    return f"\\approx {ondalik_tex(_float_text(value, digits))}"


def _lam(value: Fraction) -> str:
    """λ düzyazıda ve etiketlerde: "λ = 6" ya da "λ ≈ 1,1667"."""

    digits = kesir_basamak(value, 4, 0)
    return f"λ {'=' if kesir_isaret(value, digits) == '=' else '≈'} {kesir_sayi(value, digits)}"


def _binom(n: int, p: Fraction, x: int) -> Fraction:
    return math.comb(n, x) * p ** x * (1 - p) ** (n - x)


def _hyper(population: int, successes: int, draws: int, x: int) -> Fraction:
    return Fraction(math.comb(successes, x) * math.comb(population - successes, draws - x),
                    math.comb(population, draws))


def _context(values: Mapping[str, float], texts: Mapping[str, str] | None) -> dict:
    n, x = int(values["n"]), int(values["x"])
    p = _fraction(values["p"])
    rate, minutes = _fraction(values["saatlik"]), int(values["dakika"])
    lam = rate * minutes / 60
    population, successes, draws, x_h = (int(values[key]) for key in ("N", "r", "n_h", "x_h"))
    return {"n": n, "x": x, "p": p, "q": 1 - p, "p_value": float(values["p"]), "rate": rate, "minutes": minutes,
            "lam": lam, "x_pois": int(values["x_pois"]), "N": population, "r": successes, "n_h": draws, "x_h": x_h,
            "texts": dict(texts or {})}


# --- Adımlar -------------------------------------------------------------------------------

def _binom_story(ctx: dict) -> str:
    if ctx["texts"].get("binom"):
        return ctx["texts"]["binom"]
    if ctx["n"] == 1:
        return f"Tek bir denemede başarı olasılığı $p = {_pt(ctx['p'])}$ olsun."
    return f"{ctx['n']} bağımsız denemenin her birinde başarı olasılığı $p = {_pt(ctx['p'])}$ olsun."


def _sum_text(n: int) -> str:
    """X = Y1 + ... + Yn yazımı (n = 1: X = Y1; n = 2: X = Y1 + Y2)."""

    terms = [f"Y{index}" for index in range(1, n + 1)]
    return "X = " + (" + ".join(terms) if n <= 3 else f"Y1 + ... + Y{n}")


def _span(start: int, end: int, dots: str = "…") -> str:
    """Ardışık tam sayılar: "4", "0 ve 1", "0, 1, 2 ve 3", "0, 1, …, 10" (kod açıklamalarında üç nokta "...")."""

    if end - start <= 3:
        return liste([str(value) for value in range(start, end + 1)])
    return f"{start}, {start + 1}, {dots}, {end}"


def _sequences(n: int, x: int) -> str:
    count = math.comb(n, x)
    if count == 1:
        return f"Tam {x} başarı içeren tek bir dizi vardır; olasılığı"
    return f"Tam {x} başarı içeren {count} dizi vardır ve hepsinin olasılığı aynıdır; toplamları"


def _step1(ctx: dict) -> LabStep:
    n, x, p, q = ctx["n"], ctx["x"], ctx["p"], ctx["q"]
    exact = _binom(n, p, x)
    at_least = 1 - q ** n
    d_x, d_one = _digits(float(exact), exact), _digits(float(at_least), at_least)
    pc, qc = _const(p), _const(q)
    sequences = (f"{n} deneme bağımsızsa $2^{{{n}}} = {2 ** n}$ olası sonuç dizisi vardır" if n > 1 else
                 "Tek denemede $2^{1} = 2$ olası sonuç vardır")
    lead = (f"{_binom_story(ctx)} Tek bir denemenin başarılı olup olmaması bir Bernoulli denemesidir: başarı $Y = 1$ "
            f"(olasılık $p = {_pt(p)}$), başarısızlık $Y = 0$. {sequences}. İçinde $x$ başarı bulunan bir dizinin "
            "olasılığı $p^x(1-p)^{n-x}$'tir; başarı sayısı $X = Y_1 + \\cdots + Y_n$'dir.")
    if n > LIST_LIMIT:
        return LabStep(
            number=1,
            title="Bernoulli denemelerinden binoma: bütün diziler",
            note=NoteRef("9.3", objects=("Şekil 9.3", "Şekil 9.4")),
            explanation=(f"{lead} Bu kadar dizi tek tek listelenmez (en çok $2^{{{LIST_LIMIT}}}$ dizi listelenir); "
                         "aynı $x$'i veren dizilerin sayısı kombinasyonla, olasılıkların toplamı çarpımla bulunur."),
            operations=(
                Scalar("dizi_sayisi", E.power(2, n), f"Dizi sayısı 2^{n}", decimals=0),
                Scalar("x_dizi_sayisi", E.comb(n, x), f"{x} başarılı dizi: C({n}, {x})", decimals=0),
                Scalar("tek_dizi", E.mul(E.power(pc, x), E.power(qc, n - x)), "Bir dizinin olasılığı",
                       decimals=_digits(float(p ** x * q ** (n - x)))),
                Scalar("P_x_dizi", E.mul(E.ref("x_dizi_sayisi"), E.ref("tek_dizi")), f"P(X = {x}) dizilerden",
                       decimals=d_x),
            ),
            checks=(
                _scalar("dizi_sayisi", f"2^{n}", 0),
                _scalar("x_dizi_sayisi", f"C({n}, {x})", 0),
                _scalar("P_x_dizi", f"P(X = {x})", d_x),
            ),
            takeaway=(
                f"{_sequences(n, x)}: P(X = {x}) {_shown(float(exact), exact, d_x)}. Binom rassal değişkeni, bağımsız "
                "Bernoulli denemelerindeki başarıların toplamıdır (§9.3)."
            ),
        )
    columns = tuple(f"Y{index}" for index in range(1, n + 1))
    return LabStep(
        number=1,
        title="Bernoulli denemelerinden binoma: bütün diziler",
        note=NoteRef("9.3", objects=("Şekil 9.3", "Şekil 9.4")),
        explanation=(f"{lead} Aynı $x$'i veren dizilerin olasılıkları toplanınca binom olasılık fonksiyonu elde "
                     "edilir."),
        operations=(
            Outcomes("diziler", tuple((column, (0, 1)) for column in columns),
                     f"{n} denemenin bütün sonuç dizileri: 1 = başarı, 0 = başarısızlık"),
            RowSum("diziler", "x", columns, f"{_sum_text(n)}: dizideki başarı sayısı (satır toplamı)"),
            Derive("diziler", "olasilik", E.mul(E.power(pc, E.var("x")), E.power(qc, E.sub(n, E.var("x")))),
                   f"Dizinin olasılığı: p^x (1 − p)^({n} − x)"),
            GroupSummary("diziler", "x", (("dizi_sayisi", "olasilik", "count"), ("olasilik", "olasilik", "sum")),
                         "binom_dizi", tuple(range(n + 1)), decimals=max(4, d_x)),
            BarChart("binom_dizi", "olasilik", "Başarı sayısı, x", "P(X = x)",
                     "Aynı x'i veren dizilerin olasılıkları toplamı", decimals=3),
            Event("diziler", "en_az_bir", "x", tuple(range(1, n + 1)), "X ≥ 1: en az bir başarı"),
            Statistic("diziler", "olasilik", "sum", "P_en_az_bir_dizi", "P(X ≥ 1): en az bir başarı içeren diziler",
                      where=("en_az_bir", 1), decimals=d_one),
        ),
        checks=(
            Check(f"P(X = {x}): {x} başarılı {math.comb(n, x)} dizinin toplamı",
                  TableTarget("binom_dizi", x, "olasilik"), 0.0, d_x),
            _scalar("P_en_az_bir_dizi", "P(X ≥ 1)", d_one),
        ),
        takeaway=(
            f"{_sequences(n, x)}: P(X = {x}) {_shown(float(exact), exact, d_x)}. Dizi sayısı sütunu binom "
            f"katsayısıdır: {x} başarının {n} konuma C({n}, {x}) farklı yerleşimi. Binom rassal değişkeni, bağımsız "
            "Bernoulli denemelerindeki başarıların toplamıdır (§9.3)."
        ),
    )


def _complement(n: int) -> str:
    if n == 1:
        return "Tek denemede “en az bir başarı” başarının kendisidir; tümleyen kuralı da aynı sayıyı verir:"
    return f"En az bir başarı için tek tek x = {_span(1, n)} olasılıklarını toplamak yerine tümleyen yeterlidir:"


def _events(n: int, x: int) -> str:
    """"Tam", "en az" ve "en çok" olaylarının farkı; x = 0 ya da x = n iken ikisi aynı olaydır."""

    if n == 0:
        return ""
    if x == 0:
        return ("x = 0 iken {X ≤ 0} ile {X = 0} aynı olaydır, {X ≥ 0} ise kesin olaydır; tümleyen kuralı “en az bir” "
                "olayını bu yüzden P(X = 0) ile yazar")
    if x == n:
        others = "" if n == 1 else "; 0 < x < n değerlerinde “tam”, “en az” ve “en çok” farklı olaylardır"
        return f"x = n iken {{X ≥ {n}}} ile {{X = {n}}} aynı olaydır, {{X ≤ {n}}} ise kesin olaydır{others}"
    return (f"P(X = {x}), P(X ≥ {x}) ve P(X ≤ {x}) farklı olaylardır; “en az” ifadesindeki eşitlik çizgisi {x} "
            "değerini olaya katar")


def _step2(ctx: dict) -> LabStep:
    n, x, p, q = ctx["n"], ctx["x"], ctx["p"], ctx["q"]
    exact = _binom(n, p, x)
    at_least = 1 - q ** n
    d_x, d_one = _digits(float(exact), exact), _digits(float(at_least), at_least)
    pc, qc = _const(p), _const(q)
    return LabStep(
        number=2,
        title="Binom olasılık fonksiyonu ve tümleyen",
        note=NoteRef("9.3", objects=("(9.2)", "(9.3)")),
        explanation=(
            "$n$ denemede tam $x$ başarının olasılığı $P(X = x) = \\binom{n}{x}p^x(1-p)^{n-x}$'tir (Denklem "
            f"9.2): $P(X = {x}) = \\binom{{{n}}}{{{x}}}({_pt(p)})^{{{x}}}({_pt(q)})^{{{n - x}}} "
            f"{_math(float(exact), exact, d_x)}$. “En az bir” olayı için tümleyen kısa yoldur: $P(X \\geq 1) = 1 - P(X "
            "= 0) = 1 - (1 - p)^n$ (Denklem 9.3). Yazılımda binom olasılık fonksiyonu Python'da `stats.binom.pmf`, "
            "R'de `dbinom`; birikimli olasılık $P(X \\leq x)$ ise `stats.binom.cdf` ve `pbinom` ile hesaplanır."
        ),
        operations=(
            Scalar("yerlesim", E.comb(n, x), f"C({n}, {x}): yerleşim sayısı", decimals=0),
            Scalar("Px_binom_formul", E.mul(E.comb(n, x), E.mul(E.power(pc, x), E.power(qc, n - x))),
                   f"P(X = {x}) formülle", decimals=d_x),
            Scalar("Px_binom", E.dbinom(x, n, pc), f"P(X = {x}) yazılımla", decimals=d_x),
            Scalar("P_en_az_bir", E.sub(1, E.power(qc, n)), f"P(X ≥ 1) = 1 − (1 − p)^{n}", decimals=d_one),
            Scalar("P_en_az_bir_birikimli", E.sub(1, E.pbinom(0, n, pc)), "P(X ≥ 1) = 1 − P(X ≤ 0)", decimals=d_one),
        ),
        checks=(
            _scalar("yerlesim", f"C({n}, {x})", 0),
            _scalar("Px_binom_formul", f"P(X = {x}) formülle", d_x),
            _scalar("Px_binom", f"P(X = {x}) yazılımla", d_x),
            _scalar("P_en_az_bir", f"P(X ≥ 1) = 1 − (1 − p)^{n}", d_one),
            _scalar("P_en_az_bir_birikimli", "P(X ≥ 1) birikimli olasılıkla", d_one),
        ),
        takeaway=(
            f"Formül ve yazılım aynı sayıyı verir: P(X = {x}) {_shown(float(exact), exact, d_x)}. {_complement(n)} "
            f"P(X ≥ 1) {_shown(float(at_least), at_least, d_one)}. {_events(n, x)} (§9.3)."
        ),
    )


def _moments(frame: str, suffix: str, label: str, mean_digits: int, var_digits: int) -> tuple:
    """Konu 8'in tanımları olasılık fonksiyonu tablosuna: E(X) = Σ x f(x), Var(X) = Σ (x − μ)² f(x)."""

    mean, variance = f"E_{suffix}", f"Var_{suffix}"
    return (
        Derive(frame, "xf", E.mul(E.var("x"), E.var("f")), "x f(x)"),
        Statistic(frame, "xf", "sum", mean, f"E(X) = Σ x f(x): {label}", decimals=mean_digits),
        Derive(frame, "kare", E.mul(E.power(E.sub(E.var("x"), E.ref(mean)), 2), E.var("f")), "(x − μ)² f(x)"),
        Statistic(frame, "kare", "sum", variance, f"Var(X) = Σ (x − μ)² f(x): {label}", decimals=var_digits),
    )


def _step3(ctx: dict) -> LabStep:
    n, p, q = ctx["n"], ctx["p"], ctx["q"]
    mean, variance = n * p, n * p * q
    d_mean, d_var = kesir_basamak(mean, 4, 0), kesir_basamak(variance, 4, 0)
    pc, qc = _const(p), _const(q)
    return LabStep(
        number=3,
        title="Binomda beklenen değer ve varyans",
        note=NoteRef("9.3", objects=("(9.4)–(9.5)",)),
        explanation=(
            "Binom dağılımı Konu 8'deki kesikli dağılımın özel bir hâlidir: $E(X) = \\sum_x x f(x)$ ve "
            "$\\operatorname{Var}(X) = \\sum_x (x - \\mu)^2 f(x)$ tanımları olasılık fonksiyonu tablosuna aynen "
            "uygulanır. Binomda bu toplamlar $E(X) = np$ ve $\\operatorname{Var}(X) = np(1 - p)$ formüllerine "
            "indirgenir (Denklem 9.4–9.5)."
        ),
        operations=(
            Support("binom_n", "x", 0, n, f"Bin({n}, {_p(p)}): X'in olası değerleri {_span(0, n, '...')}"),
            Derive("binom_n", "f", E.dbinom(E.var("x"), n, pc), "f(x) = P(X = x)"),
            *_moments("binom_n", "binom", "tablodan", d_mean, d_var),
            ShowFrame("binom_n", ("x", "f", "xf", "kare"), "Olasılık fonksiyonu tablosu ve momentlerin hesabı"),
            Scalar("E_np", E.mul(n, pc), "E(X) = np", decimals=d_mean),
            Scalar("Var_npq", E.mul(E.mul(n, pc), qc), "Var(X) = np(1 − p)", decimals=d_var),
        ),
        checks=(
            _scalar("E_binom", "E(X) = Σ x f(x)", d_mean),
            _scalar("Var_binom", "Var(X) = Σ (x − μ)² f(x)", d_var),
            _scalar("E_np", f"E(X) = {n}({_p(p)})", d_mean),
            _scalar("Var_npq", f"Var(X) = {n}({_p(p)})({_p(q)})", d_var),
        ),
        takeaway=(
            f"Tablodan hesaplanan momentler formüllerle aynıdır: E(X) {_shown(float(mean), mean, d_mean)}, Var(X) "
            f"{_shown(float(variance), variance, d_var)}. Beklenen değer, {n} denemede mutlaka bu kadar başarı olacağı "
            f"anlamına gelmez; çok sayıda benzer {n} denemelik grupta başarı sayısının uzun dönem ortalamasıdır (§9.3)."
        ),
    )


def _shape_name(p: Fraction) -> str:
    return f"f_{int(p * 100):03d}"


def _modes_binom(n: int, p: Fraction) -> list[int]:
    probabilities = [_binom(n, p, value) for value in range(n + 1)]
    top = max(probabilities)
    return [value for value, probability in enumerate(probabilities) if probability == top]


def _step4(ctx: dict) -> LabStep:
    n, p = ctx["n"], ctx["p"]
    shapes = sorted({p, Fraction(1, 2), 1 - p})
    columns = [_shape_name(value) for value in shapes]
    operations = [Support("binom_sekil", "x", 0, n, f"n = {n}: olası değerler {_span(0, n, '...')}")]
    checks = []
    for value, column in zip(shapes, columns):
        operations.append(Derive("binom_sekil", column, E.dbinom(E.var("x"), n, _const(value)),
                                 f"f(x), p = {_p(value)}"))
    operations.append(ShowFrame("binom_sekil", ("x", *columns), "Binom dağılımları aynı değer ekseninde"))
    for value, column in zip(shapes, columns):
        shape = "simetrik" if value == Fraction(1, 2) else ("sağa çarpık" if value < Fraction(1, 2) else "sola çarpık")
        operations.append(BarChart("binom_sekil", column, "Başarı sayısı, x", "P(X = x)",
                                   f"Bin({n}, {_p(value)}): {shape}", x="x", decimals=3))
        mode = _modes_binom(n, value)[0]
        probability = _binom(n, value, mode)
        checks.append(Check(f"p = {_p(value)}: P(X = {mode}), en olası değer",
                            CellTarget("binom_sekil", column, mode + 1), 0.0, _digits(float(probability), probability)))
    if len(shapes) == 1:
        story = (f"p = 0,50'de Bin({n}, 0,50) tam simetriktir; p ile 1 − p aynı olduğu için tek bir dağılım çizilir. "
                 "Başka bir p seçildiğinde p ve 1 − p birbirinin aynadaki görüntüsüdür.")
        explanation = (f"$n = {n}$ sabitken $p = 0{{,}}50$ alınır; olasılık fonksiyonu olası değerler ({_span(0, n)}) "
                       "üzerinde yazılır.")
    else:
        low = shapes[0]
        story = (f"p arttıkça dağılım daha büyük başarı sayılarına kayar; en yüksek sütun E(X) = np çevresindedir. "
                 f"p = 0,50'de dağılım simetriktir; p = {_p(low)} ile p = {_p(1 - low)} birbirinin "
                 f"aynadaki görüntüsüdür: P(X = x | p) = P(X = {n} − x | 1 − p).")
        explanation = (f"$n = {n}$ sabitken başarı olasılığı ${_pt(shapes[0])}$, $0{{,}}50$ ve "
                       f"${_pt(shapes[-1])}$ alınır (girilen $p$ ve tümleyeni $1 - p$). Her $p$ için olasılık "
                       f"fonksiyonu aynı olası değerler ({_span(0, n)}) üzerinde yazılır.")
    return LabStep(
        number=4,
        title="p değiştiğinde binom dağılımının biçimi",
        note=NoteRef("9.3", objects=("Şekil 9.6",)),
        explanation=explanation,
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=f"{story} Sezgi sekmesindeki Deney 1'de n ve p kaydırıcılarla değişir (§9.3).",
    )


def _poisson_story(ctx: dict) -> str:
    return ctx["texts"].get("poisson") or (f"Bir süreçte saatte ortalama {_num(float(ctx['rate']))} olay gerçekleşsin; "
                                           f"{ctx['minutes']} dakikalık bir aralık incelensin.")


def _step5(ctx: dict) -> LabStep:
    lam, x = ctx["lam"], ctx["x_pois"]
    lam_value = float(lam)
    probability = stats.poisson.pmf(x, lam_value)
    d_lam = kesir_basamak(lam, 4, 0)
    d_x = _digits(probability)
    rate, minutes = _const(ctx["rate"]), ctx["minutes"]
    lam_text = kesir_tex(lam, d_lam)
    sign = kesir_isaret(lam, d_lam)
    return LabStep(
        number=5,
        title="Poisson: λ'yı aralığa taşımak ve olasılık fonksiyonu",
        note=NoteRef("9.4", objects=("Şekil 9.7",)),
        explanation=(
            f"{_poisson_story(ctx)} Aralığın ortalaması $\\lambda = {_tex(rate)}({minutes}/60) {sign} {lam_text}$ "
            f"olur. Tam {x} olay olasılığı $P(X = {x}) = \\lambda^{{{x}}} e^{{-\\lambda}}/{x}!$ ile bulunur "
            "(Denklem 9.7). Yazılımda Poisson olasılık fonksiyonu Python'da `stats.poisson.pmf`, R'de `dpois`'tir."
        ),
        operations=(
            Scalar("lambda_t", E.mul(rate, E.div(minutes, 60)), f"λ = {_num(rate)} × {minutes}/60", decimals=d_lam),
            Scalar("Px_pois_formul",
                   E.div(E.mul(E.power(E.ref("lambda_t"), x), E.exp(E.neg(E.ref("lambda_t")))), E.factorial(x)),
                   f"P(X = {x}) formülle", decimals=d_x),
            Scalar("Px_pois", E.dpois(x, E.ref("lambda_t")), f"P(X = {x}) yazılımla", decimals=d_x),
        ),
        checks=(
            _scalar("lambda_t", f"λ = {_num(rate)}({minutes}/60)", d_lam),
            _scalar("Px_pois_formul", f"P(X = {x}) formülle", d_x),
            _scalar("Px_pois", f"P(X = {x}) yazılımla", d_x),
        ),
        takeaway=(
            f"{minutes} dakikalık olasılık hesabında saatlik ortalama değil, aralığın ortalaması kullanılır: olay hızı "
            f"önce sorudaki aralığa taşınır. Tam {x} olay olasılığı {_shown(probability, None, d_x)} (§9.4)."
            if minutes != 60 else
            f"Aralık bir saat olduğu için λ saatlik ortalamanın kendisidir. Tam {x} olay olasılığı "
            f"{_shown(probability, None, d_x)} (§9.4)."
        ),
    )


def _support_end(lam: float, tail: float) -> int:
    """Kuyruk olasılığı P(X > k) ``tail``'in altına inen en küçük k."""

    k = max(0, int(lam))
    while stats.poisson.sf(k, lam) >= tail:
        k += 1
    return k


def _poisson_modes(lam: Fraction) -> list[int]:
    if lam.denominator == 1:
        return [int(lam) - 1, int(lam)] if lam >= 1 else [0]
    return [math.floor(lam)]


def _step6(ctx: dict) -> LabStep:
    lam = ctx["lam"]
    lam_value = float(lam)
    end = _support_end(lam_value, TAIL)
    shapes = (lam / 2, lam, 2 * lam)
    chart_end = max(10, _support_end(float(2 * lam), 1e-3))
    d_lam = kesir_basamak(lam, 4, 0)
    columns = ("f_yarim", "f_lambda", "f_iki_kat")
    operations = [
        Support("pois_tam", "x", 0, end,
                f"Pois(λ): olası değerler {_span(0, end, '...')} (sonraki değerlerin olasılığı ihmal edilebilir)"),
        Derive("pois_tam", "f", E.dpois(E.var("x"), E.ref("lambda_t")), "f(x) = P(X = x)"),
        Statistic("pois_tam", "f", "sum", "toplam_pois", f"Σ f(x), x = {_span(0, end, '...')}", decimals=4),
        *_moments("pois_tam", "pois", "λ", d_lam, d_lam),
        Support("pois_sekil", "x", 0, chart_end, f"x = {_span(0, chart_end, '...')}"),
    ]
    checks = [_scalar("E_pois", "E(X) = λ", d_lam), _scalar("Var_pois", "Var(X) = λ", d_lam),
              _scalar("toplam_pois", "Σ f(x)", 4)]
    for value, column in zip(shapes, columns):
        operations.append(Derive("pois_sekil", column, E.dpois(E.var("x"), _const(value)), f"f(x), {_lam(value)}"))
    operations.append(ShowFrame("pois_sekil", ("x", *columns), "Üç Poisson dağılımı aynı değer ekseninde"))
    for value, column in zip(shapes, columns):
        operations.append(BarChart("pois_sekil", column, "Olay sayısı, x", "P(X = x)", f"Pois: {_lam(value)}", x="x",
                                   decimals=3))
        mode = _poisson_modes(value)[-1]
        if mode <= chart_end:
            probability = stats.poisson.pmf(mode, float(value))
            checks.append(Check(f"{_lam(value)}: P(X = {mode})", CellTarget("pois_sekil", column, mode + 1), 0.0,
                                _digits(probability)))
    modes = _poisson_modes(lam)
    if len(modes) == 2:
        likely = f"λ tam sayı olduğu için en olası iki değer λ − 1 ve λ'dır ({modes[0]} ve {modes[1]})"
    else:
        likely = f"en olası değer λ'nın tam kısmıdır ({modes[0]})"
    return LabStep(
        number=6,
        title="Poisson'da E(X) = Var(X) = λ ve λ'nın biçime etkisi",
        note=NoteRef("9.4", objects=("Şekil 9.8",)),
        explanation=(
            "Poisson rassal değişkeninin teorik üst sınırı yoktur, ama $x$ büyüdükçe olasılıklar hızla küçülür: "
            f"$\\lambda {kesir_isaret(lam, d_lam)} {kesir_tex(lam, d_lam)}$ için $x > {end}$ değerlerinin toplam "
            "olasılığı $10^{-20}$'den küçüktür. Bu yüzden $x = 0, 1, \\ldots$ değerleriyle $\\sum x f(x)$ ve "
            "$\\sum (x - \\mu)^2 f(x)$ hesaplanabilir. Biçimi görmek için $\\lambda/2$, $\\lambda$ ve $2\\lambda$ "
            "dağılımları aynı eksende çizilir."
        ),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=(
            f"Teorik Poisson modelinde ortalama ile varyans eşittir: ikisi de λ; {likely}. λ küçükken dağılım belirgin "
            "biçimde sağa çarpıktır; λ büyüdükçe sağa kayar ve daha dengeli bir biçim alır (§9.4)."
        ),
    )


def _hyper_story(ctx: dict) -> str:
    return ctx["texts"].get("hiper") or (f"{ctx['N']} birimlik bir anakütlede {ctx['r']} başarı vardır; "
                                         f"{ctx['n_h']} birim yerine koymadan seçilir.")


def _variance_text(ctx: dict) -> str:
    """Sonlu anakütle çarpanının yorumu; uç durumlarda (r = 0, r = N, n = 1, n = N) ayrı cümle."""

    population, successes, draws = ctx["N"], ctx["r"], ctx["n_h"]
    share = Fraction(successes, population)
    variance = draws * share * (1 - share) * Fraction(population - draws, population - 1)
    binom_variance = draws * share * (1 - share)
    if successes in (0, population):
        return ("Anakütledeki bütün birimler aynı türden olduğu için (r = 0 ya da r = N) seçimdeki başarı sayısı "
                "sabittir; iki modelde de varyans sıfırdır.")
    if draws == population:
        return ("Bütün anakütle seçildiği için (n = N) seçimdeki başarı sayısı r'dir ve değişmez: (N − n)/(N − 1) "
                "çarpanı sıfırdır, hipergeometrik varyans da sıfırdır.")
    if draws == 1:
        return ("Tek birim seçildiğinde (N − n)/(N − 1) çarpanı 1'dir: hipergeometrik ve binom varyansı aynıdır.")
    d_var = kesir_basamak(variance, 4, 0)
    return (f"Varyans formülündeki (N − n)/(N − 1) = {population - draws}/{population - 1} çarpanı sonlu anakütleden "
            "yerine koymadan seçimin varyansı azaltan etkisidir: aynı p = r/N ile binom varyansı n(r/N)(1 − r/N) "
            f"{_shown(float(binom_variance), binom_variance)} olurdu; hipergeometrik varyans "
            f"{_shown(float(variance), variance, d_var)}.")


def _step7(ctx: dict) -> LabStep:
    population, successes, draws, x = ctx["N"], ctx["r"], ctx["n_h"], ctx["x_h"]
    exact = _hyper(population, successes, draws, x)
    low, high = max(0, draws - (population - successes)), min(draws, successes)
    share = Fraction(successes, population)
    mean = draws * share
    variance = draws * share * (1 - share) * Fraction(population - draws, population - 1)
    d_x = _digits(float(exact), exact)
    d_mean, d_var = kesir_basamak(mean, 4, 0), kesir_basamak(variance, 4, 0)
    return LabStep(
        number=7,
        title=f"Hipergeometrik: {population} birimden yerine koymadan {draws}",
        note=NoteRef("9.5", objects=("(9.11)–(9.13)",)),
        explanation=(
            f"{_hyper_story(ctx)} $N = {population}$, $r = {successes}$, $n = {draws}$. Tam {x} başarı olasılığı "
            f"$P(X = {x}) = \\binom{{{successes}}}{{{x}}}\\binom{{{population - successes}}}{{{draws - x}}}"
            f"/\\binom{{{population}}}{{{draws}}} {_math(float(exact), exact, d_x)}$ (Denklem 9.11). Yazılımda "
            "hipergeometrik olasılık fonksiyonu Python'da `stats.hypergeom.pmf(x, N, r, n)`, R'de "
            "`dhyper(x, r, N - r, n)`'dir: R başarı ve başarısızlık sayılarını ayrı ister."
        ),
        operations=(
            Scalar("Px_hiper_formul",
                   E.div(E.mul(E.comb(successes, x), E.comb(population - successes, draws - x)),
                         E.comb(population, draws)),
                   f"P(X = {x}) formülle", decimals=d_x),
            Scalar("Px_hiper", E.dhyper(x, population, successes, draws), f"P(X = {x}) yazılımla", decimals=d_x),
            Support("hiper", "x", low, high,
                    f"Hiper({population}, {successes}, {draws}): "
                    + (f"tek olası değer {low}" if low == high else f"olası değerler {_span(low, high, '...')}")),
            Derive("hiper", "f", E.dhyper(E.var("x"), population, successes, draws), "f(x) = P(X = x)"),
            *_moments("hiper", "hiper", "tablodan", d_mean, d_var),
            ShowFrame("hiper", ("x", "f", "xf", "kare"), "Olasılık fonksiyonu tablosu ve momentlerin hesabı"),
            Scalar("E_hiper_formul", E.mul(draws, E.div(successes, population)), "E(X) = n r/N", decimals=d_mean),
            Scalar("Var_hiper_formul",
                   E.mul(E.mul(E.mul(draws, E.div(successes, population)), E.sub(1, E.div(successes, population))),
                         E.div(population - draws, population - 1)),
                   "Var(X) = n (r/N)(1 − r/N)(N − n)/(N − 1)", decimals=d_var),
        ),
        checks=(
            _scalar("Px_hiper_formul", f"P(X = {x}) formülle", d_x),
            _scalar("Px_hiper", f"P(X = {x}) yazılımla", d_x),
            _scalar("E_hiper", "E(X) = Σ x f(x)", d_mean),
            _scalar("Var_hiper", "Var(X) = Σ (x − μ)² f(x)", d_var),
            _scalar("E_hiper_formul", f"E(X) = {draws}({successes}/{population})", d_mean),
            _scalar("Var_hiper_formul", "Var(X) formülle", d_var),
        ),
        takeaway=(
            f"Seçilen {draws} birimde tam {x} başarı olasılığı {_shown(float(exact), exact, d_x)}. "
            f"{_variance_text(ctx)} Sezgi sekmesindeki Deney 3 iki modeli karşılaştırır (§9.5–9.6)."
        ),
    )


def _step8(ctx: dict) -> LabStep:
    n, p, q, lam = ctx["n"], ctx["p"], ctx["q"], ctx["lam"]
    population, successes, draws = ctx["N"], ctx["r"], ctx["n_h"]
    at_least = 1 - q ** n
    none = math.exp(-float(lam))
    hyper_any = 1 - _hyper(population, successes, draws, 0) if draws <= population - successes else Fraction(1)
    d_b, d_p, d_h = _digits(float(at_least), at_least), _digits(none), _digits(float(hyper_any), hyper_any)
    qc, pc = _const(q), _const(p)
    first = "tek deneme başarılı olur mu" if n == 1 else f"{n} denemeden en az biri başarılı olur mu"
    intro = ctx["texts"].get("outro") or (
        f"Aynı gün üç soru sorulsun: {first}, {ctx['minutes']} dakikalık aralıkta "
        f"hiç olay gerçekleşmez mi, yerine koymadan seçilen {draws} birimde en az bir başarı var mı?")
    return LabStep(
        number=8,
        title="Bütünleştirici uygulama: aynı süreçte üç model",
        note=NoteRef("9.12", objects=("Tablo 9.6",)),
        explanation=(
            f"{intro} Üç soru üç farklı veri üretim mekanizmasıdır: $X \\sim \\operatorname{{Bin}}({n}, "
            f"{_pt(p)})$, $Y \\sim \\operatorname{{Pois}}(\\lambda)$ ({_lam(lam)}), $Z \\sim "
            f"\\text{{Hiper}}({population}, {successes}, {draws})$. İstenen olasılıklar $P(X \\geq 1)$, $P(Y = 0)$ ve "
            "$P(Z \\geq 1)$'dir; her biri formülle ve yazılımın fonksiyonuyla iki yoldan hesaplanır."
        ),
        operations=(
            Scalar("P_donusum", E.sub(1, E.power(qc, n)), f"P(X ≥ 1) = 1 − (1 − p)^{n}", decimals=d_b),
            Scalar("P_donusum_birikimli", E.sub(1, E.pbinom(0, n, pc)), "P(X ≥ 1) = 1 − P(X ≤ 0)", decimals=d_b),
            Scalar("P_hic", E.exp(E.neg(E.ref("lambda_t"))), "P(Y = 0) = e^(−λ)", decimals=d_p),
            Scalar("P_hic_pois", E.dpois(0, E.ref("lambda_t")), "P(Y = 0) yazılımla", decimals=d_p),
            Scalar("P_kalite", E.sub(1, E.div(E.comb(population - successes, draws), E.comb(population, draws))),
                   "P(Z ≥ 1) = 1 − P(Z = 0)", decimals=d_h),
            Scalar("P_kalite_hiper", E.sub(1, E.phyper(0, population, successes, draws)), "P(Z ≥ 1) = 1 − P(Z ≤ 0)",
                   decimals=d_h),
        ),
        checks=(
            _scalar("P_donusum", "P(X ≥ 1)", d_b),
            _scalar("P_donusum_birikimli", "P(X ≥ 1) birikimli olasılıkla", d_b),
            _scalar("P_hic", "P(Y = 0)", d_p),
            _scalar("P_hic_pois", "P(Y = 0) yazılımla", d_p),
            _scalar("P_kalite", "P(Z ≥ 1)", d_h),
            _scalar("P_kalite_hiper", "P(Z ≥ 1) yazılımla", d_h),
        ),
        takeaway=(
            f"P(X ≥ 1) {_shown(float(at_least), at_least, d_b)}, P(Y = 0) {_shown(none, None, d_p)}, P(Z ≥ 1) "
            f"{_shown(float(hyper_any), hyper_any, d_h)}. Aynı süreçte üç farklı dağılım gerekir. Model konunun "
            "adından değil, veri üretim mekanizmasından seçilir: sabit sayıda bağımsız deneme (binom), bir aralıktaki "
            "olay sayısı (Poisson), sonlu anakütleden yerine koymadan seçim (hipergeometrik) (§9.12)."
        ),
    )


def build(values: Mapping[str, float], texts: Mapping[str, str] | None = None, source: str = "kendi") -> LabSpec:
    """Konu 9 uygulamasını verilen parametrelerle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    validate(values)
    ctx = _context(values, texts)
    steps = (_step1(ctx), _step2(ctx), _step3(ctx), _step4(ctx), _step5(ctx), _step6(ctx), _step7(ctx), _step8(ctx))
    labels = [("x", "x"), ("f", "f(x)"), ("xf", "x f(x)"), ("kare", "(x − μ)² f(x)"), ("olasilik", "Olasılık"),
              ("dizi_sayisi", "Dizi sayısı"), ("en_az_bir", "X ≥ 1")]
    for value in sorted({ctx["p"], Fraction(1, 2), 1 - ctx["p"]}):
        labels.append((_shape_name(value), f"p = {_p(value)}"))
    for column, value in zip(("f_yarim", "f_lambda", "f_iki_kat"), (ctx["lam"] / 2, ctx["lam"], 2 * ctx["lam"])):
        labels.append((column, _lam(value)))
    spec = LabSpec(
        topic_key="konu09",
        title=TITLE,
        note_section="9",
        steps=steps,
        labels=tuple(labels),
        source=source,
    )
    return with_app_values(spec)


def validate(values: Mapping[str, float]) -> None:
    """Parametreler arasındaki koşullar: x ≤ n; λ ≤ 50; r ≤ N; n ≤ N; x seçimde mümkün olmalı."""

    n, x = int(values["n"]), int(values["x"])
    if x > n:
        raise K.UploadError(f"Binom: başarı sayısı x ({x}) deneme sayısı n'den ({n}) büyük olamaz.")
    lam = _fraction(values["saatlik"]) * int(values["dakika"]) / 60
    if lam > MAX_LAMBDA:
        raise K.UploadError(f"Poisson: aralığın ortalaması λ = saatlik ortalama × t/60 en çok {MAX_LAMBDA} olabilir; "
                            f"şu an {_lam(lam)}. Saatlik ortalamayı ya da aralığı küçültün.")
    population, successes, draws, x_h = (int(values[key]) for key in ("N", "r", "n_h", "x_h"))
    if successes > population:
        raise K.UploadError(f"Hipergeometrik: başarı sayısı r ({successes}) anakütle büyüklüğü N'den ({population}) "
                            "büyük olamaz.")
    if draws > population:
        raise K.UploadError(f"Hipergeometrik: seçilen birim sayısı n ({draws}) anakütle büyüklüğü N'den ({population}) "
                            "büyük olamaz.")
    low, high = max(0, draws - (population - successes)), min(draws, successes)
    if not low <= x_h <= high:
        raise K.UploadError(f"Hipergeometrik: bu seçimde başarı sayısı x en az {low}, en çok {high} olabilir "
                            f"(şu an {x_h}).")


# --- Alternatif örnek ve kendi değerlerin ----------------------------------------------------

@cache
def alternative() -> LabSpec:
    return build(ALT_VALUES, ALT_TEXTS, source="alternatif")


PARAMETERS = (
    Parameter("n", "Deneme sayısı n", 1, 50, ALT_VALUES["n"], group="Binom", steps=(1, 2, 3, 4, 8),
              help=f"Bağımsız deneme sayısı; n ≤ {LIST_LIMIT} iken bütün diziler listelenir."),
    Parameter("p", "Başarı olasılığı p", 0.01, 0.99, ALT_VALUES["p"], step=0.01, decimals=2, group="Binom",
              steps=(1, 2, 3, 4, 8), help="Her denemede başarı olasılığı (iki ondalık)."),
    Parameter("x", "Başarı sayısı x", 0, 50, ALT_VALUES["x"], group="Binom", steps=(1, 2),
              help="P(X = x) için başarı sayısı; n'den büyük olamaz."),
    Parameter("saatlik", "Saatlik ortalama olay sayısı", 0.5, 120, ALT_VALUES["saatlik"], step=0.5, decimals=1,
              group="Poisson", steps=(5, 6, 8), help="Bir saatte ortalama olay sayısı (ör. çağrı, sipariş)."),
    Parameter("dakika", "Aralık t (dakika)", 1, 240, ALT_VALUES["dakika"], group="Poisson", steps=(5, 6, 8),
              help=f"İncelenen aralığın uzunluğu; λ = saatlik ortalama × t/60 en çok {MAX_LAMBDA}."),
    Parameter("x_pois", "Olay sayısı x", 0, 150, ALT_VALUES["x_pois"], group="Poisson", steps=(5,),
              help="P(X = x) için olay sayısı."),
    Parameter("N", "Anakütle büyüklüğü N", 2, 500, ALT_VALUES["N"], group="Hipergeometrik", steps=(7, 8),
              help="Sonlu anakütledeki birim sayısı."),
    Parameter("r", "Anakütledeki başarı sayısı r", 0, 500, ALT_VALUES["r"], group="Hipergeometrik", steps=(7, 8),
              help="Anakütlede başarı sayılan birimler (ör. hatalı paket); N'den büyük olamaz."),
    Parameter("n_h", "Seçilen birim sayısı n", 1, 500, ALT_VALUES["n_h"], group="Hipergeometrik", steps=(7, 8),
              help="Yerine koymadan seçilen birim sayısı; N'den büyük olamaz."),
    Parameter("x_h", "Seçimdeki başarı sayısı x", 0, 500, ALT_VALUES["x_h"], group="Hipergeometrik", steps=(7,),
              help="P(X = x) için seçimdeki başarı sayısı."),
)

PARAMS = ParamLab(
    parameters=PARAMETERS,
    build=lambda values: build(values),
    intro=(
        "Bu konuda dosya yüklenmez: üç modelin parametrelerini aşağıya girin. Binom değerleri Adım 1–4'ü, Poisson "
        "değerleri Adım 5–6'yı, hipergeometrik değerler Adım 7'yi kurar; Adım 8 üçünü birlikte kullanır. Başlangıç "
        "değerleri alternatif örneğinkilerdir."
    ),
    groups=("Binom", "Poisson", "Hipergeometrik"),
    validate=validate,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, params=PARAMS)


def default_values() -> dict[str, int | float]:
    return parameter_values(PARAMS)
