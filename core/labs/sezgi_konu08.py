"""Konu 8 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Uzun dönem ortalaması: çekilişlerin ortalaması E(X)'e yaklaşır mı?  (Notlar §8.8, Şekil 8.8)
Deney 2  Aynı beklenen değer, farklı yayılım                               (Notlar §8.10, Tablo 8.5)
Deney 3  Ortak dağılım ve kovaryans: dönüşüm olasılığı                    (Notlar §8.11–8.13)

Deney 1'in varsayılan ayarları (Tablo 8.1'in dağılımı, n = 100, tohum 217) notlardaki Şekil 8.8'i birebir üretir.
"""

from __future__ import annotations

import math

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, plain
from core.labs.spec import (
    CrossTab,
    Derive,
    Draw,
    DrawDiscrete,
    Event,
    FrequencyTable,
    HeatMap,
    Histogram,
    LineChart,
    NewSample,
    NoteRef,
    PairStatistic,
    Scalar,
    ScalarTable,
    Statistic,
)

SEED = 217
TOPIC = "konu08"

ADDON_VALUES = (0, 1, 2, 3, 4)
ADDON_PROBABILITIES = (0.10, 0.30, 0.35, 0.20, 0.05)
"""Tablo 8.1: bir işlemde satın alınan ek ürün sayısının dağılımı; E(X) = 1,80."""
ADDON_MEAN = 1.80


# --- Deney 1: uzun dönem ortalaması ------------------------------------------------------------

def _build_long_run(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    return (
        NewSample("cekilis", n, SEED),
        DrawDiscrete("cekilis", "x", ADDON_VALUES, ADDON_PROBABILITIES,
                     "X: Tablo 8.1'deki dağılımdan bağımsız çekiliş"),
        Derive("cekilis", "k", E.seq(E.var("x")), "Çekiliş sırası k = 1, 2, …, n"),
        Derive("cekilis", "ortalama", E.cummean(E.var("x")), "Birikimli ortalama: ilk k çekilişin ortalaması"),
        Statistic("cekilis", "x", "sum", "toplam", "Çekilişlerin toplamı", decimals=0),
        Statistic("cekilis", "x", "mean", "son_ortalama", "n çekilişin ortalaması", decimals=4),
        Scalar("E_X", E.const(ADDON_MEAN), "Beklenen değer E(X) = Σ x f(x)", decimals=2),
        LineChart("cekilis", "k", "ortalama", "Çekiliş sayısı k", "O ana kadarki ortalama",
                  "Birikimli ortalama ve beklenen değer", references=(("E_X", "E(X) = 1,80"),), markers=False),
        FrequencyTable("cekilis", "x", "frekans", ADDON_VALUES),
    )


def _long_run_dgp(parameters: Parameters) -> tuple[str, ...]:
    n = int(parameters["n"])
    return (
        rf"P(X = x) = f(x): \quad f(0) = 0{{,}}10,\ f(1) = 0{{,}}30,\ f(2) = 0{{,}}35,\ f(3) = 0{{,}}20,\ "
        rf"f(4) = 0{{,}}05, \qquad n = {n}",
        r"\bar{x}_k = \frac{x_1 + x_2 + \cdots + x_k}{k}, \qquad E(X) = \sum_x x f(x) = 1{,}80",
    )


def _mean_at(state: LabState, k: int) -> float | None:
    means = state.frames["cekilis"]["ortalama"]
    return float(means.iloc[k - 1]) if k <= len(means) else None


def _long_run_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    n = int(parameters["n"])
    final = state.scalars["son_ortalama"]
    items = [SimMetric("İlk çekiliş", plain(float(state.frames["cekilis"]["x"].iloc[0]), 0), "x₁: ilk ek ürün sayısı.")]
    early = _mean_at(state, 10)
    if early is not None and n > 10:
        items.append(SimMetric("İlk 10 çekilişin ortalaması", plain(early, 3), "E(X) = 1,80 ile karşılaştırın."))
    items.append(SimMetric("Son ortalama", plain(final, 3),
                           f"Toplam {int(state.scalars['toplam'])}; çekiliş sayısı n = {n}."))
    items.append(SimMetric("|x̄ − E(X)|", plain(abs(final - ADDON_MEAN), 3),
                           "Son ortalamanın beklenen değerden uzaklığı."))
    return tuple(items)


def _long_run_takeaway(state: LabState, parameters: Parameters) -> str:
    n = int(parameters["n"])
    final = state.scalars["son_ortalama"]
    text = (
        f"Tek tek çekilişler 0 ile 4 arasında değişir, ama birikimli ortalama çekiliş arttıkça 1,80 çevresinde "
        f"daha dar bir bantta kalır; n = {n} için son ortalama {plain(final, 3)}. Beklenen değer tek bir işlemin "
        "tahmini değil, çok sayıda tekrarın ortalamasının istikrar kazandığı düzeydir (§8.8). "
    )
    if n == 100:
        text += ("Bu ayarlar notlardaki Şekil 8.8'in veri üretim sürecidir: ilk çekiliş 3, 100 çekilişin toplamı "
                 "177, son ortalama 1,77.")
    else:
        text += "Varsayılan ayar (n = 100) notlardaki Şekil 8.8'i üretir."
    return text


LONG_RUN = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Uzun dönem ortalaması: çekilişlerin ortalaması E(X)'e yaklaşır mı?",
    question="Ek ürün sayısı dağılımından tekrar tekrar çekiliş yapıldığında, gerçekleşen değerlerin ortalaması "
             "beklenen değerle nasıl ilişkilidir?",
    note=NoteRef("8.8", objects=("Şekil 8.8",)),
    parameters=(
        SimParameter("n", "Çekiliş sayısı n", 10, 5000, 100, 10, "Notlardaki Şekil 8.8'de n = 100.", integer=True,
                     decimals=0),
    ),
    dgp=_long_run_dgp,
    dgp_note=(
        "Her çekiliş Tablo 8.1'deki dağılımdan, öncekilerden bağımsız olarak yapılır: u ~ Tek-düze(0, 1) çekilir ve "
        "X, birikimli olasılığı F(x) u'yu ilk aşan değerdir. Tohum 217'dir; n = 100 notlardaki Şekil 8.8'i birebir "
        "üretir."
    ),
    look_at=(
        "**Çizgi grafiği** — birikimli ortalamanın ilk çekilişlerdeki dalgalanması ve E(X) = 1,80 çevresine "
        "yerleşmesi.",
        "**Frekans tablosu** — çekilişlerde her değerin göreli frekansı; Tablo 8.1'deki f(x) ile karşılaştırın.",
    ),
    build=_build_long_run,
    metrics=_long_run_metrics,
    takeaway=_long_run_takeaway,
    tables=(("frekans", "Çekilişlerin frekans dağılımı"),),
    labels=(("x", "Ek ürün sayısı x"), ("k", "Çekiliş sayısı k"), ("ortalama", "O ana kadarki ortalama")),
)


# --- Deney 2: aynı beklenen değer, farklı yayılım ------------------------------------------------

CENTRE = 2.0
SPREAD_PROBABILITIES = (0.25, 0.50, 0.25)


def _whole(value: float) -> float | int:
    """Tam sayı değerleri tam sayı olarak (0, 2, 4); tablo ve kodda 0.0 yerine 0 yazılır."""

    return int(value) if float(value).is_integer() else value


def _spread_values(parameters: Parameters) -> tuple[float | int, ...]:
    d = round(float(parameters["d"]), 1)
    return tuple(_whole(round(value, 1)) for value in (CENTRE - d, CENTRE, CENTRE + d))


def _tex(value: float) -> str:
    return number(value, 0 if float(value).is_integer() else 1)


def _build_spread(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    d = round(float(parameters["d"]), 1)
    values = _spread_values(parameters)
    return (
        NewSample("cekilis", n, SEED),
        DrawDiscrete("cekilis", "x", values, SPREAD_PROBABILITIES, "X: 2 − d, 2, 2 + d değerleri 0,25, 0,50, 0,25"),
        Statistic("cekilis", "x", "mean", "ortalama", "Çekilişlerin ortalaması", decimals=3),
        Statistic("cekilis", "x", "var", "s2", "Çekilişlerin varyansı s²", decimals=3),
        Statistic("cekilis", "x", "std", "s", "Çekilişlerin standart sapması s", decimals=3),
        Scalar("Var_X", E.const(round(d * d / 2, 10)), "Var(X) = d²/2 (DGP)", decimals=3),
        FrequencyTable("cekilis", "x", "frekans", values),
        Histogram("cekilis", (("x", "Çekilişler"),), 13, -1.25, 5.25, "Aynı merkez, seçilen yayılım",
                  "X'in değeri", references=((CENTRE, "E(X) = 2"),), y_label="Çekiliş sayısı"),
    )


def _spread_dgp(parameters: Parameters) -> tuple[str, ...]:
    n = int(parameters["n"])
    d = round(float(parameters["d"]), 1)
    low, _, high = _spread_values(parameters)
    return (
        rf"X \in \{{{_tex(low)},\ 2,\ {_tex(high)}\}}, \qquad f = 0{{,}}25,\ 0{{,}}50,\ 0{{,}}25, "
        rf"\qquad d = {_tex(d)}, \qquad n = {n}",
        rf"E(X) = 2, \qquad \operatorname{{Var}}(X) = 0{{,}}25\,d^2 + 0{{,}}25\,d^2 = \frac{{d^2}}{{2}} = "
        rf"{number(d * d / 2, 3)}",
    )


def _spread_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    d = round(float(parameters["d"]), 1)
    return (
        SimMetric("Çekilişlerin ortalaması", plain(s["ortalama"], 3), "DGP: E(X) = 2, her d için."),
        SimMetric("Çekilişlerin varyansı s²", plain(s["s2"], 3), f"DGP: Var(X) = d²/2 = {plain(d * d / 2, 3)}."),
        SimMetric("Standart sapma s", plain(s["s"], 3), f"DGP: σ = d/√2 = {plain(d / math.sqrt(2), 3)}."),
    )


def _spread_takeaway(state: LabState, parameters: Parameters) -> str:
    s = state.scalars
    d = round(float(parameters["d"]), 1)
    text = (
        f"Merkez her ayarda 2'dir (örneklemde {plain(s['ortalama'], 3)}), ama olası değerler merkezden "
        f"uzaklaştıkça varyans d²/2 ile büyür: d = {plain(d, 0 if d.is_integer() else 1)} için Var(X) = "
        f"{plain(d * d / 2, 3)}, örneklemde s² = {plain(s['s2'], 3)}. Beklenen değer yayılım hakkında bilgi "
        "vermez; aynı ortalama sonuç farklı belirsizlik taşıyabilir (§8.10). "
    )
    if d == 2:
        text += "d = 2 notlardaki A dağılımıdır (0, 2, 4; Var = 2); d = 1 ile B dağılımını (1, 2, 3; Var = 0,5) görün."
    elif d == 1:
        text += "d = 1 notlardaki B dağılımıdır (1, 2, 3; Var = 0,5); d = 2 ile A dağılımını (0, 2, 4; Var = 2) görün."
    return text


SPREAD = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Aynı beklenen değer, farklı yayılım",
    question="Beklenen değeri aynı kalan bir dağılımda olası değerler merkezden uzaklaşınca çekilişler ve varyans "
             "nasıl değişir?",
    note=NoteRef("8.10", objects=("Tablo 8.5", "Şekil 8.10")),
    parameters=(
        SimParameter("d", "Merkezden uzaklık d", 0.5, 3.0, 2.0, 0.5,
                     "d = 2: Tablo 8.5'teki A (0, 2, 4); d = 1: B (1, 2, 3).", decimals=1),
        SimParameter("n", "Çekiliş sayısı n", 50, 10000, 1000, 50, "Dağılımdan yapılan bağımsız çekiliş sayısı.",
                     integer=True, decimals=0),
    ),
    dgp=_spread_dgp,
    dgp_note=(
        "X, 2 − d, 2 ve 2 + d değerlerini 0,25, 0,50 ve 0,25 olasılıklarıyla alır; çekilişler birbirinden "
        "bağımsızdır. Olasılıklar simetrik olduğu için beklenen değer d'den bağımsız olarak 2'dir. Tohum 217'dir."
    ),
    look_at=(
        "**Histogram** — yatay eksen her ayarda aynıdır; d büyüdükçe iki uç sütun merkezden uzaklaşır.",
        "**Metrikler** — ortalama 2 çevresinde kalırken varyans d²/2 ile büyür.",
    ),
    build=_build_spread,
    metrics=_spread_metrics,
    takeaway=_spread_takeaway,
    tables=(("frekans", "Çekilişlerin frekans dağılımı"),),
    labels=(("x", "X'in değeri"),),
)


# --- Deney 3: ortak dağılım ve kovaryans ------------------------------------------------------------

REQUEST_VALUES = (0, 1, 2)
REQUEST_PROBABILITIES = (0.25, 0.35, 0.40)
"""Tablo 8.6'nın X marjinali: P(X = 0) = 0,25, P(X = 1) = 0,35, P(X = 2) = 0,40; E(X) = 1,15, Var(X) = 0,6275."""
REQUEST_MEAN, REQUEST_VARIANCE, REQUEST_SQUARE = 1.15, 0.6275, 1.95


def _joint_truth(q: float) -> dict[str, float]:
    """DGP'nin özellikleri: E(Y) = 1,15q, E(XY) = 1,95q, Cov = 0,6275q, Var(Y) = 1,15q(1 − q) + 0,6275q²."""

    var_y = REQUEST_MEAN * q * (1 - q) + REQUEST_VARIANCE * q * q
    covariance = REQUEST_VARIANCE * q
    return {
        "E_Y": REQUEST_MEAN * q,
        "E_XY": REQUEST_SQUARE * q,
        "Cov": covariance,
        "rho": covariance / math.sqrt(REQUEST_VARIANCE * var_y),
    }


def _build_joint(parameters: Parameters) -> tuple:
    n = int(parameters["n"])
    q = round(float(parameters["q"]), 2)
    truth = _joint_truth(q)
    converts = "her talep q olasılıkla satışa dönüşür"
    return (
        NewSample("gun", n, SEED),
        DrawDiscrete("gun", "x", REQUEST_VALUES, REQUEST_PROBABILITIES, "X: günlük teklif talebi sayısı"),
        Draw("gun", "u1", "uniform", 0, 1, "Birinci talep için u ~ Tek-düze(0, 1)"),
        Draw("gun", "u2", "uniform", 0, 1, "İkinci talep için u ~ Tek-düze(0, 1)"),
        Derive(
            "gun", "y",
            E.add(E.mul(E.compare("ge", E.var("x"), 1), E.compare("lt", E.var("u1"), q)),
                  E.mul(E.compare("ge", E.var("x"), 2), E.compare("lt", E.var("u2"), q))),
            f"Y: satışa dönüşen talep sayısı; {converts}",
        ),
        Derive("gun", "pay", E.div(1, n), "Her günün payı 1/n"),
        CrossTab("gun", "y", "x", "ortak", REQUEST_VALUES, REQUEST_VALUES, margins=True, decimals=3, weights="pay"),
        HeatMap("ortak", "X: teklif talebi sayısı", "Y: satış sayısı", "Örneklemde ortak göreli frekanslar",
                decimals=3),
        PairStatistic("gun", "x", "y", "cov", "s_xy", "Örneklem kovaryansı s_xy", decimals=4),
        PairStatistic("gun", "x", "y", "corr", "r_xy", "Örneklem korelasyonu r_xy", decimals=3),
        Event("gun", "X1", "x", (1,), "X = 1"),
        Event("gun", "Y1", "y", (1,), "Y = 1"),
        Derive("gun", "X1_ve_Y1", E.mul(E.var("X1"), E.var("Y1")), "X = 1 ve Y = 1"),
        Statistic("gun", "X1", "mean", "oran_X1", "X = 1 oranı", decimals=3),
        Statistic("gun", "Y1", "mean", "oran_Y1", "Y = 1 oranı", decimals=3),
        Statistic("gun", "X1_ve_Y1", "mean", "oran_X1_Y1", "X = 1, Y = 1 oranı", decimals=3),
        Scalar("carpim", E.mul(E.ref("oran_X1"), E.ref("oran_Y1")), "X = 1 oranı × Y = 1 oranı", decimals=3),
        ScalarTable(
            (
                ("Cov(X, Y) = 0,6275q: DGP", E.const(round(truth["Cov"], 10))),
                ("s_xy: örneklem", E.ref("s_xy")),
                ("ρ: DGP", E.const(round(truth["rho"], 10))),
                ("r_xy: örneklem", E.ref("r_xy")),
                ("X = 1, Y = 1 oranı", E.ref("oran_X1_Y1")),
                ("X = 1 oranı × Y = 1 oranı", E.ref("carpim")),
            ),
            "ozet",
            decimals=4,
        ),
    )


def _joint_dgp(parameters: Parameters) -> tuple[str, ...]:
    n = int(parameters["n"])
    q = round(float(parameters["q"]), 2)
    truth = _joint_truth(q)
    return (
        rf"P(X = 0) = 0{{,}}25,\ P(X = 1) = 0{{,}}35,\ P(X = 2) = 0{{,}}40, \qquad q = {number(q, 2)}, "
        rf"\qquad n = {n}",
        r"Y = \text{satışa dönüşen talep sayısı} \le X, \qquad f(x, y) = P(X = x)\,P(Y = y \mid X = x)",
        r"E(X) = 1{,}15, \qquad E(Y) = 1{,}15q, \qquad E(XY) = 1{,}95q",
        rf"\operatorname{{Cov}}(X, Y) = 1{{,}}95q - 1{{,}}15(1{{,}}15q) = 0{{,}}6275q = {number(truth['Cov'], 4)}",
    )


def _joint_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    s = state.scalars
    truth = _joint_truth(round(float(parameters["q"]), 2))
    return (
        SimMetric("Örneklem kovaryansı s_xy", plain(s["s_xy"], 4), f"DGP: Cov(X, Y) = {plain(truth['Cov'], 4)}."),
        SimMetric("Örneklem korelasyonu r_xy", plain(s["r_xy"], 3), f"DGP: ρ = {plain(truth['rho'], 3)}."),
        SimMetric("X = 1, Y = 1 oranı", plain(s["oran_X1_Y1"], 3),
                  f"Bağımsızlık altında beklenen: oranların çarpımı {plain(s['carpim'], 3)}."),
    )


def _joint_takeaway(state: LabState, parameters: Parameters) -> str:
    s = state.scalars
    q = round(float(parameters["q"]), 2)
    truth = _joint_truth(q)
    return (
        f"Daha çok talep olan günlerde daha çok satış görülür: kovaryans pozitiftir (örneklemde "
        f"{plain(s['s_xy'], 4)}, DGP'de 0,6275q = {plain(truth['Cov'], 4)}). q küçüldükçe satış talebi daha zayıf "
        f"izler ve birlikte hareket azalır. X ve Y hiçbir q için bağımsız değildir: satış talebi aşamaz, bu yüzden "
        "X = 0 sütununda Y ≥ 1 hücreleri sıfırdır, oysa marjinallerin çarpımı sıfırdan büyüktür. X = 1, Y = 1 "
        f"hücresinde de ortak oran ({plain(s['oran_X1_Y1'], 3)}) oranların çarpımından ({plain(s['carpim'], 3)}) "
        "ayrılır (§8.11–8.13)."
    )


JOINT = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Ortak dağılım ve kovaryans: dönüşüm olasılığı",
    question="Teklif talepleri satışa q olasılıkla dönüşüyorsa talep sayısı ile satış sayısının ortak dağılımı, "
             "kovaryansı ve bağımsızlığı nasıl görünür?",
    note=NoteRef("8.12"),
    parameters=(
        SimParameter("q", "Dönüşüm olasılığı q", 0.10, 1.00, 0.60, 0.05,
                     "Her talebin satışa dönüşme olasılığı; talepler birbirinden bağımsızdır.", decimals=2),
        SimParameter("n", "Gün sayısı n", 100, 20000, 2000, 100, "Gözlenen iş günü sayısı.", integer=True,
                     decimals=0),
    ),
    dgp=_joint_dgp,
    dgp_note=(
        "Günlük teklif talebi sayısı X, Tablo 8.6'nın X marjinaline sahiptir. Her talep diğerlerinden bağımsız olarak "
        "q olasılıkla satışa dönüşür; Y dönüşen talep sayısıdır ve X'i aşamaz. Ortak olasılık çarpma kuralıyla "
        "kurulur (§7.7). Tohum 217'dir."
    ),
    look_at=(
        "**Isı haritası** — örneklemdeki ortak göreli frekanslar; Y > X hücreleri boş kalır.",
        "**Özet tablosu** — örneklem kovaryansı ve korelasyonu ile DGP değerleri; X = 1, Y = 1 hücresinde çarpım "
        "kontrolü.",
    ),
    build=_build_joint,
    metrics=_joint_metrics,
    takeaway=_joint_takeaway,
    tables=(("ortak", "Ortak göreli frekanslar ve marjinaller"), ("ozet", "Birlikte hareket ve bağımsızlık")),
    labels=(("x", "X: teklif talebi"), ("y", "Y: satış")),
)


KONU08_EXPERIMENTS = (LONG_RUN, SPREAD, JOINT)
