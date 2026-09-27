"""Konu 9 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Binom dağılımı: n ve p dağılımın biçimini nasıl değiştirir?        (Notlar §9.3, Şekil 9.6)
Deney 2  Poisson: aralık uzadıkça λ ve dağılım nasıl değişir?               (Notlar §9.4, Şekil 9.7–9.8)
Deney 3  Yerine koymadan seçim: hipergeometrik binomdan ne zaman ayrılır?   (Notlar §9.5–9.6, Tablo 9.1)

Notlarda simülasyonla üretilmiş bir şekil yoktur. Varsayılan ayarlar notların örnekleridir: Deney 1'de
n = 10, p = 0,20 (Şekil 9.6'nın ilk paneli), Deney 2'de t = 15 dakika, λ = 3 (§9.4), Deney 3'te N = 40, r = 4,
n = 8 (Tablo 9.1). Olasılık sütunları bu ayarlarda notlardaki değerlerin aynısıdır.
"""

from __future__ import annotations

import math

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, plain
from core.labs.spec import (
    Derive,
    DrawCount,
    Event,
    FrequencyTable,
    GroupedBarChart,
    GroupSummary,
    JoinColumns,
    NewSample,
    NoteRef,
    Scalar,
    ScalarTable,
    Statistic,
    Support,
)

SEED = 217
TOPIC = "konu09"


def _short(value: float, decimals: int = 3) -> str:
    """Sondaki sıfırları atılmış düz metin sayı (1,6; 2; 0,591)."""

    text = f"{value:.{decimals}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",").replace("-", "−")


def _tex(value: float, decimals: int = 3) -> str:
    return _short(value, decimals).replace(",", "{,}").replace("−", "-")


def _largest_gap(table, first: str, second: str) -> float:
    return float((table[first] - table[second]).abs().max())


# --- Deney 1: binom dağılımının biçimi --------------------------------------------------------

def _binomial_settings(parameters: Parameters) -> tuple[int, float, int]:
    return int(parameters["n"]), round(float(parameters["p"]), 2), int(parameters["tekrar"])


def _build_binomial(parameters: Parameters) -> tuple:
    n, p, reps = _binomial_settings(parameters)
    values = tuple(range(n + 1))
    return (
        Support("dagilim", "x", 0, n, "Olası başarı sayıları: 0, 1, …, n"),
        Derive("dagilim", "f", E.dbinom(E.var("x"), n, p), "Binom olasılık fonksiyonu P(X = x), (9.2)"),
        GroupSummary("dagilim", "x", (("f", "f", "sum"),), "teorik", values, decimals=4),
        NewSample("deney", reps, SEED),
        DrawCount("deney", "x", "binomial", (n, p), "X = Y₁ + ⋯ + Yₙ: her tekrarda n Bernoulli denemesi"),
        FrequencyTable("deney", "x", "simulasyon", values),
        JoinColumns("karsilastirma", (("Binom olasılığı", "teorik", "f"),
                                      ("Simülasyon oranı", "simulasyon", "goreli")), decimals=4),
        GroupedBarChart("karsilastirma", "Başarı sayısı x", "Olasılık / göreli frekans",
                        "Binom olasılıkları ve tekrarlardaki oranlar", series="sutun", decimals=3, labels=False),
        Statistic("deney", "x", "mean", "ortalama", "Tekrarlardaki başarı sayısının ortalaması", decimals=3),
        Statistic("deney", "x", "var", "varyans", "Tekrarlardaki başarı sayısının varyansı s²", decimals=3),
        Scalar("E_X", E.mul(n, p), "E(X) = np, (9.4)", decimals=3),
        Scalar("Var_X", E.mul(E.mul(n, p), E.sub(1, p)), "Var(X) = np(1 − p), (9.5)", decimals=3),
    )


def _binomial_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, p, reps = _binomial_settings(parameters)
    return (
        rf"Y_i \sim \text{{Bernoulli}}(p) \text{{ bağımsız}}, \qquad X = Y_1 + \cdots + Y_n \sim "
        rf"\operatorname{{Bin}}(n, p), \qquad n = {n},\ p = {number(p, 2)}, \qquad {reps} \text{{ tekrar}}",
        rf"P(X = x) = \binom{{n}}{{x}} p^x (1 - p)^{{n - x}}, \qquad E(X) = np = {_tex(n * p)}, \qquad "
        rf"\operatorname{{Var}}(X) = np(1 - p) = {_tex(n * p * (1 - p), 4)}",
    )


def _binomial_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    n, p, _ = _binomial_settings(parameters)
    s = state.scalars
    return (
        SimMetric("Tekrarların ortalaması", plain(s["ortalama"], 3), f"E(X) = np = {_short(n * p)}."),
        SimMetric("Tekrarların varyansı s²", plain(s["varyans"], 3),
                  f"Var(X) = np(1 − p) = {_short(n * p * (1 - p), 4)}."),
        SimMetric("En büyük fark", plain(_largest_gap(state.tables["karsilastirma"], "Simülasyon oranı",
                                                      "Binom olasılığı"), 3),
                  "n + 1 değer içinde |oran − olasılık| farkının en büyüğü."),
    )


def _shape(n: int, p: float) -> str:
    """Dağılımın biçimi; çarpıklık katsayısı (1 − 2p)/√(np(1 − p)) ile: p = 0,5'te simetrik, p 0,5'e yakın ve n
    büyükken yalnız hafifçe çarpık."""

    if n == 1:
        return "n = 1 iken X yalnız 0 ya da 1 değerini alır: tek bir Bernoulli denemesidir (§9.3.1)."
    if p == 0.5:
        return "p = 0,50 iken dağılım simetriktir: P(X = x) = P(X = n − x)."
    side = "sağa" if p < 0.5 else "sola"
    if abs(1 - 2 * p) / math.sqrt(n * p * (1 - p)) < 0.25:
        return (f"Dağılım yalnız hafifçe {side} çarpıktır ve grafik neredeyse simetrik görünür: p 0,50'ye "
                "yaklaştıkça ve n büyüdükçe binom dağılımı simetriye yaklaşır.")
    if p < 0.5:
        return ("p küçük olduğu için olasılık küçük başarı sayılarında toplanır ve sağ kuyruk uzundur: dağılım "
                "sağa çarpıktır.")
    return ("p büyük olduğu için olasılık büyük başarı sayılarında toplanır ve sol kuyruk uzundur: dağılım "
            "sola çarpıktır.")


def _binomial_takeaway(state: LabState, parameters: Parameters) -> str:
    n, p, _ = _binomial_settings(parameters)
    s = state.scalars
    text = (
        f"Tekrarların ortalaması {plain(s['ortalama'], 3)}, varyansı {plain(s['varyans'], 3)}; binom modelinde "
        f"E(X) = np = {_short(n * p)} ve Var(X) = np(1 − p) = {_short(n * p * (1 - p), 4)}. {_shape(n, p)} "
        "p büyüdükçe dağılım np ile birlikte sağa kayar. Her tekrar n bağımsız Bernoulli denemesidir; X bu "
        "denemelerdeki başarıların toplamıdır (§9.3.2, §9.3.5). "
    )
    if n == 10 and p in (0.2, 0.5, 0.8):
        text += f"Bu ayarın binom olasılıkları Şekil 9.6'daki p = {plain(p, 2)} panelidir."
    else:
        text += "n = 10 ile p = 0,20, 0,50 ve 0,80 Şekil 9.6'nın üç panelini verir."
    return text


BINOMIAL_SHAPE = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Binom dağılımı: n ve p dağılımın biçimini nasıl değiştirir?",
    question="Her biri p olasılıkla başarılı olan n bağımsız denemedeki başarı sayısı tekrar tekrar gözlenirse, "
             "oranlar binom olasılıklarıyla uyuşur mu ve dağılımın biçimi n ile p'ye göre nasıl değişir?",
    note=NoteRef("9.3", objects=("Şekil 9.6",)),
    parameters=(
        SimParameter("n", "Deneme sayısı n", 1, 30, 10, 1, "Şekil 9.6'da n = 10.", integer=True, decimals=0),
        SimParameter("p", "Başarı olasılığı p", 0.05, 0.95, 0.20, 0.05, "Şekil 9.6: p = 0,20, 0,50 ve 0,80.",
                     decimals=2),
        SimParameter("tekrar", "Tekrar sayısı", 100, 10000, 1000, 100,
                     "Her tekrarda n deneme yapılır ve başarılar sayılır.", integer=True, decimals=0),
    ),
    dgp=_binomial_dgp,
    dgp_note=(
        "Her tekrarda n bağımsız Bernoulli denemesi yapılır; her denemenin başarı olasılığı p'dir ve X başarıların "
        "sayısıdır, (9.1). Tekrarlar birbirinden bağımsızdır; tohum 217'dir. Binom olasılıkları (9.2) "
        "formülünden hesaplanır."
    ),
    look_at=(
        "**Sütun grafiği** — her x için binom olasılığı ve tekrarlardaki oran yan yana; p değişince dağılımın "
        "kaydığını ve biçiminin değiştiğini izleyin.",
        "**Metrikler** — tekrarların ortalaması ve varyansı ile np ve np(1 − p).",
    ),
    build=_build_binomial,
    metrics=_binomial_metrics,
    takeaway=_binomial_takeaway,
    tables=(("karsilastirma", "Binom olasılıkları ve simülasyon oranları"),),
    labels=(("x", "Başarı sayısı x"),),
)


# --- Deney 2: Poisson'da aralık ve λ ------------------------------------------------------------

HOURLY_RATE = 12
"""§9.4.1: saatte ortalama 12 çağrı; t dakikalık aralıkta λ = 12 t/60."""


def _poisson_settings(parameters: Parameters) -> tuple[int, float, int]:
    minutes = int(parameters["t"])
    return minutes, round(HOURLY_RATE * minutes / 60, 10), int(parameters["tekrar"])


def poisson_upper(lam: float) -> int:
    """Gösterilen en büyük çağrı sayısı ⌈2λ + 4√λ + 6⌉: 1 ≤ λ ≤ 12 için bu sınırı aşma olasılığı 10⁻¹⁰'dan
    küçüktür; λ = 1'de 12 (Şekil 9.8'in ekseni)."""

    return math.ceil(2 * lam + 4 * math.sqrt(lam) + 6)


def _build_poisson(parameters: Parameters) -> tuple:
    minutes, lam, reps = _poisson_settings(parameters)
    values = tuple(range(poisson_upper(lam) + 1))
    return (
        Scalar("lam", E.div(E.mul(HOURLY_RATE, minutes), 60), "λ = saatlik ortalama × t/60 (Şekil 9.7)",
               decimals=2),
        Support("dagilim", "x", 0, values[-1], "Gösterilen çağrı sayıları; ötesinin olasılığı 10⁻¹⁰'dan küçük"),
        Derive("dagilim", "f", E.dpois(E.var("x"), E.ref("lam")), "Poisson olasılık fonksiyonu P(X = x), (9.7)"),
        GroupSummary("dagilim", "x", (("f", "f", "sum"),), "teorik", values, decimals=4),
        NewSample("aralik", reps, SEED),
        DrawCount("aralik", "x", "poisson", (lam,), "X: t dakikalık aralıkta gelen çağrı sayısı"),
        FrequencyTable("aralik", "x", "simulasyon", values),
        JoinColumns("karsilastirma", (("Poisson olasılığı", "teorik", "f"),
                                      ("Simülasyon oranı", "simulasyon", "goreli")), decimals=4),
        GroupedBarChart("karsilastirma", "Çağrı sayısı x", "Olasılık / göreli frekans",
                        "Poisson olasılıkları ve aralıklardaki oranlar", series="sutun", decimals=3, labels=False),
        Statistic("aralik", "x", "mean", "ortalama", "Aralıklardaki çağrı sayısının ortalaması", decimals=3),
        Statistic("aralik", "x", "var", "varyans", "Aralıklardaki çağrı sayısının varyansı s²", decimals=3),
        Event("aralik", "sifir", "x", (0,), "Hiç çağrı gelmeyen aralık"),
        Statistic("aralik", "sifir", "mean", "oran_sifir", "Hiç çağrı gelmeyen aralıkların oranı", decimals=3),
        Scalar("P_sifir", E.exp(E.neg(E.ref("lam"))), "P(X = 0) = e^(−λ)", decimals=4),
    )


def _poisson_dgp(parameters: Parameters) -> tuple[str, ...]:
    minutes, lam, reps = _poisson_settings(parameters)
    return (
        rf"\lambda = 12 \times \frac{{t}}{{60}} = 12 \times \frac{{{minutes}}}{{60}} = {_tex(lam, 2)}, \qquad "
        rf"X \sim \operatorname{{Pois}}(\lambda), \qquad {reps} \text{{ aralık}}",
        r"P(X = x) = \frac{\lambda^x e^{-\lambda}}{x!}, \quad x = 0, 1, 2, \ldots, \qquad E(X) = \operatorname{Var}(X)"
        r" = \lambda",
    )


def _poisson_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    _, lam, _ = _poisson_settings(parameters)
    s = state.scalars
    return (
        SimMetric("λ = 12 × t/60", _short(lam, 2), "İncelenen aralıktaki beklenen çağrı sayısı."),
        SimMetric("Aralıkların ortalaması", plain(s["ortalama"], 3), f"E(X) = λ = {_short(lam, 2)}."),
        SimMetric("Aralıkların varyansı s²", plain(s["varyans"], 3), f"Var(X) = λ = {_short(lam, 2)}."),
        SimMetric("Çağrısız aralık oranı", plain(s["oran_sifir"], 3), f"P(X = 0) = e^(−λ) {_tiny(s['P_sifir'])}."),
    )


FIGURE_9_8 = {5: "λ = 1", 15: "λ = 3", 30: "λ = 6"}


def _tiny(value: float) -> str:
    """Küçük olasılık ilişkisiyle: "= 0,0003" ya da 0,0001'in altındaysa "< 0,0001"."""

    return f"= {plain(value, 4)}" if value >= 0.00005 else "< 0,0001"


def _poisson_takeaway(state: LabState, parameters: Parameters) -> str:
    minutes, lam, _ = _poisson_settings(parameters)
    s = state.scalars
    if minutes == 60:
        conversion = ("t = 60 dakikada λ saatlik ortalamanın kendisidir, λ = 12; başka her aralıkta saatlik "
                      "ortalama önce o aralığa dönüştürülmelidir (§9.4.1). ")
    else:
        conversion = (f"t = {minutes} dakika için λ = 12 × {minutes}/60 = {_short(lam, 2)}: saatlik ortalama "
                      "incelenen aralığa dönüştürülmeden kullanılsaydı bütün olasılıklar yanlış olurdu (§9.4.1). ")
    text = conversion + (
        f"Aralıklardaki çağrı sayısının ortalaması {plain(s['ortalama'], 3)}, varyansı {plain(s['varyans'], 3)}; "
        "Poisson modelinde ikisi de λ'dır, (9.8)–(9.9). λ büyüdükçe dağılım sağa kayar, yayılır ve daha az çarpık "
        "görünür. X'in teorik bir üst sınırı yoktur; grafik pratikte anlamlı bir aralığı gösterir ve bu aralığın "
        "ötesinin olasılığı 10⁻¹⁰'dan küçüktür (§9.4). "
    )
    if minutes in FIGURE_9_8:
        text += f"Bu ayarın Poisson olasılıkları Şekil 9.8'deki {FIGURE_9_8[minutes]} panelidir."
    else:
        text += "t = 5, 15 ve 30 dakika Şekil 9.8'in λ = 1, 3 ve 6 panellerini verir."
    return text


POISSON_INTERVAL = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Poisson: aralık uzadıkça λ ve dağılım nasıl değişir?",
    question="Saatte ortalama 12 çağrı gelen bir destek merkezinde incelenen aralık uzadıkça beklenen çağrı sayısı "
             "λ, olasılıklar ve gözlenen çağrı sayılarının ortalaması ile varyansı nasıl değişir?",
    note=NoteRef("9.4", objects=("Şekil 9.7", "Şekil 9.8")),
    parameters=(
        SimParameter("t", "Aralık uzunluğu t (dakika)", 5, 60, 15, 5,
                     "λ = 12 × t/60; notlardaki örnekte t = 15, λ = 3.", integer=True, decimals=0),
        SimParameter("tekrar", "Gözlenen aralık sayısı", 100, 10000, 1000, 100,
                     "Birbirinden ayrık, eşit uzunlukta aralıklar.", integer=True, decimals=0),
    ),
    dgp=_poisson_dgp,
    dgp_note=(
        "Çağrılar sabit bir hızla gelir: eşit uzunluktaki aralıklarda olay oluşum davranışı aynıdır ve ayrık "
        "aralıklardaki çağrılar birbirinden bağımsızdır (§9.4). Her aralıktaki çağrı sayısı Pois(λ) dağılımından "
        "çekilir; tohum 217'dir."
    ),
    look_at=(
        "**Sütun grafiği** — her çağrı sayısı için Poisson olasılığı ve aralıklardaki oran yan yana.",
        "**Metrikler** — ortalama ile varyansın ikisinin de λ çevresinde olması; hiç çağrı gelmeyen aralıkların "
        "oranı ve e^(−λ).",
    ),
    build=_build_poisson,
    metrics=_poisson_metrics,
    takeaway=_poisson_takeaway,
    tables=(("karsilastirma", "Poisson olasılıkları ve simülasyon oranları"),),
    labels=(("x", "Çağrı sayısı x"),),
)


# --- Deney 3: yerine koymadan seçim -------------------------------------------------------------

SAMPLE = 8
"""Tablo 9.1: partiden seçilen ürün sayısı n = 8; partideki kusurlu oranı r/N = 0,10."""
COUNTS = tuple(range(SAMPLE + 1))


def _lot_settings(parameters: Parameters) -> tuple[int, int, int]:
    population = int(parameters["N"])
    return population, population // 10, int(parameters["tekrar"])


def _hyper_truth(population: int) -> dict[str, float]:
    p = 0.1
    correction = (population - SAMPLE) / (population - 1)
    return {"E": SAMPLE * p, "Var_binom": SAMPLE * p * (1 - p), "duzeltme": correction,
            "Var_hiper": SAMPLE * p * (1 - p) * correction}


def _build_lot(parameters: Parameters) -> tuple:
    population, defective, reps = _lot_settings(parameters)
    p = E.div(defective, population)
    return (
        Support("dagilim", "x", 0, SAMPLE, "Seçilen 8 üründeki olası kusurlu sayıları"),
        Derive("dagilim", "hiper", E.dhyper(E.var("x"), population, defective, SAMPLE),
               "Hipergeometrik P(X = x), (9.11): yerine koymadan seçim"),
        Derive("dagilim", "binom", E.dbinom(E.var("x"), SAMPLE, p),
               "Binom P(X = x), (9.2): bağımsız denemeler, p = r/N"),
        GroupSummary("dagilim", "x", (("hiper", "hiper", "sum"), ("binom", "binom", "sum")), "teorik", COUNTS,
                     decimals=4),
        NewSample("secim", reps, SEED),
        DrawCount("secim", "x", "hypergeometric", (population, defective, SAMPLE),
                  "X: partiden seçilen 8 üründeki kusurlu sayısı"),
        FrequencyTable("secim", "x", "simulasyon", COUNTS),
        JoinColumns("karsilastirma", (("Hipergeometrik olasılık", "teorik", "hiper"),
                                      ("Binom olasılığı", "teorik", "binom"),
                                      ("Simülasyon oranı", "simulasyon", "goreli")), decimals=4),
        GroupedBarChart("karsilastirma", "Kusurlu sayısı x", "Olasılık / göreli frekans",
                        "Yerine koymadan seçim: hipergeometrik, binom ve simülasyon", series="sutun", decimals=3,
                        labels=False),
        Statistic("secim", "x", "mean", "ortalama", "Seçimlerdeki kusurlu sayısının ortalaması", decimals=3),
        Statistic("secim", "x", "var", "varyans", "Seçimlerdeki kusurlu sayısının varyansı s²", decimals=3),
        Scalar("E_X", E.mul(SAMPLE, p), "E(X) = n r/N, (9.12): iki modelde aynı", decimals=3),
        Scalar("Var_binom", E.mul(E.mul(SAMPLE, p), E.sub(1, p)), "Binom varyansı n(r/N)(1 − r/N)", decimals=4),
        Scalar("duzeltme", E.div(E.sub(population, SAMPLE), E.sub(population, 1)),
               "Sonlu anakütle düzeltmesi (N − n)/(N − 1)", decimals=4),
        Scalar("Var_hiper", E.mul(E.ref("Var_binom"), E.ref("duzeltme")), "Hipergeometrik varyans, (9.13)",
               decimals=4),
        ScalarTable(
            (
                ("E(X) = n r/N: iki modelde aynı", E.ref("E_X")),
                ("Simülasyon ortalaması", E.ref("ortalama")),
                ("Var(X): binom, np(1 − p)", E.ref("Var_binom")),
                ("Var(X): hipergeometrik, (9.13)", E.ref("Var_hiper")),
                ("Simülasyon varyansı s²", E.ref("varyans")),
                ("Düzeltme çarpanı (N − n)/(N − 1)", E.ref("duzeltme")),
            ),
            "ozet",
            decimals=4,
        ),
    )


def _lot_dgp(parameters: Parameters) -> tuple[str, ...]:
    population, defective, reps = _lot_settings(parameters)
    truth = _hyper_truth(population)
    return (
        rf"N = {population},\ r = {defective},\ n = 8, \qquad X \sim \text{{Hiper}}(N, r, n), \qquad "
        rf"\text{{karşılaştırma: }} \operatorname{{Bin}}(8,\ 0{{,}}10), \qquad {reps} \text{{ tekrar}}",
        rf"E(X) = n\frac{{r}}{{N}} = 0{{,}}8, \qquad \operatorname{{Var}}(X) = n\frac{{r}}{{N}}\left(1 - "
        rf"\frac{{r}}{{N}}\right)\frac{{N - n}}{{N - 1}} = 0{{,}}72 \times {_tex(truth['duzeltme'], 4)} = "
        rf"{_tex(truth['Var_hiper'], 4)}",
    )


def _lot_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    population, _, _ = _lot_settings(parameters)
    truth = _hyper_truth(population)
    table = state.tables["karsilastirma"]
    return (
        SimMetric("Düzeltme çarpanı", plain(truth["duzeltme"], 3), "(N − n)/(N − 1): N büyüdükçe 1'e yaklaşır."),
        SimMetric("Simülasyon varyansı s²", plain(state.scalars["varyans"], 3),
                  f"Hipergeometrik {plain(truth['Var_hiper'], 3)}; binom 0,720."),
        SimMetric("En büyük olasılık farkı", plain(_largest_gap(table, "Hipergeometrik olasılık", "Binom olasılığı"),
                                                   3),
                  "Hipergeometrik ve binom olasılıkları arasındaki en büyük fark."),
    )


def _lot_takeaway(state: LabState, parameters: Parameters) -> str:
    population, defective, _ = _lot_settings(parameters)
    truth = _hyper_truth(population)
    gap = _largest_gap(state.tables["karsilastirma"], "Hipergeometrik olasılık", "Binom olasılığı")
    text = (
        f"N = {population} birimlik partide r = {defective} kusurlu ürün vardır. Seçilen her ürün geri konmadığı "
        "için sonraki seçimlerde kusurlu oranı değişir; seçimler bağımsız değildir (§9.5, Şekil 9.9). "
        "Ortalama iki modelde de n r/N = 0,8'dir, ama düzeltme çarpanı (N − 8)/(N − 1) = "
        f"{plain(truth['duzeltme'], 3)} varyansı binomdakinin altına çeker: {plain(truth['Var_hiper'], 3)} < 0,720 "
        f"(simülasyonda s² = {plain(state.scalars['varyans'], 3)}). İki modelin olasılıkları arasındaki en büyük "
        f"fark {plain(gap, 3)}; parti büyüdükçe çarpan 1'e yaklaşır ve hipergeometrik olasılıklar binom "
        "olasılıklarına yaklaşır (§9.6). "
    )
    if population == 40:
        text += "Bu ayar Tablo 9.1'deki iki senaryodur: Hiper(N = 40, r = 4, n = 8) ve Bin(8, 0,10)."
    else:
        text += "N = 40 Tablo 9.1'deki partidir."
    return text


WITHOUT_REPLACEMENT = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Yerine koymadan seçim: hipergeometrik binomdan ne zaman ayrılır?",
    question="Kusurlu oranı %10 olan bir partiden 8 ürün yerine koymadan seçildiğinde kusurlu sayısının dağılımı, "
             "bağımsız denemelerin binom modelinden ne kadar ayrılır ve parti büyüdükçe ne olur?",
    note=NoteRef("9.6", objects=("Tablo 9.1", "(9.13)")),
    parameters=(
        SimParameter("N", "Parti büyüklüğü N", 10, 400, 40, 10,
                     "Partideki kusurlu sayısı r = N/10; Tablo 9.1'de N = 40, r = 4.", integer=True, decimals=0),
        SimParameter("tekrar", "Tekrar sayısı", 100, 10000, 1000, 100,
                     "Her tekrarda partiden 8 ürün yerine koymadan seçilir.", integer=True, decimals=0),
    ),
    dgp=_lot_dgp,
    dgp_note=(
        "Her tekrarda N birimlik partiden 8 ürün yerine koymadan seçilir ve kusurlu ürünler sayılır; parti her "
        "tekrarda yeniden kurulur. Karşılaştırılan binom modeli, her ürünün bağımsız olarak 0,10 olasılıkla kusurlu "
        "olduğu üretim hikâyesidir (Tablo 9.1). Tohum 217'dir."
    ),
    look_at=(
        "**Sütun grafiği** — hipergeometrik ve binom olasılıkları ile seçimlerdeki oran; küçük partide farkı, "
        "büyük partide yakınlaşmayı izleyin.",
        "**Özet tablosu** — iki modelde aynı ortalama; varyansta sonlu anakütle düzeltmesi.",
    ),
    build=_build_lot,
    metrics=_lot_metrics,
    takeaway=_lot_takeaway,
    tables=(("karsilastirma", "Olasılıklar ve simülasyon oranları"),
            ("ozet", "Ortalama, varyans ve sonlu anakütle düzeltmesi")),
    labels=(("x", "Kusurlu sayısı x"),),
)


KONU09_EXPERIMENTS = (BINOMIAL_SHAPE, POISSON_INTERVAL, WITHOUT_REPLACEMENT)
