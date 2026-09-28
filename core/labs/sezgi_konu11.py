"""Konu 11 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Normal alan: tablo kuralı, tam değer ve simülasyon                   (Notlar §11.3–11.4, Şekil 11.4)
Deney 2  Binomdan normale: yaklaşım ve süreklilik düzeltmesi                  (Notlar §11.7–11.8, Tablo 11.3)
Deney 3  Üstel bekleme süresi: ortalama süre, kuyruk olasılığı ve geliş hızı  (Notlar §11.10–11.11)

Notlarda simülasyonla üretilmiş bir şekil yoktur. Varsayılan ayarlar notların örnekleridir: Deney 1'de sınav puanı
N(70, 10²) ve P(60 ≤ X ≤ 80) (§11.4), Deney 2'de tam 12 hatalı fatura, Bin(100, 0,10) (§11.8.1), Deney 3'te saatte 12
müşteri, μ = 5 dakika ve P(T > 10) (§11.11). Tablo kuralı Uygulama sekmesiyle aynıdır: z iki, Φ(z) dört ondalık
basamağa yuvarlanır.
"""

from __future__ import annotations

import math

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, plain
from core.labs.spec import (
    DensityPlot,
    Derive,
    Draw,
    DrawCount,
    Histogram,
    JoinColumns,
    NewSample,
    NoteRef,
    PmfWithDensity,
    Scalar,
    ScalarTable,
    Statistic,
    Support,
)

SEED = 217
TOPIC = "konu11"


def _short(value: float, decimals: int = 3) -> str:
    """Sondaki sıfırları atılmış düz metin sayı (5; 7,5; 11,5)."""

    text = f"{value:.{decimals}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",").replace("-", "−")


def _tex(value: float, decimals: int = 3) -> str:
    return _short(value, decimals).replace(",", "{,}").replace("−", "-")


def _whole(value: float) -> float | int:
    """Tam sayı değerler tam sayı olarak (kodda 5.0 yerine 5 yazılır)."""

    return int(value) if float(value).is_integer() else value


def _at_least_five(value: float) -> bool:
    """np ≥ 5 karşılaştırması; 0,05 × 100 gibi çarpımlardaki kayan nokta artığı sonucu değiştirmez."""

    return round(value, 9) >= 5


# --- Deney 1: normal alan -------------------------------------------------------------------

MEAN, SD = 70, 10
"""§11.4: sınav puanı X ~ N(70, 10²)."""
AXIS = (30, 110)
"""μ ± 4σ: a = 30 pratikte sol kuyruk, b = 110 pratikte sağ kuyruk verir (Φ(−4) ve 1 − Φ(4) dört basamakta 0)."""


def _table_phi(z: E.Expr) -> E.Expr:
    """Tablo değeri: z iki, Φ(z) dört ondalık basamağa yuvarlanır (Tablo 11.1)."""

    return E.roundto(E.normcdf(E.roundto(z, 2)), 4)


def _area_settings(parameters: Parameters) -> tuple[int, int, int]:
    low, high = sorted((int(parameters["a"]), int(parameters["b"])))
    return low, high, int(parameters["n"])


def _build_area(parameters: Parameters) -> tuple:
    low, high, n = _area_settings(parameters)
    x = E.var("x")
    return (
        NewSample("puan", n, SEED),
        Draw("puan", "x", "normal", MEAN, SD, "X ~ N(70, 10²): sınav puanı"),
        Derive("puan", "aralikta", E.mul(E.compare("ge", x, low), E.compare("le", x, high)),
               "Gösterge: a ≤ X ≤ b ise 1, değilse 0"),
        Statistic("puan", "aralikta", "mean", "pay", "a ile b arasındaki puanların payı", decimals=4),
        Scalar("z_a", E.div(E.sub(low, MEAN), SD), "z_a = (a − μ)/σ", decimals=2),
        Scalar("z_b", E.div(E.sub(high, MEAN), SD), "z_b = (b − μ)/σ", decimals=2),
        Scalar("P_tablo", E.sub(_table_phi(E.ref("z_b")), _table_phi(E.ref("z_a"))),
               "Tablo kuralıyla Φ(z_b) − Φ(z_a), (11.5)", decimals=4),
        Scalar("P_tam", E.sub(E.normcdf(E.ref("z_b")), E.normcdf(E.ref("z_a"))), "Yuvarlamasız Φ(z_b) − Φ(z_a)",
               decimals=4),
        DensityPlot("normal", MEAN, SD, AXIS, "N(70, 10²): a ile b arasındaki alan", "Sınav puanı x",
                    shade=((low, high),), references=((MEAN, "μ = 70"),)),
        Histogram("puan", (("x", "Puanlar"),), 80, AXIS[0], AXIS[1], "Puanların histogramı", "Sınav puanı x",
                  references=((low, f"a = {low}"), (high, f"b = {high}")), y_label="Öğrenci sayısı",
                  curves=(("normal", MEAN, SD, "Beklenen sayı: N(70, 10²)"),)),
    )


def _area_dgp(parameters: Parameters) -> tuple[str, ...]:
    low, high, n = _area_settings(parameters)
    z_low, z_high = (low - MEAN) / SD, (high - MEAN) / SD
    return (
        rf"X \sim N(70, 10^2), \qquad a = {low},\ b = {high}, \qquad n = {n}",
        r"P(a \le X \le b) = \Phi\!\left(\frac{b - 70}{10}\right) - \Phi\!\left(\frac{a - 70}{10}\right) = "
        rf"\Phi({number(z_high, 2)}) - \Phi({number(z_low, 2)})",
    )


def _area_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    _, _, n = _area_settings(parameters)
    s = state.scalars
    return (
        SimMetric("z sınırları", f"{plain(s['z_a'], 2)} ve {plain(s['z_b'], 2)}",
                  "z = (x − 70)/10: a ve b standart ölçekte."),
        SimMetric("Tablo kuralıyla olasılık", plain(s["P_tablo"], 4),
                  "Φ(z_b) − Φ(z_a); Φ tablodaki gibi dört basamak (Tablo 11.1)."),
        SimMetric("Yuvarlamasız olasılık", plain(s["P_tam"], 4), "Φ yuvarlanmadan hesaplanır."),
        SimMetric("Simülasyondaki pay", plain(s["pay"], 3),
                  f"n = {n} öğrenciden a ile b arasında puan alanların oranı."),
    )


def _area_takeaway(state: LabState, parameters: Parameters) -> str:
    low, high, n = _area_settings(parameters)
    s = state.scalars
    if low == high:
        text = (
            "a = b iken aralık tek bir puandır: sürekli dağılımda tek bir noktanın alanı sıfırdır ve olasılık 0'dır "
            f"(§10.2). Simülasyonda tam olarak bu puanı alan öğrencilerin payı {plain(s['pay'], 3)}. "
        )
    else:
        text = (
            f"Sınırlar z ölçeğinde {plain(s['z_a'], 2)} ve {plain(s['z_b'], 2)}; alan Φ(z_b) − Φ(z_a) ile bulunur, "
            f"(11.5). Tablo kuralıyla (z iki, Φ dört basamak) olasılık {plain(s['P_tablo'], 4)}, yuvarlamasız "
            f"{plain(s['P_tam'], 4)}; fark yalnız tablonun yuvarlamasından gelir. n = {n} öğrencide a ile b arasında "
            f"puan alanların payı {plain(s['pay'], 3)}. Standartlaştırma alanı değiştirmez; önce istenen alanın türü "
            "belirlenir (Şekil 11.4). "
        )
        if low == AXIS[0]:
            text += "a = 30 = μ − 4σ olduğundan aralık pratikte sol kuyruktur: P(X ≤ b) = Φ(z_b), (11.2). "
        if high == AXIS[1]:
            text += "b = 110 = μ + 4σ olduğundan aralık pratikte sağ kuyruktur: P(X ≥ a) = 1 − Φ(z_a), (11.4). "
    if (low, high) == (60, 80):
        text += "Bu ayar §11.4'teki P(60 ≤ X ≤ 80) = 0,8413 − 0,1587 = 0,6826 örneğidir."
    else:
        text += ("a = 60, b = 80 §11.4'teki P(60 ≤ X ≤ 80) = 0,6826 örneğidir; a = 30, b = 85 ile P(X ≤ 85) = 0,9332 "
                 "bulunur.")
    return text


NORMAL_AREA = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Normal alan: tablo kuralı, tam değer ve simülasyon",
    question="Sınav puanları N(70, 10²) dağılıyorsa iki puan arasındaki olasılık Φ tablosuyla nasıl bulunur; tablo "
             "kuralının verdiği değer, yuvarlamasız değer ve öğrencilerde gözlenen pay birbirine ne kadar yakındır?",
    note=NoteRef("11.4", objects=("Şekil 11.4", "(11.5)")),
    parameters=(
        SimParameter("a", "Alt sınır a", AXIS[0], AXIS[1], 60, 1,
                     "§11.4: a = 60. a > b seçilirse sınırlar yer değiştirir.", integer=True, decimals=0),
        SimParameter("b", "Üst sınır b", AXIS[0], AXIS[1], 80, 1, "§11.4: b = 80; a = 30 ile b = 85 P(X ≤ 85) verir.",
                     integer=True, decimals=0),
        SimParameter("n", "Öğrenci sayısı n", 100, 20000, 10000, 100, "N(70, 10²) dağılımından bağımsız çekilişler.",
                     integer=True, decimals=0),
    ),
    dgp=_area_dgp,
    dgp_note=(
        "Puanlar N(70, 10²) dağılımından birbirinden bağımsız çekilir; tohum 217'dir. Tablo kuralı notlardaki "
        "standart normal tablodur: z iki, Φ(z) dört ondalık basamağa yuvarlanır. Kaydırıcılar μ ± 4σ = 30–110 "
        "aralığındadır."
    ),
    look_at=(
        "**Yoğunluk eğrisi** — boyalı alan a ile b arasındaki olasılıktır; a'yı 30'a ya da b'yi 110'a çekince sol ve "
        "sağ kuyruk ortaya çıkar.",
        "**Metrikler** — tablo kuralıyla ve yuvarlamasız olasılık ile öğrencilerde gözlenen pay.",
    ),
    build=_build_area,
    metrics=_area_metrics,
    takeaway=_area_takeaway,
    labels=(("x", "Sınav puanı x"),),
)


# --- Deney 2: binomun normal yaklaştırması --------------------------------------------------------

def _binomial_settings(parameters: Parameters) -> tuple[int, float, int, int]:
    n = int(parameters["n"])
    return n, round(float(parameters["p"]), 2), min(int(parameters["x"]), n), int(parameters["tekrar"])


def binomial_window(n: int, p: float, x: int) -> tuple[int, int]:
    """Gösterilen başarı sayıları: np ± (5σ + 3), 0 ile n arasında, ve x. Kaydırıcıların her değerinde pencere
    dışının olasılığı 2 × 10⁻⁷'den küçüktür."""

    mean, sd = n * p, math.sqrt(n * p * (1 - p))
    low, high = max(0, math.floor(mean - 5 * sd) - 3), min(n, math.ceil(mean + 5 * sd) + 3)
    return min(low, x), max(high, x)


def _z(value: float) -> E.Expr:
    """Normal yaklaşımda standartlaştırma (değer − μ)/σ; μ ve σ önceden hesaplanan skalerlerdir."""

    return E.div(E.sub(value, E.ref("mu")), E.ref("sigma"))


def _build_binomial(parameters: Parameters) -> tuple:
    n, p, x, reps = _binomial_settings(parameters)
    low, high = binomial_window(n, p, x)
    count = E.var("basari")
    return (
        Scalar("mu", E.mul(n, p), "Normal yaklaşımın ortalaması μ = np", decimals=2),
        Scalar("sigma", E.sqrt(E.mul(E.mul(n, p), E.sub(1, p))), "Standart sapma σ = √(np(1 − p))", decimals=4),
        Support("dagilim", "x", low, high, "Gösterilen başarı sayıları; pencere dışının olasılığı ihmal edilebilir"),
        Derive("dagilim", "f", E.dbinom(E.var("x"), n, p), "Binom olasılığı P(X = x), (9.2)"),
        NewSample("deney", reps, SEED),
        DrawCount("deney", "basari", "binomial", (n, p), "X ~ Bin(n, p): her tekrarda n bağımsız deneme"),
        Derive("deney", "esit", E.compare("eq", count, x), f"Gösterge: X = {x} ise 1, değilse 0"),
        Derive("deney", "en_cok", E.compare("le", count, x), f"Gösterge: X ≤ {x} ise 1, değilse 0"),
        Statistic("deney", "esit", "mean", "pay_esit", f"Tekrarlarda X = {x} olanların payı", decimals=4),
        Statistic("deney", "en_cok", "mean", "pay_en_cok", f"Tekrarlarda X ≤ {x} olanların payı", decimals=4),
        ScalarTable(
            (
                ("Binom (tam)", E.dbinom(x, n, p)),
                ("Normal, süreklilik düzeltmeli", E.sub(E.normcdf(_z(x + 0.5)), E.normcdf(_z(x - 0.5)))),
                ("Normal, düzeltmesiz", E.sub(E.normcdf(_z(x)), E.normcdf(_z(x)))),
                ("Simülasyon payı", E.ref("pay_esit")),
            ),
            "tek_deger",
            decimals=4,
        ),
        ScalarTable(
            (
                ("Binom (tam)", E.pbinom(x, n, p)),
                ("Normal, süreklilik düzeltmeli", E.normcdf(_z(x + 0.5))),
                ("Normal, düzeltmesiz", E.normcdf(_z(x))),
                ("Simülasyon payı", E.ref("pay_en_cok")),
            ),
            "birikimli",
            decimals=4,
        ),
        JoinColumns("karsilastirma", ((f"P(X = {x})", "tek_deger", "deger"), (f"P(X ≤ {x})", "birikimli", "deger")),
                    decimals=4),
        PmfWithDensity("dagilim", "x", "f", "normal", "mu", "sigma", "Başarı sayısı x", "Olasılık / yoğunluk",
                       "Binom olasılıkları ve normal yaklaşım", "Binom olasılığı P(X = x)",
                       "Normal yaklaşım N(np, np(1 − p))", shade=((x - 0.5, x + 0.5),)),
    )


def _binomial_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, p, x, reps = _binomial_settings(parameters)
    mean, sd = n * p, math.sqrt(n * p * (1 - p))
    return (
        rf"X \sim \operatorname{{Bin}}(n, p), \qquad n = {n},\ p = {number(p, 2)}, \qquad {reps} \text{{ tekrar}}",
        rf"Y \sim N\bigl(np,\ np(1 - p)\bigr) = N({_tex(mean, 2)},\ {_tex(sd, 4)}^2), \qquad P(X = {x}) \approx "
        rf"P({_tex(x - 0.5)} < Y < {_tex(x + 0.5)})",
    )


def _condition(n: int, p: float) -> bool:
    return _at_least_five(n * p) and _at_least_five(n * (1 - p))


def _binomial_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    n, p, x, reps = _binomial_settings(parameters)
    column = state.tables["karsilastirma"][f"P(X = {x})"]
    condition = ("Koşul (11.6) sağlanıyor: ikisi de en az 5." if _condition(n, p)
                 else "Koşul (11.6) sağlanmıyor: ikisinin de en az 5 olması gerekir.")
    return (
        SimMetric("np ve n(1 − p)", f"{_short(n * p, 2)} ve {_short(n * (1 - p), 2)}", condition),
        SimMetric("Binom P(X = x)", plain(column["Binom (tam)"], 4), f"Tam olasılık, x = {x}; (9.2)."),
        SimMetric("Düzeltmeli normal yaklaşım", plain(column["Normal, süreklilik düzeltmeli"], 4),
                  f"P({_short(x - 0.5)} < Y < {_short(x + 0.5)}), Y ~ N(np, np(1 − p))."),
        SimMetric("Simülasyon payı", plain(state.scalars["pay_esit"], 4), f"{reps} tekrarda X = {x} olanların oranı."),
    )


def _binomial_takeaway(state: LabState, parameters: Parameters) -> str:
    n, p, x, _ = _binomial_settings(parameters)
    table = state.tables["karsilastirma"]
    single, cumulative = table[f"P(X = {x})"], table[f"P(X ≤ {x})"]
    text = (
        "Binom dağılımı yalnız tam sayılarda olasılık taşır, normal eğri süreklidir. Tek bir değerin normal karşılığı "
        "düzeltmesiz alınırsa alan sıfırdır; süreklilik düzeltmesi çubuğu x − 0,5 ile x + 0,5 arasına yayar (§11.8, "
        f"Tablo 11.3). Bu ayarda P(X = x) için tam olasılık {plain(single['Binom (tam)'], 4)}, düzeltmeli yaklaşım "
        f"{plain(single['Normal, süreklilik düzeltmeli'], 4)}; P(X ≤ x) için tam olasılık "
        f"{plain(cumulative['Binom (tam)'], 4)}, düzeltmeli yaklaşım "
        f"{plain(cumulative['Normal, süreklilik düzeltmeli'], 4)}, düzeltmesiz yaklaşım "
        f"{plain(cumulative['Normal, düzeltmesiz'], 4)}. "
    )
    if _condition(n, p):
        text += "np ve n(1 − p) en az 5 olduğundan koşul (11.6) sağlanır ve normal eğri çubukları yakından izler. "
    else:
        text += ("Koşul (11.6) sağlanmıyor: beklenen başarı ya da başarısızlık sayısı küçüktür, dağılım çarpıktır ve "
                 "normal eğri çubukları iyi izlemez. ")
    if int(parameters["x"]) > n:
        text += "x, n'den büyük seçildiği için x = n alındı. "
    if (n, p, x) == (100, 0.10, 12):
        text += ("Bu ayar §11.8.1'deki tam 12 hatalı fatura örneğidir: tablo kuralıyla 0,7967 − 0,6915 = 0,1052, "
                 "yuvarlamasız 0,1062; tam binom olasılığı 0,0988.")
    else:
        text += "n = 100, p = 0,10 ve x = 12 §11.8.1'deki tam 12 hatalı fatura örneğidir."
    return text


BINOMIAL_NORMAL = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Binomdan normale: yaklaşım ve süreklilik düzeltmesi",
    question="Binom olasılığı aynı ortalama ve standart sapmalı normal eğriyle ne zaman iyi yaklaştırılır; süreklilik "
             "düzeltmesi yapılmazsa ne olur?",
    note=NoteRef("11.8", objects=("(11.6)", "Şekil 11.8", "Tablo 11.3")),
    parameters=(
        SimParameter("n", "Deneme sayısı n", 10, 200, 100, 5, "§11.8.1: 100 fatura.", integer=True, decimals=0),
        SimParameter("p", "Başarı olasılığı p", 0.05, 0.95, 0.10, 0.05, "§11.8.1: faturaların %10'unda hata var.",
                     decimals=2),
        SimParameter("x", "Başarı sayısı x", 0, 200, 12, 1, "P(X = x) ve P(X ≤ x); x > n seçilirse x = n alınır.",
                     integer=True, decimals=0),
        SimParameter("tekrar", "Tekrar sayısı", 1000, 20000, 10000, 1000,
                     "Her tekrarda n deneme yapılır ve başarılar sayılır.", integer=True, decimals=0),
    ),
    dgp=_binomial_dgp,
    dgp_note=(
        "Her tekrarda n bağımsız deneme yapılır; her denemenin başarı olasılığı p'dir ve X başarıların sayısıdır "
        "(Konu 9). Tohum 217'dir. Normal yaklaşım aynı ortalama np ve standart sapma √(np(1 − p)) ile kurulur. Grafik "
        "np ± (5σ + 3) penceresini gösterir; pencere dışının olasılığı 2 × 10⁻⁷'den küçüktür."
    ),
    look_at=(
        "**Çubuklar ve eğri** — binom olasılıkları ile normal eğri; boyalı alan x − 0,5 ile x + 0,5 arasındaki "
        "süreklilik düzeltmesi.",
        "**Karşılaştırma tablosu** — tam binom, düzeltmeli ve düzeltmesiz normal yaklaşım ile simülasyon payı; p'yi "
        "0,05'e ya da n'yi 10'a indirip koşulun bozulmasını izleyin.",
    ),
    build=_build_binomial,
    metrics=_binomial_metrics,
    takeaway=_binomial_takeaway,
    tables=(("karsilastirma", "Tam binom olasılığı, normal yaklaşımlar ve simülasyon payı"),),
    labels=(("x", "Başarı sayısı x"), ("basari", "Başarı sayısı")),
)


# --- Deney 3: üstel bekleme süresi -----------------------------------------------------------------

def _wait_settings(parameters: Parameters) -> tuple[float | int, int, int]:
    return _whole(round(float(parameters["mu"]), 1)), int(parameters["t"]), int(parameters["n"])


def wait_axis(mu: float, t: int) -> int:
    """Yatay eksenin üst sınırı: en az 6μ (P(T > 6μ) = e⁻⁶ ≈ 0,0025) ve t'nin biraz ötesi."""

    return math.ceil(max(6 * mu, 1.2 * t))


def _build_wait(parameters: Parameters) -> tuple:
    mu, t, n = _wait_settings(parameters)
    upper = wait_axis(mu, t)
    return (
        NewSample("bekleme", n, SEED),
        Draw("bekleme", "sure", "exponential", mu, mu, "T ~ Üstel(μ): bir sonraki müşteriye kadar geçen süre"),
        Derive("bekleme", "uzun", E.compare("gt", E.var("sure"), t), f"Gösterge: T > {t} dakika ise 1, değilse 0"),
        Statistic("bekleme", "sure", "mean", "ortalama", "Bekleme sürelerinin ortalaması", decimals=2),
        Statistic("bekleme", "sure", "std", "s", "Bekleme sürelerinin standart sapması", decimals=2),
        Statistic("bekleme", "uzun", "mean", "pay", f"{t} dakikadan uzun beklemelerin payı", decimals=4),
        Scalar("P_uzun", E.exp(E.neg(E.div(t, mu))), "P(T > t) = e^(−t/μ), (11.9)", decimals=4),
        Scalar("lam", E.div(60, mu), "λ = 60/μ: saatteki ortalama geliş sayısı, (11.11)", decimals=2),
        DensityPlot("exponential", mu, mu, (0, upper), "Üstel yoğunluk: boyalı alan P(T > t)",
                    "Bekleme süresi (dakika)", shade=((t, upper),), references=((mu, f"μ = {_short(mu)}"),)),
        Histogram("bekleme", (("sure", "Bekleme süreleri"),), 60, 0, upper, "Bekleme sürelerinin histogramı",
                  "Bekleme süresi (dakika)", references=((t, f"t = {t} dakika"),), y_label="Gözlem sayısı",
                  curves=(("exponential", mu, mu, "Beklenen sayı: Üstel(μ)"),)),
    )


def _wait_dgp(parameters: Parameters) -> tuple[str, ...]:
    mu, t, n = _wait_settings(parameters)
    return (
        rf"T \sim \operatorname{{Exp}}(\mu), \quad f(x) = \frac{{1}}{{\mu}} e^{{-x/\mu}},\ x \ge 0, \qquad "
        rf"\mu = {_tex(mu)} \text{{ dakika}}, \qquad n = {n}",
        rf"P(T > t) = e^{{-t/\mu}} = e^{{-{t}/{_tex(mu)}}} = {number(math.exp(-t / mu), 4)}, \qquad "
        rf"\lambda = \frac{{60}}{{\mu}} = {_tex(60 / mu, 2)} \text{{ geliş/saat}}",
    )


def _wait_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    mu, _, n = _wait_settings(parameters)
    s = state.scalars
    return (
        SimMetric("λ = 60/μ", f"{_short(s['lam'], 2)} geliş/saat",
                  "Aynı süreçte bir saatteki geliş sayısı Poisson dağılımlıdır, (11.11)."),
        SimMetric("P(T > t) = e^(−t/μ)", plain(s["P_uzun"], 4), "Üstel sağ kuyruk, (11.9)."),
        SimMetric("Simülasyondaki pay", plain(s["pay"], 3), f"{n} bekleme içinde t dakikadan uzun olanların oranı."),
        SimMetric("Ortalama ve std. sapma", f"{plain(s['ortalama'], 2)} ve {plain(s['s'], 2)}",
                  f"Üstel dağılımda ikisi de μ = {_short(mu)}, (11.10)."),
    )


NOTE_EXAMPLES = {
    (5, 10): "Bu ayar §11.11'deki örnektir: saatte 12 müşteri, ortalama 5 dakika ve P(T > 10) = e^(−2) ≈ 0,1353.",
    (7.5, 10): "Bu ayar §11.13'teki bekleme sorusudur: saatte 8 müşteri, ortalama 7,5 dakika ve P(T > 10) ≈ 0,2636.",
    (15, 18): "Bu ayar Şekil 11.10'daki yükleme süresidir: P(T > 18) = 1 − 0,6988 = 0,3012.",
}


def _wait_takeaway(state: LabState, parameters: Parameters) -> str:
    mu, t, _ = _wait_settings(parameters)
    s = state.scalars
    text = (
        f"Ortalama süre μ = {_short(mu)} dakika ise gelişler saatte ortalama λ = 60/μ = {_short(s['lam'], 2)} kez olur "
        "(11.11): saatteki geliş sayısı Poisson, iki geliş arasındaki süre üstel dağılımlıdır (§11.11). Beklemenin "
        f"t = {t} dakikayı aşma olasılığı e^(−t/μ) = {plain(s['P_uzun'], 4)}; simülasyondaki pay "
        f"{plain(s['pay'], 3)}. Beklemelerin ortalaması {plain(s['ortalama'], 2)}, standart sapması "
        f"{plain(s['s'], 2)}: üstel dağılımda ikisi de μ'dür (11.10). Histogram sağa çarpıktır; kısa beklemeler sık, "
        "uzun beklemeler seyrektir. "
    )
    text += NOTE_EXAMPLES.get((mu, t), "μ = 5 ve t = 10 §11.11'deki örnektir; μ = 7,5 ile §11.13'teki bekleme sorusu, "
                                       "μ = 15 ve t = 18 ile Şekil 11.10 elde edilir.")
    return text


EXPONENTIAL_WAIT = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Üstel bekleme süresi: ortalama süre, kuyruk olasılığı ve geliş hızı",
    question="Müşteriler arasındaki bekleme süresi üstel dağılıyorsa bekleme t dakikayı hangi olasılıkla aşar; "
             "ortalama süre uzadıkça saatteki geliş sayısı ve beklemelerin yayılımı nasıl değişir?",
    note=NoteRef("11.11", objects=("(11.9)", "(11.10)", "(11.11)")),
    parameters=(
        SimParameter("mu", "Ortalama bekleme süresi μ (dakika)", 1, 30, 5, 0.5,
                     "§11.11: saatte 12 müşteri, μ = 60/12 = 5 dakika.", decimals=1),
        SimParameter("t", "Eşik t (dakika)", 1, 60, 10, 1, "P(T > t): bekleme t dakikadan uzun.", integer=True,
                     decimals=0),
        SimParameter("n", "Gözlenen bekleme sayısı n", 100, 20000, 10000, 100,
                     "Üstel dağılımdan bağımsız çekilişler; n küçüldükçe pay daha çok dalgalanır.", integer=True,
                     decimals=0),
    ),
    dgp=_wait_dgp,
    dgp_note=(
        "Bekleme süreleri ortalaması μ olan üstel dağılımdan birbirinden bağımsız çekilir; tohum 217'dir. Üstel "
        "dağılımda standart sapma da μ'dür. Yatay eksen en az 6μ'ye uzanır; bu sınırı aşan beklemelerin olasılığı "
        "e⁻⁶ ≈ 0,0025'tir."
    ),
    look_at=(
        "**Yoğunluk eğrisi** — boyalı sağ kuyruk P(T > t); μ büyüdükçe eğri basıklaşır ve sağa uzar.",
        "**Histogram ve metrikler** — t'den uzun beklemelerin payı ile e^(−t/μ); ortalama ile standart sapmanın "
        "ikisinin de μ çevresinde olması.",
    ),
    build=_build_wait,
    metrics=_wait_metrics,
    takeaway=_wait_takeaway,
    labels=(("sure", "Bekleme süresi (dakika)"),),
)


KONU11_EXPERIMENTS = (NORMAL_AREA, BINOMIAL_NORMAL, EXPONENTIAL_WAIT)
