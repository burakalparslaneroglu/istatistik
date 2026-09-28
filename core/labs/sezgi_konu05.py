"""Konu 5 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Tek uç gözlem: hangi yayılım ölçüsü etkilenir?        (Notlar §5.2, §5.9)
Deney 2  Chebyshev ve ampirik kural: biçim önemli mi?            (Notlar §5.6, §5.8)
Deney 3  Korelasyon eğrisel ilişkiyi görür mü?                   (Notlar §5.12)
"""

from __future__ import annotations

import math

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, percent, plain
from core.labs.spec import (
    BoxPlot,
    Derive,
    Draw,
    Histogram,
    JoinColumns,
    NewSample,
    NoteRef,
    PairStatistic,
    Percentile,
    Scalar,
    ScalarTable,
    ScatterPlot,
    Statistic,
)

SEED = 217
TOPIC = "konu05"


# --- Deney 1: tek uç gözlem ------------------------------------------------------------------

CENTER, SPREAD = 25, 3
"""Olağan gözlemler N(25, 3²): notlardaki gelir verisinin 20–30 aralığına benzer."""
MEASURES = ("Değişim aralığı", "Standart sapma s", "IQR")
NAMES = ("aralik", "s", "iqr")


def _spread(frame: str, variable: str, suffix: str, label: str) -> tuple:
    """Bir değişkenin değişim aralığı, standart sapması ve IQR'si (çeyrekler ders kuralıyla)."""

    return (
        Statistic(frame, variable, "max", f"en_buyuk_{suffix}", f"{label}: en büyük", decimals=2),
        Statistic(frame, variable, "min", f"en_kucuk_{suffix}", f"{label}: en küçük", decimals=2),
        Scalar(f"aralik_{suffix}", E.sub(E.ref(f"en_buyuk_{suffix}"), E.ref(f"en_kucuk_{suffix}")),
               f"{label}: değişim aralığı", decimals=2),
        Statistic(frame, variable, "std", f"s_{suffix}", f"{label}: standart sapma", decimals=2),
        Percentile(frame, variable, 25, f"q1_{suffix}", f"{label}: Q₁"),
        Percentile(frame, variable, 75, f"q3_{suffix}", f"{label}: Q₃"),
        Scalar(f"iqr_{suffix}", E.sub(E.ref(f"q3_{suffix}"), E.ref(f"q1_{suffix}")), f"{label}: IQR", decimals=2),
    )


def _rows(*names: str) -> tuple:
    return tuple(zip(MEASURES, (E.ref(name) for name in names)))


def _build_outlier(parameters: Parameters) -> tuple:
    n, delta = int(parameters["n"]), int(parameters["delta"])
    return (
        NewSample("veri", n, SEED),
        Draw("veri", "z", "normal", 0, 1, "Standart normal çekiliş"),
        Derive("veri", "x", E.add(CENTER, E.mul(SPREAD, E.var("z"))), "Uç değersiz veri"),
        Derive("veri", "son", E.compare("eq", E.seq(E.var("z")), n), "Son gözlem mi? (1: evet)"),
        Derive("veri", "x_uc", E.add(E.var("x"), E.mul(delta, E.var("son"))), "Son gözleme Δ eklenmiş veri"),
        *_spread("veri", "x", "ozgun", "Özgün veri"),
        *_spread("veri", "x_uc", "uc", "Uç değerli veri"),
        ScalarTable(_rows("aralik_ozgun", "s_ozgun", "iqr_ozgun"), "ozgun"),
        ScalarTable(_rows("aralik_uc", "s_uc", "iqr_uc"), "uclu"),
        ScalarTable(
            tuple(zip(MEASURES, (E.sub(E.ref(f"{name}_uc"), E.ref(f"{name}_ozgun")) for name in NAMES))),
            "fark",
        ),
        JoinColumns("olculer", (("Özgün veri", "ozgun", "deger"), ("Son gözlem + Δ", "uclu", "deger"),
                                ("Değişim", "fark", "deger")), decimals=2),
        BoxPlot((("veri", "x", "Özgün veri"), ("veri", "x_uc", "Son gözlem + Δ")), "Değer", "Veri seti",
                "Aynı veri: son gözleme Δ eklenmeden ve eklendikten sonra"),
    )


def _outlier_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, delta = int(parameters["n"]), int(parameters["delta"])
    return (
        rf"X_i = {CENTER} + {SPREAD} Z_i, \qquad Z_i \sim N(0,\ 1), \qquad i = 1, \dots, n = {n}",
        rf"\text{{Uç değerli veri: }} X_n^{{*}} = X_n + \Delta = X_n + {delta}, \qquad "
        rf"X_i^{{*}} = X_i \ (i < n)",
    )


def _outlier_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    return (
        SimMetric("Değişim aralığı", f"{plain(s['aralik_ozgun'], 2)} → {plain(s['aralik_uc'], 2)}",
                  "Özgün veri → son gözleme Δ eklenmiş veri."),
        SimMetric("Standart sapma s", f"{plain(s['s_ozgun'], 2)} → {plain(s['s_uc'], 2)}",
                  "Bütün gözlemlerin ortalamadan kareli sapmalarına dayanır."),
        SimMetric("IQR", f"{plain(s['iqr_ozgun'], 2)} → {plain(s['iqr_uc'], 2)}",
                  "Q₃ − Q₁: orta %50'nin genişliği (ders kuralıyla çeyrekler)."),
    )


def _outlier_takeaway(state: LabState, parameters: Parameters) -> str:
    delta = int(parameters["delta"])
    s = state.scalars
    if delta == 0:
        return "Δ = 0: iki veri seti aynıdır. Δ'yı artırarak tek bir uç gözlemin etkisini izleyin (§5.2, §5.9)."
    ratio = s["s_uc"] / s["s_ozgun"]
    growth = s["aralik_uc"] - s["aralik_ozgun"]
    ranged = (f"Değişim aralığı {plain(growth, 2)} birim arttı" if growth > 0.005 else
              "Değişim aralığı değişmedi (son gözlem en büyük değeri aşmadı)")
    if ratio >= 1.005:
        spread = f"standart sapma {plain(ratio, 2)} katına çıktı"
    elif ratio <= 0.995:
        spread = f"standart sapma {plain(ratio, 2)} katına indi (son gözlem ortalamaya yaklaştı)"
    else:
        spread = "standart sapma neredeyse değişmedi"
    outside = s["en_buyuk_uc"] > s["q3_uc"] + 1.5 * s["iqr_uc"]
    box = ("Kutu grafiğinde uç gözlem üst sınırın dışında ayrı bir nokta olarak görünür" if outside else
           "Bu Δ ile son gözlem henüz üst sınırın (Q₃ + 1,5·IQR) içinde kalıyor; Δ'yı artırın")
    return (
        f"Yalnız bir gözlem değişti. {ranged}, {spread}; IQR'deki değişim "
        f"ise yalnız {plain(abs(s['iqr_uc'] - s['iqr_ozgun']), 2)} birim. Değişim aralığı iki uç gözleme, standart "
        "sapma bütün kareli sapmalara dayanır; IQR orta %50'yi kullandığı için uç değere dayanıklıdır. "
        f"{box} (§5.2, §5.9, §5.10)."
    )


OUTLIER_SPREAD = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Tek uç gözlem: hangi yayılım ölçüsü etkilenir?",
    question="Bir veri setinde yalnız tek bir gözlem büyürse değişim aralığı, standart sapma ve IQR ne kadar değişir?",
    note=NoteRef("5.9", objects=("Şekil 5.10",)),
    parameters=(
        SimParameter("delta", "Son gözleme eklenen Δ", 0, 80, 40, 5,
                     "Notlardaki gelir verisinde en büyük değer 65, diğerleri 20–30 arasındadır.", integer=True,
                     decimals=0),
        SimParameter("n", "Gözlem sayısı n", 10, 200, 30, 5, "Veri setindeki gözlem sayısı.", integer=True,
                     decimals=0),
    ),
    dgp=_outlier_dgp,
    dgp_note="İki veri seti aynı çekilişten gelir; yalnız son gözlem farklıdır. Böylece farkın tek nedeni uç değerdir.",
    look_at=(
        "**Kutu grafikleri** — kutu (orta %50) neredeyse aynı kalır; uç gözlem sınırların dışında ayrı bir noktadır.",
        "**Ölçüler tablosu** — değişim aralığı, standart sapma ve IQR'nin ne kadar değiştiği.",
    ),
    build=_build_outlier,
    metrics=_outlier_metrics,
    takeaway=_outlier_takeaway,
    tables=(("olculer", "Yayılım ölçüleri"),),
    labels=(("x", "Değer"), ("x_uc", "Değer (son gözlem + Δ)")),
)


# --- Deney 2: Chebyshev ve ampirik kural ------------------------------------------------------

K_VALUES = (1, 2, 3)
EMPIRICAL = (0.68, 0.95, 0.997)


def _histogram_range(alpha: float) -> tuple[int, int]:
    """x̄ ± 2s çizgilerini ve verinin hemen hepsini gösteren yatay eksen (Gamma(α, 1): μ = α, σ = √α)."""

    return math.floor(alpha - 4 * math.sqrt(alpha)), math.ceil(alpha + 6 * math.sqrt(alpha))


def _build_rules(parameters: Parameters) -> tuple:
    n, alpha = int(parameters["n"]), float(parameters["alpha"])
    lower, upper = _histogram_range(alpha)
    inside = []
    for k in K_VALUES:
        inside += [
            Derive("veri", f"ic_{k}", E.compare("le", E.absolute(E.var("z")), k), f"x̄ ± {k}s içinde mi? (1: evet)"),
            Statistic("veri", f"ic_{k}", "mean", f"oran_{k}", f"x̄ ± {k}s içindeki gözlemlerin oranı", decimals=3),
        ]
    labels = tuple(f"k = {k}" for k in K_VALUES)
    return (
        NewSample("veri", n, SEED),
        Draw("veri", "x", "gamma", alpha, 1, f"Gamma(α = {plain(alpha, 1)}, ölçek = 1) çekilişi"),
        Statistic("veri", "x", "mean", "ortalama", "Ortalama x̄", decimals=3),
        Statistic("veri", "x", "std", "s", "Standart sapma s", decimals=3),
        Derive("veri", "z", E.div(E.sub(E.var("x"), E.ref("ortalama")), E.ref("s")), "z-skoru (x − x̄)/s"),
        *inside,
        Scalar("alt_2s", E.sub(E.ref("ortalama"), E.mul(2, E.ref("s"))), "x̄ − 2s", decimals=3),
        Scalar("ust_2s", E.add(E.ref("ortalama"), E.mul(2, E.ref("s"))), "x̄ + 2s", decimals=3),
        ScalarTable(tuple(zip(labels, (E.ref(f"oran_{k}") for k in K_VALUES))), "gozlenen", decimals=3),
        ScalarTable(tuple(zip(labels, (E.sub(1, E.div(1, k * k)) for k in K_VALUES))), "chebyshev", decimals=3),
        ScalarTable(tuple(zip(labels, (E.const(value) for value in EMPIRICAL))), "ampirik", decimals=3),
        JoinColumns("kurallar", (("Gözlenen oran", "gozlenen", "deger"), ("Chebyshev (en az)", "chebyshev", "deger"),
                                 ("Ampirik kural (yaklaşık)", "ampirik", "deger")), decimals=3),
        Histogram("veri", (("x", "Gözlemler"),), 40, lower, upper, "Verinin histogramı ve x̄ ± 2s aralığı", "Değer",
                  references=(("alt_2s", "x̄ − 2s"), ("ust_2s", "x̄ + 2s")), y_label="Gözlem sayısı"),
    )


def _rules_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, alpha = int(parameters["n"]), float(parameters["alpha"])
    skew = 2 / math.sqrt(alpha)
    return (
        rf"X \sim \text{{Gamma}}(\alpha = {number(alpha, 1)},\ \text{{ölçek}} = 1), \qquad "
        rf"\mu = \alpha, \qquad \sigma = \sqrt{{\alpha}}, \qquad n = {n}",
        rf"\text{{Çarpıklık}} = 2/\sqrt{{\alpha}} = {number(skew, 2)} \qquad "
        r"(\alpha \text{ büyüdükçe dağılım çan biçimine yaklaşır})",
    )


def _rules_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    helps = {
        1: "Ampirik kural yaklaşık %68 der; Chebyshev k = 1'de bilgi vermez (alt sınır 0).",
        2: "Chebyshev: en az %75. Ampirik kural: yaklaşık %95.",
        3: "Chebyshev: en az %88,9. Ampirik kural: yaklaşık %99,7.",
    }
    return tuple(SimMetric(f"x̄ ± {k}s içinde", percent(100 * s[f"oran_{k}"], 1), helps[k]) for k in K_VALUES)


def _rules_takeaway(state: LabState, parameters: Parameters) -> str:
    s = state.scalars
    alpha = float(parameters["alpha"])
    gaps = [abs(s[f"oran_{k}"] - rule) for k, rule in zip(K_VALUES, EMPIRICAL)]
    shape = ("belirgin biçimde sağa çarpık" if alpha < 4 else
             "hafif sağa çarpık" if alpha < 16 else "çan biçimine yakın")
    text = (
        f"α = {plain(alpha, 1)}: dağılım {shape}. Gözlenen oranlar k = 2 ve k = 3 için Chebyshev'in alt sınırlarının "
        f"(%75 ve %88,9) üzerindedir; bu her veri setinde böyledir. Ampirik kuraldan en büyük sapma "
        f"{plain(100 * max(gaps), 1)} yüzde puandır. "
    )
    if alpha < 4:
        return text + ("Çarpık veride ampirik kuralın oranları tutmayabilir (ör. x̄ ± 1s içinde %68'den çok daha "
                       "fazla gözlem). x̄ − 2s sıfırın altına iner: simetrik aralık çarpık veriyi iyi betimlemez. "
                       "α'yı büyüterek çan biçimine yaklaşın (§5.6, §5.8).")
    return text + ("Dağılım çan biçimine yaklaştıkça gözlenen oranlar %68, %95 ve %99,7'ye yaklaşır. Chebyshev "
                   "her biçim için geçerli ama gevşek bir alt sınırdır (§5.8).")


EMPIRICAL_RULE = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Chebyshev ve ampirik kural: biçim önemli mi?",
    question="Ortalamanın k standart sapma çevresinde gözlemlerin ne kadarı bulunur ve bu oran dağılımın biçimine "
             "bağlı mıdır?",
    note=NoteRef("5.8", objects=("Şekil 5.9",)),
    parameters=(
        SimParameter("alpha", "Biçim parametresi α", 0.5, 30.0, 1.0, 0.5,
                     "Küçük α: güçlü sağa çarpıklık (α = 1 üstel dağılımdır). Büyük α: çan biçimine yakın.",
                     decimals=1),
        SimParameter("n", "Gözlem sayısı n", 100, 5000, 1000, 100, "Veri setindeki gözlem sayısı.", integer=True,
                     decimals=0),
    ),
    dgp=_rules_dgp,
    dgp_note=(
        "Gamma dağılımı pozitif değerler alır; biçim parametresi α küçükken uzun sağ kuyruklu, büyükken yaklaşık "
        "simetriktir. Oranlar örneklemin kendi x̄ ve s değerleriyle hesaplanır."
    ),
    look_at=(
        "**Histogram** — dağılımın biçimi ve x̄ ± 2s aralığı.",
        "**Kurallar tablosu** — gözlenen oranlar, Chebyshev'in alt sınırları ve ampirik kuralın oranları.",
    ),
    build=_build_rules,
    metrics=_rules_metrics,
    takeaway=_rules_takeaway,
    tables=(("kurallar", "x̄ ± ks içindeki gözlemlerin oranı"),),
    labels=(("x", "Değer"),),
)


# --- Deney 3: korelasyon ve eğrisel ilişki ----------------------------------------------------

X_LIMIT = 3


def _true_correlation(c: float) -> float:
    """X ~ U(−3, 3), ε ~ N(0, 1), Y = aX + cX² + ε, a = 2(1 − c) için anakütle korelasyonu.

    Var(X) = 3, Cov(X, X²) = E[X³] = 0, Var(X²) = 81/5 − 9 = 7,2. Buradan Cov(X, Y) = 3a ve
    Var(Y) = 3a² + 7,2c² + 1; ρ = 3a / √(3(3a² + 7,2c² + 1)).
    """

    a = 2 * (1 - c)
    return 3 * a / math.sqrt(3 * (3 * a * a + 7.2 * c * c + 1))


def _build_curvature(parameters: Parameters) -> tuple:
    n, c = int(parameters["n"]), float(parameters["c"])
    a = round(2 * (1 - c), 10)
    return (
        NewSample("veri", n, SEED),
        Draw("veri", "x", "uniform", -X_LIMIT, X_LIMIT, "X ~ Tek-düze(−3, 3)"),
        Draw("veri", "hata", "normal", 0, 1, "Hata terimi ε ~ N(0, 1)"),
        Derive("veri", "y", E.add(E.add(E.mul(a, E.var("x")), E.mul(c, E.power(E.var("x"), 2))), E.var("hata")),
               "Y = aX + cX² + ε"),
        PairStatistic("veri", "x", "y", "corr", "r", "Örneklem korelasyonu r", decimals=3),
        Scalar("rho", E.const(round(_true_correlation(c), 10)), "DGP'deki (anakütle) korelasyon ρ", decimals=3),
        ScatterPlot("veri", "x", "y", "X", "Y", "Serpilme diyagramı"),
    )


def _curvature_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, c = int(parameters["n"]), float(parameters["c"])
    a = 2 * (1 - c)
    return (
        rf"Y = aX + cX^2 + \varepsilon, \qquad a = 2(1 - c) = {number(a, 1)}, \qquad c = {number(c, 1)}",
        rf"X \sim \text{{Tek-düze}}(-3,\ 3), \qquad \varepsilon \sim N(0,\ 1), \qquad n = {n}, \qquad "
        rf"\rho = \frac{{3a}}{{\sqrt{{3(3a^2 + 7{{,}}2c^2 + 1)}}}} = {number(_true_correlation(c), 3)}",
    )


def _curvature_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    c = float(parameters["c"])
    return (
        SimMetric("Örneklem korelasyonu r", plain(s["r"], 3), "Pearson korelasyonu: doğrusal ilişkinin ölçüsü."),
        SimMetric("Anakütle korelasyonu ρ", plain(s["rho"], 3), "DGP'den hesaplanan gerçek korelasyon."),
        SimMetric("Doğrusal bileşen a", plain(2 * (1 - c), 1), "Y'nin X'e doğrusal bağlılığı."),
        SimMetric("Eğrisel bileşen c", plain(c, 1), "Y'nin X²'ye bağlılığı."),
    )


def _curvature_takeaway(state: LabState, parameters: Parameters) -> str:
    c = float(parameters["c"])
    r = state.scalars["r"]
    if c >= 0.9:
        return (
            f"c = {plain(c, 1)}: Y, X'e çok güçlü biçimde bağlıdır (U biçimli ilişki), ama r = {plain(r, 3)} sıfıra "
            "yakındır. X'in negatif ve pozitif değerlerinde Y aynı yönde artar; doğrusal eğilimler birbirini götürür. "
            "r ≈ 0 \"ilişki yok\" demek değildir; korelasyon yalnız doğrusal ilişkiyi ölçer. Serpilme diyagramına "
            "bakmadan korelasyon yorumlanmaz (§5.12, Şekil 5.16)."
        )
    if c <= 0.1:
        return (
            f"c = {plain(c, 1)}: ilişki neredeyse tamamen doğrusaldır ve r = {plain(r, 3)} yüksektir. c'yi artırarak "
            "ilişkiyi eğriselleştirin: ilişki güçlü kalsa da r düşer (§5.12)."
        )
    return (
        f"c = {plain(c, 1)}: ilişkinin bir kısmı doğrusal, bir kısmı eğriseldir; r = {plain(r, 3)}. Korelasyon "
        "yalnız doğrusal kısmı yakalar: c büyüdükçe Y ile X arasındaki bağ güçlü kalırken r sıfıra iner (§5.12)."
    )


CURVATURE = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Korelasyon eğrisel ilişkiyi görür mü?",
    question="İki değişken arasında güçlü ama eğrisel bir ilişki varsa korelasyon katsayısı bunu gösterir mi?",
    note=NoteRef("5.12", objects=("Şekil 5.16",)),
    parameters=(
        SimParameter("c", "Eğrisel bileşen c", 0.0, 1.0, 0.5, 0.1,
                     "c = 0: tamamen doğrusal (Y = 2X + ε). c = 1: tamamen eğrisel (Y = X² + ε).", decimals=1),
        SimParameter("n", "Gözlem sayısı n", 20, 500, 100, 10, "Veri setindeki gözlem sayısı.", integer=True,
                     decimals=0),
    ),
    dgp=_curvature_dgp,
    dgp_note=(
        "Doğrusal ve eğrisel bileşenin ağırlığı tek parametreyle (c) değişir; hata terimi her durumda aynıdır. "
        "X sıfır çevresinde simetrik olduğu için X² ile X'in kovaryansı sıfırdır."
    ),
    look_at=(
        "**Serpilme diyagramı** — noktaların bir doğru mu, bir eğri mi çevresinde toplandığı.",
        "**r ve ρ** — ilişki güçlü kalırken korelasyonun nasıl değiştiği.",
    ),
    build=_build_curvature,
    metrics=_curvature_metrics,
    takeaway=_curvature_takeaway,
    labels=(("x", "X"), ("y", "Y")),
)


KONU05_EXPERIMENTS = (OUTLIER_SPREAD, EMPIRICAL_RULE, CURVATURE)
