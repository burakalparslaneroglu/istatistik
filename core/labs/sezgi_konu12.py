"""Konu 12 Sezgi deneyleri: veri üretim süreci bilinen kontrollü simülasyonlar.

Deney 1  Tutarlılık: örneklem büyüdükçe X̄ₙ'in yolu ve daralan band          (Notlar §12.12.2, Şekil 12.13)
Deney 2  Merkezi Limit Teoremi: çarpık anakütleden örneklem ortalamaları      (Notlar §12.8, Şekil 12.8)
Deney 3  Örneklem oranının örnekleme dağılımı                                 (Notlar §12.10, Şekil 12.10)

Şekil 12.13 bu modülün Deney 1'iyle üretilmiştir: varsayılan ayarlar (N(50, 20²), n = 100, tohum 217) şekildeki yolun
aynısını verir. Deney 2'nin anakütlesi Şekil 12.8'deki üstel dağılımdır (μ = σ = 1); tam dağılım eğrileri şekildeki
eğrilerdir. Deney 3'ün varsayılan ayarları Şekil 12.10'un sağ panelidir (p = 0,40, n = 100).
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

from core.labs import expr as E
from core.labs.runner import LabState
from core.labs.sezgi import Parameters, SimExperiment, SimMetric, SimParameter, number, percent, plain
from core.labs.spec import (
    DensityPlot,
    Derive,
    Draw,
    DrawCount,
    Histogram,
    JoinColumns,
    LineChart,
    MonteCarlo,
    NewSample,
    NoteRef,
    Scalar,
    ScalarTable,
    Statistic,
)

SEED = 217
TOPIC = "konu12"


def _short(value: float, decimals: int = 3) -> str:
    """Sondaki sıfırları atılmış düz metin sayı (5; 0,4; 7,5)."""

    text = f"{value:.{decimals}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",").replace("-", "−")


def _tex(value: float, decimals: int = 3) -> str:
    return _short(value, decimals).replace(",", "{,}").replace("−", "-")


def _whole(value: float) -> float | int:
    """Tam sayı değerler tam sayı olarak (kodda 5.0 yerine 5 yazılır)."""

    return int(value) if float(value).is_integer() else value


def _listing(values: list[str]) -> str:
    """Ondalık virgüllü sayıların listesi: "0,4295; 0,2113; 0,0124 ve 0,0000"."""

    return "; ".join(values[:-1]) + " ve " + values[-1]


# --- Deney 1: tutarlılık ---------------------------------------------------------------------

POPULATION_MEAN = 50
"""Şekil 12.13: anakütle N(50, 20²)."""
TABLE_SIZES = (10, 25, 100, 400)
"""Olasılık tablosundaki örneklem büyüklükleri."""


def _path_settings(parameters: Parameters) -> tuple[int, int, float | int]:
    return int(parameters["n"]), int(parameters["sigma"]), _whole(round(float(parameters["eps"]), 1))


def _outside_probability(eps: float | int, size: int, sigma: int) -> E.Expr:
    """P(|X̄ₙ − μ| > ε) = 2[1 − Φ(ε√n/σ)]: normal anakütlede X̄ₙ ~ N(μ, σ²/n)."""

    return E.mul(2, E.sub(1, E.normcdf(E.div(E.mul(eps, E.sqrt(size)), sigma))))


def _build_path(parameters: Parameters) -> tuple:
    size, sigma, eps = _path_settings(parameters)
    mu = POPULATION_MEAN
    half = E.div(E.mul(2, sigma), E.sqrt(E.var("n")))
    return (
        Scalar("mu", E.const(mu), "Gerçek parametre μ", decimals=0),
        NewSample("orneklem", size, SEED),
        Draw("orneklem", "x", "normal", mu, sigma, "X ~ N(50, σ²): gözlemler sırayla gelir"),
        Derive("orneklem", "n", E.seq(E.var("x")), "Örneklem büyüklüğü n = 1, 2, …: ilk n gözlem"),
        Derive("orneklem", "ortalama", E.cummean(E.var("x")), "X̄ₙ: ilk n gözlemin ortalaması"),
        Derive("orneklem", "ust", E.add(mu, half), "Bandın üst kenarı μ + 2σ/√n"),
        Derive("orneklem", "alt", E.sub(mu, half), "Bandın alt kenarı μ − 2σ/√n"),
        Derive("orneklem", "sapma", E.absolute(E.sub(E.var("ortalama"), mu)), "|X̄ₙ − μ|: tahminin uzaklığı"),
        Derive("orneklem", "bant_disi", E.compare("gt", E.var("sapma"), half), "Gösterge: X̄ₙ bandın dışındaysa 1"),
        Derive("orneklem", "eps_disi_n", E.mul(E.var("n"), E.compare("gt", E.var("sapma"), eps)),
               "|X̄ₙ − μ| > ε ise n, değilse 0"),
        Statistic("orneklem", "x", "mean", "son_ortalama", "Bütün gözlemlerin ortalaması: en büyük n için X̄ₙ",
                  decimals=2),
        Statistic("orneklem", "bant_disi", "sum", "bant_disi_sayisi", "Bandın dışındaki nokta sayısı", decimals=0),
        Statistic("orneklem", "eps_disi_n", "max", "son_eps_disi", "|X̄ₙ − μ| > ε olan en büyük n (hiç yoksa 0)",
                  decimals=0),
        ScalarTable(tuple((f"n = {k}", E.div(sigma, E.sqrt(k))) for k in TABLE_SIZES), "standart_hata", decimals=4),
        ScalarTable(tuple((f"n = {k}", _outside_probability(eps, k, sigma)) for k in TABLE_SIZES), "olasilik",
                    decimals=4),
        JoinColumns("tutarlilik", (("Standart hata σ/√n", "standart_hata", "deger"),
                                   ("P(|X̄ₙ − μ| > ε)", "olasilik", "deger")), decimals=4),
        LineChart("orneklem", "n", "ortalama", "Örneklem büyüklüğü n", "Örneklem ortalaması X̄ₙ",
                  "Tek bir örneklem büyürken örneklem ortalamasının yolu",
                  references=(("mu", f"Gerçek parametre μ = {mu}"),), markers=False,
                  bands=(("ust", "μ ± 2σ/√n bandı"), ("alt", ""))),
    )


def _path_dgp(parameters: Parameters) -> tuple[str, ...]:
    size, sigma, eps = _path_settings(parameters)
    return (
        rf"X_i \sim N(50, \sigma^2) \text{{ bağımsız}}, \quad \sigma = {sigma}, \qquad \bar X_n = \frac{{1}}{{n}}"
        rf"\sum_{{i=1}}^{{n}} X_i, \quad n = 1, 2, \ldots, {size}",
        rf"\mu \pm \frac{{2\sigma}}{{\sqrt{{n}}}} = 50 \pm \frac{{{2 * sigma}}}{{\sqrt{{n}}}}, \qquad "
        r"P\bigl(|\bar X_n - \mu| > \varepsilon\bigr) = 2\left[1 - \Phi\!\left(\frac{\varepsilon\sqrt{n}}{\sigma}"
        rf"\right)\right], \quad \varepsilon = {_tex(eps)}",
    )


def _path_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    size, sigma, eps = _path_settings(parameters)
    s = state.scalars
    last = int(s["son_eps_disi"])
    return (
        SimMetric("Son tahmin X̄ₙ", plain(s["son_ortalama"], 2), f"n = {size} gözlemin ortalaması; μ = 50."),
        SimMetric("Standart hata σ/√n", plain(sigma / math.sqrt(size), 2), f"n = {size} için; band μ ± 2σ/√n."),
        SimMetric("Bandın dışındaki nokta", str(int(s["bant_disi_sayisi"])),
                  "Her n için olasılık yaklaşık %5; noktalar aynı yolun parçası olduğundan bağımsız değildir."),
        SimMetric("ε'dan uzak kalınan son n", str(last) if last else "yok",
                  f"|X̄ₙ − 50| > ε = {_short(eps)} olan en büyük n."),
    )


def _path_takeaway(state: LabState, parameters: Parameters) -> str:
    size, sigma, eps = _path_settings(parameters)
    s = state.scalars
    probabilities = [plain(value, 4) for value in state.tables["tutarlilik"]["P(|X̄ₙ − μ| > ε)"]]
    text = (
        "Yol ilk gözlemlerde büyük dalgalanır, sonra μ = 50 çevresinde yoğunlaşır: n = "
        f"{size} gözlemde X̄ₙ = {plain(s['son_ortalama'], 2)}. Standart hata σ/√n küçüldükçe band daralır. Tahminin "
        f"μ'den ε = {_short(eps)} birimden fazla uzak olma olasılığı n = 10, 25, 100 ve 400 için sırasıyla "
        f"{_listing(probabilities)}: n büyüdükçe sıfıra gider. Tutarlılık budur (§12.12.2). Yol her adımda μ'ye "
        "yaklaşmak zorunda değildir; tek tek tahminler dalgalanabilir. "
    )
    if sigma == 20 and size == 100:
        text += ("Bu ayarın yolu Şekil 12.13'teki yoldur: n = 5'te 44,34; n = 14'te 50,35; n = 100'de 47,78 "
                 "(tohum 217).")
    elif sigma == 20 and size > 100:
        text += "İlk 100 nokta Şekil 12.13'teki yoldur (σ = 20, tohum 217); yol aynı örneklemin devamıdır."
    else:
        text += "n = 100 ve σ = 20 Şekil 12.13'teki yolu verir (tohum 217)."
    return text


CONSISTENCY = SimExperiment(
    topic_key=TOPIC,
    number=1,
    title="Tutarlılık: örneklem büyüdükçe X̄ₙ'in yolu ve daralan band",
    question="Tek bir örneklem gözlem gözlem büyürken örneklem ortalaması gerçek μ'ye nasıl yaklaşır; tahminin μ'den "
             "belirli bir uzaklıktan fazla sapma olasılığı n büyüdükçe neden sıfıra gider?",
    note=NoteRef("12.12.2", objects=("Şekil 12.13",)),
    parameters=(
        SimParameter("n", "En büyük örneklem n", 20, 1000, 100, 10,
                     "Yol n = 1'den bu değere kadar çizilir; Şekil 12.13'te n = 100.", integer=True, decimals=0),
        SimParameter("sigma", "Anakütle standart sapması σ", 5, 40, 20, 5, "Şekil 12.13'te σ = 20.", integer=True,
                     decimals=0),
        SimParameter("eps", "Uzaklık ε", 1, 10, 5, 0.5, "Olasılık tablosu ve son metrik için: |X̄ₙ − μ| > ε.",
                     decimals=1),
    ),
    dgp=_path_dgp,
    dgp_note=(
        "Gözlemler N(50, σ²) dağılımından birbirinden bağımsız çekilir ve sırayla gelir; tohum 217'dir. n. noktadaki "
        "değer ilk n gözlemin ortalamasıdır, yani yol tek bir örneklemin büyümesidir. Normal anakütlede X̄ₙ ~ N(μ, "
        "σ²/n) olduğundan tablodaki olasılıklar tam değerdir. Varsayılan ayarlar Şekil 12.13'ü üretir."
    ),
    look_at=(
        "**Yol ve band** — X̄ₙ'in dalgalanması, kesikli μ ± 2σ/√n bandının daralması; n'yi büyütünce aynı yolun "
        "devam ettiğini izleyin.",
        "**Olasılık tablosu** — standart hata ve P(|X̄ₙ − μ| > ε), n = 10, 25, 100 ve 400 için.",
    ),
    build=_build_path,
    metrics=_path_metrics,
    takeaway=_path_takeaway,
    tables=(("tutarlilik", "Standart hata ve tahminin ε'dan fazla sapma olasılığı"),),
    labels=(("n", "Örneklem büyüklüğü n"), ("ortalama", "Örneklem ortalaması X̄ₙ"), ("x", "Gözlem x")),
)


# --- Deney 2: Merkezi Limit Teoremi ----------------------------------------------------------------

CLT_AXIS = (0, 4)
CLT_BINS = 80


def _clt_settings(parameters: Parameters) -> tuple[int, int]:
    return int(parameters["n"]), int(parameters["tekrar"])


def gamma_tails(n: int) -> tuple[float, float]:
    """Üstel(1) anakütlede X̄'in tam dağılımı gamma (biçim n, oran n): P(X̄ > 1 + 2/√n) ve P(X̄ < 1 − 2/√n)."""

    half = 2 / math.sqrt(n)
    right = float(stats.gamma.sf(1 + half, n, scale=1 / n))
    left = float(stats.gamma.cdf(1 - half, n, scale=1 / n)) if half < 1 else 0.0
    return right, left


def _build_clt(parameters: Parameters) -> tuple:
    n, reps = _clt_settings(parameters)
    half = E.div(2, E.sqrt(n))
    xbar = E.ref("xbar")
    return (
        MonteCarlo(
            "tekrarlar",
            reps,
            SEED,
            (
                NewSample("orneklem", n, None),
                Draw("orneklem", "x", "exponential", 1, 1, "X ~ Üstel(μ = 1): sağa çarpık anakütle"),
                Statistic("orneklem", "x", "mean", "xbar", "Örneklem ortalaması x̄"),
            ),
            (
                ("xbar", xbar),
                ("sag_kuyruk", E.compare("gt", xbar, E.add(1, half))),
                ("sol_kuyruk", E.compare("lt", xbar, E.sub(1, half))),
            ),
            "Her tekrarda üstel anakütleden n gözlemlik yeni bir örneklem çekilir ve ortalaması alınır",
        ),
        Scalar("se", E.div(1, E.sqrt(n)), "σ_X̄ = σ/√n = 1/√n, (12.3)", decimals=4),
        DensityPlot("exponential", 1, 1, CLT_AXIS, "Anakütle: üstel dağılım, μ = σ = 1", "Gözlem x",
                    references=((1, "μ = 1"),)),
        Histogram("tekrarlar", (("xbar", "Örneklem ortalamaları x̄"),), CLT_BINS, CLT_AXIS[0], CLT_AXIS[1],
                  "Örneklem ortalamalarının dağılımı", "Örneklem ortalaması x̄", references=((1, "μ = 1"),),
                  y_label="Örneklem sayısı",
                  curves=(("gamma", n, n, "X̄'in tam dağılımı"), ("normal", 1, "se", "Normal yaklaşım N(1, 1/n)"))),
    )


def _clt_dgp(parameters: Parameters) -> tuple[str, ...]:
    n, reps = _clt_settings(parameters)
    return (
        rf"X_i \sim \operatorname{{Exp}}(1) \text{{ bağımsız}}: \ \mu = \sigma = 1, \qquad n = {n}, \qquad {reps} "
        r"\text{ örneklem}",
        rf"E(\bar X) = \mu = 1, \qquad \sigma_{{\bar X}} = \frac{{\sigma}}{{\sqrt{{n}}}} = "
        rf"{number(1 / math.sqrt(n), 4)}, \qquad"
        r" \bar X \overset{\text{yaklaşık}}{\sim} N\!\left(1, \frac{1}{n}\right) \ (n \text{ büyükken})",
    )


def _clt_summary(state: LabState) -> tuple[float, float, float, float]:
    table = state.tables["tekrarlar"]
    return (float(table["xbar"].mean()), float(table["xbar"].std()), float(table["sag_kuyruk"].mean()),
            float(table["sol_kuyruk"].mean()))


def _clt_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    n, _ = _clt_settings(parameters)
    mean, sd, right, left = _clt_summary(state)
    exact_right, exact_left = gamma_tails(n)
    return (
        SimMetric("x̄'lerin ortalaması", plain(mean, 3), "E(X̄) = μ = 1, (12.2)."),
        SimMetric("x̄'lerin standart sapması", plain(sd, 3), f"σ/√n = {plain(1 / math.sqrt(n), 3)}, (12.3)."),
        SimMetric("Sağ kuyruk: x̄ > μ + 2σ/√n", percent(100 * right, 1),
                  f"Tam dağılımda {percent(100 * exact_right, 1)}; normal eğride %2,3."),
        SimMetric("Sol kuyruk: x̄ < μ − 2σ/√n", percent(100 * left, 1),
                  f"Tam dağılımda {percent(100 * exact_left, 1)}; normal eğride %2,3."),
    )


FIGURE_12_8 = {1: "anakütle panelidir", 2: "n = 2 panelidir", 5: "n = 5 panelidir", 30: "n = 30 panelidir"}


def _clt_takeaway(state: LabState, parameters: Parameters) -> str:
    n, reps = _clt_settings(parameters)
    mean, sd, right, left = _clt_summary(state)
    text = (
        f"Anakütle sağa çarpıktır, ama {reps} örneklemin ortalamaları μ = 1 çevresinde toplanır: x̄'lerin ortalaması "
        f"{plain(mean, 3)}, standart sapması {plain(sd, 3)}; formül σ/√n = {plain(1 / math.sqrt(n), 3)} (12.3). "
    )
    if n == 1:
        text += "n = 1 iken x̄ tek bir gözlemdir: histogram anakütlenin kendisidir. "
    else:
        text += (
            f"Kuyruklar çarpıklığı gösterir: sağ kuyruk payı {percent(100 * right, 1)}, sol kuyruk payı "
            f"{percent(100 * left, 1)}; normal dağılımda ikisi de %2,3 olurdu. n büyüdükçe iki pay birbirine yaklaşır "
            "ve histogram normal eğriye oturur. "
        )
    text += (
        "Merkezi Limit Teoremi X̄'in dağılımıyla ilgilidir; tek tek gözlemler hâlâ üstel dağılır. n ≥ 30 pratik bir "
        "başlangıç kuralıdır, evrensel bir eşik değildir (§12.8). "
    )
    if n in FIGURE_12_8:
        text += f"Bu ayarın tam dağılım eğrisi Şekil 12.8'in {FIGURE_12_8[n]}."
    else:
        text += "n = 1, 2, 5 ve 30 Şekil 12.8'in dört panelini verir."
    return text


CENTRAL_LIMIT = SimExperiment(
    topic_key=TOPIC,
    number=2,
    title="Merkezi Limit Teoremi: çarpık anakütleden örneklem ortalamaları",
    question="Anakütle belirgin biçimde sağa çarpıksa, n gözlemlik örneklemlerin ortalamaları nasıl dağılır; n "
             "büyüdükçe bu dağılımın merkezi, yayılımı ve biçimi nasıl değişir?",
    note=NoteRef("12.8", objects=("Şekil 12.8", "(12.3)")),
    parameters=(
        SimParameter("n", "Örneklem büyüklüğü n", 1, 50, 5, 1, "Şekil 12.8: n = 1 (anakütle), 2, 5 ve 30.",
                     integer=True, decimals=0),
        SimParameter("tekrar", "Örneklem sayısı", 500, 5000, 2000, 500, "Her tekrarda yeni bir örneklem çekilir.",
                     integer=True, decimals=0),
    ),
    dgp=_clt_dgp,
    dgp_note=(
        "Anakütle ortalaması 1 olan üstel dağılımdır (Konu 11): sağa çarpıktır ve μ = σ = 1. Her tekrarda bu "
        "anakütleden n bağımsız gözlem çekilir ve ortalaması alınır; tohum 217'dir. Üstel anakütlede X̄'in tam "
        "dağılımı bilinir (gamma dağılımı; bu dersin konusu değildir): histogramdaki tam dağılım eğrisi Şekil "
        "12.8'deki eğrilerdir. Histogram 0–4 aralığını gösterir."
    ),
    look_at=(
        "**İki grafik** — anakütlenin çarpık yoğunluğu ile örneklem ortalamalarının histogramı; n = 1, 2, 5 ve 30'u "
        "karşılaştırın.",
        "**Metrikler** — x̄'lerin ortalaması ve standart sapması; sağ ve sol kuyruk paylarının birbirine yaklaşması.",
    ),
    build=_build_clt,
    metrics=_clt_metrics,
    takeaway=_clt_takeaway,
    labels=(("xbar", "Örneklem ortalaması x̄"), ("x", "Gözlem x")),
)


# --- Deney 3: örneklem oranı ------------------------------------------------------------------------

def _proportion_settings(parameters: Parameters) -> tuple[float, int, int]:
    return round(float(parameters["p"]), 2), int(parameters["n"]), int(parameters["tekrar"])


def proportion_bins(n: int) -> tuple[int, float, float]:
    """Her kutu p̂'nin alabileceği tek bir değeri (k/n) içerir: n + 1 kutu, sınırlar (k ± 0,5)/n."""

    return n + 1, round(-0.5 / n, 6), round(1 + 0.5 / n, 6)


def _normal_condition(n: int, p: float) -> bool:
    return round(n * p, 9) >= 5 and round(n * (1 - p), 9) >= 5


def two_se_probability(n: int, p: float) -> float:
    """p̂'nin p ± 2σ_p̂ aralığına düşme olasılığı, binom dağılımından tam olarak; aralık simülasyondaki göstergeyle
    aynı kayan nokta işlemleriyle belirlenir."""

    k = np.arange(n + 1)
    inside = np.abs(k / n - p) <= 2 * math.sqrt(p * (1 - p) / n)
    return float(stats.binom.pmf(k[inside], n, p).sum())


def _build_proportion(parameters: Parameters) -> tuple:
    p, n, reps = _proportion_settings(parameters)
    bins, lower, upper = proportion_bins(n)
    share = E.var("p_sapka")
    return (
        Scalar("se", E.sqrt(E.div(E.mul(p, E.sub(1, p)), n)), "σ_p̂ = √(p(1 − p)/n), (12.8)", decimals=4),
        NewSample("orneklemler", reps, SEED),
        DrawCount("orneklemler", "x", "binomial", (n, p), "X: n birimlik örneklemde özelliğe sahip birim sayısı"),
        Derive("orneklemler", "p_sapka", E.div(E.var("x"), n), "Örneklem oranı p̂ = x/n, (12.6)"),
        Derive("orneklemler", "iki_se", E.compare("le", E.absolute(E.sub(share, p)), E.mul(2, E.ref("se"))),
               "Gösterge: p̂, p ± 2σ_p̂ aralığındaysa 1"),
        Statistic("orneklemler", "p_sapka", "mean", "ortalama", "Örneklem oranlarının ortalaması", decimals=4),
        Statistic("orneklemler", "p_sapka", "std", "s", "Örneklem oranlarının standart sapması", decimals=4),
        Statistic("orneklemler", "iki_se", "mean", "pay", "p ± 2σ_p̂ içindeki örneklem oranlarının payı",
                  decimals=3),
        Histogram("orneklemler", (("p_sapka", "Örneklem oranları p̂"),), bins, lower, upper,
                  "Örneklem oranlarının dağılımı", "Örneklem oranı p̂", references=((p, f"p = {plain(p, 2)}"),),
                  y_label="Örneklem sayısı", curves=(("normal", p, "se", "Normal yaklaşım N(p, p(1 − p)/n)"),)),
    )


def _proportion_dgp(parameters: Parameters) -> tuple[str, ...]:
    p, n, reps = _proportion_settings(parameters)
    se = math.sqrt(p * (1 - p) / n)
    return (
        rf"X \sim \operatorname{{Bin}}(n, p), \quad \hat p = \frac{{X}}{{n}}, \qquad p = {number(p, 2)},\ n = {n}, "
        rf"\qquad {reps} \text{{ örneklem}}",
        rf"E(\hat p) = p = {number(p, 2)}, \qquad \sigma_{{\hat p}} = \sqrt{{\frac{{p(1 - p)}}{{n}}}} = "
        rf"{number(se, 4)}",
    )


def _proportion_metrics(state: LabState, parameters: Parameters) -> tuple[SimMetric, ...]:
    p, n, _ = _proportion_settings(parameters)
    s = state.scalars
    condition = ("Koşul (12.10) sağlanıyor: ikisi de en az 5." if _normal_condition(n, p)
                 else "Koşul (12.10) sağlanmıyor: ikisinin de en az 5 olması gerekir.")
    return (
        SimMetric("p̂'lerin ortalaması", plain(s["ortalama"], 4), f"E(p̂) = p = {plain(p, 2)}, (12.7)."),
        SimMetric("p̂'lerin standart sapması", plain(s["s"], 4), f"σ_p̂ = {plain(s['se'], 4)}, (12.8)."),
        SimMetric("p ± 2σ_p̂ içindeki pay", plain(s["pay"], 3),
                  f"Binom dağılımında tam olarak {plain(two_se_probability(n, p), 3)}; normal yaklaşımda yaklaşık "
                  "0,954."),
        SimMetric("np ve n(1 − p)", f"{_short(n * p, 2)} ve {_short(n * (1 - p), 2)}", condition),
    )


def _proportion_takeaway(state: LabState, parameters: Parameters) -> str:
    p, n, reps = _proportion_settings(parameters)
    s = state.scalars
    text = (
        f"{reps} örneklemin oranları p = {plain(p, 2)} çevresinde toplanır: ortalamaları {plain(s['ortalama'], 4)}. "
        f"p̂ yansızdır, E(p̂) = p (12.7). Standart sapmaları {plain(s['s'], 4)}; formül σ_p̂ = √(p(1 − p)/n) = "
        f"{plain(s['se'], 4)} (12.8). n dört katına çıkınca standart hata yarıya iner. "
    )
    if _normal_condition(n, p):
        text += "np ve n(1 − p) en az 5 olduğundan dağılım normal eğriye yakındır (12.10). "
    else:
        text += ("Koşul (12.10) sağlanmıyor: p̂ yalnız birkaç değere yığılır ve dağılım çarpıktır; normal eğri iyi bir "
                 "yaklaşım değildir. ")
    if (p, n) == (0.40, 100):
        text += "Bu ayar Şekil 12.10'un sağ panelidir: σ_p̂ = 0,049."
    elif (p, n) == (0.40, 25):
        text += "Bu ayar Şekil 12.10'un sol panelidir: σ_p̂ = 0,098."
    else:
        text += "p = 0,40 ile n = 25 ve n = 100 Şekil 12.10'un iki panelini verir."
    return text


SAMPLE_PROPORTION = SimExperiment(
    topic_key=TOPIC,
    number=3,
    title="Örneklem oranı: merkez p, yayılım √(p(1 − p)/n)",
    question="Anakütlede bir özelliğe sahip birimlerin oranı p ise, n birimlik örneklemlerin oranları p̂ nasıl "
             "dağılır; n büyüdükçe ve p değiştikçe bu dağılım nasıl değişir?",
    note=NoteRef("12.10", objects=("Şekil 12.10", "(12.8)", "(12.10)")),
    parameters=(
        SimParameter("p", "Anakütle oranı p", 0.05, 0.95, 0.40, 0.05, "Şekil 12.10'da p = 0,40.", decimals=2),
        SimParameter("n", "Örneklem büyüklüğü n", 10, 500, 100, 5, "Şekil 12.10: n = 25 ve n = 100.", integer=True,
                     decimals=0),
        SimParameter("tekrar", "Örneklem sayısı", 500, 10000, 5000, 500, "Her tekrarda yeni bir örneklem çekilir.",
                     integer=True, decimals=0),
    ),
    dgp=_proportion_dgp,
    dgp_note=(
        "Anakütle çok büyük kabul edilir; birimlerin p oranı özelliğe sahiptir. Bu yüzden n birimlik rassal "
        "örneklemdeki özellikli birim sayısı Bin(n, p) dağılımına sahiptir (Konu 9). Her tekrar yeni bir örneklemdir; "
        "tohum 217'dir. Histogramın her kutusu p̂'nin alabileceği tek bir değeri (k/n) içerir."
    ),
    look_at=(
        "**Histogram** — örneklem oranlarının p çevresindeki dağılımı ve normal eğri; n'yi 25'ten 100'e çıkarınca "
        "genişliğin yarıya indiğini izleyin.",
        "**Metrikler** — p̂'lerin ortalaması ve standart sapması ile (12.7)–(12.8); koşul (12.10) bozulunca normal "
        "eğrinin uyumu.",
    ),
    build=_build_proportion,
    metrics=_proportion_metrics,
    takeaway=_proportion_takeaway,
    labels=(("p_sapka", "Örneklem oranı p̂"), ("x", "Özellikli birim sayısı")),
)


KONU12_EXPERIMENTS = (CONSISTENCY, CENTRAL_LIMIT, SAMPLE_PROPORTION)
